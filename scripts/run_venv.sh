#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

VENV=".venv"

if [ ! -x "$VENV/bin/python" ]; then
  echo "Virtualenv not found; run scripts/setup_venv.sh first."
  exit 1
fi

echo "==> Django check & auto-migrate"
"$VENV/bin/python" manage.py check
"$VENV/bin/python" manage.py migrate

echo "==> Starting server at http://localhost:8000"
exec "$VENV/bin/python" manage.py runserver 0.0.0.0:8000
