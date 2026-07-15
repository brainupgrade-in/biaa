#!/usr/bin/env bash
# Heavy, cacheable setup - runs in onCreateCommand so its result is BAKED INTO
# the Codespaces prebuild image (see .devcontainer/README.md). Everything here
# is content-derived and secret-free, so it's safe to prebuild:
#   * biaa-venv + all lab deps + the 'biaa' Jupyter kernel (scripts/setup-linux.sh)
#   * OpenCode (rapid app-dev prototyping)
#   * shell convenience (auto-activate the venv, OpenCode on PATH)
# Per-Codespace, secret-touching steps live in post-create.sh instead.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "=============================================="
echo " biaa Codespace - onCreate (prebuild-cacheable)"
echo "=============================================="

# --- Python env + deps + kernel (reuses the repo's setup script) --------
echo "==> Building biaa-venv and installing lab dependencies (this can take a few minutes)..."
bash "$ROOT/scripts/setup-linux.sh" || {
  echo "!! setup-linux.sh reported an error - open a terminal and re-run:"
  echo "     bash scripts/setup-linux.sh"
}

# --- OpenCode -----------------------------------------------------------
if command -v opencode >/dev/null 2>&1; then
  echo "==> OpenCode already installed: $(opencode --version 2>/dev/null | head -1)"
else
  echo "==> Installing OpenCode (opencode.ai)"
  curl -fsSL https://opencode.ai/install | bash || \
    echo "    (OpenCode install failed - re-run: curl -fsSL https://opencode.ai/install | bash)"
fi

# --- shell convenience --------------------------------------------------
if [ -d "$HOME/.opencode/bin" ] && ! grep -q '.opencode/bin' "$HOME/.bashrc" 2>/dev/null; then
  echo 'export PATH="$HOME/.opencode/bin:$PATH"' >> "$HOME/.bashrc"
fi
if ! grep -q 'biaa-venv/bin/activate' "$HOME/.bashrc" 2>/dev/null; then
  {
    echo ''
    echo '# biaa: auto-activate the workshop virtual env'
    echo '[ -f "'"$ROOT"'/biaa-venv/bin/activate" ] && source "'"$ROOT"'/biaa-venv/bin/activate"'
  } >> "$HOME/.bashrc"
fi

echo "==> onCreate done."
