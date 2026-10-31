"""Bounded strict JSON and deterministic raw-byte integrity."""

import hashlib
import json
from pathlib import Path


def encode(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                       separators=(",", ":")) + "\n").encode("utf-8")


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def load(path):
    raw = Path(path).read_bytes()
    if len(raw) > 16 * 1024 * 1024:
        raise ValueError("input_too_large")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("nonfinite_json")

    value = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)
    encode(value).decode("utf-8")
    return value


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode(value))
