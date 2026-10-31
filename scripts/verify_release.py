"""Bounded source exports only; never install dependencies or copy Git history."""

import argparse
import hashlib
from importlib.metadata import version
import io
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

from factuality_uncertainty.io import write


def archive(repository, directory):
    raw = subprocess.check_output(["git", "archive", "HEAD"], cwd=repository)
    with tarfile.open(fileobj=io.BytesIO(raw)) as stream:
        stream.extractall(directory, filter="data")
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contracts-repo", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    dependency = args.contracts_repo.resolve()
    import jsonschema
    site = Path(jsonschema.__file__).resolve().parent.parent
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dependency_revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=dependency, text=True).strip()
    with tempfile.TemporaryDirectory(prefix="ai02-source-export-") as tmp:
        scratch = Path(tmp)
        exported = scratch / "project"
        exported.mkdir()
        contracts = scratch / "contracts"
        contracts.mkdir()
        source_hash, dependency_hash = archive(root, exported), archive(dependency, contracts)
        completed = subprocess.run([sys.executable, "-I", "-B", str(exported / "scripts/isolated_check.py"),
            "--contracts-src", str(contracts / "src"), "--site-packages", str(site)], cwd=exported,
            capture_output=True, text=True, timeout=120)
        def portable(value):
            replacements = {str(scratch): "<source-export>", str(scratch.resolve()): "<source-export>",
                            str(root): "<source-repository>", str(dependency): "<contracts-repository>",
                            str(site): "<validator-dependencies>", sys.base_prefix: "<python-base>"}
            for source in sorted(replacements, key=len, reverse=True):
                value = value.replace(source, replacements[source])
            return value
        stdout, stderr = portable(completed.stdout), portable(completed.stderr)
    receipt = {"status": "PASS" if completed.returncode == 0 else "FAIL", "source_revision": revision,
        "source_archive_sha256": source_hash, "contracts_revision": dependency_revision,
        "contracts_archive_sha256": dependency_hash, "python": sys.version,
        "dependencies": {p: version(p) for p in ["jsonschema", "referencing", "attrs", "rpds-py", "jsonschema-specifications"]},
        "mode": "Gitless exports, existing interpreter and read-only installed validator dependencies",
        "network": "disabled during tests, CLI and replay", "fresh_installation": False,
        "temporary_resources_removed": True, "returncode": completed.returncode, "stdout": stdout, "stderr": stderr}
    if args.receipt.exists():
        raise ValueError("preserve_original_verification_receipt")
    write(args.receipt, receipt)
    print({k: v for k, v in receipt.items() if k not in {"stdout", "stderr"}})
    if completed.returncode:
        print(stderr)
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
