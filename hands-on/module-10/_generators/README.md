# Module 10 lab generators (the course finale)

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
- Course prefix `biaa`; each lab works in `/tmp/biaa-lab-10-NN/`.
- Flow: Concept → Demo → Your Turn (`___`) → auto-grader ([PASS]/[FAIL]/[TODO] + Score).
- **This is the "Ethics & Responsible AI" module (Lab 5.2)** — the labs cover BOTH halves the deck
  teaches: (1) responsible-AI practice — treat untrusted input as data (prompt injection), least
  privilege, fairness across groups, the responsible-agent checklist, the eval loop as a guardrail
  regression suite; and (2) **debugging agents** — read the trace, classify the failure mode, detect
  loops, and run a full debug-and-fix loop.
- Every GRADED step is **offline & deterministic** (pure Python standard library) — no
  numpy/sklearn/transformers, no network, no keys. The agent-assembly labs (10–12) reuse the
  compact **LangChain-shaped shim** from Modules 6–9 (`LC_TOOL`, `LC_MODEL`, `LC_PROMPT`, `LC_EXEC`)
  driven by a deterministic scripted `FakeChatModel`.
- Any arithmetic uses a small **AST-based safe evaluator** (`SAFE_CALC`) — never bare `eval()`.
- Advanced labs (10–12) add an **optional, non-graded** cell (`optional_real(...)`) that runs the
  SAME shapes against the **real LangChain** (Ollama `llama3.2:1b`, Groq `ChatGroq`) — it degrades
  gracefully if a package/model/key is absent and never affects verification.
- Keep every `___` blank inside a function body or a `try/except` so student notebooks still run
  top-to-bottom (blanks land as `[TODO]`/`[FAIL]`), never a bare module-level `___`.

## Verify
Generation needs only the stdlib. Confirm graders by executing the **solution** notebooks in a
venv (`nbconvert nbformat ipykernel`) — each should print a full `Score: n/n`. Also run the
**student** notebooks — they must complete without uncaught errors (blanks → `[TODO]`/`[FAIL]`).
