# Delivery-day runbook

A one-page operations sheet for running **Building Intelligent AI Agents** live.
`SETUP.md` is the participant install guide; this is the **instructor + in-room
troubleshooting** sheet. Assume a **Windows-majority room using Git Bash** — the
least-hassle path is called out at each step.

---

## 30-second pre-flight, every morning

Each participant runs the check for **that day** before the session starts:

```bash
source biaa-venv/Scripts/activate      # Windows Git Bash  (macOS/Linux: biaa-venv/bin/activate)
bash scripts/smoke-test.sh --day 3     # <- today's day number (1-5)
```

It prints `[PASS]/[FAIL]` for exactly what the day needs (packages + that day's
LLM/API) and ends with **"Day N: ready to go."** or points at the fix. No flag =
the full check across all five days.

---

## What each day needs (provider progression)

| Day | Modules | LLM / service | Key or model | Least-hassle on Windows |
|----|---------|---------------|--------------|--------------------------|
| 1 | 1-2 Foundations & Deep Learning | **None** (NumPy/scikit-learn/**TensorFlow-CPU**, MNIST) | — | Nothing to configure |
| 2 | 3-4 Transformers & fine-tuning | **Hugging Face** (`transformers`+CPU `torch`, fine-tunes `bert-tiny`); hosted text-gen via Groq | `GROQ_API_KEY` (optional; cells self-skip without) | Runs offline; models download on first use |
| 3 | 5-6 Agentic AI + frameworks | **Local Ollama** `llama3.1:8b` on `127.0.0.1:11434`; Module 6 also Serper + Wolfram | pull `llama3.1:8b` (~4.9 GB); `SERPER_API_KEY`, `WOLFRAM_ALPHA_APPID` (optional) | **Pull the model the night before.** Or set the Day-3 labs to Groq (see below) |
| 4 | 7-8 Task automation & multi-agent | **Groq** `openai/gpt-oss-20b` | `GROQ_API_KEY` | Cloud key only — nothing local |
| 5 | 9-10 Industry agents & responsible AI | **Groq** `openai/gpt-oss-20b` | `GROQ_API_KEY` | Cloud key only — nothing local |

**Day 5 also includes the live demo of the FrontDesk AI production app** (a
self-evolving multi-agent support desk) — run from its own repo, not these labs.

> **Least-hassle overall:** get a free **Groq** key (`console.groq.com`) into
> `.env` once — it covers Days 2, 4, 5 with zero local services. **Day 3 is the
> only day that needs a local model.** For a low-spec or locked-down Windows
> room, either pre-pull `llama3.1:8b` ahead of time, or swap the Module 5-6 labs'
> `ChatOllama(...)` for `ChatGroq("openai/gpt-oss-20b")` so the whole course runs
> on Groq alone.

---

## Ports

| Port | Service | When |
|------|---------|------|
| 8888 | Jupyter Lab | All days |
| 11434 | Ollama (local, `127.0.0.1`) | Day 3 only |

No other inbound ports. Everything else (Groq / Serper / Wolfram / Hugging Face
downloads) is outbound HTTPS — see `SETUP.md` §6 for the firewall allowlist.

---

## Error recovery (Windows-first)

| Symptom | Fix |
|---------|-----|
| **"Which kernel?" / imports fail in a lab** | The notebooks must use the **`biaa`** kernel. Setup sets this automatically; if a notebook shows "Python 3" instead, run `python scripts/set-notebook-kernel.py`, then reopen it and pick **"Python 3.12 (biaa)"**. |
| **`python: command not found` (Git Bash)** | Python 3.12 wasn't added to PATH, or Git Bash wasn't reopened. Reinstall Python 3.12 with **"Add python.exe to PATH"** ticked, close & reopen Git Bash. Or install `uv` and re-run setup (no manual Python needed). |
| **`apt install python3.12` fails / distro has no 3.12** | Install `uv` (`curl -LsSf https://astral.sh/uv/install.sh \| sh`), reopen shell, re-run the setup script — uv provisions Python 3.12 itself. |
| **Day 3: "Ollama not reachable" / connection refused** | Start the server: `ollama serve` (new terminal), or launch the Ollama app. Verify with `bash scripts/smoke-test.sh --day 3`. Always use `127.0.0.1:11434`, not `localhost` (a proxy env var can hijack `localhost`). |
| **Day 3: "llama3.1:8b missing"** | `ollama pull llama3.1:8b` (~4.9 GB — do this before the session on venue Wi-Fi). |
| **Day 3 model too slow / low RAM** | Switch the Module 5-6 labs to Groq: replace `ChatOllama(...)` with `ChatGroq("openai/gpt-oss-20b")` and ensure `GROQ_API_KEY` is set. |
| **Groq `429` / rate-limited** | Free tier is per-key; **stagger class starts** and avoid everyone running the same cell at once. Wait ~60s and retry. Each participant should use **their own** key. |
| **`GROQ_API_KEY not set` but it's in `.env`** | The lab reads `.env` via `load_dotenv`; a bare shell doesn't. That's fine — the labs still pick it up. To satisfy a shell check too: `export GROQ_API_KEY=...`. |
| **TensorFlow install slow (Day 1/2)** | Large download (~several hundred MB); give it a few minutes on first run. Pre-run setup before the room arrives. |
| **Port 8888 in use** | Another Jupyter is running: `jupyter lab --port 8899`, or stop the other one. |
| **Environment wedged / half-installed** | Rebuild: `rm -rf biaa-venv` then re-run `bash scripts/setup-windows.sh` (or `setup-linux.sh`). Safe to re-run any time — it reuses an existing venv. |

---

*© 2026 Gheware DevOps & Agentic AI · devops.gheware.com · training@gheware.com · +91-9606795215*
