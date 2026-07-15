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

if [ -d "$DEST" ]; then
  echo "ERROR: $DEST already exists. Pick another name or remove it."
  exit 1
fi

echo "==> Scaffolding Expo app at $DEST (blank TypeScript template)..."
# --yes avoids the interactive prompt; runs npx create-expo-app under the hood.
npx --yes create-expo-app@latest "$DEST" --template blank-typescript

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
