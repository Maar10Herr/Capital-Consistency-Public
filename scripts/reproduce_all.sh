#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
RUNTIME_DIR=$(mktemp -d "$PROJECT_DIR/.runtime.XXXXXX")
trap 'rm -rf -- "$RUNTIME_DIR"' EXIT HUP INT TERM

export PYTHONPATH="$PROJECT_DIR/src"
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR="$RUNTIME_DIR"

python3 -m unittest discover -s "$PROJECT_DIR/tests" -p 'test_*.py' -v
python3 "$PROJECT_DIR/experiments/run_exact_examples.py"
python3 "$PROJECT_DIR/experiments/run_adversarial_atlas.py"

for certificate in "$PROJECT_DIR"/artifacts/certificates/*.json; do
  python3 -m capital_consistency.cli verify-certificate "$certificate"
done

echo "public reproduction completed"
