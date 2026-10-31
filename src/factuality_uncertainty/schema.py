"""Versioned JSON Schema 2020-12 definitions; semantic checks remain separate."""

from jsonschema import Draft202012Validator, FormatChecker

STRING = {"type": "string", "minLength": 1, "maxLength": 100000}
STRINGS = {"type": "array", "items": STRING, "uniqueItems": True, "maxItems": 1000}
TIME = {"type": "string", "format": "date-time"}
VALUE = {"type": ["string", "number"]}
PROBABILITY = {"type": "number", "minimum": 0, "maximum": 1}
SPAN = {"type": "array", "items": {"type": "integer", "minimum": 0}, "minItems": 2, "maxItems": 2}


def object_schema(properties, required):
    return {"type": "object", "properties": properties, "required": required, "additionalProperties": False}


OPERAND = object_schema({"value": VALUE, "unit": STRING}, ["value", "unit"])
ARITHMETIC = object_schema({"op": {"enum": ["add", "subtract", "multiply", "divide"]},
                            "left": OPERAND, "right": OPERAND}, ["op", "left", "right"])
TYPED = {"subject": STRING, "predicate": STRING, "value": VALUE,
         "qualifiers": STRINGS, "assumption_refs": STRINGS, "unit": STRING, "tolerance": VALUE}
CLAIM = object_schema(TYPED | {"claim_id": STRING, "claim_type": {"enum": ["text", "numeric", "opinion"]},
    "text": STRING, "answer_span": SPAN, "as_of": TIME, "domain": STRING,
    "model_confidence": PROBABILITY, "arithmetic": ARITHMETIC},
    ["claim_id", "claim_type", "text", "answer_span", "as_of", "domain", "subject", "predicate", "value",
     "qualifiers", "assumption_refs"])
CLAIM["allOf"] = [{"if": {"properties": {"claim_type": {"const": "numeric"}}}, "then": {"required": ["unit"]}}]
FACT = object_schema(TYPED | {"quote_span": SPAN, "valid_from": TIME, "valid_until": {"anyOf": [TIME, {"type": "null"}]},
    "bounds": {"type": "array", "items": VALUE, "minItems": 2, "maxItems": 2}},
    ["subject", "predicate", "value", "qualifiers", "assumption_refs", "quote_span", "valid_from", "valid_until"])
SOURCE = object_schema({"source_id": STRING, "version": STRING, "domain": STRING,
    "access_scope": STRING, "quality": STRING, "license": STRING, "published_at": TIME, "as_of": TIME,
    "retrieved_at": TIME, "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "text": STRING, "facts": {"type": "array", "items": FACT, "maxItems": 1000}},
    ["source_id", "version", "domain", "access_scope", "quality", "license", "published_at", "as_of",
     "retrieved_at", "sha256", "text", "facts"])
CLAIM_BUNDLE = object_schema({"version": {"const": "0.1.0"}, "bundle_id": STRING, "answer": STRING,
    "family": STRING, "domain": STRING, "raw_probability": PROBABILITY,
    "claims": {"type": "array", "items": CLAIM, "minItems": 1, "maxItems": 1000}},
    ["version", "bundle_id", "answer", "claims"])
EVIDENCE_BUNDLE = object_schema({"version": {"const": "0.1.0"},
    "sources": {"type": "array", "items": SOURCE, "maxItems": 1000}}, ["version", "sources"])
for name, schema in [("claims", CLAIM_BUNDLE), ("evidence", EVIDENCE_BUNDLE)]:
    schema.update({"$schema": "https://json-schema.org/draft/2020-12/schema",
                   "$id": f"urn:ai02:{name}:0.1.0"})
    Draft202012Validator.check_schema(schema)


def validate(document, schema):
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document),
                    key=lambda e: str(list(e.absolute_path)))
    if errors:
        first = errors[0]
        raise ValueError("schema_error:" + "/".join(map(str, first.absolute_path)) + ":" + first.message)


if __name__ == "__main__":
    import json
    print(json.dumps({"ClaimBundle": CLAIM_BUNDLE, "EvidenceBundle": EVIDENCE_BUNDLE}, indent=2))
