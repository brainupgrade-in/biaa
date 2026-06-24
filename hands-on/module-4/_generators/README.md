# Module 4 lab generators

The 12 lab notebooks, their answer keys, and `index.html` are **generated** from these scripts.
**Do not hand-edit the `.ipynb` files** — edit the generators and re-run.

## Files
- `gen_labs.py` — emits `../lab-*.ipynb` and `../solutions/lab-*.ipynb`. Each lab is one
  `@lab(...)`-decorated builder; blanks use the `{"s": <student>, "a": <answer>}` convention.
  Writes `_meta.json` (here) for the index generator.
- `gen_index.py` — reads `_meta.json`, writes `../index.html`.
- `regenerate.sh` — runs both.

## Regenerate
```bash
./regenerate.sh            # or: python3 gen_labs.py && python3 gen_index.py
```

## Conventions
- Course prefix `biaa`; each lab works in `/tmp/biaa-lab-04-NN/`.
- Flow: Concept → Demo → Your Turn (`___`) → auto-grader ([PASS]/[FAIL]/[TODO] + Score).
- **All graded steps are offline** (numpy / scikit-learn / matplotlib) — no network, no keys.
- Advanced labs add an **optional, non-graded** Hugging Face cell (`transformers` + `torch`,
  tiny models) that degrades gracefully if not installed. No graded cell needs an API key.

## Verify
Generation needs only the stdlib. Confirm graders by executing the **solution** notebooks in a
venv (numpy scikit-learn matplotlib nbconvert ipykernel) — each should print a full `Score`.
Also run the **student** notebooks — they must complete without uncaught errors (blanks → `[TODO]`).
