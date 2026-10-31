"""T2 synthetic annotation imports; no fabricated human review evidence."""

from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from audit import validate_annotations


class AnnotationTests(unittest.TestCase):
    def fixture(self):
        packet = {"rubric_sha256": "rubric-v1", "cases": [{"audit_id": "sample-1", "claims": {"claims": [1]}}]}
        document = {"annotator_id": "synthetic-test-rater", "qualification": "test-only mock, not human evidence",
            "rubric_sha256": "rubric-v1", "annotations": [{"audit_id": "sample-1", "claim_states": ["supported"],
                "question_correct": True, "rationale": "test-only", "minutes": 1}]}
        return packet, document

    def test_missing_unknown_duplicate_annotations(self):
        for mutation in ["missing", "unknown", "duplicate"]:
            packet, document = self.fixture()
            if mutation == "missing": document["annotations"] = []
            elif mutation == "unknown": document["annotations"][0]["audit_id"] = "other"
            else: document["annotations"].append(deepcopy(document["annotations"][0]))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_annotations(document, packet)

    def test_blank_template_is_not_evidence(self):
        packet, document = self.fixture()
        document["annotations"][0]["claim_states"] = [None]
        with self.assertRaisesRegex(ValueError, "incomplete_claim_annotations"):
            validate_annotations(document, packet)

    def test_uncertain_truth_requires_reason(self):
        packet, document = self.fixture()
        document["annotations"][0]["question_correct"] = None
        with self.assertRaisesRegex(ValueError, "truth_uncertainty_reason"):
            validate_annotations(document, packet)
        document["annotations"][0]["unresolved_truth_reason"] = "test-only insufficient evidence"
        self.assertEqual(len(validate_annotations(document, packet)), 1)
