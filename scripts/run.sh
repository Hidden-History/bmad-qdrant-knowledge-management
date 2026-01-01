#!/bin/bash
#
# Wrapper script to run Qdrant knowledge management scripts
# Automatically loads environment variables from .env
#
# Usage:
#   ./scripts/run.sh create_collections.py --check-only
#   ./scripts/run.sh create_collections.py
#   ./scripts/run.sh qdrant_cleanup.py --audit
#

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment from .env if it exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "Loading environment from .env..."
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
else
    echo "Note: No .env file found. Using environment variables directly."
fi

# Find Python - try in order: python3, python
PYTHON=""
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "ERROR: Python not found. Please install Python 3.8+"
    exit 1
fi

echo "Using Python: $($PYTHON --version)"

# Get script name from first argument
SCRIPT_NAME="$1"
shift 2>/dev/null || true

if [ -z "$SCRIPT_NAME" ]; then
    echo "Usage: $0 <script_name> [args...]"
    echo ""
    echo "Available scripts:"
    ls -1 "$SCRIPT_DIR"/*.py 2>/dev/null | xargs -n 1 basename
    exit 1
fi

# Add .py extension if not present
if [[ "$SCRIPT_NAME" != *.py ]]; then
    SCRIPT_NAME="${SCRIPT_NAME}.py"
fi

SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_NAME"

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "ERROR: Script not found: $SCRIPT_PATH"
    exit 1
fi

# Run the script from project root (so imports work)
cd "$PROJECT_ROOT"
exec "$PYTHON" "$SCRIPT_PATH" "$@"
