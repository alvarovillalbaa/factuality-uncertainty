"""Export FND-01 result records referencing the immutable study analysis."""

from datetime import datetime, timezone
import hashlib
from pathlib import Path

from research_contracts import validate, verify_payloads
from factuality_uncertainty.io import load, write

ROOT = Path(__file__).resolve().parents[1]


def main():
    target = ROOT / "reports/main/contracts"
    if target.exists():
        raise ValueError("preserve_original_contract_export")
    analysis = load(ROOT / "reports/main/analysis.json")
    analysis_ref = {"artifact_id": "ai02-main-analysis-v1", "hash_scope": "payload",
        "locator": "reports/main/analysis.json", "sha256": hashlib.sha256((ROOT / "reports/main/analysis.json").read_bytes()).hexdigest()}
    execution = load(ROOT / "reports/main/execution.json")
    artifact = {"schema_version": "0.1.0", "artifact_id": analysis_ref["artifact_id"], "project_id": "AI-02",
        "artifact_type": "synthetic-factuality-study", "producer_version": "0.1.0",
        "payload_path": analysis_ref["locator"], "payload_sha256": analysis_ref["sha256"],
        "payload_schema": "urn:ai02:study-analysis:0.1.0", "evidence_class": "synthetic_fixture",
        "units": {"coverage": "fraction of scheduled questions", "unsupported": "fraction of asserted factual claims"},
        "provenance": {"source_refs": ["urn:ai02:synthetic-v1"], "created_at": datetime.now(timezone.utc).isoformat(),
                       "producer_revision": execution["source_revision"], "parent_artifact_ids": []},
        "limitations": ["Independent pilot/final human annotations pending.", "Invented templates; no empirical model or physical claim."]}
    documents = [("artifact", artifact)]
    for name, summary in analysis["summaries"].items():
        split, arm = name.split(":")
        for metric, value in [("coverage", summary["coverage"]), ("unsupported", summary["unsupported_assertion_rate"])]:
            result = {"schema_version": "0.1.0", "result_id": f"ai02-{split}-{arm}-{metric}", "project_id": "AI-02",
                "experiment_id": "ai02-synthetic-v1", "arm_id": arm, "metric_id": metric,
                "evidence_class": "synthetic_fixture", "scheduled_count": summary["scheduled"], "unattempted_count": 0,
                "unattempted_reasons": [], "attempted_count": summary["attempted"], "valid_count": summary["attempted"],
                "failed_count": 0, "independent_unit_count": summary["independent_source_families"],
                "estimate": {"status": "reported" if value is not None else "not_estimated", "value": value,
                             "unit": "fraction", "method": "frozen synthetic rubric; full denominators in analysis payload"},
                "failures": [], "analysis_artifact": analysis_ref,
                "limitations": artifact["limitations"] + ["valid_count means structurally scored attempts, not correct/accepted answers."]}
            documents.append(("result", result))
    for index, (kind, document) in enumerate(documents):
        errors = validate(document, kind, root=ROOT) + verify_payloads(document, root=ROOT)
        if errors:
            raise ValueError(errors)
        write(target / f"{index:02}-{kind}.json", document)
    print({"fnd01_envelopes": len(documents), "status": "PASS"})


if __name__ == "__main__":
    main()
