#!/usr/bin/env python3
"""Point every lab notebook at the course kernel ('biaa').

The setup scripts register a Jupyter kernel named 'biaa' ("Python 3.12 (biaa)"),
but the committed notebooks ship with the generic 'python3' kernelspec -- so
Jupyter and VS Code make participants pick a kernel by hand. That is the #1
live-workshop time-sink, and it is worst on Windows/VS Code (multiple 'Python 3'
entries, none obviously the venv). This rewrites metadata.kernelspec in every
hands-on/**/*.ipynb to 'biaa' so the labs auto-select the right environment.

Run from anywhere; it finds the repo root relative to this file. Idempotent --
re-running changes nothing once notebooks already point at 'biaa'. This is a
local, student-side action: the committed notebooks keep 'python3' so they stay
portable (Colab, a differently-named venv, etc.). --reset restores 'python3'.

Usage:
  python scripts/set-notebook-kernel.py           # set the labs to the 'biaa' kernel
  python scripts/set-notebook-kernel.py --reset    # restore the generic 'python3' kernel
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HANDS_ON = REPO / "hands-on"

BIAA = {"display_name": "Python 3.12 (biaa)", "language": "python", "name": "biaa"}
GENERIC = {"display_name": "Python 3", "language": "python", "name": "python3"}


def main(argv):
    if argv and argv != ["--reset"]:
        print(__doc__.split("Usage:")[1].strip())
        return 2 if argv != ["-h"] and argv != ["--help"] else 0
    target = GENERIC if "--reset" in argv else BIAA
    nbs = [p for p in sorted(HANDS_ON.rglob("*.ipynb"))
           if ".ipynb_checkpoints" not in p.parts]
    changed = 0
    for f in nbs:
        try:
            nb = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"  [skip] {f.relative_to(REPO)}: {e}")
            continue
        md = nb.setdefault("metadata", {})
        if md.get("kernelspec") == target:
            continue
        md["kernelspec"] = dict(target)
        # Match the generators' serialization (indent=1, ensure_ascii=False, no
        # trailing newline) so re-runs and a later regenerate stay minimal-diff.
        f.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
        changed += 1
    print(f"  Kernel '{target['name']}' set on {changed} notebook(s) "
          f"({len(nbs) - changed} already correct, {len(nbs)} total).")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
