#!/usr/bin/env bash
# Building Intelligent AI Agents - environment setup for Windows (Git Bash)
# Run this in the "Git Bash" shell that ships with Git for Windows.
# Creates the biaa-venv virtual env and installs everything the 120 labs need.
# Source of truth: SETUP.md (Python 3.12, Tier 1-3 packages).
#
# Uses uv (https://docs.astral.sh/uv/) when it is installed: uv creates the
# venv on Python 3.12 (fetching a standalone 3.12 automatically if none is
# installed) and installs packages far faster than pip. Without uv it falls
# back to a system Python 3.12 (via the 'py -3.12' launcher) + venv + pip.
#
# Usage (in Git Bash, from the course folder):
#   bash scripts/setup-windows.sh                 # full install (all labs, incl. transformers + CPU torch)
#   bash scripts/setup-windows.sh --with-ollama   # also install Ollama + pull llama3.2:1b (Day-1 local LLM)
# (--with-hf is accepted but now a no-op: transformers is part of the core install.)
set -euo pipefail

WITH_HF=0
WITH_OLLAMA=0
for arg in "$@"; do
  case "$arg" in
    --with-hf)     WITH_HF=1 ;;
    --with-ollama) WITH_OLLAMA=1 ;;
    *) echo "WARNING: ignoring unknown flag '$arg'" >&2 ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/biaa-venv"
cd "$ROOT"

echo "=============================================="
echo " Building Intelligent AI Agents - setup"
echo " (Windows - Git Bash)"
echo "=============================================="

if command -v uv >/dev/null 2>&1; then USE_UV=1; else USE_UV=0; fi
is312() { "$@" -c 'import sys; sys.exit(0 if sys.version_info[:2]==(3,12) else 1)' 2>/dev/null; }

# Install into the active venv: uv (fast) when available, else pip.
venv_install() {
  if [ "$USE_UV" -eq 1 ]; then uv pip install "$@"; else python -m pip install "$@"; fi
}

# Resolve the ollama command: on PATH, or the default winget install location.
ollama_cmd() {
  if command -v ollama >/dev/null 2>&1; then
    echo "ollama"
  elif [ -x "${LOCALAPPDATA:-}/Programs/Ollama/ollama.exe" ]; then
    echo "${LOCALAPPDATA:-}/Programs/Ollama/ollama.exe"
  else
    echo ""
  fi
}

# Install the Ollama runtime (if absent) and pull the Day-1 local model.
# Best-effort: a failure here never aborts the Python setup (guarded by callers).
install_ollama() {
  if [ -n "$(ollama_cmd)" ]; then
    echo "==> Ollama already installed"
  elif command -v winget >/dev/null 2>&1; then
    echo "==> Installing Ollama via winget"
    winget install --id Ollama.Ollama -e --source winget \
      --accept-package-agreements --accept-source-agreements || true
  else
    echo "==> Could not auto-install Ollama (no winget found)."
    echo "    Download the Windows installer: https://ollama.com/download/windows"
    return 0
  fi

  OLLAMA="$(ollama_cmd)"
  if [ -n "$OLLAMA" ]; then
    echo "==> Pulling llama3.2:1b (Day-1 local LLM, ~1.3 GB)"
    "$OLLAMA" pull llama3.2:1b || echo "    (pull failed - open a NEW Git Bash and run 'ollama pull llama3.2:1b')"
  else
    echo "==> Ollama installed, but not on PATH yet."
    echo "    CLOSE and REOPEN Git Bash, then run:  ollama pull llama3.2:1b"
  fi
}

# --- 1. create the virtual env on Python 3.12 ---------------------------
if [ "$USE_UV" -eq 1 ]; then
  echo "==> Using uv $(uv --version | awk '{print $2}')"
  if [ -d "$VENV" ]; then
    echo "==> Reusing existing venv: $VENV"
  else
    echo "==> Creating venv on Python 3.12 (uv fetches 3.12 if needed): $VENV"
    uv venv "$VENV" --python 3.12 --seed
  fi
else
  # No uv: find a real Python 3.12. On Windows it may be exposed as 'python',
  # or via the 'py' launcher as 'py -3.12'. We probe both.
  PY_LAUNCH=""
  if command -v py >/dev/null 2>&1 && is312 py -3.12; then
    PY_LAUNCH="py -3.12"
  else
    for c in python python3 python3.12; do
      if command -v "$c" >/dev/null 2>&1 && is312 "$c"; then PY_LAUNCH="$c"; break; fi
    done
  fi
  if [ -z "$PY_LAUNCH" ]; then
    echo "ERROR: Python 3.12 not found and no uv to provision it."
    echo "The workshop requires Python 3.12 (SETUP.md section 2). Either:"
    echo "  A) Install from https://www.python.org/downloads/release/python-3120/"
    echo "     - tick 'Add python.exe to PATH' during install"
    echo "     - then CLOSE and REOPEN Git Bash, and re-run this script."
    echo "  B) Install uv (PowerShell): irm https://astral.sh/uv/install.ps1 | iex"
    echo "     - reopen Git Bash, then re-run: bash scripts/setup-windows.sh"
    exit 1
  fi
  echo "==> Using $($PY_LAUNCH --version 2>&1) (launcher: $PY_LAUNCH)"
  if [ -d "$VENV" ]; then
    echo "==> Reusing existing venv: $VENV"
  else
    echo "==> Creating venv: $VENV"
    $PY_LAUNCH -m venv "$VENV"
  fi
fi

# On Windows the venv puts executables under Scripts/, not bin/.
# shellcheck disable=SC1091
source "$VENV/Scripts/activate"

# --- 2. install packages -------------------------------------------------
if [ "$USE_UV" -eq 0 ]; then
  echo "==> Upgrading pip"
  python -m pip install --upgrade pip
fi

echo "==> Installing CORE requirements (Tier 1 + 2, incl. transformers)"
venv_install -r "$ROOT/scripts/requirements-core.txt"

# CPU-only torch for the Hugging Face labs (now core; small, no CUDA/nvidia
# bloat). Windows PyPI torch is already CPU, but pinning the cpu index keeps it
# consistent and guaranteed small.
echo "==> Installing CPU-only torch (for the transformer labs)"
venv_install torch --index-url https://download.pytorch.org/whl/cpu
# Back-compat placeholder (now empty; transformers moved to core).
venv_install -r "$ROOT/scripts/requirements-optional.txt"
[ "$WITH_HF" -eq 1 ] && echo "==> (--with-hf is now the default; transformers is core)"

# --- 2b. optional: install Ollama + Day-1 model -------------------------
if [ "$WITH_OLLAMA" -eq 1 ]; then
  install_ollama || echo "==> Ollama step failed (non-fatal); see messages above."
else
  echo "==> Skipping Ollama. Add --with-ollama to install it + pull llama3.2:1b."
fi

# --- 3. register a Jupyter kernel ---------------------------------------
echo "==> Registering Jupyter kernel 'biaa'"
python -m ipykernel install --user --name biaa --display-name "Python 3.12 (biaa)" >/dev/null

# --- 4. smoke test -------------------------------------------------------
echo
bash "$ROOT/scripts/smoke-test.sh" || true

cat <<EOF

==============================================
 Done. Next steps (in Git Bash):
   1. Activate the env in each new Git Bash window:
        source biaa-venv/Scripts/activate
   2. (Optional) set your API keys - Groq / Serper / Wolfram:
        export GROQ_API_KEY=...       SERPER_API_KEY=...       WOLFRAM_ALPHA_APPID=...
      or use Ollama locally (re-run with --with-ollama to auto-install):
        ollama pull llama3.2:1b
   3. Launch the labs:
        jupyter lab
==============================================
EOF
