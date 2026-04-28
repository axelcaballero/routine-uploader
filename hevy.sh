#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -x ".venv/Scripts/python.exe" ]; then
    PYTHON=".venv/Scripts/python.exe"
elif [ -x "venv/bin/python3" ]; then
    PYTHON="venv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
else
    PYTHON="python"
fi

exec "$PYTHON" hevy_cli.py "$@"