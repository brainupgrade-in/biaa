#!/usr/bin/env bash
# Building Intelligent AI Agents - pre-workshop smoke test (SETUP.md section 8)
# Cross-platform: works on Linux, macOS and Windows Git Bash.
# Run it AFTER setup, from inside the activated biaa-venv (the setup scripts
# call it automatically at the end). If run standalone it will find and use the
# venv's python without needing activation.
set -u

# --- locate the venv python (works activated or not) ---------------------
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/biaa-venv"
if [ -x "$VENV/bin/python" ]; then
  PY="$VENV/bin/python"          # Linux / macOS
elif [ -x "$VENV/Scripts/python.exe" ]; then
  PY="$VENV/Scripts/python.exe"  # Windows Git Bash
elif [ -n "${PYTHON:-}" ]; then
  PY="$PYTHON"                   # explicit override
elif command -v python >/dev/null 2>&1; then
  PY="python"                    # PATH fallback (no venv yet)
else
  PY="python3"                   # Linux where only python3 exists
fi

pass=0; fail=0
check() { # check "label" command...
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    printf '  [PASS] %s\n' "$label"; pass=$((pass+1))
  else
    printf '  [FAIL] %s\n' "$label"; fail=$((fail+1))
  fi
}

echo "=============================================="
echo " Building Intelligent AI Agents - smoke test"
echo "=============================================="
echo "python: $("$PY" --version 2>&1)  ($PY)"
echo
echo "Tier 1 - core science + notebook stack"
check "numpy / scikit-learn / matplotlib" "$PY" -c "import numpy, sklearn, matplotlib"
check "tensorflow-cpu (MNIST, Day 1)"      "$PY" -c "import tensorflow"
check "jupyter / nbformat"                 "$PY" -c "import jupyterlab, nbformat"
echo
echo "Tier 2 - agent + LLM stack (Days 3-5)"
check "langchain / community / langgraph"  "$PY" -c "import langchain, langchain_community, langgraph"
check "langchain-groq (Groq option)"       "$PY" -c "import langchain_groq"
check "langchain-ollama (Ollama option)"   "$PY" -c "import langchain_ollama"
check "wolframalpha (Day 3)"               "$PY" -c "import wolframalpha"
echo

echo "Tier 3 - optional Hugging Face demo (Day 2)"
if "$PY" -c "import transformers, torch" >/dev/null 2>&1; then
  echo "  [PASS] transformers / torch (optional)"
else
  echo "  [ ok ] transformers / torch not installed - optional, labs still pass"
fi
echo

echo "LLM reachability (need ONE of these for the full experience)"
if command -v ollama >/dev/null 2>&1; then
  echo "  [ ok ] ollama CLI found - run: ollama pull llama3.2:1b"
else
  echo "  [info] ollama CLI not found (fine if you are using Groq)"
fi
echo

echo "API keys / env vars (Day 3 + LLM) - blank is OK if using the fallback"
"$PY" - <<'PYEOF'
import os
for k in ("GROQ_API_KEY", "SERPER_API_KEY", "WOLFRAM_ALPHA_APPID", "OPENAI_API_KEY", "HF_TOKEN"):
    print(f"  {'[set ]' if os.getenv(k) else '[    ]'} {k}")
PYEOF
echo
echo "----------------------------------------------"
echo "Result: $pass passed, $fail failed"
if [ "$fail" -eq 0 ]; then
  echo "All core checks passed - you are ready for the workshop."
else
  echo "Some checks failed - re-run the setup script or see scripts/README.md."
fi
echo "----------------------------------------------"
exit "$fail"
