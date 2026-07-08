# Environment setup scripts

Automated environment setup for the **Building Intelligent AI Agents** 5-day
workshop (120 hands-on Jupyter labs). These scripts do everything in
[`../SETUP.md`](../SETUP.md) for you: verify Python 3.12, create the `biaa-venv`
virtual environment, install the Tier 1–2 packages every lab needs (plus
optional Tier 3), register a Jupyter kernel, and run a smoke test.

> `SETUP.md` remains the human-readable reference (hardware, firewall allowlist,
> accounts to create). These scripts automate the install steps in it.

## Which script do I run?

| Your machine | Shell to use | Command |
|---|---|---|
| **Windows 10/11** | **Git Bash** (ships with [Git for Windows](https://git-scm.com/download/win)) | `bash scripts/setup-windows.sh` |
| **Linux** | Terminal (bash) | `bash scripts/setup-linux.sh` |
| **macOS** | Terminal (bash/zsh) | `bash scripts/setup-linux.sh` |

Run the command **from the course root folder** (the one containing `SETUP.md`
and this `scripts/` folder), not from inside `scripts/`.

## Prerequisite: Python 3.12

Install **Python 3.12** first — the scripts verify it and stop with instructions
if it's missing.

- **Windows:** download from
  [python.org/downloads/release/python-3120](https://www.python.org/downloads/release/python-3120/).
  During install, tick **"Add python.exe to PATH"**, then **close and reopen Git Bash**.
- **Linux (Ubuntu/Debian):** `sudo apt install python3.12 python3.12-venv`
- **macOS (Homebrew):** `brew install python@3.12`

We pin 3.12 because it has mature, well-tested wheels for every workshop package
(including TensorFlow), which avoids install/troubleshooting headaches.

## Files in this folder

| File | Purpose |
|---|---|
| `setup-linux.sh` | Setup for Linux / macOS |
| `setup-windows.sh` | Setup for Windows (Git Bash) |
| `smoke-test.sh` | Cross-platform verification (setup runs it automatically; also runnable on its own) |
| `requirements-core.txt` | Tier 1 + 2 — everything the 120 labs need |
| `requirements-optional.txt` | Tier 3 — optional Hugging Face `transformers` + `torch` |

## Options

Add the optional Hugging Face demo packages (Day 2 real `bert-tiny` cells — the
graded labs pass without them):

```bash
bash scripts/setup-linux.sh   --with-hf     # Linux / macOS
bash scripts/setup-windows.sh --with-hf     # Windows Git Bash
```

## After setup

**Activate the environment in every new terminal** before launching the labs:

```bash
# Linux / macOS
source biaa-venv/bin/activate

# Windows (Git Bash)
source biaa-venv/Scripts/activate
```

Then start Jupyter and pick the **"Python 3.12 (biaa)"** kernel:

```bash
jupyter lab
```

### (Optional) real LLM + external API keys

The agent labs (Days 3–5) run their graded cells on a built-in offline fallback,
but for the **full experience** set up **one** LLM and the Day-3 API keys:

```bash
# LLM — pick ONE:
export GROQ_API_KEY=...                 # Option A: free Groq API
ollama pull llama3.2:1b                  # Option B: local Ollama (no key)

# Day 3 external APIs:
export SERPER_API_KEY=...                # Google Serper (search)
export WOLFRAM_ALPHA_APPID=...           # Wolfram Alpha
```

On Windows Git Bash, `export` sets the key for the current session. To persist
it, add the `export ...` lines to `~/.bashrc`. See `SETUP.md` §7 for where to get
each free key.

## Re-running / troubleshooting

- **Re-run any time** — the scripts reuse an existing `biaa-venv` and just
  re-install/upgrade. Safe to run again if an install was interrupted.
- **Start fresh** — delete the venv and re-run:
  `rm -rf biaa-venv` (Linux/macOS/Git Bash).
- **Verify only** — `bash scripts/smoke-test.sh` (finds the venv automatically;
  no activation needed).
- **`python: command not found` on Windows** — you skipped "Add to PATH" during
  the Python install, or didn't reopen Git Bash. Reinstall Python with the PATH
  box ticked, then reopen Git Bash.
- **TensorFlow install is slow** — it's a large download (~several hundred MB).
  Give it a few minutes on the first run.

---

*© 2026 Gheware DevOps & Agentic AI · devops.gheware.com · training@gheware.com · +91-9606795215*
