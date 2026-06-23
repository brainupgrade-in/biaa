#!/usr/bin/env bash
# Regenerate all Module 2 labs, solutions, and the index landing page.
# Notebooks are GENERATED -- edit the generators here, never the .ipynb files directly.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "$HERE/gen_labs.py"     # -> ../lab-*.ipynb  and  ../solutions/lab-*.ipynb
python3 "$HERE/gen_index.py"    # -> ../index.html   (reads _meta.json written above)

echo "Done. To verify graders, execute the solution notebooks, e.g.:"
echo "  python -m venv /tmp/v && /tmp/v/bin/pip -q install numpy scikit-learn matplotlib tensorflow-cpu nbconvert ipykernel"
echo "  for f in $HERE/../solutions/lab-*.ipynb; do /tmp/v/bin/python -m nbconvert --to notebook --execute --stdout \"\$f\" >/dev/null && echo \"ok \$f\"; done"
