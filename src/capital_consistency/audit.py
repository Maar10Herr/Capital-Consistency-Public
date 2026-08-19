"""Content hashing and deterministic run manifests."""

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_hash(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def run_manifest(
    command: Iterable[str],
    inputs: Iterable[Path],
    outputs: Iterable[Path],
    assumptions: Iterable[str],
    project_dir: Path,
    solver: str,
    solver_status: str,
    arithmetic: str,
    claim_status: str,
    tolerances: Mapping[str, float],
    random_seed: Optional[int] = None,
) -> Dict[str, Any]:
    project_dir = project_dir.resolve()

    def manifest_name(path: Path) -> str:
        resolved = path.resolve()
        try:
            return str(resolved.relative_to(project_dir))
        except ValueError:
            raise ValueError("manifest path escaped project directory: %s" % resolved)

    input_hashes = {manifest_name(path): sha256_file(path) for path in inputs}
    output_hashes = {manifest_name(path): sha256_file(path) for path in outputs}
    return {
        "manifest_schema": "capital_consistency_run/v2",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": list(command),
        # Public manifests deliberately do not inspect or record repository
        # metadata. Reproducibility is based on content hashes and stated
        # assumptions, so the bundle remains portable and contains no private
        # commit identifiers.
        "git_commit": None,
        "python": sys.version,
        "package_versions": {"capital-consistency": "0.1.0", "standard_library_only": True},
        "platform": platform.platform(),
        "inputs": input_hashes,
        "input_bundle_sha256": canonical_json_hash(input_hashes),
        "outputs": output_hashes,
        "solver": solver,
        "solver_status": solver_status,
        "arithmetic": arithmetic,
        "claim_status": claim_status,
        "tolerances": dict(tolerances),
        "random_seed": random_seed,
        "assumptions": list(assumptions),
    }
