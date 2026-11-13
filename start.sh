#!/bin/bash
set -e
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python missing. Install Python 3.11+ from python.org first."; exit 1
fi
"$PYTHON" - <<'PY'
import sys
if sys.version_info < (3, 11) or sys.version_info >= (3, 16):
    raise SystemExit("Install Python 3.11–3.15. Current version: " + sys.version.split()[0])
PY
if [ ! -d .venv ]; then "$PYTHON" -m venv .venv; fi
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
