# Module 5 lab generators

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
- Course prefix `biaa`; each lab works in `/tmp/biaa-lab-05-NN/`.
- Flow: Concept → Demo → Your Turn (`___`) → auto-grader ([PASS]/[FAIL]/[TODO] + Score).
- **This is the "What is Agentic AI?" module** — every graded step builds the agent mechanics
  by hand (tools, the reason → act → observe loop, ReAct parsing, tool routing, memory,
  guardrails, plan-and-execute, reflection) using **only the Python standard library**, driven by
  a deterministic rule-based "mock LLM" policy. No numpy/sklearn/transformers, no network, no keys.
- The calculator tool uses a small **AST-based safe evaluator** — never bare `eval()` on free text.
- Advanced labs (10–12) add an **optional, non-graded** cell that swaps the rule-based policy for a
  **real LLM via LangChain** (Ollama `llama3.2:1b`, or Groq `ChatGroq`) — it degrades gracefully if
  absent and never affects verification.

## Verify
Generation needs only the stdlib. Confirm graders by executing the **solution** notebooks in a
venv (`nbconvert nbformat ipykernel`) — each should print a full `Score: n/n`. Also run the
**student** notebooks — they must complete without uncaught errors (blanks → `[TODO]`).
