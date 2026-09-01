"""Content hashing and deterministic run manifests."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

from . import __version__


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError("manifest entries must be regular, non-symbolic-link files: %s" % path)
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
    project_dir = project_dir.absolute()
    resolved_project_dir = project_dir.resolve()

    def manifest_name(path: Path) -> str:
        lexical_path = path.absolute()
        try:
            lexical_relative = lexical_path.relative_to(project_dir)
        except ValueError:
            raise ValueError("manifest path is outside project directory: %s" % path)
        current = project_dir
        for part in lexical_relative.parts:
            current /= part
            if current.is_symlink():
                raise ValueError("manifest entries cannot traverse symbolic links: %s" % path)
        resolved = path.resolve()
        try:
            relative = resolved.relative_to(resolved_project_dir)
        except ValueError:
            raise ValueError("manifest path escaped project directory: %s" % resolved)
        if not path.is_file() or path.is_symlink():
            raise ValueError("manifest entries must be regular files: %s" % path)
        return relative.as_posix()

    def hash_paths(paths: Iterable[Path], label: str) -> Dict[str, str]:
        hashes: Dict[str, str] = {}
        for path in paths:
            name = manifest_name(path)
            if name in hashes:
                raise ValueError("duplicate %s manifest path: %s" % (label, name))
            hashes[name] = sha256_file(path)
        return hashes

    input_hashes = hash_paths(inputs, "input")
    output_hashes = hash_paths(outputs, "output")
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
