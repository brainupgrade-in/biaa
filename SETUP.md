# Building Intelligent AI Agents — Participant Setup Guide

*Gheware UniGPS Solutions · Trainer: Rajesh Gheware · 5-day hands-on workshop*
*Labs are Jupyter notebooks run **locally** on each participant's machine — no browser-based/cloud lab is provided.*

---

## ⭐ Read this first
- The workshop is **120 hands-on labs** delivered as Jupyter notebooks (`.ipynb`), run **locally**.
- **The curriculum requires** working with **MNIST**, a **real LLM** (agent labs), and **external APIs — Google Search & Wolfram Alpha** (Day 3). Set these up — they are **not** optional.
- Every lab also ships a **built-in offline fallback** (see §5). That is a **safety net** so a flaky key or a blocked port never strands a participant mid-session — **not** a reason to skip setup.
- Notebooks + full answer keys are **provided by the trainer** — participants don't fetch course files.

---

## 1. Hardware & OS
- **OS:** Windows 10/11, macOS, or Linux (64-bit)
- **RAM:** 8 GB minimum · **16 GB recommended** (comfortable for a local model)
- **Disk:** **~10 GB free** (Python + TensorFlow + transformers/torch + a local model)
- **Permissions:** ability to **install software** and **run local servers** on `localhost` — ports `8888` (Jupyter) and `11434` (Ollama, if used)

## 2. TIER 1 — Required core software (every lab)
- **Python 3.12** &mdash; **please use this exact version.** It has mature, well-tested wheels for every workshop package (incl. TensorFlow), which avoids environment/install troubleshooting. *(Other versions may work but are not supported for this workshop.)*
- **A virtual environment** (`biaa-venv`) · **Jupyter** (JupyterLab / Notebook, or VS Code + Jupyter extension) · **Editor:** VS Code recommended

### ✅ Recommended: one-command setup
Just run the setup script for your OS — **you don't need to install anything first**
(not even Python, `uv`, or `curl`):

```bash
# from the course folder:
bash scripts/setup-linux.sh              # Linux / macOS
bash scripts/setup-windows.sh            # Windows (Git Bash)
#   installs everything the labs need, including transformers + CPU-only torch
```
The script uses [`uv`](https://docs.astral.sh/uv/) to **create the `biaa-venv` on
Python 3.12 and install every package** — and **provisions a standalone Python 3.12
automatically**, so you don't install Python yourself (this also fixes the
`apt install python3.12` failure on newer distros like **Ubuntu 25.10+**, which ship
only 3.13/3.14). **If `uv` itself isn't installed, the script downloads it for you** —
on Windows via PowerShell (no `curl` required), on Linux/macOS via curl/wget/python —
and adds it to your `PATH`. The script also registers a **"Python 3.12 (biaa)"**
Jupyter kernel, points every lab notebook at it, and — on Windows — **sets Git Bash as
the VS Code default terminal**, then runs a smoke test. See
[`scripts/README.md`](scripts/README.md) for details.

> **🪟 Windows:** run the setup in the **Git Bash** shell bundled with
> [Git for Windows](https://git-scm.com/download/win). After setup, every terminal
> you open in VS Code is Git Bash automatically — nothing else to configure. (If you
> ever need to set it by hand: `Ctrl+Shift+P` &rarr; **Terminal: Select Default
> Profile** &rarr; **Git Bash**.) The notebooks themselves are **OS-agnostic** — each
> lab's scratch folder resolves to a writable temp dir on Windows, macOS, and Linux
> with no per-machine step.

### Manual alternative (no scripts)
```bash
python -m venv biaa-venv
# activate:  Windows -> biaa-venv\Scripts\activate   |   macOS/Linux -> source biaa-venv/bin/activate
pip install --upgrade pip
pip install jupyterlab ipykernel nbformat numpy scikit-learn matplotlib tensorflow-cpu
```
- `numpy · scikit-learn · matplotlib` → Days 1–2 (neural nets, transformers)
- `tensorflow-cpu` → **Day 1 · MNIST classifier** (Module 2, Advanced labs)
- `jupyterlab · ipykernel · nbformat` → run & grade every notebook

## 3. TIER 2 — Required for the course's named lab exercises
These are **part of the curriculum**, not extras.

### 3a. MNIST dataset (Day 1)
- Framework is installed in Tier 1 (`tensorflow-cpu`).
- Participants must be able to **download MNIST** → allow **`storage.googleapis.com`** (see §6).

### 3b. A real LLM for the agent labs (Days 3–5) — **Groq or Ollama**
Pick **either** (both free, no paid account):
- **Option A — Groq free API (simplest):**
  - Create a **free Groq account** → generate an **API key** → set env var **`GROQ_API_KEY`**
- **Option B — Ollama local model (no key, offline after download):**
  - Install **Ollama** → `ollama pull llama3.1:8b` (~4.9 GB) → serves on `127.0.0.1:11434`

> **Which day uses what:** **Days 4–5** (Modules 7–10) run on **Groq** — just a
> key, nothing local. **Day 3** (Modules 5–6) uses the **local Ollama
> `llama3.1:8b`** by default. Least-hassle path (esp. on Windows): use **Groq for
> everything** — a Groq key covers Days 2, 4, 5, and you can point the Day-3 labs
> at Groq too (swap `ChatOllama(...)` → `ChatGroq("openai/gpt-oss-20b")`). Pull
> the 8 B model **before** the session if you want to run Day 3 locally.

```bash
pip install langchain langchain-community langchain-ollama langchain-groq langgraph
```

> **💡 BYOK — OpenAI (bring your own key):** the LLM labs run on **Groq / Ollama by default**. OpenAI is supported on a **Bring-Your-Own-Key** basis — create an OpenAI account, set **`OPENAI_API_KEY`**, and install its client for the use you want: `pip install openai` for the **Day-2 GPT text-generation** snippet (a commented reference in that lab), or `pip install langchain-openai` to use **OpenAI as the LLM in the Day 3–5 agent labs** (swap for `ChatGroq`). OpenAI is paid/metered (Groq and Ollama are free — hence the default); if you use its free token tier, heed the **personal-account** warning in §7.

### 3c. External APIs — Google Search & Wolfram Alpha (Day 3, Module 6)
The Day-3 "connect agents to external APIs" lab uses both. Create the free keys **before** the workshop:
- **Google Serper** (Google Search) → free key → env var **`SERPER_API_KEY`**
- **Wolfram Alpha** → free developer **App ID** → env var **`WOLFRAM_ALPHA_APPID`**

```bash
pip install wolframalpha       # langchain-community (from 3b) provides the Serper + Wolfram wrappers
```

### 3d. Hugging Face transformers (Day 2, Modules 3–4)
The transformer / pre-trained-model labs use a **real** Hugging Face model, so these are **required**:
```bash
pip install "transformers>=4.40,<5" tf-keras
# CPU-only torch (no ~2.5 GB CUDA wheels) — the setup scripts do this for you:
pip install torch --index-url https://download.pytorch.org/whl/cpu
```
- `transformers` is pinned **<5** (5.x can't load `bert-tiny`'s slow WordPiece tokenizer).
- `tf-keras` gives `transformers` a Keras-2 API to probe; it does **not** disturb the Keras 3 used by the Day-1 MNIST labs.
- Participants must be able to **download models** → allow **`huggingface.co`** + **`cdn-lfs.huggingface.co`** (see §6).

## 4. TIER 3 — Genuinely optional (BYOK only)
- **OpenAI** is the only genuinely-optional add-on — the LLM labs default to **Groq / Ollama**. Bring your own key (`OPENAI_API_KEY`) and `pip install openai` / `langchain-openai` only if you prefer OpenAI. *(See the BYOK note under 3b.)*

## 5. If a service is down, labs still open (safety net — NOT a reason to skip setup)
The notebooks **run top-to-bottom without crashing** even if a key or port is
unreachable, so a blocked service never halts a session:
- **MNIST** blocked → falls back to an offline 8×8 digits dataset (same exercise, smaller data).
- **LLM / Serper / Wolfram** unreachable → the "run it for real" cells **detect it and print a note instead of erroring** (the Ollama cells self-skip via a reachability check; real tools catch errors and return a message).
> The labs are **built around the real services** — set them up for the full
> experience. The safety net only keeps "Run All" from breaking; it does **not**
> reproduce the real model output.

## 6. Network / firewall allowlist (for participants' IT teams)
Needed for package install + the Tier-2 services:

| Purpose | Allow |
|---|---|
| **pip / PyPI** (all installs) | `pypi.org`, `files.pythonhosted.org` |
| **MNIST dataset** (Day 1) | `storage.googleapis.com` |
| **Groq** (LLM, Option A) | `console.groq.com`, `api.groq.com` |
| **Ollama** (LLM, Option B) | `ollama.com`, `registry.ollama.ai` *(runtime is local — `127.0.0.1:11434`)* |
| **Google Serper** (Day 3) | `serper.dev`, `google.serper.dev` |
| **Wolfram Alpha** (Day 3) | `developer.wolframalpha.com`, `api.wolframalpha.com` |
| **Hugging Face** (Day 2, required) | `huggingface.co`, `cdn-lfs.huggingface.co` |
| **OpenAI** (optional, BYOK only) | `platform.openai.com`, `api.openai.com` |

## 7. Accounts / keys to create BEFORE the workshop
- ☐ **Groq** free account + `GROQ_API_KEY` *(or use Ollama locally — no account)*
- ☐ **Serper.dev** free `SERPER_API_KEY` *(Day 3)*
- ☐ **Wolfram Alpha** developer `WOLFRAM_ALPHA_APPID` *(Day 3)*
- ☐ *(BYOK, optional)* **OpenAI** account + `OPENAI_API_KEY` — only if using OpenAI instead of Groq

> **⚠️ Create every key on a PERSONAL account, not an employer/org account.** Free tiers are granted
> on terms an org account should not silently accept — rate limits, usage analytics, and (for OpenAI)
> opting into training on your API traffic. Those terms bind the **whole org**, not just your workshop
> use. A personal account keeps the workshop's throwaway keys entirely separate from anything your
> employer runs, and all keys here are free, so there is no reason to bill them to an org.

*Set keys as environment variables (or in a `.env` file the trainer will point to).*

## 8. Pre-workshop 5-minute smoke test
Fastest check — the setup script runs this for you, and you can re-run it any time
(add `--day N` for just what a given day needs):
```bash
bash scripts/smoke-test.sh          # full check
bash scripts/smoke-test.sh --day 3  # only what Day 3 needs (packages + Ollama)
```

Or verify by hand inside the activated environment — all should succeed:
```bash
python --version
python -c "import numpy, sklearn, matplotlib; print('sci stack OK')"
python -c "import tensorflow as tf; print('tensorflow', tf.__version__)"
python -c "import langchain, langchain_community, langgraph; print('langchain stack OK')"
python -c "import transformers, torch, tf_keras; print('transformers stack OK')"
jupyter lab --version

# LLM — run ONE of:
ollama run llama3.1:8b "say hi"                       # Option B (Ollama, Day 3)
python -c "import langchain_groq; print('groq lib OK')"   # Option A (Groq, Days 4-5)

# Keys present (Day 3 + LLM):
python -c "import os; [print(k, bool(os.getenv(k))) for k in ('GROQ_API_KEY','SERPER_API_KEY','WOLFRAM_ALPHA_APPID')]"
```

## 9. What participants do NOT need
- No GPU · No cloud/VM · No admin server · No paid subscription **by default** (Groq, Ollama, Serper, Wolfram all have free tiers)
- OpenAI is **optional (BYOK)**, not required
- The notebooks won't **crash** if a service is down (they self-skip and print a note), but the Tier-2 services are required to run the labs **as designed** — there is no offline substitute for real model output

---

*© 2026 Gheware DevOps & Agentic AI · devops.gheware.com · training@gheware.com · +91-9606795215*
