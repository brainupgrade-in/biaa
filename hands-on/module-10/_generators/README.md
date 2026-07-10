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
- **Real LangChain, no shim.** The labs use `langchain_core.tools.@tool`, real message traces
  (`AIMessage`/`ToolMessage`), and (labs 10–11) `langchain_ollama.ChatOllama` +
  `langchain.agents.create_agent`. **Grade-scaffolding pattern:** every GRADED cell asserts only on
  **deterministic** structure (guardrail logic, trace-reading over fixed real message lists, tool wiring,
  agent is a `CompiledStateGraph`) and **never calls an LLM** — so labs verify offline (no keys/network)
  against the course **`biaa-venv`**, not stdlib-only. Real-import constant `TOOL_IMPORT`; `shimcell`→`realcell`.
- Any arithmetic uses a small **AST-based safe evaluator** (`SAFE_CALC`) — never bare `eval()`.
- **Live demos** use `live(...)`: an optional, non-graded cell calling a real `ChatOllama("llama3.2:1b")`
  that **self-skips** via the `ollama_up()` check in each lab's `setup()`. Non-model interface cells use
  `optional_real(...)` (no network).
- **Real `@tool` requires a docstring** — never blank a docstring to a bare `___` comment. Keep every
  `___` blank inside a function body or a `try/except`.

## Verify
Graded cells need the real libraries, so verify against **`biaa-venv`** (has `langchain`,
`langchain-ollama`), not a bare stdlib venv. Execute the **solution** notebooks — each should print a
full `Score: n/n`. Also run the
**student** notebooks — they must complete without uncaught errors (blanks → `[TODO]`/`[FAIL]`).
