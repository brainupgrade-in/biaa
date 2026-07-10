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
- **This is the "Frameworks for Building AI Agents" module** — the labs use the **real LangChain 1.x**
  directly (**no shim, no `FakeChatModel`**): `langchain_core.tools.@tool`, `PromptTemplate`,
  `langchain_ollama.ChatOllama`, `langchain.agents.create_agent` (a `CompiledStateGraph`), and
  `langgraph.StateGraph`.
- **Grade-scaffolding pattern.** Every GRADED cell asserts only on **deterministic** structure the
  student builds — tool `name`/`args`/`.invoke`, `prompt.format`, the agent being a
  `CompiledStateGraph` with `model`+`tools` nodes, pure routing/guardrail logic, and reading a fixed
  real message trace — and **never calls an LLM**. So the labs verify **offline** (no keys/network),
  but now against the course **`biaa-venv`** (langchain/langgraph installed), **not** stdlib-only.
- The calculator/compute tools use a small **AST-based safe evaluator** (`SAFE_CALC`) — never bare `eval()`.
- **Live demos** use the `live(...)` helper: an **optional, non-graded** cell that calls a real
  `ChatOllama("llama3.2:1b")` (Groq alt; Serper/Wolfram need keys). It **self-skips** via the
  `ollama_up()` reachability check defined in each lab's `setup()` cell, so "Run All" never hangs offline.
- **Real `@tool` requires a docstring.** Docstring blanks must keep a `"""___ (TODO...)"""` **stub**
  (never a bare `___` comment) — otherwise the function has no `__doc__` and `@tool` raises a
  `ValueError` at decoration time, crashing the notebook. Keep all other `___` blanks inside a function
  body or a `try/except`.

## Verify
Graded cells need the real libraries, so verify against the course venv (**`biaa-venv`** — has
`langchain`, `langgraph`, `langchain-ollama`), not a bare stdlib venv. Execute the **solution**
notebooks — each should print a full `Score: n/n`. Also run the **student** notebooks — they must
complete without uncaught errors (blanks → `[TODO]`/`[FAIL]`). The live demo cells will call a local
Ollama if one is running; they self-skip otherwise. `regenerate.sh` is idempotent (byte-identical reruns).
