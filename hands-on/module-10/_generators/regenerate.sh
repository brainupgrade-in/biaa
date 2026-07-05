#!/usr/bin/env bash
# Regenerate all Module 10 labs, solutions, and the index landing page.
# Notebooks are GENERATED -- edit the generators here, never the .ipynb files directly.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$HERE/gen_labs.py"
python3 "$HERE/gen_index.py"
echo "Done. Graded cells are stdlib-only; verify by executing the solution notebooks, e.g.:"
echo "  python -m venv /tmp/v && /tmp/v/bin/pip -q install nbconvert nbformat ipykernel"
echo "  for f in $HERE/../solutions/lab-*.ipynb; do /tmp/v/bin/python -m nbconvert --to notebook --execute --stdout \"\$f\" >/dev/null && echo \"ok \$f\"; done"
