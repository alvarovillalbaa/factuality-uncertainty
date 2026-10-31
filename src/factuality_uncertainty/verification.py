"""Two deterministic source-support adapters over explicitly typed claims."""

from datetime import datetime
import re

from .io import digest, encode
from .numeric import check, number
from .schema import CLAIM_BUNDLE, EVIDENCE_BUNDLE, validate

STATES = {"supported", "contradicted", "insufficient_evidence", "not_fact_checkable"}
DEFAULT_POLICY = {"adapter": "structured", "scopes": ["public"],
                  "time_filter": True, "numeric": True, "contradictions": True,
                  "retrieval": True, "decomposition": True, "max_sources": 100}


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone_required")
    return parsed


def sentence(fact):
    tail = "" if fact.get("unit") is None else " " + fact["unit"]
    qualifiers = "".join(" [" + q + "]" for q in sorted(fact.get("qualifiers", [])))
    return f"{fact['subject']} {fact['predicate']} {fact['value']}{tail}{qualifiers}."


def _unique(items, field):
    values = [x[field] for x in items]
    if len(set(values)) != len(values):
        raise ValueError("duplicate_" + field)


def validate_input(bundle, evidence):
    if len(encode([bundle, evidence])) > 16 * 1024 * 1024:
        raise ValueError("input_too_large")
    validate(bundle, CLAIM_BUNDLE)
    validate(evidence, EVIDENCE_BUNDLE)
    if bundle.get("version") != "0.1.0" or evidence.get("version") != "0.1.0":
        raise ValueError("unknown_version")
    claims = bundle["claims"]
    sources = evidence["sources"]
    if not claims or len(claims) > 1000 or len(sources) > 1000:
        raise ValueError("invalid_input_count")
    _unique(claims, "claim_id")
    _unique(sources, "source_id")
    for claim in claims:
        start, end = claim["answer_span"]
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(bundle["answer"]):
            raise ValueError("invalid_answer_span")
        if bundle["answer"][start:end] != claim["text"]:
            raise ValueError("answer_span_mismatch")
        if claim["claim_type"] not in {"text", "numeric", "opinion"}:
            raise ValueError("unknown_claim_type")
        timestamp(claim["as_of"])
        if claim["claim_type"] != "opinion" and sentence(claim) != claim["text"]:
            raise ValueError("typed_claim_text_mismatch")
        if "model_confidence" in claim and not 0 <= number(claim["model_confidence"]) <= 1:
            raise ValueError("invalid_confidence")
    for source in sources:
        required = ["source_id", "version", "domain", "access_scope", "quality", "published_at",
                    "as_of", "retrieved_at", "sha256", "text", "facts", "license"]
        if any(key not in source for key in required) or source["version"] in {"latest", "main", "HEAD"}:
            raise ValueError("incomplete_source_provenance")
        import hashlib
        if hashlib.sha256(source["text"].encode("utf-8")).hexdigest() != source["sha256"]:
            raise ValueError("source_hash_mismatch")
        for key in ["published_at", "as_of", "retrieved_at"]:
            timestamp(source[key])
        if timestamp(source["published_at"]) > timestamp(source["retrieved_at"]):
            raise ValueError("retrieval_before_publication")
        for fact in source["facts"]:
            start, end = fact["quote_span"]
            if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(source["text"]):
                raise ValueError("invalid_quote_span")
            if source["text"][start:end] != sentence(fact):
                raise ValueError("typed_source_text_mismatch")
            timestamp(fact["valid_from"])
            if fact.get("valid_until") is not None:
                if timestamp(fact["valid_until"]) <= timestamp(fact["valid_from"]):
                    raise ValueError("invalid_validity_interval")


def _citation(source, fact):
    return {key: source[key] for key in ["source_id", "version", "sha256", "published_at",
            "as_of", "retrieved_at", "access_scope", "quality", "license"]} | {
        "quote_span": fact["quote_span"],
        "quote": source["text"][fact["quote_span"][0]:fact["quote_span"][1]]}


def _literal(claim, fact, source):
    # Whole quoted sentence equality, never a substring that could omit negation.
    quote = source["text"][fact["quote_span"][0]:fact["quote_span"][1]]
    return re.sub(r"\s+", " ", claim["text"].strip()) == re.sub(r"\s+", " ", quote.strip())


def _structured(claim, fact):
    if claim.get("unit") is not None and fact.get("unit") is not None:
        # Prose support ignores the units: the independent numeric check owns them.
        try:
            return number(claim["value"]) == number(fact["value"])
        except ValueError:
            return False
    return str(claim["value"]).casefold() == str(fact["value"]).casefold()


def verify(claims, evidence, policy=None, *, calibrator=None):
    """Verify a ClaimBundle against supplied local EvidenceBundle; no I/O/tools."""
    validate_input(claims, evidence)
    effective = DEFAULT_POLICY | (policy or {})
    if set(effective) != set(DEFAULT_POLICY) or effective["adapter"] not in {"literal", "structured"}:
        raise ValueError("unknown_policy")
    if not effective["scopes"] or type(effective["max_sources"]) is not int or effective["max_sources"] < 0:
        raise ValueError("invalid_policy")
    for key in ["time_filter", "numeric", "contradictions", "retrieval", "decomposition"]:
        if type(effective[key]) is not bool:
            raise ValueError("invalid_policy_boolean")
    results = []
    for index, claim in enumerate(claims["claims"]):
        supported, contrary, reasons, numeric = [], [], [], []
        considered = 0
        if claim["claim_type"] == "opinion":
            state = "not_fact_checkable"
            reasons = ["opinion_outside_factual_event"]
        else:
            if not effective["retrieval"]:
                reasons.append("retrieval_disabled")
            if not effective["decomposition"] and index > 0:
                reasons.append("claim_not_decomposed")
            candidates = evidence["sources"] if not reasons else []
            for source in candidates:
                if source["access_scope"] not in effective["scopes"]:
                    reasons.append("evidence_excluded_by_scope")
                    continue
                if source["domain"] != claim["domain"]:
                    reasons.append("irrelevant_domain")
                    continue
                when = timestamp(claim["as_of"])
                if effective["time_filter"] and (timestamp(source["published_at"]) > when or
                        timestamp(source["as_of"]) > when):
                    reasons.append("evidence_from_future")
                    continue
                if considered >= effective["max_sources"]:
                    reasons.append("retrieval_budget_exhausted")
                    continue
                considered += 1
                for fact in source["facts"]:
                    if (fact["subject"], fact["predicate"]) != (claim["subject"], claim["predicate"]):
                        continue
                    if effective["time_filter"] and (timestamp(fact["valid_from"]) > when or
                            fact.get("valid_until") and when >= timestamp(fact["valid_until"])):
                        reasons.append("evidence_outside_validity")
                        continue
                    if set(fact.get("qualifiers", [])) != set(claim.get("qualifiers", [])):
                        reasons.append("qualifier_scope_mismatch")
                        continue
                    citation = _citation(source, fact)
                    match = (_literal(claim, fact, source) if effective["adapter"] == "literal"
                             else _structured(claim, fact))
                    if effective["numeric"] and claim["claim_type"] == "numeric":
                        checked = check(claim, fact)
                        numeric.append(checked | {"source_id": source["source_id"]})
                        if checked["status"] == "fail":
                            contrary.append(citation)
                            reasons.extend(checked["failures"])
                            continue
                        # Equivalent converted quantities remain supportable.
                        match = True
                    (supported if match else contrary).append(citation)
            if contrary and effective["contradictions"]:
                state = "contradicted"
                reasons.append("conflicting_evidence" if supported else "contrary_evidence")
            elif supported:
                state = "supported"
            else:
                state = "insufficient_evidence"
                reasons.append("no_supporting_authorized_evidence")
        results.append({"claim_id": claim["claim_id"], "claim_type": claim["claim_type"], "text": claim["text"],
            "answer_span": claim["answer_span"], "state": state, "support": supported,
            "contradictions": contrary, "numeric_checks": numeric,
            "reason_codes": sorted(set(reasons)), "sources_considered": considered,
            "confidence": {"model_elicited": claim.get("model_confidence"),
                "verifier": {"method": effective["adapter"] + "-deterministic-v1",
                             "score": int(state == "supported"), "is_probability": False},
                "empirical_calibrated": None, "unavailable_reason": "no_applicable_calibration_supplied"},
            "suggested_action": "answer" if state == "supported" else "review" if contrary else "abstain",
            "unresolved_requirements": [] if state == "supported" else
                ["consistent authorized evidence valid at claim as_of with matching qualifiers and assumptions"]})
    probability = {"value": None, "reason": "no_applicable_calibration_supplied"}
    if calibrator is not None:
        from .calibration import predict
        if any(k not in claims for k in ["domain", "family", "raw_probability"]):
            raise ValueError("question_calibration_metadata_required")
        probability = predict(calibrator, claims["raw_probability"], domain=claims["domain"],
                              family=claims["family"], policy_sha256=digest(effective))
    return {"version": "0.1.0", "bundle_id": claims["bundle_id"],
            "claims_sha256": digest(claims), "evidence_sha256": digest(evidence),
            "policy_sha256": digest(effective), "results": results,
            "question_confidence": {"model_elicited": claims.get("raw_probability"),
                                    "empirical_calibrated": probability}}


def select(results, risk_policy=None):
    policy = {"require_numeric": True, "minimum_probability": None} | (risk_policy or {})
    if set(policy) != {"require_numeric", "minimum_probability"}:
        raise ValueError("unknown_risk_policy")
    threshold = policy["minimum_probability"]
    if threshold is not None and not 0 <= number(threshold) <= 1:
        raise ValueError("invalid_probability_threshold")
    factual = [r for r in results["results"] if r["state"] != "not_fact_checkable"]
    reasons = []
    if not factual:
        reasons.append("no_factual_answer")
    for result in factual:
        if result["state"] != "supported" or result["contradictions"]:
            reasons.append("unresolved_claim")
        if policy["require_numeric"] and result["claim_type"] == "numeric" and (
                not result["numeric_checks"] or any(c["status"] != "pass" for c in result["numeric_checks"])):
            reasons.append("numeric_check_failed")
    probability = results["question_confidence"]["empirical_calibrated"]
    if threshold is not None and (probability["value"] is None or probability["value"] < float(threshold)):
        reasons.append("calibration_unavailable_or_below_threshold")
    return {"action": "answer" if not reasons else "review" if any(
        r["contradictions"] for r in factual) else "abstain", "reason_codes": sorted(set(reasons))}
