# Module 6 lab generators

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
- Course prefix `biaa`; each lab works in `/tmp/biaa-lab-06-NN/`.
- Flow: Concept → Demo → Your Turn (`___`) → auto-grader ([PASS]/[FAIL]/[TODO] + Score).
- **This is the "Frameworks for Building AI Agents" module** — the graded steps teach the REAL
  LangChain workflow (`@tool`, `PromptTemplate`, `create_react_agent`, `AgentExecutor` +
  `max_iterations`, memory, a LangGraph-style state graph, guardrails, tracing) through a compact
  **LangChain-shaped shim** whose names and shapes mirror the real library. It runs on a
  deterministic scripted `FakeChatModel`, using **only the Python standard library** — no
  numpy/sklearn/transformers, no network, no keys. Reusable shim blocks in `gen_labs.py`:
  `LC_TOOL`, `LC_MODEL`, `LC_PROMPT`, `LC_EXEC`, and `SAFE_CALC`.
- The calculator/compute tools use a small **AST-based safe evaluator** — never bare `eval()`.
- Advanced labs (10–12) add an **optional, non-graded** cell (`optional_real(...)`) that runs the
  SAME shapes against the **real LangChain** (Ollama `llama3.2:1b`, Groq `ChatGroq`, Google Serper,
  Wolfram Alpha) — it degrades gracefully if a package/model/key is absent and never affects
  verification.
- Keep every `___` blank inside a function body or a `try/except` so student notebooks still run
  top-to-bottom (blanks land as `[TODO]`), never a bare module-level `___`.

## Verify
Generation needs only the stdlib. Confirm graders by executing the **solution** notebooks in a
venv (`nbconvert nbformat ipykernel`) — each should print a full `Score: n/n`. Also run the
**student** notebooks — they must complete without uncaught errors (blanks → `[TODO]`).
