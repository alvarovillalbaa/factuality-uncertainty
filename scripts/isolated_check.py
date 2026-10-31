"""Gitless, network-disabled source replay with explicit read-only dependencies."""

import argparse
import contextlib
import hashlib
import io
from pathlib import Path
import runpy
import socket
import sys
import tempfile
import unittest


class DisabledSocket(socket.socket):
    def __new__(cls, *args, **kwargs):
        raise PermissionError("verification_network_disabled")


def denied(*args, **kwargs):
    raise PermissionError("verification_network_disabled")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contracts-src", required=True)
    parser.add_argument("--site-packages", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sys.path[:0] = [str(root / "src"), args.contracts_src, args.site_packages]
    socket.socket, socket.create_connection = DisabledSocket, denied
    import factuality_uncertainty
    from factuality_uncertainty.io import load, write
    if not Path(factuality_uncertainty.__file__).is_relative_to(root):
        raise ValueError("import_outside_export")
    seal = load(root / "protocols/freeze.json")
    for name, sha in seal["files"].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != sha:
            raise ValueError("export_seal_mismatch:" + name)
    suite = unittest.defaultTestLoader.discover(str(root / "tests/unit"))
    result = unittest.TextTestRunner().run(suite)
    if not result.wasSuccessful():
        raise ValueError("isolated_tests_failed")
    study = runpy.run_path(str(root / "experiments/study.py"))
    study["replay"]("pilot")
    study["replay"]("main")
    from factuality_uncertainty.cli import main as cli
    first = load(root / "fixtures/tasks.json")[0]
    with tempfile.TemporaryDirectory(prefix="ai02-cli-") as tmp:
        directory = Path(tmp)
        write(directory / "claims.json", first["claims"])
        write(directory / "evidence.json", first["evidence"])
        sys.argv = ["factuality-uncertainty", str(directory / "claims.json"), str(directory / "evidence.json"),
                    str(directory / "out"), "--revision", "isolated-export-v1"]
        with contextlib.redirect_stdout(io.StringIO()):
            cli()
        if load(directory / "out/verification.json")["selection"]["action"] != "answer":
            raise ValueError("cli_selection_failed")
    from research_contracts import validate, verify_payloads
    count = 0
    for path in (root / "reports/main/contracts").glob("*.json"):
        document = load(path)
        kind = "artifact" if "artifact_id" in document else "result"
        errors = validate(document, kind, root=root) + verify_payloads(document, root=root)
        if errors:
            raise ValueError(errors)
        count += 1
    if count != 49:
        raise ValueError("missing_contracts")
    print({"status": "PASS", "tests": result.testsRun, "cli": "PASS", "envelopes": count,
           "network": "disabled", "import_from_export": True, "fresh_installation": False})


if __name__ == "__main__":
    main()
