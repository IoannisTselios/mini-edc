#!/usr/bin/env bash
set -euo pipefail

# Always run from repo root
cd "$(dirname "$0")/.."

PY=${PYTHON:-python3}
VENV=".venv"

echo "==> Creating virtualenv at ${VENV}"
$PY -m venv "$VENV"

echo "==> Upgrading pip"
"$VENV/bin/python" -m pip install --upgrade pip

echo "==> Installing requirements"
if [ -f requirements.txt ]; then
  "$VENV/bin/pip" install -r requirements.txt
else
  # Fallback minimal deps (safe if requirements.txt missing)
  "$VENV/bin/pip" install "Django>=5,<6" "pytest>=8" "pytest-django>=4.8" "dj-database-url>=2.2" "psycopg[binary]>=3.2"
fi

echo "==> Running Django checks & migrations (SQLite)"
"$VENV/bin/python" manage.py check
"$VENV/bin/python" manage.py migrate

echo ""
echo "All set! To run the server:"
echo "  $VENV/bin/python manage.py runserver 0.0.0.0:8000"
echo "Admin user (optional):"
echo "  $VENV/bin/python manage.py createsuperuser"
