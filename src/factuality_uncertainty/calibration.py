"""Held-out histogram calibration for a declared answer correctness event."""

from collections import defaultdict
import math
import statistics

from .io import digest

EVENT = "all_required_factual_claims_correct"


def validate_splits(rows):
    seen, identities = set(), {key: {} for key in ["family", "entity", "document"]}
    for row in rows:
        if row["row_id"] in seen:
            raise ValueError("duplicate_row_id")
        seen.add(row["row_id"])
        if row["split"] not in {"development", "pilot", "calibration", "test", "shift"}:
            raise ValueError("unknown_split")
        for key, mapping in identities.items():
            identity = row[key]
            if identity in mapping and mapping[identity] != row["split"]:
                raise ValueError("split_leakage:" + key)
            mapping[identity] = row["split"]


def _probability(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("invalid_probability")
    return value


def fit(rows, *, policy_sha256, bins=5):
    validate_splits(rows)
    if not rows or any(r["split"] != "calibration" for r in rows):
        raise ValueError("calibration_split_required")
    if bins != 5:
        raise ValueError("version_1_uses_five_fixed_bins")
    counts = defaultdict(list)
    for row in rows:
        if type(row["correct"]) is not bool:
            raise ValueError("boolean_label_required")
        counts[min(bins - 1, int(_probability(row["raw_probability"]) * bins))].append(row["correct"])
    return {"version": "0.1.0", "method": "five-bin-laplace-v1", "event": EVENT,
            "policy_sha256": policy_sha256, "calibration_sha256": digest(rows),
            "families": sorted({r["family"] for r in rows}),
            "domains": sorted({r["domain"] for r in rows}), "bins": bins,
            "cells": [{"count": len(counts[i]), "correct": sum(counts[i]),
                       "probability": (sum(counts[i]) + 1) / (len(counts[i]) + 2)} for i in range(bins)]}


def predict(calibrator, probability, *, domain, family, policy_sha256):
    _probability(probability)
    if calibrator["policy_sha256"] != policy_sha256:
        return {"value": None, "reason": "policy_outside_calibration_scope"}
    if family in calibrator["families"]:
        return {"value": None, "reason": "calibration_family_reuse"}
    if domain not in calibrator["domains"]:
        return {"value": None, "reason": "domain_outside_calibration_scope"}
    cell = calibrator["cells"][min(calibrator["bins"] - 1, int(probability * calibrator["bins"]))]
    if not cell["count"]:
        return {"value": None, "reason": "empty_calibration_bin"}
    return {"value": cell["probability"], "method": calibrator["method"],
            "event": EVENT, "calibration_sha256": calibrator["calibration_sha256"]}


def scores(probabilities, labels):
    if not probabilities or len(probabilities) != len(labels) or any(type(y) is not bool for y in labels):
        raise ValueError("invalid_scoring_pairs")
    cells = []
    for i in range(5):
        indexes = [j for j, p in enumerate(probabilities)
                   if min(4, int(_probability(p) * 5)) == i]
        cells.append({"lower": i / 5, "upper": (i + 1) / 5, "count": len(indexes),
                      "mean_probability": statistics.mean(probabilities[j] for j in indexes) if indexes else None,
                      "accuracy": statistics.mean(labels[j] for j in indexes) if indexes else None})
    # Clipping is solely a finite-log diagnostic rule, never a calibration claim.
    clipped = [min(1 - 1e-12, max(1e-12, p)) for p in probabilities]
    return {"count": len(labels), "brier": statistics.mean((p - y)**2 for p, y in zip(probabilities, labels)),
            "log_loss": -statistics.mean(math.log(p if y else 1 - p) for p, y in zip(clipped, labels)),
            "log_clip": 1e-12, "bins": cells,
            "ece": sum(c["count"] / len(labels) * abs(c["mean_probability"] - c["accuracy"])
                       for c in cells if c["count"])}
