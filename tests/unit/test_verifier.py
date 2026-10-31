"""T2 synthetic data: scope, integrity, arithmetic and calibrated selection."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from factuality_uncertainty import select, verify
from factuality_uncertainty.artifacts import export
from factuality_uncertainty.calibration import fit, predict, scores, validate_splits
from factuality_uncertainty.io import digest, load, write
from factuality_uncertainty.numeric import check
from factuality_uncertainty.verification import DEFAULT_POLICY, sentence

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "experiments"))
from dataset import CASES, case


class VerifierTests(unittest.TestCase):
    def fixture(self, kind="supported", track="short-question"):
        return case("development", 1, kind, track)

    def test_all_known_states(self):
        for kind in CASES:
            with self.subTest(kind=kind):
                row, label = self.fixture(kind)
                result = verify(row["claims"], row["evidence"])
                self.assertEqual(result["results"][0]["state"], label["state"])

    def test_conflict_preserved(self):
        row, _ = self.fixture("conflict")
        result = verify(row["claims"], row["evidence"])
        self.assertTrue(result["results"][0]["support"])
        self.assertTrue(result["results"][0]["contradictions"])
        self.assertEqual(select(result)["action"], "review")

    def test_no_scope_content_disclosure(self):
        row, _ = self.fixture("scope")
        result = verify(row["claims"], row["evidence"])["results"][0]
        self.assertFalse(result["support"] + result["contradictions"])
        self.assertNotIn(row["evidence"]["sources"][0]["source_id"], json.dumps(result))

    def test_poison_is_inert(self):
        row, _ = self.fixture("poison")
        result = verify(row["claims"], row["evidence"])["results"][0]
        self.assertEqual(result["state"], "supported")
        self.assertNotIn("shell", result["support"][0]["quote"])

    def test_span_identity_and_typed_text(self):
        row, _ = self.fixture()
        row["claims"]["claims"][0]["answer_span"][0] = 1
        with self.assertRaisesRegex(ValueError, "span_mismatch"):
            verify(row["claims"], row["evidence"])
        row, _ = self.fixture()
        row["claims"]["claims"][0]["value"] = "red"
        with self.assertRaisesRegex(ValueError, "typed_claim_text"):
            verify(row["claims"], row["evidence"])

    def test_conjunction_spans(self):
        row, _ = self.fixture(track="long-answer")
        result = verify(row["claims"], row["evidence"])
        self.assertEqual(len(result["results"]), 2)
        for claim in result["results"]:
            a, b = claim["answer_span"]
            self.assertEqual(row["claims"]["answer"][a:b], claim["text"])

    def test_hash_and_quote_binding(self):
        row, _ = self.fixture()
        row["evidence"]["sources"][0]["text"] += "tampered"
        with self.assertRaisesRegex(ValueError, "hash_mismatch"):
            verify(row["claims"], row["evidence"])
        row, _ = self.fixture()
        row["evidence"]["sources"][0]["facts"][0]["value"] = "red"
        with self.assertRaisesRegex(ValueError, "typed_source_text"):
            verify(row["claims"], row["evidence"])

    def test_duplicate_claim_and_source_ids(self):
        for key in ["claims", "sources"]:
            row, _ = self.fixture()
            container = row["claims"] if key == "claims" else row["evidence"]
            container[key].append(deepcopy(container[key][0]))
            with self.assertRaisesRegex(ValueError, "duplicate"):
                verify(row["claims"], row["evidence"])

    def test_temporal_exclusions(self):
        for kind, reason in [("future", "evidence_from_future"), ("stale", "evidence_outside_validity")]:
            row, _ = self.fixture(kind)
            self.assertIn(reason, verify(row["claims"], row["evidence"])["results"][0]["reason_codes"])

    def test_qualifier_omission(self):
        row, _ = self.fixture("qualifier")
        self.assertEqual(select(verify(row["claims"], row["evidence"]))["action"], "abstain")

    def test_independent_literal_approach(self):
        row, _ = self.fixture("supported")
        result = verify(row["claims"], row["evidence"], {"adapter": "literal"})
        self.assertEqual(result["results"][0]["state"], "supported")
        self.assertEqual(result["results"][0]["confidence"]["verifier"]["method"], "literal-deterministic-v1")

    def test_numeric_text_support_not_sufficient(self):
        row, _ = self.fixture("arithmetic")
        result = verify(row["claims"], row["evidence"], {"numeric": False})
        self.assertEqual(result["results"][0]["state"], "supported")
        self.assertNotEqual(select(result)["action"], "answer")

    def test_unknown_policy_rejected(self):
        row, _ = self.fixture()
        with self.assertRaisesRegex(ValueError, "unknown_policy"):
            verify(row["claims"], row["evidence"], {"exec": True})

    def test_output_contract_rejects_missing_provenance(self):
        from jsonschema import Draft202012Validator, FormatChecker
        root = Path(__file__).resolve().parents[2]
        validator = Draft202012Validator(load(root / "schemas/verification.schema.json"), format_checker=FormatChecker())
        row, _ = self.fixture()
        result = verify(row["claims"], row["evidence"])
        self.assertEqual(list(validator.iter_errors(result)), [])
        result["results"][0]["support"][0].pop("sha256")
        self.assertTrue(list(validator.iter_errors(result)))

    def test_confidence_types_and_missing_calibration(self):
        row, _ = self.fixture()
        result = verify(row["claims"], row["evidence"])
        confidence = result["results"][0]["confidence"]
        self.assertIsNone(confidence["empirical_calibrated"])
        self.assertFalse(confidence["verifier"]["is_probability"])
        self.assertEqual(select(result, {"minimum_probability": 0.8})["action"], "abstain")


class NumericTests(unittest.TestCase):
    def test_conversion_and_dimensional_mismatch(self):
        fact = {"value": "2000", "unit": "Wh"}
        self.assertEqual(check({"value": "2", "unit": "kWh"}, fact)["status"], "pass")
        self.assertIn("unit_mismatch", check({"value": "2000", "unit": "W"}, fact)["failures"])

    def test_tolerance_cannot_be_invented(self):
        self.assertIn("unauthorized_tolerance", check({"value": "99", "unit": "Wh", "tolerance": "100"},
                                                     {"value": "2", "unit": "Wh"})["failures"])

    def test_assumptions_and_bounds(self):
        result = check({"value": "5", "unit": "Wh"}, {"value": "5", "unit": "Wh",
                       "assumption_refs": ["nominal-temperature"], "bounds": ["0", "4"]})
        self.assertEqual(result["failures"], ["assumptions_mismatch", "outside_bounds"])

    def test_nonfinite_boolean_and_unknown_units(self):
        for value, unit in [("NaN", "Wh"), (True, "Wh"), ("1", "furlong")]:
            self.assertEqual(check({"value": value, "unit": unit}, {"value": "1", "unit": "Wh"})["status"], "fail")

    def test_zero_denominator_and_code_not_evaluated(self):
        claim = {"value": "1", "unit": "1", "arithmetic": {"op": "divide",
            "left": {"value": "1", "unit": "Wh"}, "right": {"value": "0", "unit": "Wh"}}}
        self.assertIn("unsupported_arithmetic", check(claim, {"value": "1", "unit": "1"})["failures"])
        claim["arithmetic"]["op"] = "__import__('os').system('false')"
        self.assertEqual(check(claim, {"value": "1", "unit": "1"})["status"], "fail")


class CalibrationAndExportTests(unittest.TestCase):
    def rows(self):
        return [{"row_id": str(i), "family": f"f{i}", "entity": f"e{i}", "document": f"d{i}",
                 "domain": "electrical", "split": "calibration", "raw_probability": 0.75, "correct": i % 2 == 0}
                for i in range(10)]

    def test_no_test_fit_or_cross_split_family(self):
        rows = self.rows()
        rows[0]["split"] = "test"
        with self.assertRaisesRegex(ValueError, "calibration_split_required"):
            fit(rows, policy_sha256="abc")
        for key in ["family", "entity", "document"]:
            rows = self.rows()
            rows[0]["split"] = "test"
            rows[1][key] = rows[0][key]
            with self.assertRaisesRegex(ValueError, "split_leakage"):
                validate_splits(rows)

    def test_scope_and_reuse_rejected(self):
        fitted = fit(self.rows(), policy_sha256="abc")
        for domain, family, policy, reason in [("thermal", "new", "abc", "domain_outside_calibration_scope"),
                ("electrical", "f0", "abc", "calibration_family_reuse"),
                ("electrical", "new", "changed", "policy_outside_calibration_scope")]:
            self.assertEqual(predict(fitted, 0.75, domain=domain, family=family, policy_sha256=policy)["reason"], reason)
        self.assertEqual(predict(fitted, 0.75, domain="electrical", family="new", policy_sha256="abc")["value"], 0.5)

    def test_question_probability_never_becomes_claim_probability(self):
        row, _ = case("development", 1, "supported", "short-question")
        fitted = fit(self.rows(), policy_sha256=digest(DEFAULT_POLICY))
        row["claims"].update(domain="electrical", family="new", raw_probability=0.75)
        result = verify(row["claims"], row["evidence"], calibrator=fitted)
        self.assertEqual(result["question_confidence"]["empirical_calibrated"]["value"], 0.5)
        self.assertIsNone(result["results"][0]["confidence"]["empirical_calibrated"])
        self.assertEqual(select(result, {"minimum_probability": 0.6})["action"], "abstain")

    def test_proper_scores_and_missing_bins(self):
        self.assertEqual(scores([0.9, 0.1], [True, False])["count"], 2)
        self.assertAlmostEqual(scores([0.9, 0.1], [True, False])["brier"], 0.01)
        fitted = fit(self.rows(), policy_sha256="abc")
        self.assertIsNone(predict(fitted, 0.1, domain="electrical", family="new", policy_sha256="abc")["value"])

    def test_fnd01_export_and_no_overwrite(self):
        row, _ = case("development", 1, "supported", "short-question")
        with tempfile.TemporaryDirectory(prefix="ai02-unit-") as tmp:
            result = verify(row["claims"], row["evidence"])
            envelope = export(tmp, result, revision="test-source-v1")
            self.assertEqual(envelope["project_id"], "AI-02")
            self.assertEqual(hashlib.sha256(Path(tmp, "verification.json").read_bytes()).hexdigest(), envelope["payload_sha256"])
            with self.assertRaisesRegex(ValueError, "preserve_existing_export"):
                export(tmp, result, revision="test-source-v1")

    def test_strict_json(self):
        with tempfile.TemporaryDirectory(prefix="ai02-json-") as tmp:
            path = Path(tmp) / "bad.json"
            for raw in ['{"x":1,"x":2}', '{"x":NaN}']:
                path.write_text(raw)
                with self.assertRaises(ValueError):
                    load(path)
