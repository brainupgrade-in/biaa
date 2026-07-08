#!/usr/bin/env bash
# Building Intelligent AI Agents - environment setup for Linux / macOS
# Creates the biaa-venv virtual env and installs everything the 120 labs need.
# Source of truth: SETUP.md (Python 3.12, Tier 1-3 packages).
#
# Usage:
#   bash scripts/setup-linux.sh              # core install (all labs)
#   bash scripts/setup-linux.sh --with-hf    # also install optional Tier 3 (transformers, torch)
set -euo pipefail

WITH_HF=0
[ "${1:-}" = "--with-hf" ] && WITH_HF=1

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/biaa-venv"
cd "$ROOT"

echo "=============================================="
echo " Building Intelligent AI Agents - setup"
echo " (Linux / macOS)"
echo "=============================================="

# --- 1. find Python 3.12 -------------------------------------------------
PY=""
for c in python3.12 python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info[:2]==(3,12) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo "ERROR: Python 3.12 not found on PATH."
  echo "The workshop requires Python 3.12 (SETUP.md section 2)."
  echo "Install it, then re-run this script:"
  echo "  Ubuntu/Debian : sudo apt install python3.12 python3.12-venv"
  echo "  macOS (brew)  : brew install python@3.12"
  echo "  or download   : https://www.python.org/downloads/release/python-3120/"
  exit 1
fi
echo "==> Using $($PY --version) ($(command -v "$PY"))"

# --- 2. create the virtual env ------------------------------------------
if [ -d "$VENV" ]; then
  echo "==> Reusing existing venv: $VENV"
else
  echo "==> Creating venv: $VENV"
  "$PY" -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

# --- 3. install packages -------------------------------------------------
echo "==> Upgrading pip"
python -m pip install --upgrade pip

echo "==> Installing CORE requirements (Tier 1 + 2) - this can take a few minutes"
python -m pip install -r "$ROOT/scripts/requirements-core.txt"

if [ "$WITH_HF" -eq 1 ]; then
  echo "==> Installing OPTIONAL requirements (Tier 3: transformers, torch)"
  python -m pip install -r "$ROOT/scripts/requirements-optional.txt"
else
  echo "==> Skipping optional Tier 3 (transformers/torch). Add --with-hf to include it."
fi

# --- 4. register a Jupyter kernel ---------------------------------------
echo "==> Registering Jupyter kernel 'biaa'"
python -m ipykernel install --user --name biaa --display-name "Python 3.12 (biaa)" >/dev/null

# --- 5. smoke test -------------------------------------------------------
echo
bash "$ROOT/scripts/smoke-test.sh" || true

cat <<EOF

==============================================
 Done. Next steps:
   1. Activate the env in each new terminal:
        source biaa-venv/bin/activate
   2. (Optional) set your API keys - Groq / Serper / Wolfram:
        export GROQ_API_KEY=...       SERPER_API_KEY=...       WOLFRAM_ALPHA_APPID=...
      or use Ollama locally:  ollama pull llama3.2:1b
   3. Launch the labs:
        jupyter lab
==============================================
EOF
