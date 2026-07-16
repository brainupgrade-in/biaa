#!/usr/bin/env bash
# Launch the demo app (dev mode): FastAPI serves the chat UI + /chat on one port.
# No Node, no Expo — works identically on any Codespace (Alpine or Debian).
#
#   bash demo/run.sh            # http://localhost:8000  (open the forwarded 8000 port)
#
# Production-like alternative:  docker compose -f demo/docker-compose.yml up --build
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Port the app listens on (demo.app reads $PORT; default 8000). Override: PORT=8250 bash demo/run.sh
export PORT="${PORT:-8000}"

# Prefer the course venv; fall back to any python3.
PY="$ROOT/biaa-venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3 || command -v python)"

echo "==> Installing demo deps into $($PY -c 'import sys;print(sys.prefix)')"
"$PY" -m pip install -q -r "$ROOT/demo/requirements.txt"

if [ ! -f "$ROOT/.env" ] || ! grep -q '^GROQ_API_KEY=gsk_' "$ROOT/.env" 2>/dev/null; then
  echo "!! GROQ_API_KEY not set in .env — /chat will return a placeholder until you add it."
fi

echo "=============================================="
echo " Demo app:  http://localhost:$PORT"
echo " In a Codespace: open the forwarded port $PORT (PORTS panel) — make it Public"
echo " Ctrl+C to stop."
echo "=============================================="
exec "$PY" -m demo.app
