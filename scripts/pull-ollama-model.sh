#!/usr/bin/env bash
# Pull the Day-3 (Modules 5-6) local model into the Codespace on demand.
# The Ollama binary is installed by the devcontainer feature; the ~4.9 GB
# llama3.1:8b weights are NOT pulled at create time, so run this when you
# actually need Day 3. Days 4-5 use Groq (cloud) and need nothing here.
set -uo pipefail

MODEL="${1:-llama3.1:8b}"

if ! command -v ollama >/dev/null 2>&1; then
  echo "ERROR: ollama not found. Rebuild the Codespace (the devcontainer feature installs it)."
  exit 1
fi

# Start a transient server if the daemon isn't already up.
if ! ollama list >/dev/null 2>&1; then
  echo "==> Starting 'ollama serve' in the background..."
  ollama serve >/tmp/ollama.log 2>&1 &
  for _ in $(seq 1 15); do
    ollama list >/dev/null 2>&1 && break
    sleep 1
  done
fi

echo "==> Pulling $MODEL (this is large; grab a coffee)..."
ollama pull "$MODEL"
echo "==> Done. Modules 5-6 labs will now find Ollama at http://127.0.0.1:11434"
