# Module 7 lab generators

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
- Course prefix `biaa`; each lab works in `/tmp/biaa-lab-07-NN/`.
- Flow: Concept → Demo → Your Turn (`___`) → auto-grader ([PASS]/[FAIL]/[TODO] + Score).
- **This is the "Task Automation with AI Agents" module** — the labs build the
  **email-drafting agent** (the client's Lab 4.1) piece by piece, exactly as the deck teaches:
  the automation pipeline (trigger → gather → draft → validate → approve → act), the three
  patterns (**draft / extract / route**), structured output, reliability (validation, retries,
  idempotency), the **draft-not-send** human-in-the-loop guardrail, and observability.
- **Real LangChain, no shim.** The labs use `langchain_core.tools.@tool`, `PromptTemplate`, and
  (labs 11–12) `langchain_ollama.ChatOllama` + `langchain.agents.create_agent`. **Grade-scaffolding
  pattern:** every GRADED cell asserts only on **deterministic** structure (tool wiring, prompt
  formatting, the pipeline, the gather-only guardrail, `create_agent` returning a `CompiledStateGraph`)
  and **never calls an LLM** — so labs verify offline (no keys/network) against the course
  **`biaa-venv`**, not stdlib-only. Real-import constants: `TOOL_IMPORT`, `PROMPT_IMPORT` (+ `SAFE_CALC`).
- **Live demos** use `live(...)`: an optional, non-graded cell calling a real `ChatOllama("llama3.2:1b")`
  that **self-skips** via the `ollama_up()` check in each lab's `setup()`. Non-model "see the real
  interface" cells use `optional_real(...)` (no network).
- **Real `@tool` requires a docstring** — never blank a docstring to a bare `___` comment (it raises at
  decoration time). Keep every `___` blank inside a function body or a `try/except`.

## Verify
Graded cells need the real libraries, so verify against **`biaa-venv`** (has `langchain`,
`langchain-ollama`), not a bare stdlib venv. Execute the **solution** notebooks — each should print a
full `Score: n/n`. Also run the
**student** notebooks — they must complete without uncaught errors (blanks → `[TODO]`/`[FAIL]`).
