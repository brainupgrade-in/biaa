# Module 9 lab generators

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
- Course prefix `biaa`; each lab works in `/tmp/biaa-lab-09-NN/`.
- Flow: Concept → Demo → Your Turn (`___`) → auto-grader ([PASS]/[FAIL]/[TODO] + Score).
- **This is the "Agents in Finance, Healthcare & Cybersecurity" module** — the labs build the
  **financial-report insight agent** (the client's Lab 5.1) piece by piece: ground & cite every
  figure → compute derived metrics → flag anomalies → the **no-advice guardrail** → **withhold the
  trade tool** → validate grounding → the audit trail → privacy/redaction → assistive-not-autonomous
  → the assembled agent.
- **Responsible-AI framing is the point:** the agent is informational only — it grounds & cites
  every figure, gives **no investment advice**, and has **no trade tool**; a human analyst decides.
- **Real LangChain, no shim.** The labs use `langchain_core.tools.@tool`, `PromptTemplate`, and
  (lab 11) `langchain_ollama.ChatOllama` + `langchain.agents.create_agent`. **Grade-scaffolding
  pattern:** every GRADED cell asserts only on **deterministic** structure (grounding/citation/compute
  logic, tool wiring, the **read-only guardrail**: `place_trade` is defined but never bound, agent is a
  `CompiledStateGraph`, `needs_review` wrapper) and **never calls an LLM** — so labs verify offline
  (no keys/network) against the course **`biaa-venv`**, not stdlib-only. Real-import constants
  `TOOL_IMPORT`/`PROMPT_IMPORT`; `shimcell`→`realcell`.
- Financial math uses a small **AST-based safe evaluator** (`SAFE_CALC`) — never bare `eval()`.
- **Live demos** use `live(...)`: an optional, non-graded cell calling a real `ChatOllama("llama3.2:1b")`
  that **self-skips** via the `ollama_up()` check in each lab's `setup()`. Non-model interface cells use
  `optional_real(...)` (no network).
- **Real `@tool` requires a docstring** — never blank a docstring to a bare `___` comment (it raises at
  decoration time). Keep every `___` blank inside a function body or a `try/except`.

## Verify
Graded cells need the real libraries, so verify against **`biaa-venv`** (has `langchain`,
`langchain-ollama`), not a bare stdlib venv. Execute the **solution** notebooks — each should print a
full `Score: n/n`. Also run the
**student** notebooks — they must complete without uncaught errors (blanks → `[TODO]`/`[FAIL]`).
