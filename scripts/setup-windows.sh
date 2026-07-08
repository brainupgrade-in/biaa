#!/usr/bin/env bash
# Building Intelligent AI Agents - environment setup for Windows (Git Bash)
# Run this in the "Git Bash" shell that ships with Git for Windows.
# Creates the biaa-venv virtual env and installs everything the 120 labs need.
# Source of truth: SETUP.md (Python 3.12, Tier 1-3 packages).
#
# Usage (in Git Bash, from the course folder):
#   bash scripts/setup-windows.sh              # core install (all labs)
#   bash scripts/setup-windows.sh --with-hf    # also install optional Tier 3 (transformers, torch)
set -euo pipefail

WITH_HF=0
[ "${1:-}" = "--with-hf" ] && WITH_HF=1

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/biaa-venv"
cd "$ROOT"

echo "=============================================="
echo " Building Intelligent AI Agents - setup"
echo " (Windows - Git Bash)"
echo "=============================================="

# --- 1. find Python 3.12 -------------------------------------------------
# On Windows, python 3.12 may be exposed as 'python', or via the 'py' launcher
# as 'py -3.12'. We probe both and keep the launch prefix in PY_LAUNCH.
PY_LAUNCH=""
is312() { "$@" -c 'import sys; sys.exit(0 if sys.version_info[:2]==(3,12) else 1)' 2>/dev/null; }

if command -v py >/dev/null 2>&1 && is312 py -3.12; then
  PY_LAUNCH="py -3.12"
else
  for c in python python3 python3.12; do
    if command -v "$c" >/dev/null 2>&1 && is312 "$c"; then
      PY_LAUNCH="$c"; break
    fi
  done
fi
# Fall back to a uv-managed 3.12 (distro/OS-independent; auto-installs if missing).
if [ -z "$PY_LAUNCH" ] && command -v uv >/dev/null 2>&1; then
  echo "==> No system Python 3.12; using uv to provide one"
  uv python install 3.12 >/dev/null 2>&1 || true
  UVPY="$(uv python find 3.12 2>/dev/null || true)"
  if [ -n "$UVPY" ] && is312 "$UVPY"; then PY_LAUNCH="$UVPY"; fi
fi
if [ -z "$PY_LAUNCH" ]; then
  echo "ERROR: Python 3.12 not found."
  echo "The workshop requires Python 3.12 (SETUP.md section 2). Either:"
  echo "  A) Install from https://www.python.org/downloads/release/python-3120/"
  echo "     - tick 'Add python.exe to PATH' during install"
  echo "     - then CLOSE and REOPEN Git Bash, and re-run this script."
  echo "  B) Install uv (powershell): irm https://astral.sh/uv/install.ps1 | iex"
  echo "     - reopen Git Bash, then re-run: bash scripts/setup-windows.sh"
  exit 1
fi
echo "==> Using $($PY_LAUNCH --version 2>&1) (launcher: $PY_LAUNCH)"

# --- 2. create the virtual env ------------------------------------------
if [ -d "$VENV" ]; then
  echo "==> Reusing existing venv: $VENV"
else
  echo "==> Creating venv: $VENV"
  $PY_LAUNCH -m venv "$VENV"
fi
# On Windows the venv puts executables under Scripts/, not bin/.
# shellcheck disable=SC1091
source "$VENV/Scripts/activate"

# --- 3. install packages -------------------------------------------------
echo "==> Upgrading pip"
python -m pip install --upgrade pip

echo "==> Installing CORE requirements (Tier 1 + 2) - this can take several minutes"
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
 Done. Next steps (in Git Bash):
   1. Activate the env in each new Git Bash window:
        source biaa-venv/Scripts/activate
   2. (Optional) set your API keys - Groq / Serper / Wolfram:
        export GROQ_API_KEY=...       SERPER_API_KEY=...       WOLFRAM_ALPHA_APPID=...
      or use Ollama locally:  ollama pull llama3.2:1b
   3. Launch the labs:
        jupyter lab
==============================================
EOF
