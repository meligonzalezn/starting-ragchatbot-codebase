#!/bin/bash
# Full quality check: format then lint

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running formatter..."
bash "$SCRIPT_DIR/format.sh"

echo ""
echo "Running linter..."
bash "$SCRIPT_DIR/lint.sh"
