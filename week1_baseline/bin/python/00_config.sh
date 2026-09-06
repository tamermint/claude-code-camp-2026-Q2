#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_DIR="$SCRIPT_DIR/../python/00_config"
VENV_DIR="$PYTHON_DIR/.venv"

cd "$PYTHON_DIR"

# Ensure a self-contained virtual environment exists
if [[ ! -d "$VENV_DIR" ]]; then
    python3 -m venv "$VENV_DIR"
fi

# Install requirements into the isolated virtual environment
"$VENV_DIR/bin/pip" install -q -r requirements.txt

# Run example using the virtual environment's Python
"$VENV_DIR/bin/python" examples/example.py
