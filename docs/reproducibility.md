# Reproducibility

The public bundle uses only the Python standard library. Deterministic computations record their seed, tolerances, package version, content hashes, and claim status. The release contains no private data, credentials, database files, or repository metadata.

Canonical verification commands:

```sh
bash scripts/reproduce_all.sh
bash scripts/audit_repository.sh
```

Tests use `unittest` and require no third-party Python dependencies:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \\
  python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The reviewed technical report is distributed as
`artifacts/reports/capital-consistency-technical-report.pdf`. Its LaTeX source and
build environment are intentionally not part of this implementation-focused
public bundle; the PDF is the publication artifact.

The reproduction scripts are local-only: they use synthetic examples and write
deterministic certificates/reports beneath `artifacts/`. They do not contact
external services or inspect Git metadata.
