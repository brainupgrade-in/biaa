# Module 8 lab generators

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
- Course prefix `biaa`; each lab works in `/tmp/biaa-lab-08-NN/`.
- Flow: Concept → Demo → Your Turn (`___`) → auto-grader ([PASS]/[FAIL]/[TODO] + Score).
- **This is the "Multi-Agent Collaboration & Decision Making" module** — the labs build the
  **multi-agent customer-service chatbot** (the client's Lab 4.2) piece by piece, exactly as the deck
  teaches: specialist roles → the supervisor/router → shared state & message passing → the
  orchestration shapes (sequential pipeline, parallel fan-out, explicit handoff) → the decision
  mechanisms (**voting, critique/debate, synthesis**) → observability → the assembled chatbot.
- Every GRADED step is **offline & deterministic** (pure Python standard library) — no
  numpy/sklearn/transformers, no network, no keys. The agent-assembly labs (11–12) reuse the
  compact **LangChain-shaped shim** from Modules 6–7 (`LC_TOOL`, `LC_MODEL`, `LC_PROMPT`, `LC_EXEC`)
  driven by a deterministic scripted `FakeChatModel`.
- Advanced labs (10–12) add an **optional, non-graded** cell (`optional_real(...)`) that runs the
  SAME shapes against the **real LangChain / LangGraph** (Ollama `llama3.2:1b`, Groq `ChatGroq`) — it
  degrades gracefully if a package/model/key is absent and never affects verification.
- Keep every `___` blank inside a function body or a `try/except` so student notebooks still run
  top-to-bottom (blanks land as `[TODO]`/`[FAIL]`), never a bare module-level `___`.

## Verify
Generation needs only the stdlib. Confirm graders by executing the **solution** notebooks in a
venv (`nbconvert nbformat ipykernel`) — each should print a full `Score: n/n`. Also run the
**student** notebooks — they must complete without uncaught errors (blanks → `[TODO]`/`[FAIL]`).
