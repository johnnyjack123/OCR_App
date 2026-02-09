#!/usr/bin/env bash
set -euo pipefail

# Projektordner = Ordner, in dem dieses Script liegt
SCRIPT_DIR="$(cd "$(dirname -- "$0")" && pwd)"  # robustes "dirname $0" Pattern [web:22]
VENV_DIR="${SCRIPT_DIR}/.venv"

# Was soll gestartet werden?
PY_SCRIPT="${1:-app.py}"   # optional: erster Parameter, sonst main.py

cd "$SCRIPT_DIR"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "No venv found -> create: $VENV_DIR"
  python3 -m venv "$VENV_DIR"

  # venv aktivieren
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"  # Aktivierung via source .../activate [web:17]

  if [[ -f "requirements.txt" ]]; then
    python -m pip install -r requirements.txt  # installiert aus requirements-Datei [web:24]
  else
    echo "Info: requirements.txt not found. Make sure to have the file located in the same folder like this file."
  fi
else
  echo "venv exists -> acticate: $VENV_DIR"
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"  # Aktivierung via source .../activate [web:17]
fi

echo "Execute script: $PY_SCRIPT"
exec python "$PY_SCRIPT"
