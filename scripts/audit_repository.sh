#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)

bash "$PROJECT_DIR/scripts/reproduce_all.sh"

[ -s "$PROJECT_DIR/artifacts/reports/capital-consistency-technical-report.pdf" ]

if find "$PROJECT_DIR" -type l -print | grep . >/dev/null 2>&1; then
  echo "audit failed: symbolic links require manual containment review" >&2
  exit 1
fi

if find "$PROJECT_DIR" -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '*.log' \) -print | grep . >/dev/null 2>&1; then
  echo "audit failed: generated interpreter or log artifacts found" >&2
  exit 1
fi

echo "public repository audit passed"
