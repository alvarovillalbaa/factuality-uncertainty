"""Blinded packets and strict independent annotation import; never invent labels."""

import argparse
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

from factuality_uncertainty.io import digest, load, write
from factuality_uncertainty.verification import STATES

ROOT = Path(__file__).resolve().parents[1]


def packet():
    rows = load(ROOT / "fixtures/tasks.json")
    groups = defaultdict(list)
    for row in rows:
        if row["split"] in {"pilot", "test", "shift"}:
            groups[(row["split"], row["kind"])].append(row)
    selected = [min(group, key=lambda r: digest(r["row_id"])) for _, group in sorted(groups.items())]
    cases, mapping = [], []
    for row in selected:
        audit_id = digest(["ai02-audit-v1", row["row_id"]])[:24]
        claims, evidence = deepcopy(row["claims"]), deepcopy(row["evidence"])
        claims["bundle_id"] = audit_id
        claims.pop("raw_probability", None)
        claims.pop("family", None)
        for index, claim in enumerate(claims["claims"]):
            claim["claim_id"] = f"claim-{index + 1}"
            claim.pop("model_confidence", None)
        for index, source in enumerate(evidence["sources"]):
            source["source_id"] = f"source-{index + 1}"
        cases.append({"audit_id": audit_id, "claims": claims, "evidence": evidence})
        mapping.append({"audit_id": audit_id, "row_id": row["row_id"], "split": row["split"], "stratum": row["kind"]})
    cases.sort(key=lambda r: r["audit_id"])
    rubric = (ROOT / "rubrics/source-support.md").read_bytes()
    import hashlib
    target = ROOT / "audit"
    if target.exists():
        raise ValueError("preserve_existing_audit_packet")
    write(target / "packet.json", {"version": "0.1.0", "rubric_sha256": hashlib.sha256(rubric).hexdigest(),
        "sample_policy": "one smallest-hash row per split and scenario stratum; arm/confidence/design labels removed",
        "cases": cases})
    write(target / "private-map.json", mapping)
    write(target / "annotation-template.json", {"annotator_id": None, "qualification": None,
        "rubric_sha256": hashlib.sha256(rubric).hexdigest(), "annotations": [
            {"audit_id": c["audit_id"], "claim_states": [None for _ in c["claims"]["claims"]],
             "question_correct": None, "unresolved_truth_reason": None, "rationale": None, "minutes": None}
            for c in cases]})
    print({"cases": len(cases), "status": "awaiting_two_independent_annotators", "human_labels_created": 0})


def validate_annotations(document, packet):
    for key in ["annotator_id", "qualification"]:
        if not isinstance(document.get(key), str) or not document[key].strip():
            raise ValueError("missing_" + key)
    if document.get("rubric_sha256") != packet["rubric_sha256"]:
        raise ValueError("rubric_mismatch")
    expected = {c["audit_id"]: len(c["claims"]["claims"]) for c in packet["cases"]}
    indexed = {}
    for item in document["annotations"]:
        identity = item["audit_id"]
        if identity in indexed or identity not in expected:
            raise ValueError("duplicate_or_unknown_audit_id")
        if len(item["claim_states"]) != expected[identity] or any(s not in STATES for s in item["claim_states"]):
            raise ValueError("incomplete_claim_annotations")
        if type(item["question_correct"]) not in {bool, type(None)}:
            raise ValueError("invalid_correctness_label")
        if item["question_correct"] is None and not item.get("unresolved_truth_reason"):
            raise ValueError("missing_truth_uncertainty_reason")
        if not isinstance(item.get("rationale"), str) or not item["rationale"].strip():
            raise ValueError("missing_annotation_rationale")
        minutes = item.get("minutes")
        if type(minutes) not in {int, float} or not 0 < minutes <= 480:
            raise ValueError("invalid_annotation_time")
        indexed[identity] = item
    if set(indexed) != set(expected):
        raise ValueError("missing_annotations")
    return indexed


def import_pair(first, second, output):
    source = load(ROOT / "audit/packet.json")
    left, right = load(first), load(second)
    if left["annotator_id"] == right["annotator_id"]:
        raise ValueError("independent_annotators_required")
    a, b = validate_annotations(left, source), validate_annotations(right, source)
    disagreement = [key for key in a if (a[key]["claim_states"], a[key]["question_correct"]) !=
                    (b[key]["claim_states"], b[key]["question_correct"])]
    unresolved = [key for key in a if a[key]["question_correct"] is None or b[key]["question_correct"] is None]
    if Path(output).exists():
        raise ValueError("preserve_original_audit_import")
    write(output, {"packet_sha256": digest(source), "annotation_sha256": [digest(left), digest(right)],
        "annotators": [left["annotator_id"], right["annotator_id"]], "cases": len(a),
        "disagreement_count": len(disagreement), "disagreement_rate": len(disagreement) / len(a),
        "adjudication_required": disagreement, "unresolved_truth": unresolved,
        "minutes": sum(x["minutes"] for d in [a, b] for x in d.values()),
        "status": "adjudication_or_truth_evidence_required" if disagreement or unresolved else "independent_annotations_received",
        "release_promotion": "requires_review_of_joined_evidence_and_new_report_version",
        "annotations": [left, right]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["packet", "import"])
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()
    if args.mode == "packet":
        packet()
    elif len(args.paths) == 3:
        import_pair(*args.paths)
    else:
        parser.error("import requires annotator1.json annotator2.json output.json")
