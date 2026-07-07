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
- **Disk:** **~10 GB free** (Python + TensorFlow + a local model + optional libs)
- **Permissions:** ability to **install software** and **run local servers** on `localhost` — ports `8888` (Jupyter) and `11434` (Ollama, if used)

## 2. TIER 1 — Required core software (every lab)
- **Python 3.12** &mdash; **please use this exact version.** It has mature, well-tested wheels for every workshop package (incl. TensorFlow), which avoids environment/install troubleshooting. *(Other versions may work but are not supported for this workshop.)*
- **A virtual environment** (built-in `venv`)
- **Jupyter** — JupyterLab / Notebook, **or** VS Code with the Jupyter extension
- **Editor:** VS Code recommended

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
  - Install **Ollama** → `ollama pull llama3.2:1b` (~1.3 GB, CPU-friendly) → serves on `localhost:11434`

```bash
pip install langchain langchain-community langchain-ollama langchain-groq langgraph
```

> **💡 BYOK — OpenAI (bring your own key):** the LLM labs run on **Groq / Ollama by default**. If a participant (or the client) prefers **OpenAI**, it's supported on a **Bring-Your-Own-Key** basis — create an OpenAI account, set **`OPENAI_API_KEY`**, and `pip install langchain-openai`; the optional real-LLM cells will use it. *(OpenAI is paid/metered; Groq and Ollama are free — hence the default.)*

### 3c. External APIs — Google Search & Wolfram Alpha (Day 3, Module 6)
The Day-3 "connect agents to external APIs" lab uses both. Create the free keys **before** the workshop:
- **Google Serper** (Google Search) → free key → env var **`SERPER_API_KEY`**
- **Wolfram Alpha** → free developer **App ID** → env var **`WOLFRAM_ALPHA_APPID`**

```bash
pip install wolframalpha       # langchain-community (from 3b) provides the Serper + Wolfram wrappers
```

## 4. TIER 3 — Genuinely optional (nice-to-have)
- **Real Hugging Face transformers** for the Day-2 "real BERT / GPT" demonstration cells:
  ```bash
  pip install transformers torch
  ```
  *(The Day-2 fine-tune lab has a complete, faithful offline path in scikit-learn — this only adds the real `bert-tiny` demo.)*

## 5. Built-in resilience (safety net — NOT a reason to skip setup)
Every lab degrades gracefully if a service is unreachable, so a blocked key or port never halts the session:
- **MNIST** blocked → falls back to an offline 8×8 digits dataset (same exercise, smaller data)
- **Google Serper / Wolfram** unavailable → a deterministic local stand-in runs the graded steps
- **LLM key/model** absent → a deterministic mock model runs the graded steps
> Set up the real services for the **full intended experience**; the fallback just keeps everyone unblocked.

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
| **Hugging Face** (optional, Day 2) | `huggingface.co`, `cdn-lfs.huggingface.co` |
| **OpenAI** (optional, BYOK only) | `platform.openai.com`, `api.openai.com` |

## 7. Accounts / keys to create BEFORE the workshop
- ☐ **Groq** free account + `GROQ_API_KEY` *(or use Ollama locally — no account)*
- ☐ **Serper.dev** free `SERPER_API_KEY` *(Day 3)*
- ☐ **Wolfram Alpha** developer `WOLFRAM_ALPHA_APPID` *(Day 3)*
- ☐ *(BYOK, optional)* **OpenAI** account + `OPENAI_API_KEY` — only if using OpenAI instead of Groq

*Set keys as environment variables (or in a `.env` file the trainer will point to).*

## 8. Pre-workshop 5-minute smoke test
Run inside the activated environment — all should succeed:
```bash
python --version
python -c "import numpy, sklearn, matplotlib; print('sci stack OK')"
python -c "import tensorflow as tf; print('tensorflow', tf.__version__)"
python -c "import langchain, langchain_community, langgraph; print('langchain stack OK')"
jupyter lab --version

# LLM — run ONE of:
ollama run llama3.2:1b "say hi"                       # Option B (Ollama)
python -c "import langchain_groq; print('groq lib OK')"   # Option A (Groq)

# Keys present (Day 3 + LLM):
python -c "import os; [print(k, bool(os.getenv(k))) for k in ('GROQ_API_KEY','SERPER_API_KEY','WOLFRAM_ALPHA_APPID')]"
```

## 9. What participants do NOT need
- No GPU · No cloud/VM · No admin server · No paid subscription **by default** (Groq, Ollama, Serper, Wolfram all have free tiers)
- OpenAI is **optional (BYOK)**, not required
- No internet is needed to **complete or pass** any graded exercise (offline fallbacks) — but the Tier-2 services are required to perform the labs **as designed**

---

*© 2026 Gheware DevOps & Agentic AI · devops.gheware.com · training@gheware.com · +91-9606795215*
