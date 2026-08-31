"""Content hashing and deterministic run manifests."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

from . import __version__


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
        "manifest_schema": "capital_consistency_run/v3",
        "command": list(command),
        "package_versions": {"capital-consistency": __version__, "standard_library_only": True},
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
