#!/usr/bin/env bash
# Building Intelligent AI Agents - environment setup for Linux / macOS
# Creates the biaa-venv virtual env and installs everything the 120 labs need.
# Source of truth: SETUP.md (Python 3.12, Tier 1-3 packages).
#
# Uses uv (https://docs.astral.sh/uv/) when it is installed: uv creates the
# venv on Python 3.12 (fetching a standalone 3.12 automatically if the system
# has none) and installs packages far faster than pip. Without uv it falls
# back to a system Python 3.12 + the stdlib venv + pip.
#
# Usage:
#   bash scripts/setup-linux.sh                 # full install (all labs, incl. transformers + CPU torch)
#   bash scripts/setup-linux.sh --with-ollama   # also install Ollama + pull llama3.2:1b (Day-1 local LLM)
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
echo " (Linux / macOS)"
echo "=============================================="

if command -v uv >/dev/null 2>&1; then USE_UV=1; else USE_UV=0; fi
is312() { "$@" -c 'import sys; sys.exit(0 if sys.version_info[:2]==(3,12) else 1)' 2>/dev/null; }

# Install into the active venv: uv (fast) when available, else pip.
venv_install() {
  if [ "$USE_UV" -eq 1 ]; then uv pip install "$@"; else python -m pip install "$@"; fi
}

# Install the Ollama runtime (if absent) and pull the Day-1 local model.
# Best-effort: a failure here never aborts the Python setup (guarded by callers).
install_ollama() {
  if command -v ollama >/dev/null 2>&1; then
    echo "==> Ollama already installed: $(ollama --version 2>/dev/null | head -1)"
  elif [ "$(uname -s)" = "Darwin" ]; then
    # macOS: the ollama.com/install.sh script is Linux-only; use Homebrew.
    if command -v brew >/dev/null 2>&1; then
      echo "==> Installing Ollama via Homebrew"
      brew install ollama
    else
      echo "==> Could not auto-install Ollama (no Homebrew found)."
      echo "    Download the macOS app: https://ollama.com/download/mac"
      return 0
    fi
  else
    # Linux: official one-line installer (sets up a systemd service where present).
    echo "==> Installing Ollama (curl -fsSL https://ollama.com/install.sh | sh)"
    curl -fsSL https://ollama.com/install.sh | sh
  fi

  # Pull the Day-1 model. Needs the ollama server running; the Linux installer
  # starts it via systemd, otherwise we launch a transient 'ollama serve'.
  if command -v ollama >/dev/null 2>&1; then
    if ! ollama list >/dev/null 2>&1; then
      echo "==> Starting a transient 'ollama serve' to pull the model"
      ollama serve >/dev/null 2>&1 &
      OLLAMA_PID=$!
      for _ in 1 2 3 4 5 6 7 8 9 10; do
        ollama list >/dev/null 2>&1 && break
        sleep 1
      done
    fi
    echo "==> Pulling llama3.2:1b (Day-1 local LLM, ~1.3 GB)"
    ollama pull llama3.2:1b || echo "    (pull failed - run 'ollama pull llama3.2:1b' after the server is up)"
    [ -n "${OLLAMA_PID:-}" ] && kill "$OLLAMA_PID" >/dev/null 2>&1 || true
  fi
}

# --- 1. create the virtual env on Python 3.12 ---------------------------
if [ "$USE_UV" -eq 1 ]; then
  echo "==> Using uv $(uv --version | awk '{print $2}')"
  if [ -d "$VENV" ]; then
    echo "==> Reusing existing venv: $VENV"
  else
    # uv fetches a standalone Python 3.12 automatically if the system lacks one
    # (works on distros with no python3.12 package, e.g. Ubuntu 25.10+).
    echo "==> Creating venv on Python 3.12 (uv fetches 3.12 if needed): $VENV"
    uv venv "$VENV" --python 3.12 --seed
  fi
else
  # No uv: find a real Python 3.12 on PATH, then use the stdlib venv module.
  PY=""
  for c in python3.12 python3 python; do
    if command -v "$c" >/dev/null 2>&1 && is312 "$c"; then PY="$c"; break; fi
  done
  if [ -z "$PY" ]; then
    echo "ERROR: Python 3.12 not found and no uv to provision it."
    echo "The workshop requires Python 3.12 (SETUP.md section 2)."
    echo "Easiest cross-distro fix (no sudo) - install uv, then re-run this script:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh     (then reopen the shell)"
    echo "Alternatives:"
    echo "  Ubuntu 24.04/Debian (older) : sudo apt install python3.12 python3.12-venv"
    echo "  macOS (brew)                : brew install python@3.12"
    echo "  or download                 : https://www.python.org/downloads/release/python-3120/"
    exit 1
  fi
  echo "==> Using $($PY --version) ($PY)"
  if [ -d "$VENV" ]; then
    echo "==> Reusing existing venv: $VENV"
  else
    echo "==> Creating venv: $VENV"
    "$PY" -m venv "$VENV"
  fi
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

# --- 2. install packages -------------------------------------------------
if [ "$USE_UV" -eq 0 ]; then
  echo "==> Upgrading pip"
  python -m pip install --upgrade pip
fi

echo "==> Installing CORE requirements (Tier 1 + 2, incl. transformers)"
venv_install -r "$ROOT/scripts/requirements-core.txt"

# CPU-only torch for the Hugging Face labs (now core). CPU-only so we don't drag
# in ~2.5 GB of CUDA/nvidia wheels. On Linux, PyPI's default torch is the CUDA
# build; the cpu index gives the '+cpu' variant. On macOS the wheel is CPU/MPS.
echo "==> Installing CPU-only torch (for the transformer labs)"
if [ "$(uname -s)" = "Linux" ]; then
  venv_install torch --index-url https://download.pytorch.org/whl/cpu
else
  venv_install torch
fi
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
 Done. Next steps:
   1. Activate the env in each new terminal:
        source biaa-venv/bin/activate
   2. (Optional) set your API keys - Groq / Serper / Wolfram:
        export GROQ_API_KEY=...       SERPER_API_KEY=...       WOLFRAM_ALPHA_APPID=...
      or use Ollama locally (re-run with --with-ollama to auto-install):
        ollama pull llama3.2:1b
   3. Launch the labs:
        jupyter lab
==============================================
EOF
