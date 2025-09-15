#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

VENV=".venv"
if [ ! -x "$VENV/bin/pip" ]; then
  echo "Virtualenv not found; run scripts/setup_venv.sh first."
  exit 1
fi

echo "==> Writing requirements.txt from current venv"
"$VENV/bin/pip" freeze | sed '/^-e /d' > requirements.txt
echo "Saved requirements.txt"
