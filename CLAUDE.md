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
- **Stage:** early build. Deliverables so far:
  `course-outline-building-intelligent-ai-agents.html` (landing/outline);
  `presentation/day1-module1-understanding-ai-and-its-evolution.html` (Day 1 Module 1 deck,
  22 slides); and `hands-on/module-1/` (Day 1 Module 1 labs &mdash; 12 notebooks + `index.html`
  landing page + `solutions/` answer keys). Remaining Modules 2&ndash;10 decks and their labs
  are not built yet.

## Hands-on labs (the convention that's now established)

- **Course prefix:** `biaa`. Each lab writes to its own `/tmp/biaa-lab-01-NN/` working dir
  (module 01, lab NN).
- **Module 1 has 12 labs** (`hands-on/module-1/lab-01..12-*.ipynb`): 6 Beginner, 3 Intermediate,
  3 Advanced &mdash; an experiential progression (rules &rarr; data &rarr; ML pipeline &rarr; overfitting
  &rarr; clustering &rarr; perceptron-from-scratch &rarr; digit NN &rarr; mini-agent capstone). ~320 min total.
- **Every notebook follows:** Concept &rarr; Demo (runnable) &rarr; Your Turn (`___` blanks) &rarr;
  auto-grader cell printing `[PASS]`/`[FAIL]`/`[TODO]` + `Score: n/total`. Grader helpers are
  `expect(label, got, want)` and `expect_true(label, fn)`; blanks/exceptions register as `[TODO]`.
- **Student vs solution:** student notebooks have `___`; full answer keys live in
  `hands-on/module-1/solutions/` (same filenames, with a SOLUTION banner cell).
- **Generators (re-run to regenerate, do NOT hand-edit the .ipynb):** live in
  `hands-on/module-1/_generators/` &mdash; `gen_labs.py` (notebooks + solutions), `gen_index.py`
  (landing page), `regenerate.sh` (runs both, no args needed), `README.md`. Blanks use the
  `{"s":..,"a":..}` student/answer convention; `_meta.json` is written beside the generators
  (not in the labs dir). Verified: `regenerate.sh` reproduces the committed files byte-identically.
  Edit the generators, never the JSON.
- **Dependencies (offline-friendly):** numpy + scikit-learn + matplotlib only. Labs 1&ndash;6, 10, 12
  need just Python/NumPy; 7&ndash;9, 11 use sklearn (11 also matplotlib). Lab 12 has an *optional*
  Ollama/LangChain step (`langchain-community`, `llama3.2:1b`) that degrades gracefully.
- **Verification done:** all 12 solution notebooks were executed with `nbconvert` and reach a
  full `Score`; all 12 student notebooks run top-to-bottom without uncaught errors (blanks land
  as `[TODO]`). Re-verify the same way after any edit.
- **Deck framework:** single self-contained HTML, custom slide engine (NOT Reveal.js) ported
  from the Sharewealth Module-1 deck &mdash; keyboard/swipe nav, slide counter, progress bar,
  `O`/Esc overview grid, `N` presenter notes (`data-note` per `<section.slide>`), `F`
  fullscreen, `#n` deep-links, `@media print`. Inline SVG diagrams, no external assets except
  reference hyperlinks. Each deck ends with a **References &amp; further study** slide of live
  links and cross-links back to the outline (HOME top-right + footer + arc slide). Match this
  shape for Modules 2&ndash;10; bump the footer `v` string on edits.
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
