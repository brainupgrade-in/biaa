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
#   bash scripts/setup-linux.sh              # core install (all labs)
#   bash scripts/setup-linux.sh --with-hf    # also install optional Tier 3 (transformers, CPU torch)
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

if command -v uv >/dev/null 2>&1; then USE_UV=1; else USE_UV=0; fi
is312() { "$@" -c 'import sys; sys.exit(0 if sys.version_info[:2]==(3,12) else 1)' 2>/dev/null; }

# Install into the active venv: uv (fast) when available, else pip.
venv_install() {
  if [ "$USE_UV" -eq 1 ]; then uv pip install "$@"; else python -m pip install "$@"; fi
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

echo "==> Installing CORE requirements (Tier 1 + 2)"
venv_install -r "$ROOT/scripts/requirements-core.txt"

if [ "$WITH_HF" -eq 1 ]; then
  echo "==> Installing OPTIONAL requirements (Tier 3: transformers + CPU-only torch)"
  # CPU-only torch so we don't drag in ~2.5 GB of CUDA/nvidia wheels. On Linux,
  # PyPI's default torch is the CUDA build; the cpu index gives the '+cpu'
  # variant. On macOS the PyPI wheel is already CPU/MPS.
  if [ "$(uname -s)" = "Linux" ]; then
    venv_install torch --index-url https://download.pytorch.org/whl/cpu
  else
    venv_install torch
  fi
  venv_install -r "$ROOT/scripts/requirements-optional.txt"
else
  echo "==> Skipping optional Tier 3 (transformers/torch). Add --with-hf to include it."
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
      or use Ollama locally:  ollama pull llama3.2:1b
   3. Launch the labs:
        jupyter lab
==============================================
EOF
