#!/usr/bin/env bash
# Regenerate all Module 6 labs, solutions, and the index landing page.
# Notebooks are GENERATED -- edit the generators here, never the .ipynb files directly.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$HERE/gen_labs.py"
python3 "$HERE/gen_index.py"
echo "Done. Graded cells use the REAL LangChain but never call an LLM, so they verify offline"
echo "against the course venv. Execute the solution notebooks to check, e.g.:"
echo "  for f in $HERE/../solutions/lab-*.ipynb; do ../../biaa-venv/bin/python -m nbconvert --to notebook --execute --stdout \"\$f\" >/dev/null && echo \"ok \$f\"; done"
