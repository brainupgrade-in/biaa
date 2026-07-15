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
- **Stage:** &#10003; **COMPLETE &mdash; all 5 days, all 10 modules (decks + labs) built &amp; verified.**
  Decks:
  `presentation/day1-module1-...` (22 slides), `day1-module2-...` (20), `day2-module3-why-transformers...`
  (19), `day2-module4-pretrained-models-and-fine-tuning...` (20), `day3-module5-what-is-agentic-ai...`
  (42 slides), `day3-module6-frameworks-for-building-ai-agents...` (43 slides),
  `day4-module7-task-automation...` (43 slides),
  `day4-module8-multi-agent-collaboration...` (43 slides),
  `day5-module9-agents-in-industry...` (43 slides),
  `day5-module10-ethics-responsible-ai...` (43 slides, the finale) &mdash; the last six each carry a
  10-question quiz (Q slide &rarr; answer slide interleaved, 4 choices each). Labs:
  `hands-on/module-1/` &hellip; `module-10/` (12 labs each + `index.html` + `solutions/` + `_generators/`
  &mdash; **120 labs total**). Outline cross-links everything (Slides badge per module 1&ndash;10; 12-Labs
  badges for modules 1&ndash;10; Day-1/2/3/4/5 labs boxes summarise the sets). Only the participant
  **capstone** framing remains as course collateral (already described in the outline); no modules left to build.

## Hands-on labs (the convention that's now established)

> **NEAR-REAL LABS (Modules 3&ndash;10) &mdash; READ THIS FIRST. This block is the SOURCE OF TRUTH; it
> SUPERSEDES the framework/verification details in the per-module bullets below.** Those bullets
> describe the earlier deterministic **grade-scaffolding** design and are now **HISTORICAL** &mdash;
> ignore their "graded cells never call an LLM / verify offline / no shim / `FakeChatModel` /
> `ChatOllama("llama3.2:1b")`" language for Modules 3&ndash;10. Keep the bullets for **what each lab
> covers** (the pedagogy and guardrail/throughline design is still accurate).
>
> On the instruction that participants have live keys/services (Ollama local; `GROQ_API_KEY`,
> `OPENAI_API_KEY`, `SERPER_API_KEY`, `WOLFRAM_ALPHA_APPID` in the repo `.env`), Modules 3&ndash;10
> were converted to **near-real** labs: a **real LLM / real HF model drives every lab**, and the
> **auto-grader was removed** (`expect`/`expect_true`/`Score` are gone). Each lab is
> **Concept &rarr; Setup (`load_dotenv(.env)` + real model) &rarr; Build it (real `___` blanks) &rarr;
> Run it for real &rarr; Read the trace/output &rarr; open "Your turn"** &mdash; **no Score cell**;
> unfilled `___` blanks print a note (via `guard()`/`runguard()`), never crash Run All. Modules
> 1&ndash;2 keep their real DL-training pedagogy and their `[PASS]`/`[FAIL]`/`Score` self-check.
>
> **Providers by day (must match the labs):** **M3&ndash;M4 (Day 2) = real Hugging Face**
> (`AutoTokenizer`/`AutoModel`, `pipeline`, real fine-tune of `prajjwal1/bert-tiny`; hosted text-gen
> via `ChatGroq`) &mdash; `sentence-transformers` is NOT installed, use `AutoModel` + mean-pooling.
> **M5&ndash;M6 (Day 3) = local `ChatOllama("llama3.1:8b")`** on `127.0.0.1:11434`.
> **M7&ndash;M10 (Day 4&ndash;5) = `ChatGroq("openai/gpt-oss-20b")`** &mdash; verified tool-calling via
> `create_agent`; do NOT use `llama-3.3-70b-versatile` (it 400s `tool_use_failed`). Real `@tool`s
> **catch their own errors and return a string** (a raising tool aborts the agent run).
>
> **Live-model gotcha &mdash; crash-proof every live cell (fixed 2026-07-15):** `gpt-oss-20b` on Groq
> will occasionally emit a **built-in `browser.search` tool call** on a **bare `llm.invoke(...)`** (no
> tools bound), which Groq rejects with **`400 tool_use_failed` &mdash; "Tool choice is none, but model
> called a tool"** and **aborts Run All**. `with_backoff` does NOT catch it (it only retries 429s). Two
> defences, both baked into the generators: (1) **every live cell is wrapped in try/except** &mdash; the
> Build-it "run it for real" cells via `runguard()`, and **reference-answer cells via `sol_answer()`**,
> which now wraps **any `groq_ready()`-guarded cell** (a groq-guarded cell IS a live cell &mdash; this
> also catches cells that reach the model through a helper like `process()`/`draft()`, not just a literal
> `llm`/`agent.invoke`); (2) **harden bare-`llm.invoke` prompts** with "use ONLY the numbers/text given;
> do not search the web or call any tool" so the model answers directly. `agent.invoke` cells (tools
> bound via `create_agent`) do not hit this 400 path. All four generators (M7&ndash;M10) share the same
> `sol_answer` wrap rule.
>
> **VERIFY BY RUNNING, not by a Score:** execute notebooks with the **sandbox disabled** (live
> LLM/model calls need network) against **`biaa-venv`** and confirm REAL output/traces appear;
> per-module `regenerate.sh` stays idempotent (byte-identical). **Status (2026-07-15):** all four
> Day-4/5 decks realigned to the **LangChain 1.x** API in their code slides (`create_agent` /
> `recursion_limit` / message-trace via `result["messages"]` &mdash; NOT `create_react_agent` /
> `AgentExecutor` / `max_iterations` / `intermediate_steps`; M7/M8 v1.2, M9 v1.2, M10 v1.3); M7&ndash;M10
> labs **run-verified with live Groq** against `biaa-venv` (48/48 per day-pair after the crash-proofing
> fix). Reference implementation: `hands-on/module-6/_generators/gen_labs.py`.

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
  **Design (near-real):** real Hugging Face drives the labs &mdash; `AutoTokenizer`/`AutoModel`
  (mean-pooled embeddings, since `sentence-transformers` is NOT installed), `pipeline`, tiny models
  (`bert-tiny`/`tiny-gpt2`), plus hosted text-gen via `ChatGroq`; a few NumPy/scikit-learn techniques
  remain where they are the right tool (e.g. TF-IDF semantic search). No grader. The client's "GPT API
  text generation" is a runnable generation lab. See the source-of-truth note for verification.
- **Module 4 has 12 labs** (`hands-on/module-4/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-04-NN/`):
  6 Beginner, 3 Intermediate, 3 Advanced &mdash; using a pretrained model, softmax confidence,
  prompt/fine-tune/RAG, model inputs (ids/mask/padding), dataset prep, train/val split (Beginner);
  frozen features + trainable head, precision/recall/confusion, data-efficiency curve (Intermediate);
  **fine-tune a sentiment classifier** (before vs after), tune &amp; evaluate (regularisation +
  confusion matrix), and a capstone adapting a model to a NEW task (Advanced). ~340 min.
  **Design (near-real):** real Hugging Face is the core &mdash; a real `bert-tiny` fine-tune/inference for
  the sentiment task &mdash; with scikit-learn transfer learning (frozen features + a trainable head) as
  the portable companion technique, and hosted text-gen via `ChatGroq`. No grader. The client's "fine-tune
  BERT for sentiment" is the real-bert path. See the source-of-truth note for verification.
- **Module 5 has 12 labs** (`hands-on/module-5/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-05-NN/`):
  6 Beginner, 3 Intermediate, 3 Advanced &mdash; model-vs-agent, build-a-tool, the reason&rarr;act&rarr;observe
  agent loop, ReAct-step parsing, tool routing, memory/scratchpad (Beginner); a rule-based ReAct agent
  (two-step task), guardrails (max-steps / allow-list / loop-detection / input validation), tool selection
  (Intermediate); plan-and-execute, reflection/self-critique, and a **mini-autonomous-agent capstone** over
  a task suite (Advanced). ~330 min. **Design (near-real):** students build a ReAct agent from rule-based
  roots (a deterministic policy, an **AST-based safe calculator** &mdash; no bare `eval`), then **run it for
  real** against a live `ChatOllama("llama3.1:8b")` via `create_agent` (`ollama_up()`-guarded, self-skips
  when Ollama is down). No grader. The bridge to Module 6 (Agent Frameworks) and the Day-3 LangChain labs.
  See the source-of-truth note for verification.
- **Module 6 has 12 labs** (`hands-on/module-6/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-06-NN/`):
  6 Beginner, 3 Intermediate, 3 Advanced &mdash; first tool with `@tool`, tool descriptions/catalog, the
  model interface (`PromptTemplate` + `ChatOllama`), assemble an agent with `create_agent`, run it &amp;
  read the message trace + `recursion_limit`, safe tool routing (Beginner); conversation memory, a real
  **LangGraph `StateGraph`** (human-approval node), multi-tool orchestration (Intermediate); connect to
  external APIs (search + Wolfram-style compute), guardrails &amp; a tracing callback, and a
  **guardrailed-LangChain-agent capstone** (Advanced). ~335 min. **Design:** real LangChain 1.x directly
  &mdash; `langchain_core.tools.@tool`, `PromptTemplate`, `langchain_ollama.ChatOllama("llama3.1:8b")`,
  `langchain.agents.create_agent` (a `CompiledStateGraph`), and `langgraph.StateGraph` (no `LC_*` shim,
  no `FakeChatModel`). **Gotcha:** a real `@tool` **requires a docstring**, so docstring blanks keep a
  `"""___ (TODO...)"""` stub (a bare `___` would raise at decoration time and crash the notebook). The
  Module-6 **deck** was realigned to the 1.x API (`create_agent`/`recursion_limit`, message-trace slide).
  `hands-on/module-6/_generators/gen_labs.py` is the **reference generator** for M6&ndash;M10. See the
  source-of-truth note above for providers, verification, and the live-cell crash-proofing rule.
- **Module 7 has 12 labs** (`hands-on/module-7/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-07-NN/`):
  6 Beginner, 3 Intermediate, 3 Advanced &mdash; this is the **task-automation** module and every lab builds
  the **email-drafting agent** (the client's Lab 4.1) piece by piece: the automation pipeline
  (trigger&rarr;gather&rarr;draft&rarr;validate&rarr;approve&rarr;act), gather-with-tools, structured output,
  the extract pattern, the route pattern, drafting a grounded reply (Beginner); validation, retry &amp;
  idempotency, and the **draft-not-send** human-in-the-loop gate (Intermediate); observability/run-log,
  **assembling the email agent** (gather-only tools &mdash; `send_email` withheld &mdash; returns a
  `needs_approval` draft), and a **capstone** that chains extract&rarr;route&rarr;gather&rarr;draft&rarr;validate
  over a suite and never auto-sends (Advanced). ~340 min. **Design (near-real, framework-first &mdash;
  revised 2026-07-16):** validation/retry-idempotency/observability/schema-coercion (labs 03/07/08/10)
  stay **rule-based Python by design** &mdash; they are supporting logic that is correctly deterministic
  even in production (you don't validate, dedupe or log with an LLM). The rest drive real framework/model:
  **01** the automation pipeline is a real `langgraph.StateGraph` (six stage nodes wired in order, offline);
  **02** gather-with-tools is a real `create_agent`; **04** the **extract pattern** is a real LLM
  structured-output extractor (`llm.with_structured_output(Extracted, method="json_schema")` &mdash;
  json_schema mode, NOT the tool-calling default, which 400s intermittently on gpt-oss) + a closed-set
  guard; **05** the **route pattern** is a real LLM closed-set classifier (`llm.invoke` over a
  `PromptTemplate`, constrained to `LABELS` + deterministic escalation); **06** drafts via real `llm.invoke`;
  **09** builds the **real gather-only `create_agent`** (send withheld) and invokes it to draft, then a
  rule-based human gate; **11** assembles the gather-only agent; **12** the capstone now **invokes** the
  real assembled agent per email (`agent.invoke` &rarr; it calls `lookup_order` and drafts; `tools_used`
  in the output) &mdash; it no longer bypasses the agent with a bare `llm.invoke`. The **gather-only
  guardrail** is the point: `send_email` is defined but **never bound** (a `CompiledStateGraph`), which
  returns a `needs_approval` draft. `order_id` is a **string** throughout. Real `@tool` requires a
  docstring, so docstring blanks keep a `"""___ (TODO...)"""` stub. Deck has **no** rule-based code slides,
  so it needed no change. Verified 2026-07-16 vs `biaa-venv` with live Groq: labs 01/04/05/09/12 solution +
  student notebooks run clean; `regenerate.sh` idempotent. See the source-of-truth note for
  provider/verification/crash-proofing.
- **Module 8 has 12 labs** (`hands-on/module-8/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-08-NN/`):
  6 Beginner, 3 Intermediate, 3 Advanced &mdash; this is the **multi-agent** module and every lab builds
  the **customer-service chatbot** (the client's Lab 4.2) piece by piece: specialist agents
  (separation of concerns), the supervisor/router (multi-intent), shared state &amp; message passing,
  the sequential pipeline, parallel fan-out, explicit capped handoff (Beginner); voting/consensus,
  critique/debate (capped loop), synthesis into one grounded reply (Intermediate); observability with
  loop-detection, **assembling the chatbot** (supervisor routes to billing/tech specialist
  `create_agent` agents &rarr; synthesise &rarr; a `needs_approval` reply, refund gated on a human), and a
  **capstone** running the full team over a suite (Advanced). ~340 min. **Design (near-real, framework-first
  &mdash; revised 2026-07-16):** labs **02&ndash;06 are real `langgraph.StateGraph` builds** &mdash; the
  orchestration patterns are the framework's own primitives, not hand-rolled Python loops: **02** supervisor =
  `StateGraph` + `add_conditional_edges` routing to **real `create_agent` specialist nodes**; **03** shared
  state = a typed `TypedDict` schema + **reducers** (`Annotated[list, add]`, offline); **04** sequential =
  `add_edge` chain with real specialist nodes; **05** parallel = fan-out edges from `START` + reducer merge +
  fault-tolerant branch; **06** handoff = `Command(goto=...)` + `recursion_limit` cap, real specialists.
  Labs **07&ndash;09** (voting/critique/synthesis) stay decision-logic Python &mdash; no framework primitive
  maps to them. Specialists everywhere are real `create_agent(llm, tools, system_prompt=...)` (a
  `build_specialist(tools, role)` helper) over `ChatGroq("openai/gpt-oss-20b")`. Labs **11&ndash;12** assemble
  the chatbot with `route()` &rarr; per-specialist `.invoke` &rarr; `synthesize()` &rarr; a refund human-gate
  (specialists have **no** refund tool). Deck slide 17 mirrors lab 11's assembly, and the deck's code-slide note
  already promises "the labs cover a real LangGraph StateGraph separately" &mdash; now true, so the **deck
  needed no change**. Verified 2026-07-16: labs 02&ndash;06 solution + student notebooks run clean against
  `biaa-venv` with live Groq (02/04/05/06 make real specialist calls; 03 is offline); `regenerate.sh`
  idempotent. See the source-of-truth note for provider/verification/crash-proofing.
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
  investment advice, has no trade tool; a human analyst decides. **Design (near-real):** the
  ground/cite/compute/flag/validate/redact logic is rule-based Python (financial math via an **AST-safe
  calculator**, no bare `eval`); the agent-assembly labs (11&ndash;12) use real LangChain 1.x (`@tool`,
  `ChatGroq("openai/gpt-oss-20b")`, `create_agent`). The **read-only guardrail** is the point:
  `place_trade` is defined but **never bound**; the agent returns a grounded, cited, `needs_review`
  insight. Deck slide 9 matches lab 11. See the source-of-truth note for provider/verification/crash-proofing.
- **Module 10 has 12 labs** (`hands-on/module-10/lab-01..12-*.ipynb`, prefix `/tmp/biaa-lab-10-NN/`) &mdash;
  the **course finale** (Lab 5.2): 6 Beginner, 3 Intermediate, 3 Advanced covering BOTH halves of the deck.
  Responsible-AI practice: treat input as data (prompt injection), least privilege, read the trace, classify
  the failure mode, detect a runaway loop, fairness across groups (Beginner); build an eval set, the
  guardrail regression suite, the responsible-agent checklist as a deploy gate (Intermediate). Debugging:
  a full **debug-and-fix loop** (read a broken-run trace &rarr; diagnose the wrong-tool bug &rarr; give the
  agent a grounding tool &rarr; verify), **assemble a guardrailed agent** (input-as-data + least-privilege +
  output-validation + trace), and a **capstone** running a responsible agent over an eval suite of
  normal/injection/advice cases (Advanced). ~340 min. **Design (near-real):** the responsible-AI logic
  (injection/least-privilege/trace-reading/fairness/eval) is rule-based Python; labs 10&ndash;12 use real
  LangChain 1.x (`@tool`, real message traces `AIMessage`/`ToolMessage`, `ChatGroq("openai/gpt-oss-20b")`,
  `create_agent`). The debug-and-fix lab reads a **recorded real message trace** (buggy vs fixed) and
  applies a `create_agent` wiring fix (add the missing grounding tool). Trace-reading uses
  `print_trace(result["messages"])` + `tools_used(...)` &mdash; the deck's debugging slide (S16) mirrors it.
  See the source-of-truth note for provider/verification/crash-proofing.
- **Engagement revision (Modules 5&ndash;10, 2026-07-10):** after a duplication/triviality/flow audit,
  all six back-half modules got an **in-place** engagement pass &mdash; **no lab count, slug or file
  renames** (still 12/module); only lab CONTENT changed, verified byte-identical file scope. Fixed **5
  grading defects** where a blank wasn't actually blank: **M9** lab09 `minimize` (student==answer),
  lab10 `owns_decision` (constant `"human"` spelled in the TODO), lab06 `agent_tools` (hardcoded list);
  **M10** lab03 `find_ungrounded` &amp; lab10 `diagnose` (`# TODO: keep` pre-filled). Engagement wins:
  deepened Advanced labs so the graded surface actually rises (M5 lab05 grades the tool-error path, lab09
  adds an adversarial non-arithmetic digit, lab11 critic is a DERIVED rule; M6 lab10 wraps a flaky source;
  M7 lab03 is now a real schema/coerce); **real-assembly capstones** that compose prior-lab assets and run
  bigger/partial-score suites with a guardrail actually firing (M5 refuses a `delete` request; M6 composes
  memory+tracing+recursion_limit; M7 suite 2&rarr;4 partial (3,4); M8 wires the vote in + reuses lab11's real
  specialists, suite&rarr;6; M9 mixed clean/advice/uncited suite + redaction wired in; M10 finale runs lab11's
  agent + folds in fairness); re-domained off-throughline labs (M8 lab04/05 &rarr; the CS chatbot). The
  `order_id` int/str throughline bug in M7 (lab04 vs lab12) was reconciled to strings. Re-verified vs
  `biaa-venv`: every changed solution + student notebook runs clean, each `regenerate.sh` idempotent.
  **Decks &amp; quizzes were NOT touched by this pass** (labs only). *(This pass predates the near-real
  conversion above, which later removed the `Score` cells it refers to &mdash; kept as a defect-fix record.)*
- **Notebook flow:** **Modules 1&ndash;2** &mdash; Concept &rarr; Demo (runnable) &rarr; Your Turn
  (`___` blanks) &rarr; a self-check cell printing `[PASS]`/`[FAIL]`/`[TODO]` + `Score: n/total`
  (`expect`/`expect_true` helpers). **Modules 3&ndash;10 (near-real)** &mdash; Concept &rarr; Setup
  (real model) &rarr; Build it (`___`) &rarr; Run it for real &rarr; Read the trace/output &rarr;
  "Your turn"; **no grader, no `Score`** (see the source-of-truth note above). Unfilled blanks print
  a `guard()`/`runguard()` note, never crash Run All.
- **Student vs solution:** student notebooks have `___`; full answer keys live in each module's
  `solutions/` dir (same filenames, with a SOLUTION banner cell).
- **Generators (re-run to regenerate, do NOT hand-edit the .ipynb):** each module has its own
  `_generators/` (`hands-on/module-1/_generators/`, `hands-on/module-2/_generators/`) with
  `gen_labs.py` (notebooks + solutions), `gen_index.py` (landing page), `regenerate.sh` (runs both,
  no args), `README.md`. Blanks use the `{"s":..,"a":..}` student/answer convention; `_meta.json`
  is written beside the generators (not in the labs dir, and gitignored). Verified: `regenerate.sh`
  reproduces the committed files byte-identically. Edit the generators, never the JSON.
- **Verification (how to re-verify after any edit):** all 120 solution + 120 student notebooks execute
  top-to-bottom without uncaught errors, and each module's `regenerate.sh` reproduces its files
  byte-identically. **Modules 1&ndash;2** reach a full `Score` (M2 Keras verified against real MNIST).
  **Modules 3&ndash;10 have no `Score`** &mdash; verify by RUNNING and confirming real output/traces
  appear (see the source-of-truth note). All of M3&ndash;M10 import `langchain`/`langgraph` and/or
  `transformers`, so **verify against the course `biaa-venv`**, not a bare stdlib venv:
  `biaa-venv/bin/python -m nbconvert --to notebook --execute <nb> --ExecutePreprocessor.timeout=300`.
  M5&ndash;M6 live cells need a **local Ollama** up (self-skip via `ollama_up()` otherwise); **M7&ndash;M10
  live cells call Groq &mdash; run with the sandbox DISABLED (network needed) and `GROQ_API_KEY` set**, or
  they self-skip via `groq_ready()`. Last full run-verify with live Groq: **2026-07-15, M7&ndash;M10 48/48
  per day-pair.**
- **Deck framework:** single self-contained HTML, custom slide engine (NOT Reveal.js) ported
  from the Sharewealth Module-1 deck &mdash; keyboard/swipe nav, slide counter, progress bar,
  `O`/Esc overview grid, `N` presenter notes (`data-note` per `<section.slide>`), `F`
  fullscreen, `#n` deep-links, `@media print`. Inline SVG diagrams, no external assets except
  reference hyperlinks. Each deck ends with a **References &amp; further study** slide of live
  links and cross-links back to the outline (HOME top-right + footer + arc slide). Match this
  shape for Modules 2&ndash;10; bump the footer `v` string on edits. The `.terminal` code/trace
  block **must** carry `white-space:pre-wrap` &mdash; without it, authored newlines collapse into
  flowing text (fixed in M5 v1.1 &amp; M6; copy decks from M6, the reference engine).
- **Git repo:** `main` branch, remote `origin` &rarr; `github.com/brainupgrade-in/biaa.git`.

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

## Delivery / setup tooling (`scripts/`)

Participants are **Windows-majority (Git Bash)** &mdash; keep setup and in-room
friction low. `SETUP.md` is the participant install guide; `scripts/RUNBOOK.md`
is the **delivery-day** ops sheet (per-day pre-flight, ports, Windows-first
error-recovery table). Key facts:

- **Env:** Python 3.12 &rarr; `biaa-venv` (repo root). `bash scripts/setup-{linux,windows}.sh`
  (uses `uv` when present; `--with-ollama` pulls the Day-3 model). Verify with
  `bash scripts/smoke-test.sh` (`--day N` = just that day's needs).
- **Kernel:** setup registers the `biaa` kernel **and** runs
  `scripts/set-notebook-kernel.py`, which rewrites every notebook's
  `metadata.kernelspec` to `biaa` so nobody hand-picks a kernel (worst friction
  on Windows/VS Code). It's a **local, student-side** action &mdash; committed
  notebooks stay on the portable `python3` kernel, so `--reset` before any commit
  and the generators are unaffected.
- **Provider by day (must match the labs):** Day 1 none · Day 2 Hugging Face ·
  **Day 3 local Ollama `llama3.1:8b`** on `127.0.0.1:11434` (+ Serper/Wolfram in
  M6) · Days 4-5 Groq `openai/gpt-oss-20b`. The setup/docs pull **`llama3.1:8b`**
  (not `1b`) &mdash; the M5-6 labs require it. Day 5 also live-demos the FrontDesk
  AI production app (separate repo).

## Preview

```bash
firefox course-outline-building-intelligent-ai-agents.html
# or
python -m http.server 8080
```
