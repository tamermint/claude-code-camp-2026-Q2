#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PYTHON_DIR="$SCRIPT_DIR/../../python/02_the_registry"
VENV_DIR="$ROOT_DIR/.venv"

cd "$PYTHON_DIR"

# Ensure root virtual environment exists
if [[ ! -d "$VENV_DIR" ]]; then
    python3 -m venv "$VENV_DIR"
fi

# Ensure requirements are satisfied in root virtual environment
"$VENV_DIR/bin/pip" install -q --disable-pip-version-check -r requirements.txt

# Run example using the root virtual environment's Python
"$VENV_DIR/bin/python" examples/example.py
