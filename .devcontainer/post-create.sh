#!/usr/bin/env bash
# Light, per-Codespace setup - runs in postCreateCommand every time a Codespace
# is created (including from a prebuild). Keep this fast: the heavy, cacheable
# work lives in on-create.sh (baked into the prebuild). Here we only do the
# per-user, secret-adjacent bits and print next steps.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# --- seed .env ----------------------------------------------------------
# .env is git-ignored, so it's absent in a fresh Codespace. If you set
# GROQ_API_KEY etc. as Codespaces secrets, they arrive as env vars and you may
# not need this file at all - but seeding it keeps the load_dotenv() labs happy.
if [ ! -f "$ROOT/.env" ] && [ -f "$ROOT/.env.example" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "==> Created .env from .env.example - add your GROQ_API_KEY (Days 4-5)."
  echo "    Tip: Settings > Codespaces > Secrets injects keys automatically."
else
  echo "==> .env already present - leaving it untouched."
fi

# Safety net: if a Codespace was created WITHOUT a prebuild and the venv is
# missing (onCreate skipped/failed), build it now so the labs still work.
if [ ! -x "$ROOT/biaa-venv/bin/python" ]; then
  echo "==> biaa-venv missing (no prebuild?) - running the full setup now..."
  bash "$ROOT/.devcontainer/on-create.sh" || true
fi

cat <<EOF

==============================================
 Codespace ready.

   Labs:        jupyter lab --no-browser --port 8888
                (or open any hands-on/**/*.ipynb - pick the 'biaa' kernel)

   Day-3 local LLM (optional, ~4.9 GB):
                bash scripts/pull-ollama-model.sh

   Ship a lab as an app (FastAPI + Expo/React Native):
                see demo/README.md   |   drive it with: opencode
==============================================
EOF
