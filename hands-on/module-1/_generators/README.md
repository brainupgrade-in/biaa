# Module 1 lab generators

The 12 lab notebooks, their answer keys, and the `index.html` landing page in this module are
**generated** from the scripts here. **Do not hand-edit the `.ipynb` files** — your changes will
be overwritten on the next regeneration. Edit the generators instead.

## Files
- `gen_labs.py` — emits the 12 student notebooks to `../lab-*.ipynb` and the answer keys to
  `../solutions/lab-*.ipynb`. Each lab is one `@lab(...)`-decorated builder; blanks use the
  `{"s": <student line>, "a": <answer line>}` convention so student/solution stay in lock-step.
  Also writes `_meta.json` (here, beside the script) for the index generator.
- `gen_index.py` — reads `_meta.json` and writes `../index.html` (level-grouped lab cards).
- `regenerate.sh` — runs both in order.

## Regenerate
```bash
./regenerate.sh           # or: python3 gen_labs.py && python3 gen_index.py
```
No arguments needed — paths are derived relative to this directory. Pass `OUT_DIR [SOL_DIR]` to
`gen_labs.py` to emit elsewhere (e.g. a scratch dir for verification).

## Conventions baked in
- Course prefix `biaa`; each lab works in `/tmp/biaa-lab-01-NN/`.
- Flow per notebook: **Concept → Demo (runnable) → Your Turn (`___` blanks) → auto-grader**.
- Grader prints `[PASS]`/`[FAIL]`/`[TODO]` + `Score: n/total` via `expect()` / `expect_true()`;
  unfilled blanks and exceptions register as `[TODO]`.
- Offline-friendly deps: numpy + scikit-learn + matplotlib. Lab 12 has an optional Ollama step.

## Verify (graders actually pass)
Generation needs only the Python stdlib. To confirm the graders, execute the **solution**
notebooks in a venv with the deps and check each prints a full `Score` (see the tail of
`regenerate.sh` for the one-liner). Also run the **student** notebooks top-to-bottom — they must
complete without uncaught errors (blanks land as `[TODO]`).
