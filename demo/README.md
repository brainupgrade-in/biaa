# Ship a lab as an app (FastAPI + a mobile-styled web UI)

Turn any hands-on lab agent into a deployable app to demonstrate **production
deployment of Agentic AI** — with the least possible friction.

**One process, one port, no Node.** A single FastAPI service serves both a
mobile-styled chat page (`app/index.html`) and the `/chat` API. It launches
identically on any Codespace (Alpine or Debian), and containerizes to a real
one-command deploy.

> Why not React Native? A native RN/Expo build needs the whole Node toolchain
> (npm install + Metro/EAS build + 3 forwarded ports) and broke on an Alpine/musl
> Codespace. For a *demo*, a responsive web page that calls the same backend is
> dramatically more reliable and tells the same "app → agent service" story.

## Layout

```
demo/
  app/
    main.py          # FastAPI: serves index.html + /chat + /health + /agents
    __main__.py      # python -m demo.app
    index.html       # phone-framed chat UI (inline CSS/JS, no external deps)
    agents/
      registry.py    # id -> lab agent; add a line to package a new lab
      lab8_12.py     # Module-8 team (route → specialists → vote → refund gate)
      generic.py     # single-agent template (word count)
  requirements.txt   # web layer + just the LangChain bits (no torch/transformers)
  Dockerfile
  docker-compose.yml
  run.sh             # dev launcher
```

## Launch

**Dev (venv):**
```bash
bash demo/run.sh
# → http://localhost:8000   (in a Codespace, open the forwarded port 8000)
```
or directly: `python -m demo.app` / `uvicorn demo.app.main:app --host 0.0.0.0 --port 8000`.

**Production-like (Docker):**
```bash
docker compose -f demo/docker-compose.yml up --build
```
The image is slim (no torch/transformers) and reads `GROQ_API_KEY` from the
repo-root `.env` at run time (never baked in).

**In a Codespace:** open the **PORTS** panel, and set port **8000** to **Public**
(or just open the forwarded `…-8000.app.github.dev` URL in the same browser).

## The GROQ key

Days 4–5 agents use Groq. Put your key in the repo-root `.env`:
```
GROQ_API_KEY=gsk_...        # free at https://console.groq.com/keys
```
or set it as a **Codespaces secret** (Settings → Codespaces → Secrets). Without it
the app still runs and the UI loads — `/chat` just returns a friendly placeholder.

## Package any lab as an agent

The whole contract is one function:

1. Add `demo/app/agents/<yourlab>.py` exposing:
   ```python
   def run(message: str) -> dict:   # must include a "reply" key;
       ...                          # may also add status / agents / conflict
   ```
   Build the model **lazily** (inside the function) and read `os.getenv("GROQ_API_KEY")`
   so the app starts without a key. Copy `generic.py` (single agent) or `lab8_12.py`
   (a multi-agent team) as your starting point.
2. Register it in `agents/registry.py`:
   ```python
   REGISTRY = { ..., "yourlab": ("Nice label", "demo.app.agents.yourlab") }
   ```
The dropdown in the UI and the `/chat` endpoint pick it up automatically.

**Worked example — Module-8 lab 8.12** (`agents/lab8_12.py`): the customer-service
*team* — `route → real billing/tech specialists → vote-on-dispute → synthesise →
refund gate`. The guardrail is the point: specialists have **no refund tool**, so a
refund request returns `status: "needs_approval"` (in the UI, an amber badge) — a
human-approval step, never an auto-action.

```bash
curl -sX POST localhost:8000/chat -H 'content-type: application/json' \
  -d '{"message":"I was charged twice for order 4471 and the app keeps crashing on login.","agent":"module8"}'
# → {"agents":["billing","tech"], "reply":"[billing] … [tech] …", "status":"needs_approval", "conflict":false}
```

## Iterate with OpenCode

```bash
opencode        # "add a refund-approval screen when status is needs_approval", etc.
```
