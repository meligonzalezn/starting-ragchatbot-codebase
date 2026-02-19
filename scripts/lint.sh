#!/bin/bash
# Lint all code in the project (no changes applied)

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0

echo "=== Checking Python formatting (black) ==="
if uv run black --check "$ROOT_DIR/backend/"; then
    echo "✓ Python formatting OK"
else
    echo "✗ Python formatting issues found (run scripts/format.sh to fix)"
    FAILED=1
fi

echo ""
echo "=== Checking Python imports (isort) ==="
if uv run isort --check-only "$ROOT_DIR/backend/"; then
    echo "✓ Import ordering OK"
else
    echo "✗ Import ordering issues found (run scripts/format.sh to fix)"
    FAILED=1
fi

echo ""
echo "=== Checking Python style (flake8) ==="
if uv run flake8 "$ROOT_DIR/backend/"; then
    echo "✓ Python style OK"
else
    echo "✗ Python style issues found"
    FAILED=1
fi

echo ""
echo "=== Checking frontend formatting (prettier) ==="
if command -v npx &>/dev/null; then
    if npx prettier --check "$ROOT_DIR/frontend/"; then
        echo "✓ Frontend formatting OK"
    else
        echo "✗ Frontend formatting issues found (run scripts/format.sh to fix)"
        FAILED=1
    fi
else
    echo "⚠ npx not found — skipping frontend check (install Node.js to enable)"
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo "All checks passed."
else
    echo "Some checks failed. See above for details."
    exit 1
fi
