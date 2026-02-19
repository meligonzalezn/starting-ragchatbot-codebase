#!/bin/bash
# Format all code in the project

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Formatting Python code ==="
uv run black "$ROOT_DIR/backend/"
uv run isort "$ROOT_DIR/backend/"
echo "✓ Python formatting done"

echo ""
echo "=== Formatting frontend code ==="
if command -v npx &>/dev/null; then
    npx prettier --write "$ROOT_DIR/frontend/"
    echo "✓ Frontend formatting done"
else
    echo "⚠ npx not found — skipping frontend formatting (install Node.js to enable)"
fi

echo ""
echo "All formatting complete."
