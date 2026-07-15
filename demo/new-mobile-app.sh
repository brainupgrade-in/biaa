#!/usr/bin/env bash
# Scaffold an Expo (React Native) app wired to the demo API, fast.
# Usage:  bash demo/new-mobile-app.sh [app-name]
#
# Produces demo/<app-name>/ (default: mobile) from the Expo blank-TypeScript
# template, then drops in an App.tsx that talks to the FastAPI /chat endpoint.
# From there, drive the real build with OpenCode:  opencode
set -euo pipefail

APP="${1:-mobile}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HERE/$APP"

# Node/npx (from the devcontainer 'node' feature, via nvm) may not be on a
# non-login shell's PATH - source nvm before giving up.
if ! command -v npx >/dev/null 2>&1; then
  export NVM_DIR="${NVM_DIR:-/usr/local/share/nvm}"
  # shellcheck disable=SC1091
  [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1 || true
  for d in "$NVM_DIR/current/bin" "$NVM_DIR"/versions/node/*/bin /usr/local/lib/nodejs/*/bin; do
    [ -d "$d" ] && export PATH="$d:$PATH"
  done
fi
if ! command -v npx >/dev/null 2>&1; then
  echo "ERROR: Node / npx not found. In a Codespace, rebuild the container" >&2
  echo "  (Command Palette > 'Codespaces: Rebuild Container') to install the" >&2
  echo "  'node' devcontainer feature, then re-run this script." >&2
  exit 1
fi

if [ -d "$DEST" ]; then
  echo "ERROR: $DEST already exists. Pick another name or remove it."
  exit 1
fi

echo "==> Scaffolding Expo app at $DEST (blank TypeScript template)..."
# CI=1 forces non-interactive: inside an existing git repo create-expo-app would
# otherwise PROMPT "Skip initializing a new git repository?" and hang a script.
# --yes runs create-expo-app without a separate install confirmation.
CI=1 npx --yes create-expo-app@latest "$DEST" --template blank-typescript --no-install
echo "==> Installing app dependencies (npm install)..."
( cd "$DEST" && CI=1 npm install --no-audit --no-fund )

echo "==> Writing a starter App.tsx wired to the demo API (/chat)..."
cat > "$DEST/App.tsx" <<'TSX'
import { useState } from "react";
import { SafeAreaView, TextInput, Button, Text, ScrollView, StyleSheet } from "react-native";

// In a Codespace, replace with your forwarded 8000 URL (…-8000.app.github.dev).
// On a device via Expo Go, use your machine's LAN IP, not localhost.
const API = "http://localhost:8000";

export default function App() {
  const [input, setInput] = useState("");
  const [reply, setReply] = useState("");
  const [busy, setBusy] = useState(false);

  async function send() {
    setBusy(true);
    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      setReply(data.reply ?? JSON.stringify(data));
    } catch (e) {
      setReply(`Request failed: ${String(e)}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <SafeAreaView style={styles.root}>
      <Text style={styles.h1}>biaa agent demo</Text>
      <TextInput
        style={styles.input}
        placeholder="Ask the agent…"
        value={input}
        onChangeText={setInput}
      />
      <Button title={busy ? "Thinking…" : "Send"} onPress={send} disabled={busy} />
      <ScrollView style={styles.out}>
        <Text>{reply}</Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, padding: 20, gap: 12 },
  h1: { fontSize: 22, fontWeight: "600" },
  input: { borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 12 },
  out: { marginTop: 16 },
});
TSX

echo ""
echo "==> Done. Next:"
echo "     1. Start the API:    uvicorn demo.backend.main:app --host 0.0.0.0 --port 8000"
echo "     2. cd demo/$APP && npx expo start"
echo "     3. In a Codespace, set API to the forwarded 8000 URL (Ports panel)."
echo "     4. Iterate fast with OpenCode:   cd demo/$APP && opencode"
