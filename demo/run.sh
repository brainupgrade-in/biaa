#!/usr/bin/env bash
# Build + launch the demo app (FastAPI backend + Expo mobile) in one command.
# Designed for GitHub Codespaces: it computes the forwarded backend URL, injects
# it into the mobile app, starts the API, and launches Expo.
#
# Usage:
#   bash demo/run.sh                         # backend app_module8 + Expo web
#   bash demo/run.sh --backend demo.backend.main:app     # the generic template
#   bash demo/run.sh --app-name m8-demo      # name the mobile app dir
#   bash demo/run.sh --mode tunnel           # Expo tunnel (phone via Expo Go)
#   bash demo/run.sh --mode backend-only     # just the API (curl / external app)
#
# Ctrl+C stops Expo; the backend it started is cleaned up automatically.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# --- defaults / args ----------------------------------------------------
BACKEND="demo.backend.app_module8:app"   # the Module-8 worked example
APP_NAME="mobile"
MODE="web"                               # web | tunnel | backend-only
PORT=8000
while [ $# -gt 0 ]; do
  case "$1" in
    --backend)   BACKEND="$2"; shift 2 ;;
    --app-name)  APP_NAME="$2"; shift 2 ;;
    --mode)      MODE="$2"; shift 2 ;;
    --port)      PORT="$2"; shift 2 ;;
    -h|--help)   grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
done
APP_DIR="$ROOT/demo/$APP_NAME"

# --- venv ---------------------------------------------------------------
if [ ! -x "$ROOT/biaa-venv/bin/python" ]; then
  echo "ERROR: biaa-venv missing. Run: bash scripts/setup-linux.sh" >&2
  exit 1
fi
PY="$ROOT/biaa-venv/bin/python"

# Node/npx (for Expo) comes from the devcontainer 'node' feature, which installs
# via nvm. In a non-login shell npx may not be on PATH even though Node exists;
# source nvm / add its bin dir before giving up.
ensure_node() {
  command -v npx >/dev/null 2>&1 && return 0
  export NVM_DIR="${NVM_DIR:-/usr/local/share/nvm}"
  # shellcheck disable=SC1091
  [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1 || true
  for d in "$NVM_DIR/current/bin" "$NVM_DIR"/versions/node/*/bin /usr/local/lib/nodejs/*/bin; do
    [ -d "$d" ] && export PATH="$d:$PATH"
  done
  command -v npx >/dev/null 2>&1
}

# --- compute the backend URL the mobile app should call -----------------
# In a Codespace, port 8000 is reachable at the forwarded domain, NOT localhost
# (the phone / web build runs outside the container).
if [ -n "${CODESPACE_NAME:-}" ]; then
  DOMAIN="${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
  BACKEND_URL="https://${CODESPACE_NAME}-${PORT}.${DOMAIN}"
  IN_CODESPACE=1
else
  BACKEND_URL="http://localhost:${PORT}"
  IN_CODESPACE=0
fi

# --- 1. backend deps ----------------------------------------------------
if ! "$PY" -c 'import fastapi, uvicorn' 2>/dev/null; then
  echo "==> Installing backend deps (fastapi, uvicorn) into biaa-venv..."
  "$PY" -m pip install -q -r "$ROOT/demo/backend/requirements.txt"
fi

if [ ! -f "$ROOT/.env" ] || ! grep -q '^GROQ_API_KEY=gsk_' "$ROOT/.env" 2>/dev/null; then
  echo "!! Warning: GROQ_API_KEY not set in .env - /chat will return an error until you add it."
  echo "   (Or set it as a Codespaces secret: Settings > Codespaces > Secrets.)"
fi

# --- 2. start the backend (background) ----------------------------------
echo "==> Starting API: uvicorn $BACKEND on 0.0.0.0:$PORT"
"$PY" -m uvicorn "$BACKEND" --host 0.0.0.0 --port "$PORT" >/tmp/biaa-demo-api.log 2>&1 &
API_PID=$!
cleanup() { echo; echo "==> Stopping API (pid $API_PID)"; kill "$API_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

# wait for /health
for _ in $(seq 1 20); do
  if "$PY" -c "import urllib.request,sys; urllib.request.urlopen('http://localhost:$PORT/health',timeout=1)" 2>/dev/null; then
    break
  fi
  sleep 0.5
done
echo "    API log: /tmp/biaa-demo-api.log"

# In a Codespace, make port 8000 public so the web build / phone can reach it.
if [ "$IN_CODESPACE" -eq 1 ] && command -v gh >/dev/null 2>&1; then
  echo "==> Making port $PORT public (so the app can call it)..."
  gh codespace ports visibility "${PORT}:public" -c "$CODESPACE_NAME" 2>/dev/null \
    || echo "    (couldn't auto-set visibility - do it in the PORTS panel: right-click $PORT > Port Visibility > Public)"
fi

if [ "$MODE" = "backend-only" ]; then
  echo
  echo "=============================================="
  echo " API up at: $BACKEND_URL"
  echo "   curl -sX POST $BACKEND_URL/chat -H 'content-type: application/json' \\"
  echo "        -d '{\"message\":\"I was charged twice for order 4471\"}'"
  echo " Ctrl+C to stop."
  echo "=============================================="
  wait "$API_PID"
  exit 0
fi

# --- 3. Node + scaffold the mobile app ----------------------------------
if ! ensure_node; then
  echo "ERROR: Node / npx not found - the Expo app needs it." >&2
  echo "  This Codespace gets Node from the devcontainer 'node' feature." >&2
  echo "  If it's missing, rebuild the container to install it:" >&2
  echo "    Command Palette (F1) > 'Codespaces: Rebuild Container'" >&2
  echo "  then re-run: bash demo/run.sh" >&2
  echo "  (To run just the API meanwhile: bash demo/run.sh --mode backend-only)" >&2
  exit 1
fi
echo "==> Using node $(node --version 2>/dev/null) / npx $(npx --version 2>/dev/null)"

if [ ! -d "$APP_DIR" ]; then
  echo "==> Scaffolding Expo app: demo/$APP_NAME"
  bash "$ROOT/demo/new-mobile-app.sh" "$APP_NAME" \
    || { echo "ERROR: Expo scaffold failed (see output above)." >&2; exit 1; }
fi
if [ ! -f "$APP_DIR/App.tsx" ]; then
  echo "ERROR: $APP_DIR/App.tsx missing after scaffold - not launching Expo." >&2
  exit 1
fi

# --- 4. point the app at the backend URL --------------------------------
# new-mobile-app.sh writes:  const API = "http://localhost:8000";
if [ -f "$APP_DIR/App.tsx" ]; then
  echo "==> Wiring App.tsx -> $BACKEND_URL"
  "$PY" - "$APP_DIR/App.tsx" "$BACKEND_URL" <<'PYEOF'
import re, sys
path, url = sys.argv[1], sys.argv[2]
s = open(path).read()
s2 = re.sub(r'const API = "[^"]*";', f'const API = "{url}";', s, count=1)
open(path, "w").write(s2)
print("    set API =", url)
PYEOF
fi

# --- 5. launch Expo -----------------------------------------------------
cd "$APP_DIR"
if [ "$MODE" = "web" ]; then
  # Web build needs these; install once (no-op if already present).
  echo "==> Ensuring web deps (react-dom, react-native-web, @expo/metro-runtime)..."
  npx --yes expo install react-dom react-native-web @expo/metro-runtime >/dev/null 2>&1 || true
  echo "=============================================="
  echo " Backend : $BACKEND_URL   (log: /tmp/biaa-demo-api.log)"
  echo " Web app : open the forwarded Expo port from the PORTS panel (8081)."
  echo " Ctrl+C to stop everything."
  echo "=============================================="
  npx --yes expo start --web
else  # tunnel
  echo "=============================================="
  echo " Backend : $BACKEND_URL"
  echo " Phone   : scan the QR below in Expo Go (tunnel mode works off-LAN)."
  echo " Ctrl+C to stop everything."
  echo "=============================================="
  npx --yes expo start --tunnel
fi
