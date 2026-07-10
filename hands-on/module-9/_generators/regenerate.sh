#!/usr/bin/env bash
# Regenerate all Module 9 labs, solutions, and the index landing page.
# Notebooks are GENERATED -- edit the generators here, never the .ipynb files directly.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$HERE/gen_labs.py"
python3 "$HERE/gen_index.py"
echo "Done. Labs use the REAL LangChain 1.x (langchain-groq); non-LLM cells verify offline against the"
echo "course biaa-venv, and the 'Run it for real' cells call Groq when GROQ_API_KEY is set. Verify e.g.:"
echo "  for f in $HERE/../solutions/lab-*.ipynb; do ../../biaa-venv/bin/python -m nbconvert --to notebook --execute --stdout \"\$f\" >/dev/null && echo \"ok \$f\"; done"
