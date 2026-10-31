"""FND-01 artifact envelope export; no domain judgment delegated to schemas."""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from research_contracts import validate, verify_payloads

from .io import write


def export(directory, payload, *, revision, artifact_id="ai02-verification"):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    payload_path = directory / "verification.json"
    envelope_path = directory / "artifact.json"
    if payload_path.exists() or envelope_path.exists():
        raise ValueError("preserve_existing_export")
    write(payload_path, payload)
    envelope = {"schema_version": "0.1.0", "artifact_id": artifact_id, "project_id": "AI-02",
        "artifact_type": "claim-verification", "producer_version": "0.1.0",
        "payload_path": "verification.json", "payload_sha256": hashlib.sha256(payload_path.read_bytes()).hexdigest(),
        "payload_schema": "urn:ai02:verification:0.1.0", "evidence_class": "synthetic_fixture",
        "units": {"verifier_score": "binary support indicator, not probability"},
        "provenance": {"source_refs": ["urn:ai02:local-authorized-evidence"],
                       "created_at": datetime.now(timezone.utc).isoformat(), "producer_revision": revision,
                       "parent_artifact_ids": []},
        "limitations": ["Source support is not truth or permission to act.",
                        "Deterministic typed claims only; no qualified human annotation claimed."]}
    errors = validate(envelope, "artifact", root=directory) + verify_payloads(envelope, root=directory)
    if errors:
        raise ValueError(errors)
    write(envelope_path, envelope)
    return envelope
