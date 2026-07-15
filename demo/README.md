# Ship a lab as an app (FastAPI + React Native / Expo)

This folder turns any hands-on lab agent into a deployable app so you can
demonstrate **production deployment of Agentic AI** in the room. It's built to be
driven with **[OpenCode](https://opencode.ai)** for rapid prototyping.

## Why a backend?

React Native can't run Python. The lab agents (LangChain / `create_agent` /
`ChatGroq`) are Python, so the production pattern is:

```
  Expo / React Native app  ──HTTP──►  FastAPI service  ──►  lab agent (ChatGroq / Ollama)
     (demo/<name>/)                    (demo/backend/)        (hands-on/**/*.ipynb logic)
```

The app stays thin (UI + `fetch`); all agent logic lives server-side, exactly as
you'd deploy it.

## Quick start (one command)

On a Codespace, `demo/run.sh` does the whole build+launch: installs backend deps,
starts the API, scaffolds the Expo app, injects the **forwarded** backend URL into
it (not `localhost`), makes port 8000 public, and starts Expo. Ctrl+C stops both.

```bash
bash demo/run.sh                                   # Module-8 example + Expo web
bash demo/run.sh --backend demo.backend.main:app   # the generic template instead
bash demo/run.sh --mode tunnel                     # phone via Expo Go (QR)
bash demo/run.sh --mode backend-only               # just the API (curl / external app)
```

Prefer the manual steps? They're below.

## 1. Run the API

```bash
# from the repo root, with biaa-venv active
pip install -r demo/backend/requirements.txt
uvicorn demo.backend.main:app --reload --host 0.0.0.0 --port 8000
# open http://localhost:8000/docs  (or the forwarded 8000 URL in a Codespace)
```

`demo/backend/main.py` ships a trivial `word_count` agent. **Swap the body of
`build_agent()`** for the lab you want to ship — e.g. lift the tools + prompt
from `hands-on/module-7` (email-drafting) or `module-8` (customer-service). Keep
the gather-only / no-send guardrails: don't bind a `send_*`/`place_trade` tool
you wouldn't run unattended.

### Packaging any lab — the recipe

1. **Read the solution, keep the reusable core.** Drop the notebook scaffolding
   (`groq_ready()` prints, `print_trace`, offline-sanity cells, the "Your turn"
   cell); keep the tools, the agent/team logic, and the model.
2. **Paste it into a module under `demo/backend/`.** Two mechanical fixes when
   lifting from a notebook: build the model **lazily** (inside a getter) so
   `/health` works without a key, and load the repo-root `.env` with a
   `Path(__file__).resolve().parents[2]` anchor (not the notebook's `find_dotenv`).
3. **Map the lab's entry point to `/chat`, matching the return shape:**

   | Lab shape | `/chat` returns |
   |-----------|-----------------|
   | Single agent (M7 email, M9 insight) | `{reply}` from `result["messages"][-1].content` |
   | Team with a `process()` (M8 8.12) | `{reply, status, agents, conflict}` — the whole verdict |
4. **Keep the guardrail.** If the lab withholds a tool (no `send_email` /
   `place_trade` / refund tool), a request for it comes back as
   `needs_approval` — in the app that's a human-approval screen, never an
   auto-action.

**Worked example — Module-8 lab 8.12** (the customer-service chatbot *team*) is
packaged in [`backend/app_module8.py`](backend/app_module8.py). It lifts
`route → real specialists → vote → synthesise → refund-gate` verbatim and returns
the structured verdict:

```bash
uvicorn demo.backend.app_module8:app --reload --host 0.0.0.0 --port 8000
curl -sX POST localhost:8000/chat -H 'content-type: application/json' \
  -d '{"message":"I was charged twice for order 4471 and the app keeps crashing on login."}'
# -> {"agents":["billing","tech"], "reply":"[billing] … [tech] …", "status":"needs_approval", "conflict":false}
```

## 2. Scaffold the mobile app

```bash
bash demo/new-mobile-app.sh            # creates demo/mobile/
# or:  bash demo/new-mobile-app.sh insight-app
cd demo/mobile
npx expo start                         # press w for web, or scan the QR in Expo Go
```

The generated `App.tsx` already POSTs to the API's `/chat`.

## 3. Wiring it up in a Codespace

- The **Ports** panel forwards `8000` (API) and `8081`/`19006` (Expo). Make the
  8000 port **Public** (or use the `…-8000.app.github.dev` URL) and set that as
  `API` in `App.tsx`.
- On a physical phone via **Expo Go**, `localhost` means the phone, not the
  server — use the forwarded public URL, or `expo start --tunnel`.

## 4. Prototype fast with OpenCode

```bash
cd demo/mobile        # or demo/backend
opencode              # installed by the devcontainer; describe the change and let it build
```

Good OpenCode prompts to start from:
- "Add a chat history list with user/agent bubbles to App.tsx."
- "Add a /stream SSE endpoint to the FastAPI app and stream tokens to the UI."
- "Wrap the module-8 customer-service agent in build_agent() and add a refund-approval screen."

## Notes

- `demo/mobile/` (and any scaffolded app) is git-ignored — it's a throwaway demo,
  regenerate it any time with `new-mobile-app.sh`.
- For a shareable web build: `npx expo export --platform web` (static output in
  `dist/`), then host anywhere. For native binaries, use EAS Build.
