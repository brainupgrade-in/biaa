#!/usr/bin/env bash
# Building Intelligent AI Agents - pre-workshop smoke test (SETUP.md section 8)
# Cross-platform: works on Linux, macOS and Windows Git Bash.
# Run it AFTER setup, from inside the activated biaa-venv (the setup scripts
# call it automatically at the end). If run standalone it will find and use the
# venv's python without needing activation.
set -u

# --- optional per-day mode: `smoke-test.sh --day N` ----------------------
# No flag  -> full check (every tier). --day N -> only what Day N needs, plus
# that day's LLM/API reachability. Handy as a 30-second check each morning.
DAY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --day) DAY="${2:-0}"; shift 2 ;;
    --day=*) DAY="${1#*=}"; shift ;;
    -h|--help)
      echo "Usage: bash scripts/smoke-test.sh [--day 1|2|3|4|5]"
      echo "  (no flag) full pre-workshop check;  --day N  just Day N's needs"
      exit 0 ;;
    *) echo "WARNING: ignoring unknown flag '$1'" >&2; shift ;;
  esac
done

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

# reachability helpers used by --day mode ---------------------------------
ollama_status() { # -> DOWN | UP_NO_MODEL | UP_HAS_MODEL
  "$PY" - <<'PYEOF'
import json, urllib.request
try:
    d = json.load(urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3))
    names = [m.get("name", "") for m in d.get("models", [])]
    print("UP_HAS_MODEL" if any(n.startswith("llama3.1:8b") for n in names) else "UP_NO_MODEL")
except Exception:
    print("DOWN")
PYEOF
}
key_set() { # true if the var is exported OR present in the repo .env (labs load_dotenv it)
  "$PY" - "$ROOT" "$1" <<'PYEOF'
import os, sys, pathlib
root, name = sys.argv[1], sys.argv[2]
if os.getenv(name):
    sys.exit(0)
envf = pathlib.Path(root) / ".env"
if envf.exists():
    for line in envf.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if s.startswith(name + "="):
            sys.exit(0 if s.split("=", 1)[1].strip().strip('"').strip("'") else 1)
sys.exit(1)
PYEOF
}
day_report() {
  echo
  echo "----------------------------------------------"
  echo "Result: $pass passed, $fail failed"
  if [ "$fail" -eq 0 ]; then
    echo "Day $DAY: ready to go."
  else
    echo "Day $DAY: fix the [FAIL] line(s) above - see scripts/RUNBOOK.md."
  fi
  echo "----------------------------------------------"
  exit "$fail"
}

if [ "$DAY" != "0" ]; then
  case "$DAY" in
    1)
      echo "Day 1 - Foundations & Deep Learning (Modules 1-2) - no LLM needed"
      check "numpy / scikit-learn / matplotlib"  "$PY" -c "import numpy, sklearn, matplotlib"
      check "tensorflow-cpu (MNIST)"              "$PY" -c "import tensorflow"
      check "jupyter / nbformat"                  "$PY" -c "import jupyterlab, nbformat"
      ;;
    2)
      echo "Day 2 - Transformers & fine-tuning (Modules 3-4) - Hugging Face"
      check "transformers / torch"               "$PY" -c "import transformers, torch"
      check "tf-keras (transformers TF backend)"  "$PY" -c "import tf_keras"
      if key_set GROQ_API_KEY; then echo "  [set ] GROQ_API_KEY (hosted text-gen cells)"
      else echo "  [info] GROQ_API_KEY not set - the hosted text-gen cells self-skip"; fi
      ;;
    3)
      echo "Day 3 - Agentic AI + frameworks (Modules 5-6) - LOCAL Ollama (llama3.1:8b)"
      check "langchain / community / langgraph"  "$PY" -c "import langchain, langchain_community, langgraph"
      check "langchain-ollama"                   "$PY" -c "import langchain_ollama"
      check "wolframalpha lib (Module 6)"         "$PY" -c "import wolframalpha"
      case "$(ollama_status)" in
        UP_HAS_MODEL) printf '  [PASS] Ollama up on :11434 with llama3.1:8b\n'; pass=$((pass+1)) ;;
        UP_NO_MODEL)  printf '  [FAIL] Ollama up but llama3.1:8b missing - run: ollama pull llama3.1:8b\n'; fail=$((fail+1)) ;;
        *)            printf '  [FAIL] Ollama not reachable on 127.0.0.1:11434 - start it (ollama serve) or switch the lab to Groq\n'; fail=$((fail+1)) ;;
      esac
      if key_set SERPER_API_KEY; then echo "  [set ] SERPER_API_KEY (search lab)"
      else echo "  [info] SERPER_API_KEY not set - the search lab self-skips"; fi
      if key_set WOLFRAM_ALPHA_APPID; then echo "  [set ] WOLFRAM_ALPHA_APPID (compute lab)"
      else echo "  [info] WOLFRAM_ALPHA_APPID not set - the compute lab self-skips"; fi
      ;;
    4|5)
      echo "Day $DAY - Real-world & responsible agents (Modules 7-10) - Groq (gpt-oss-20b)"
      check "langchain / langgraph"              "$PY" -c "import langchain, langgraph"
      check "langchain-groq"                     "$PY" -c "import langchain_groq"
      if key_set GROQ_API_KEY; then printf '  [PASS] GROQ_API_KEY is set\n'; pass=$((pass+1))
      else printf '  [FAIL] GROQ_API_KEY not set - free key at console.groq.com, then export it\n'; fail=$((fail+1)); fi
      ;;
    *)
      echo "Unknown day '$DAY' (use 1-5). Running the full check instead."
      DAY=0
      ;;
  esac
  [ "$DAY" != "0" ] && day_report
fi

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

echo "Tier 2 - Hugging Face transformers (Day 2, Modules 3-4)"
check "transformers / torch"               "$PY" -c "import transformers, torch"
check "tf-keras (transformers TF backend)" "$PY" -c "import tf_keras"
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
