#!/usr/bin/env bash
# Building Intelligent AI Agents - environment setup for Windows (Git Bash)
# Run this in the "Git Bash" shell that ships with Git for Windows.
# Creates the biaa-venv virtual env and installs everything the 120 labs need.
# Source of truth: SETUP.md (Python 3.12, Tier 1-3 packages).
#
# Uses uv (https://docs.astral.sh/uv/): uv creates the venv on Python 3.12
# (fetching a standalone 3.12 automatically if none is installed) and installs
# packages far faster than pip. If uv is missing it is DOWNLOADED automatically
# via PowerShell (no curl needed) and put on PATH -- so a machine with none of
# uv/curl/Python can still run this. Only if that download fails does it fall
# back to a system Python 3.12 (via the 'py -3.12' launcher) + venv + pip.
#
# Usage (in Git Bash, from the course folder):
#   bash scripts/setup-windows.sh                 # full install (all labs, incl. transformers + CPU torch)
#   bash scripts/setup-windows.sh --with-ollama   # also install Ollama + pull llama3.1:8b (Day-3 local LLM)
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

# Candidate dirs where the uv installer drops the binary (current + older
# layouts). A bash array so paths with spaces (e.g. C:\Users\John Doe) survive.
build_uv_dirs() {
  uv_dirs=("$HOME/.local/bin" "$HOME/.cargo/bin")
  if command -v cygpath >/dev/null 2>&1 && [ -n "${USERPROFILE:-}" ]; then
    local up; up="$(cygpath -u "$USERPROFILE")"
    uv_dirs+=("$up/.local/bin" "$up/.cargo/bin")
  fi
}

# Ensure uv is available, installing it if missing. Participants may not have
# curl (or any Python), so we download uv with PowerShell -- always present on
# Windows -- via the official installer, then put it on PATH for THIS session
# (the installer also updates the user PATH for future shells). uv then fetches
# a standalone Python 3.12 itself, so nothing else needs to be pre-installed.
bootstrap_uv() {
  build_uv_dirs
  # Already installed but not on this shell's PATH? Just add it.
  for d in "${uv_dirs[@]}"; do
    if [ -x "$d/uv.exe" ] || [ -x "$d/uv" ]; then export PATH="$d:$PATH"; fi
  done
  command -v uv >/dev/null 2>&1 && return 0

  echo "==> uv not found; downloading it (no admin rights needed)..."
  if command -v powershell.exe >/dev/null 2>&1 || command -v powershell >/dev/null 2>&1; then
    PS="powershell.exe"; command -v powershell.exe >/dev/null 2>&1 || PS="powershell"
    "$PS" -NoProfile -ExecutionPolicy Bypass -Command \
      "irm https://astral.sh/uv/install.ps1 | iex" || return 1
  elif command -v curl >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh || return 1
  else
    echo "    Could not find PowerShell or curl to download uv."
    return 1
  fi

  build_uv_dirs
  for d in "${uv_dirs[@]}"; do [ -d "$d" ] && export PATH="$d:$PATH"; done
  command -v uv >/dev/null 2>&1
}

if [ "$USE_UV" -eq 0 ]; then
  if bootstrap_uv; then USE_UV=1; else
    echo "==> Could not auto-install uv; will look for a system Python 3.12 instead."
  fi
fi

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

# Install the Ollama runtime (if absent) and pull the Day-3 local model.
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
    echo "==> Pulling llama3.1:8b (Day-3 local LLM for Modules 5-6, ~4.9 GB)"
    "$OLLAMA" pull llama3.1:8b || echo "    (pull failed - open a NEW Git Bash and run 'ollama pull llama3.1:8b')"
  else
    echo "==> Ollama installed, but not on PATH yet."
    echo "    CLOSE and REOPEN Git Bash, then run:  ollama pull llama3.1:8b"
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
[ "$WITH_HF" -eq 1 ] && echo "==> (--with-hf is now the default; transformers is core)"

# --- 2b. optional: install Ollama + Day-3 model -------------------------
if [ "$WITH_OLLAMA" -eq 1 ]; then
  install_ollama || echo "==> Ollama step failed (non-fatal); see messages above."
else
  echo "==> Skipping Ollama. Add --with-ollama to install it + pull llama3.1:8b (Day 3)."
fi

# --- 3. register a Jupyter kernel ---------------------------------------
echo "==> Registering Jupyter kernel 'biaa'"
python -m ipykernel install --user --name biaa --display-name "Python 3.12 (biaa)" >/dev/null

# --- 3b. point every lab notebook at the 'biaa' kernel ------------------
# Saves participants from hand-picking a kernel in Jupyter/VS Code (the #1
# workshop time-sink, worst on Windows). Local-only; committed notebooks stay
# on the portable 'python3' kernel.
echo "==> Pointing all lab notebooks at the 'biaa' kernel"
python "$ROOT/scripts/set-notebook-kernel.py" || \
  echo "    (skipped - you can run 'python scripts/set-notebook-kernel.py' later)"

# --- 3c. make Git Bash the VS Code default terminal ---------------------
# So every terminal a participant opens in VS Code is Git Bash (the shell this
# course's setup and `bash`/`source` commands assume) - no manual step needed.
# Best-effort and non-destructive: only writes if VS Code settings parse cleanly.
echo "==> Setting Git Bash as the VS Code default terminal"
python "$ROOT/scripts/set-vscode-terminal.py" || \
  echo "    (skipped - set it via Ctrl+Shift+P -> 'Terminal: Select Default Profile' -> Git Bash)"

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
      or use Ollama locally for Day 3 (re-run with --with-ollama to auto-install):
        ollama pull llama3.1:8b
   3. Launch the labs:
        jupyter lab
==============================================
EOF
