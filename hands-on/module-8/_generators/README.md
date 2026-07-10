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
- **Real LangChain, no shim.** The labs use `langchain_core.tools.@tool`, `PromptTemplate`, and
  (lab 11) `langchain_ollama.ChatOllama` + `langchain.agents.create_agent`. **Grade-scaffolding
  pattern:** every GRADED cell asserts only on **deterministic** structure (routing, synthesis, the
  refund gate, each specialist being a `CompiledStateGraph`) and **never calls an LLM** — so labs verify
  offline (no keys/network) against the course **`biaa-venv`**, not stdlib-only. Real-import constants:
  `TOOL_IMPORT`, `PROMPT_IMPORT`.
- **Live demos** use `live(...)`: an optional, non-graded cell calling a real `ChatOllama("llama3.2:1b")`
  that **self-skips** via the `ollama_up()` check in each lab's `setup()`. Non-model "see the real
  interface" cells use `optional_real(...)` (no network).
- **Real `@tool` requires a docstring** — never blank a docstring to a bare `___` comment (it raises at
  decoration time). Keep every `___` blank inside a function body or a `try/except`.

## Verify
Graded cells need the real libraries, so verify against **`biaa-venv`** (has `langchain`,
`langchain-ollama`), not a bare stdlib venv. Execute the **solution** notebooks — each should print a
full `Score: n/n`. Also run the **student** notebooks — they must complete without uncaught errors
(blanks → `[TODO]`/`[FAIL]`).
