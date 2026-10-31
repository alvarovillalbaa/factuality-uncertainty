"""Local JSON CLI. Corpus text is data; it cannot invoke any tool."""

import argparse
import json
from pathlib import Path

from . import select, verify
from .artifacts import export
from .io import load


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("claims", type=Path)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    try:
        result = verify(load(args.claims), load(args.evidence), load(args.policy) if args.policy else None)
        result["selection"] = select(result)
        envelope = export(args.output, result, revision=args.revision)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f"verification_failed: {exc}\n")
    print(json.dumps({"artifact_id": envelope["artifact_id"], "selection": result["selection"]}))


if __name__ == "__main__":
    main()
