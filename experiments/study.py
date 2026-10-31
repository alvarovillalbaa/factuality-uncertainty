"""Versioned synthetic study; preserve original rows and replay every verdict."""

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import math
from pathlib import Path
import random
import statistics
import subprocess
import sys
import time

from factuality_uncertainty import verify, select
from factuality_uncertainty.calibration import fit, predict, scores, validate_splits
from factuality_uncertainty.io import digest, encode, load, write
from factuality_uncertainty.verification import DEFAULT_POLICY

ROOT = Path(__file__).resolve().parents[1]
POLICIES = {"direct": {"retrieval": False}, "retrieval": {}, "citations": {},
            "literal": {"adapter": "literal", "numeric": False}, "structured": {},
            "abstention": {}, "no-retrieval": {"retrieval": False},
            "no-decomposition": {"decomposition": False}, "no-time": {"time_filter": False},
            "no-numeric": {"numeric": False}, "no-conflicts": {"contradictions": False},
            "oracle-evidence": {}}


def source_revision():
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def inputs():
    rows, labels = load(ROOT / "fixtures/tasks.json"), load(ROOT / "fixtures/labels.json")
    manifest = load(ROOT / "fixtures/manifest.json")
    validate_splits(rows)
    ordered = [{"row_id": r["row_id"], "sha256": digest(r)} for r in rows]
    if ordered != manifest["ordered_rows"] or digest(ordered) != manifest["sample_manifest_id"]:
        raise ValueError("sample_manifest_mismatch")
    if digest(labels) != manifest["labels_sha256"] or [r["row_id"] for r in rows] != [r["row_id"] for r in labels]:
        raise ValueError("label_manifest_mismatch")
    return rows, {r["row_id"]: r for r in labels}


def frozen():
    seal = load(ROOT / "protocols/freeze.json")
    for name, sha in seal["files"].items():
        committed = subprocess.check_output(["git", "show", "HEAD:" + name], cwd=ROOT)
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha or hashlib.sha256(committed).hexdigest() != sha:
            raise ValueError("changed_frozen_input:" + name)


def freeze():
    if (ROOT / "protocols/freeze.json").exists():
        raise ValueError("preserve_original_freeze")
    paths = [p for folder in ["src", "experiments", "fixtures", "rubrics", "protocols", "schemas"]
             for p in (ROOT / folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    files = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    write(ROOT / "protocols/freeze.json", {"version": "0.1.0", "parent_revision": source_revision(), "files": files})


def calibration():
    rows, labels = inputs()
    selected = [r | {"correct": labels[r["row_id"]]["correct"]} for r in rows if r["split"] == "calibration"]
    target = ROOT / "protocols/calibration.json"
    if target.exists():
        raise ValueError("preserve_original_calibration")
    write(target, {arm: fit(selected, policy_sha256=digest(DEFAULT_POLICY | policy)) for arm, policy in POLICIES.items()})


def evaluate(row, arm, calibrator):
    # The supplied corpus is exhaustive. Oracle evidence is an explicit identity
    # diagnostic: it cannot invent missing, denied or future facts.
    evidence = row["evidence"]
    started = time.perf_counter_ns()
    result = verify(row["claims"], evidence, POLICIES[arm], calibrator=calibrator)
    elapsed_ns = time.perf_counter_ns() - started
    factual = [x for x in result["results"] if x["state"] != "not_fact_checkable"]
    if arm in {"direct", "retrieval", "citations"}:
        action = "answer"
        rank = row["raw_probability"]
    elif arm == "abstention":
        action = select(result)["action"]
        rank = sum(x["state"] == "supported" for x in factual) / max(1, len(factual))
    else:
        action = "answer" if all(x["state"] == "supported" for x in factual) and factual else "abstain"
        rank = sum(x["state"] == "supported" for x in factual) / max(1, len(factual))
    return {"row_id": row["row_id"], "family": row["family"], "split": row["split"],
            "arm": arm, "action": action, "rank": rank, "raw_probability": row["raw_probability"],
            "result": result, "elapsed_ns": elapsed_ns, "provider_calls": 0, "provider_spend_eur": 0}


def summary(selected, tasks, labels):
    asserted = [r for r in selected if r["action"] == "answer"]
    claims, unsupported, correct_claims, citations, good_citations, numeric_errors, numeric_detected = 0, 0, 0, 0, 0, 0, 0
    numeric_negatives, numeric_false_alarms, retrievable, retrieved, misread = 0, 0, 0, 0, 0
    reference_count = sum(labels[r["row_id"]]["reference_claims"] for r in selected)
    states, reasons = Counter(), Counter()
    for row in selected:
        label = labels[row["row_id"]]
        for i, verdict in enumerate(row["result"]["results"]):
            states[verdict["state"]] += 1
            reasons.update(verdict["reason_codes"])
            if label["claim_states"][i] == "supported":
                retrievable += 1
                retrieved += verdict["sources_considered"] > 0
                misread += verdict["sources_considered"] > 0 and verdict["state"] != "supported"
            if row in asserted and verdict["state"] != "not_fact_checkable":
                claims += 1
                unsupported += label["claim_states"][i] not in {"supported", "not_fact_checkable"}
                correct_claims += label["claim_correct"][i]
            if row["arm"] != "direct":
                citations += len(verdict["support"])
                # A supportive quote can remain relevant even when another source contradicts it.
                good_citations += len(verdict["support"]) * (label["claim_states"][i] == "supported" or
                                                           tasks[row["row_id"]]["kind"] == "conflict")
            if verdict["claim_type"] == "numeric":
                numeric_errors += not label["claim_correct"][i]
                numeric_detected += not label["claim_correct"][i] and any(c["status"] == "fail" for c in verdict["numeric_checks"])
                numeric_negatives += label["claim_correct"][i]
                numeric_false_alarms += label["claim_correct"][i] and any(c["status"] == "fail" for c in verdict["numeric_checks"])
    elapsed = sorted(r["elapsed_ns"] / 1e6 for r in selected)
    raw = scores([r["raw_probability"] for r in selected], [labels[r["row_id"]]["correct"] for r in selected])
    calibrated_rows = [r for r in selected if r["result"]["question_confidence"]["empirical_calibrated"]["value"] is not None]
    calibrated = scores([r["result"]["question_confidence"]["empirical_calibrated"]["value"] for r in calibrated_rows],
                        [labels[r["row_id"]]["correct"] for r in calibrated_rows]) if calibrated_rows else None
    return {"scheduled": len(selected), "attempted": len(selected), "unattempted": 0,
            "independent_source_families": len({r["family"] for r in selected}), "answered": len(asserted),
            "coverage": len(asserted) / len(selected), "abstention": sum(r["action"] == "abstain" for r in selected),
            "escalation": sum(r["action"] == "review" for r in selected),
            "correct_answer_fraction_of_scheduled": sum(labels[r["row_id"]]["correct"] for r in asserted) / len(selected),
            "errors_among_accepted": sum(not labels[r["row_id"]]["correct"] for r in asserted),
            "asserted_factual_claims": claims, "unsupported_claims": unsupported,
            "unsupported_assertion_rate": unsupported / claims if claims else None,
            "correct_claim_recall": correct_claims / reference_count if reference_count else None,
            "citation_count": citations, "citation_precision_fixture_rubric": good_citations / citations if citations else None,
            "numeric_error_count": numeric_errors, "numeric_detected": numeric_detected,
            "numeric_sensitivity": numeric_detected / numeric_errors if numeric_errors else None,
            "numeric_specificity": 1 - numeric_false_alarms / numeric_negatives if numeric_negatives else None,
            "evidence_retrieval_recall": retrieved / retrievable if retrievable else None,
            "retrieved_but_misread_claims": misread,
            "states": dict(states), "reason_codes": dict(reasons), "raw_calibration": raw,
            "empirical_calibration": calibrated, "calibration_unavailable": len(selected) - len(calibrated_rows),
            "latency_ms": {"median": statistics.median(elapsed), "p95": elapsed[math.ceil(.95 * len(elapsed)) - 1]},
            "provider_spend_eur": 0, "human_audit_minutes": None}


def analyze(records, tasks, labels, protocol):
    cells = defaultdict(list)
    for r in records:
        cells[(r["split"], r["arm"])].append(r)
    summaries = {split + ":" + arm: summary(rows, tasks, labels) for (split, arm), rows in sorted(cells.items())}
    matched, curves = {}, {}
    for split in sorted({r["split"] for r in records}):
        strict = cells[(split, "abstention")]
        k = sum(r["action"] == "answer" for r in strict)
        arm_selected = {}
        for arm in POLICIES:
            ordered = sorted(cells[(split, arm)], key=lambda r: (-r["rank"], r["row_id"]))
            chosen = ordered[:k]
            arm_selected[arm] = {r["row_id"] for r in chosen}
            matched[split + ":" + arm] = {"answered": k, "coverage": k / len(ordered),
                "selected_ids": [r["row_id"] for r in chosen],
                "unsupported_assertion_rate": summary([r | {"action": "answer"} for r in chosen], tasks, labels)["unsupported_assertion_rate"] if chosen else None,
                "question_error_rate": statistics.mean(not labels[r["row_id"]]["correct"] for r in chosen) if chosen else None}
            curves[split + ":" + arm] = [{"coverage": n / len(ordered), "accepted": n,
                "risk": statistics.mean(not labels[r["row_id"]]["correct"] for r in ordered[:n])}
                for n in sorted({max(1, math.ceil(len(ordered) * x / 10)) for x in range(1, 11)})]
        groups = sorted({r["family"] for r in strict})
        baseline, candidate = arm_selected["retrieval"], arm_selected["abstention"]
        paired = []
        for group in groups:
            group_rows = [r for r in strict if r["family"] == group]
            paired.append(sum((r["row_id"] in candidate) * int(labels[r["row_id"]]["correct"]) -
                              (r["row_id"] in baseline) * int(labels[r["row_id"]]["correct"]) for r in group_rows) / len(group_rows))
        rng = random.Random(protocol["bootstrap_seed"])
        distribution = sorted(statistics.mean(rng.choices(paired, k=len(paired))) for _ in range(protocol["bootstrap_resamples"]))
        matched[split + ":paired"] = {"independent_families": len(groups),
            "difference_correct_scheduled_at_matched_coverage": statistics.mean(paired),
            "cluster_interval_95": [distribution[int(.025 * len(distribution))], distribution[int(.975 * len(distribution))]],
            "inference": "descriptive conditional on invented templates; not human/model/physical population proof"}
    return {"summaries": summaries, "matched_coverage": matched, "risk_coverage": curves,
            "promotion": "not_evaluated_human_audit_pending"}


def run(stage):
    if stage == "main":
        frozen()
    rows, labels = inputs()
    protocol = load(ROOT / "protocols/study.json")
    stages = ["pilot"] if stage == "pilot" else ["test", "shift"]
    selected = [r for r in rows if r["split"] in stages]
    maps = load(ROOT / "protocols/calibration.json") if stage == "main" else {a: None for a in POLICIES}
    target = ROOT / "reports" / stage
    if target.exists():
        raise ValueError("preserve_original_study")
    target.mkdir(parents=True)
    started = time.perf_counter()
    records = []
    for row in selected:
        for arm in POLICIES:
            records.append(evaluate(row, arm, maps[arm]))
    (target / "rows.json.gz").write_bytes(gzip.compress(encode(records), mtime=0))
    write(target / "analysis.json", analyze(records, {r["row_id"]: r for r in rows}, labels, protocol))
    write(target / "execution.json", {"source_revision": source_revision(), "python": sys.version,
        "protocol_sha256": digest(protocol), "records_sha256": hashlib.sha256((target / "rows.json.gz").read_bytes()).hexdigest(),
        "scheduled": len(selected) * len(POLICIES), "attempted": len(records), "unattempted": 0,
        "elapsed_seconds": time.perf_counter() - started, "provider_calls": 0, "provider_spend_eur": 0,
        "excluded_arms": ["hosted providers", "licensed benchmarks", "human annotation"],
        "missing_measurements": ["physical energy", "GPU hours (no GPU)", "human audit time"]})
    print({"stage": stage, "records": len(records), "output": str(target.relative_to(ROOT))})


def replay(stage):
    rows, labels = inputs()
    records = __import__("json").loads(gzip.decompress((ROOT / "reports" / stage / "rows.json.gz").read_bytes()))
    tasks = {r["row_id"]: r for r in rows}
    maps = load(ROOT / "protocols/calibration.json") if stage == "main" else {a: None for a in POLICIES}
    expected = {(r["row_id"], a) for r in rows if r["split"] in (["pilot"] if stage == "pilot" else ["test", "shift"]) for a in POLICIES}
    if len(records) != len(expected) or {(r["row_id"], r["arm"]) for r in records} != expected:
        raise ValueError("incomplete_schedule")
    for record in records:
        fresh = evaluate(tasks[record["row_id"]], record["arm"], maps[record["arm"]])
        for key in record:
            if key != "elapsed_ns" and record[key] != fresh[key]:
                raise ValueError("replay_difference:" + key)
    if analyze(records, tasks, labels, load(ROOT / "protocols/study.json")) != load(ROOT / "reports" / stage / "analysis.json"):
        raise ValueError("analysis_replay_difference")
    print({"stage": stage, "replay": "PASS", "records": len(records)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["pilot", "calibrate", "freeze", "main", "replay"])
    args = parser.parse_args()
    if args.mode == "freeze": freeze()
    elif args.mode == "calibrate": calibration()
    elif args.mode == "replay":
        frozen()
        replay("pilot")
        replay("main")
    else: run(args.mode)
