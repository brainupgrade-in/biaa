#!/usr/bin/env bash
# Regenerate all Module 3 labs, solutions, and the index landing page.
# Notebooks are GENERATED -- edit the generators here, never the .ipynb files directly.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$HERE/gen_labs.py"
python3 "$HERE/gen_index.py"
echo "Done. These labs run REAL Hugging Face models -- verify against the course biaa-venv (network for first download):"
echo "  V=$HERE/../../../biaa-venv/bin/python"
echo "  for f in $HERE/../solutions/lab-*.ipynb; do \$V -m nbconvert --to notebook --execute --ExecutePreprocessor.timeout=600 --stdout \"\$f\" >/dev/null && echo \"ok \$f\"; done"
