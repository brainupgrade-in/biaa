# CLAUDE.md

Guidance for Claude Code when working in this sub-project. Read the parent
`Training/courses/CLAUDE.md` first for the conventions shared across all courses.

## What this is

`building-intelligents-ai-agents/` is an instructor-led training course authored by
Rajesh Gheware (Gheware UniGPS Solutions LLP):

**Building Intelligent AI Agents** &mdash; *From deep-learning foundations & transformers to
autonomous, industry-ready AI agents.*

- **Length:** 5 days, hands-on (~50% concept / 50% lab)
- **Level:** Beginner &rarr; Practitioner. **No prior AI/ML/DL knowledge required**; basic
  Python recommended but not mandatory.
- **Audience:** developers, data/automation professionals, technical leads/architects moving
  into agentic AI.
- **Stage:** early build &mdash; **Days 1&ndash;4 complete + Module 9 complete**
  (Modules 1&ndash;9: decks + labs). Decks:
  `presentation/day1-module1-...` (22 slides), `day1-module2-...` (20), `day2-module3-why-transformers...`
  (19), `day2-module4-pretrained-models-and-fine-tuning...` (20), `day3-module5-what-is-agentic-ai...`
  (42 slides), `day3-module6-frameworks-for-building-ai-agents...` (43 slides),
  `day4-module7-task-automation...` (43 slides),
  `day4-module8-multi-agent-collaboration...` (43 slides),
  `day5-module9-agents-in-industry...` (43 slides) &mdash; the last five each carry a 10-question quiz
  (Q slide &rarr; answer slide interleaved, 4 choices each). Labs:
  `hands-on/module-1/` &hellip; `module-9/` (12 labs each + `index.html` + `solutions/` + `_generators/`).
  Outline cross-links all of them (Slides badge per module 1&ndash;9; 12-Labs badges for modules 1&ndash;9;
  Day-1/2/3/4/5 labs boxes summarise the sets). Remaining: **Module 10** (deck + labs, ethics &amp;
  responsible AI &mdash; the final module), not built yet.

## Hands-on labs (the convention that's now established)

- **Course prefix:** `biaa`. Each lab writes to its own `/tmp/biaa-lab-MM-NN/` working dir
  (module MM, lab NN) &mdash; e.g. `/tmp/biaa-lab-01-07/`, `/tmp/biaa-lab-02-11/`.
- **Module 1 has 12 labs** (`hands-on/module-1/lab-01..12-*.ipynb`): 6 Beginner, 3 Intermediate,
  3 Advanced &mdash; an experiential progression (rules &rarr; data &rarr; ML pipeline &rarr; overfitting
  &rarr; clustering &rarr; perceptron-from-scratch &rarr; digit NN &rarr; mini-agent capstone). ~320 min total.
- **Module 2 has 12 labs** (`hands-on/module-2/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-02-NN/`):
  6 Beginner, 3 Intermediate, 3 Advanced &mdash; the artificial neuron, activations, MSE loss,
  gradient descent, training a neuron, reading training curves (Beginner, NumPy/matplotlib);
  2-layer net from scratch, overfitting/early-stopping, hyperparameters (Intermediate, sklearn);
  **Keras on real MNIST** &mdash; first Keras net, the MNIST classifier with training curves, and
  visualising decisions/confusion matrix (Advanced). ~375 min total. **Labs 10&ndash;12 use
  `tensorflow-cpu` + `keras.datasets.mnist`**; the shared `load_image_data()` helper falls back to
  offline `load_digits` (8x8) if MNIST can't download, so they run with or without network
  (verified on Python 3.13 with tensorflow-cpu 2.21 / keras 3.14).
- **Module 3 has 12 labs** (`hands-on/module-3/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-03-NN/`):
  6 Beginner, 3 Intermediate, 3 Advanced &mdash; tokenization, embeddings/cosine, attention-by-hand,
  positional encoding, fill-mask (bigram), subword tokenizer (Beginner); semantic search (TF-IDF),
  self-attention over a sequence, attention heatmap (Intermediate); text generation (greedy/temperature),
  feature-extraction + classifier head, and a mini-transformer-pipeline capstone (Advanced). ~375 min.
  **Framework choice:** every GRADED cell is **offline (NumPy/scikit-learn/matplotlib)** &mdash; no keys,
  no downloads; each Advanced lab adds an **optional, non-graded Hugging Face cell** (`transformers`+`torch`,
  tiny models `bert-tiny`/`tiny-gpt2`) that degrades gracefully if absent. The client's "GPT API text
  generation" is reframed as a runnable local-generation lab + an optional guarded OpenAI/Groq key cell.
- **Module 4 has 12 labs** (`hands-on/module-4/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-04-NN/`):
  6 Beginner, 3 Intermediate, 3 Advanced &mdash; using a pretrained model, softmax confidence,
  prompt/fine-tune/RAG, model inputs (ids/mask/padding), dataset prep, train/val split (Beginner);
  frozen features + trainable head, precision/recall/confusion, data-efficiency curve (Intermediate);
  **fine-tune a sentiment classifier** (before vs after), tune &amp; evaluate (regularisation +
  confusion matrix), and a capstone adapting a model to a NEW task (Advanced). ~340 min.
  **Framework choice:** same as Module 3 &mdash; every GRADED cell is offline (scikit-learn transfer
  learning: frozen TF-IDF features + a trainable head, the portable form of fine-tuning); each Advanced
  lab adds an **optional, non-graded Hugging Face cell** that fine-tunes/uses a real `bert-tiny`. The
  client's "fine-tune BERT for sentiment" is the offline-graded core + the optional real-bert cell.
  (Real bert-tiny did not load on the bleeding-edge verify venv &mdash; transformers 5.x / torch 2.12
  tokenizer-backend issue &mdash; so the offline path is what guarantees verification; the optional cell
  targets the managed sandbox.)
- **Module 5 has 12 labs** (`hands-on/module-5/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-05-NN/`):
  6 Beginner, 3 Intermediate, 3 Advanced &mdash; model-vs-agent, build-a-tool, the reason&rarr;act&rarr;observe
  agent loop, ReAct-step parsing, tool routing, memory/scratchpad (Beginner); a rule-based ReAct agent
  (two-step task), guardrails (max-steps / allow-list / loop-detection / input validation), tool selection
  (Intermediate); plan-and-execute, reflection/self-critique, and a **mini-autonomous-agent capstone** over
  a task suite (Advanced). ~330 min. **Framework choice:** every GRADED cell is **pure Python stdlib** &mdash;
  students build a ReAct agent from scratch driven by a deterministic rule-based ("mock LLM") policy, with an
  **AST-based safe calculator** (no bare `eval`); no numpy/sklearn needed. Each Advanced lab adds an
  **optional, non-graded, guarded real-LLM cell** (`langchain_ollama` `llama3.2:1b`, Groq alt) that degrades
  gracefully &mdash; the bridge to Module 6 (Agent Frameworks) and the Day-3 LangChain labs. So this module
  verifies with just the Jupyter exec stack (`nbconvert nbformat ipykernel`).
- **Module 6 has 12 labs** (`hands-on/module-6/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-06-NN/`):
  6 Beginner, 3 Intermediate, 3 Advanced &mdash; first tool with `@tool`, tool descriptions/catalog, the
  model interface (`PromptTemplate` + `.invoke`), `create_react_agent`, the `AgentExecutor` loop +
  `max_iterations`, safe tool routing (Beginner); conversation memory, a LangGraph-style state graph
  (human-in-the-loop node), multi-tool orchestration (Intermediate); connect to external APIs
  (search + Wolfram-style compute), guardrails &amp; a tracing callback, and a **guardrailed-LangChain-agent
  capstone** over a task suite (Advanced). ~335 min. **Framework choice:** this is the LangChain module, so
  every GRADED cell teaches the **real LangChain workflow** through a compact **LangChain-shaped shim**
  (`LC_TOOL`/`LC_MODEL`/`LC_PROMPT`/`LC_EXEC` in `_generators/gen_labs.py` &mdash; same names/shapes as the
  real library) driven by a deterministic scripted `FakeChatModel`; **pure Python stdlib** (AST-safe
  calculator, no bare `eval`), so it verifies with just `nbconvert nbformat ipykernel`. Each Advanced lab
  (10&ndash;12) adds an **optional, non-graded, guarded real-LangChain cell** (`langchain`/`langchain-ollama`
  `llama3.2:1b`, Groq alt; Google Serper / Wolfram Alpha need their own keys) that degrades gracefully &mdash;
  the bridge to Day 4. **Note:** like Module 5, unfilled student blanks show a mix of `[TODO]` (blank raises)
  and `[FAIL]` (Jupyter pre-binds `___` to `''`, so some blanks yield a wrong value, not an exception);
  the hard invariant is that student notebooks run top-to-bottom without uncaught errors and solutions
  score full.
- **Module 7 has 12 labs** (`hands-on/module-7/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-07-NN/`):
  6 Beginner, 3 Intermediate, 3 Advanced &mdash; this is the **task-automation** module and every lab builds
  the **email-drafting agent** (the client's Lab 4.1) piece by piece: the automation pipeline
  (trigger&rarr;gather&rarr;draft&rarr;validate&rarr;approve&rarr;act), gather-with-tools, structured output,
  the extract pattern, the route pattern, drafting a grounded reply (Beginner); validation, retry &amp;
  idempotency, and the **draft-not-send** human-in-the-loop gate (Intermediate); observability/run-log,
  **assembling the email agent** (gather-only tools &mdash; `send_email` withheld &mdash; returns a
  `needs_approval` draft), and a **capstone** that chains extract&rarr;route&rarr;gather&rarr;draft&rarr;validate
  over a suite and never auto-sends (Advanced). ~340 min. **Framework choice:** every GRADED cell is
  **offline &amp; deterministic pure Python stdlib** &mdash; extract/route/validate are rule-based; the two
  agent-assembly labs (11&ndash;12) reuse Module 6's **LangChain-shaped shim** (`LC_TOOL`/`LC_MODEL`/`LC_PROMPT`/`LC_EXEC`
  in `_generators/gen_labs.py`) driven by a scripted `FakeChatModel`, so it verifies with just
  `nbconvert nbformat ipykernel`. Each Advanced lab (10&ndash;12) adds an **optional, non-graded, guarded
  real-LangChain cell** (`langchain-ollama` `llama3.2:1b`, Groq alt) that degrades gracefully &mdash; the
  bridge to Module 8. Like Modules 5&ndash;6, unfilled student blanks land as a mix of `[TODO]`/`[FAIL]`;
  the invariant is student notebooks run clean and solutions score full.
- **Module 8 has 12 labs** (`hands-on/module-8/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-08-NN/`):
  6 Beginner, 3 Intermediate, 3 Advanced &mdash; this is the **multi-agent** module and every lab builds
  the **customer-service chatbot** (the client's Lab 4.2) piece by piece: specialist agents
  (separation of concerns), the supervisor/router (multi-intent), shared state &amp; message passing,
  the sequential pipeline, parallel fan-out, explicit capped handoff (Beginner); voting/consensus,
  critique/debate (capped loop), synthesis into one grounded reply (Intermediate); observability with
  loop-detection, **assembling the chatbot** (supervisor routes to billing/tech specialist
  `AgentExecutor`s &rarr; synthesise &rarr; a `needs_approval` reply, refund gated on a human), and a
  **capstone** running the full team over a suite (Advanced). ~340 min. **Framework choice:** every
  GRADED cell is **offline &amp; deterministic pure Python stdlib** &mdash; the multi-agent constructs
  (route/handoff/vote/critique/synthesise) are rule-based; the two agent-assembly labs (11&ndash;12)
  reuse Modules 6&ndash;7's **LangChain-shaped shim** (`LC_TOOL`/`LC_MODEL`/`LC_PROMPT`/`LC_EXEC` in
  `_generators/gen_labs.py`) driven by a scripted `FakeChatModel`, so it verifies with just
  `nbconvert nbformat ipykernel`. Each Advanced lab (10&ndash;12) adds an **optional, non-graded, guarded
  real cell** (`langchain-ollama`/`langgraph` `llama3.2:1b`, Groq alt) that degrades gracefully &mdash;
  the bridge to Day 5. Like Modules 5&ndash;7, unfilled student blanks land as a mix of `[TODO]`/`[FAIL]`;
  the invariant is student notebooks run clean and solutions score full.
- **Module 9 has 12 labs** (`hands-on/module-9/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-09-NN/`):
  6 Beginner, 3 Intermediate, 3 Advanced &mdash; this is the **high-stakes/industry** module and every
  lab builds the **financial-report insight agent** (the client's Lab 5.1) piece by piece: ground a
  figure with its source, cite every claim, compute derived metrics (safe calculator), flag anomalies,
  the **no-advice guardrail**, **withholding the trade tool** (Beginner); validate grounding, the audit
  trail, privacy minimize/redact (Intermediate); assistive-not-autonomous (`needs_review` + citations
  defend automation bias), **assembling the insight agent** (read-only `extract_figure`/`compute`
  tools &mdash; no trade tool &mdash; returns a grounded, cited, `needs_review` insight), and a
  **capstone** running the agent over a report suite (Advanced). ~340 min. **Responsible-AI framing is
  the point:** the agent is informational only &mdash; grounds &amp; cites every figure, gives no
  investment advice, has no trade tool; a human analyst decides. **Framework choice:** every GRADED cell
  is **offline &amp; deterministic pure stdlib** (ground/cite/compute/flag/validate/redact are
  rule-based; financial math via an AST-safe calculator, no bare `eval`); the two agent-assembly labs
  (11&ndash;12) reuse Modules 6&ndash;8's **LangChain-shaped shim**, so it verifies with just
  `nbconvert nbformat ipykernel`. Advanced labs (10&ndash;12) add optional guarded real-LangChain cells.
  Like Modules 5&ndash;8, unfilled student blanks land as a mix of `[TODO]`/`[FAIL]`; the invariant is
  student notebooks run clean and solutions score full.
- **Every notebook follows:** Concept &rarr; Demo (runnable) &rarr; Your Turn (`___` blanks) &rarr;
  auto-grader cell printing `[PASS]`/`[FAIL]`/`[TODO]` + `Score: n/total`. Grader helpers are
  `expect(label, got, want)` and `expect_true(label, fn)`; blanks/exceptions register as `[TODO]`.
- **Student vs solution:** student notebooks have `___`; full answer keys live in each module's
  `solutions/` dir (same filenames, with a SOLUTION banner cell).
- **Generators (re-run to regenerate, do NOT hand-edit the .ipynb):** each module has its own
  `_generators/` (`hands-on/module-1/_generators/`, `hands-on/module-2/_generators/`) with
  `gen_labs.py` (notebooks + solutions), `gen_index.py` (landing page), `regenerate.sh` (runs both,
  no args), `README.md`. Blanks use the `{"s":..,"a":..}` student/answer convention; `_meta.json`
  is written beside the generators (not in the labs dir, and gitignored). Verified: `regenerate.sh`
  reproduces the committed files byte-identically. Edit the generators, never the JSON.
- **Verification done (Modules 1&ndash;9):** all 108 solution notebooks were executed with `nbconvert`
  and reach a full `Score`; all 108 student notebooks run top-to-bottom without uncaught errors
  (blanks land as `[TODO]`/`[FAIL]`); each module's `regenerate.sh` reproduces its files byte-identically.
  Module 2's Keras labs were verified against real MNIST. Modules 3&ndash;4 graded cells are offline
  (numpy/sklearn) so they verify with just `numpy scikit-learn matplotlib nbconvert`; **Modules 5&ndash;9
  graded cells are stdlib-only, so they verify with just `nbconvert nbformat ipykernel`**. Re-verify the
  same way after any edit (Module 2 advanced labs need `tensorflow-cpu` and train real nets, so
  execution is slower).
- **Deck framework:** single self-contained HTML, custom slide engine (NOT Reveal.js) ported
  from the Sharewealth Module-1 deck &mdash; keyboard/swipe nav, slide counter, progress bar,
  `O`/Esc overview grid, `N` presenter notes (`data-note` per `<section.slide>`), `F`
  fullscreen, `#n` deep-links, `@media print`. Inline SVG diagrams, no external assets except
  reference hyperlinks. Each deck ends with a **References &amp; further study** slide of live
  links and cross-links back to the outline (HOME top-right + footer + arc slide). Match this
  shape for Modules 2&ndash;10; bump the footer `v` string on edits. The `.terminal` code/trace
  block **must** carry `white-space:pre-wrap` &mdash; without it, authored newlines collapse into
  flowing text (fixed in M5 v1.1 &amp; M6; copy decks from M6, the reference engine).
- **Not a git repo** (no `.git` here).

## Important: this is a CODE-BASED course

Unlike the no-code Sharewealth template it was derived from (opencode/openclaw, plain English),
this course is **hands-on Python**. Participants write/run code in Jupyter. Keep that framing:
the header badge is `PYTHON · LAB-DRIVEN`, not "NO MANUAL CODING."

## Copyright / no client name

This is **Gheware copyright collateral**. Do **not** add any client, customer, or aggregator
name anywhere (no "Prepared for ...", no logos). Branding is Gheware-only:
devops.gheware.com, "Trainer: Rajesh Gheware." (The word "client" in Lab 4.1 means the
agent's end-user, not a training client.)

## The 5-day structure (source of truth for content)

10 modules (2/day) + 2 labs/day, mapped from the client requirement spec:

| Day | Theme | Modules | Labs |
|-----|-------|---------|------|
| 1 | Foundations of AI & Deep Learning | AI & its evolution; Intro to deep learning | MNIST neural-net classifier; visualizing model decisions |
| 2 | Transformer Models | Why transformers?; Pre-trained models & fine-tuning | OpenAI GPT API text generation; fine-tune BERT for sentiment |
| 3 | Agentic AI Foundations | What is agentic AI?; Agent frameworks | Simple LangChain agent; connect agents to external APIs (Google Search, Wolfram Alpha) |
| 4 | Real-World Agents | Task automation; Multi-agent collaboration & decisions | Email-drafting agent; multi-agent customer-service chatbot |
| 5 | Advanced & Responsible | Agents in finance/health/cyber; Ethics & responsible AI | Financial-report insight agent; responsible-AI frameworks & debugging |

Capstone: each participant builds an industry-specific autonomous agent (LangChain/AutoGPT)
that automates a task, integrates tools/APIs/databases, and is guardrailed + debuggable.

**Tech stack:** Python, PyTorch/Keras, Hugging Face Transformers (BERT), OpenAI GPT API,
LangChain, AutoGPT, external APIs (Google Search, Wolfram Alpha), Jupyter.

## Editing conventions

The outline HTML is **self-contained** (inline CSS, no external assets) and follows the
shared course design pattern. Specific to this course:

- **Palette:** indigo + cyan tech theme (not the wealth green/gold of the source template).
  Tokens: header gradient `#1e1b4b`&rarr;`#312e81`, cyan accent `#06b6d4`, indigo `#4f46e5`,
  amber `#f59e0b` for labs/capstone highlights.
- Reuse the existing component classes (`.overview-box`, `.day-header`, `.module`,
  `.module.labs`, `.callout`, `.callout.descope`, `.capstone`, `.info-box`, `.two-col-list`,
  badges `core-/key-/build-badge`). Don't invent new ones.
- **No emojis** &mdash; use HTML entities (`&#9654;`, `&rarr;`, `&mdash;`).
- `@media print` / A4 support is in place; keep it working.
- Footer carries gheware branding; bump the version string on substantive edits.

## Preview

```bash
firefox course-outline-building-intelligent-ai-agents.html
# or
python -m http.server 8080
```
