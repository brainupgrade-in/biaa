"""
Demo API: wrap a hands-on lab agent as an HTTP service a mobile app can call.

This is the *bridge* between the Python labs and a React Native / Expo front-end:
React Native can't run Python, so we expose the agent over HTTP and the app POSTs
to /chat. Mirrors the Day-4/5 lab pattern (ChatGroq + create_agent). Swap the
`build_agent()` body for whichever lab you want to ship.

Run (from repo root, venv active):
    pip install -r demo/backend/requirements.txt
    uvicorn demo.backend.main:app --reload --host 0.0.0.0 --port 8000

Then: http://localhost:8000/docs  (interactive), or POST /chat {"message": "..."}.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load the same repo-root .env the labs use (GROQ_API_KEY, etc.).
REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

MODEL = "openai/gpt-oss-20b"  # the Day-4/5 lab model (verified tool-calling)

app = FastAPI(title="biaa demo API", version="0.1.0")

# Wide-open CORS for demo convenience so an Expo web build / device can call in.
# Tighten allow_origins before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_agent():
    """Build the lab agent. Replace this body with your chosen lab's logic."""
    from langchain.agents import create_agent
    from langchain_core.tools import tool
    from langchain_groq import ChatGroq

    @tool
    def word_count(text: str) -> str:
        """Return the number of words in the given text."""
        return str(len(text.split()))

    llm = ChatGroq(model=MODEL, temperature=0)
    # create_agent returns a CompiledStateGraph; bind only the tools you trust.
    return create_agent(llm, [word_count])


# Build lazily so the server can start (and /health answer) even without a key.
_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


class ChatIn(BaseModel):
    message: str


class ChatOut(BaseModel):
    reply: str


@app.get("/health")
def health() -> dict:
    return {"ok": True, "model": MODEL, "has_key": bool(os.getenv("GROQ_API_KEY"))}


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn) -> ChatOut:
    if not os.getenv("GROQ_API_KEY"):
        return ChatOut(reply="No GROQ_API_KEY set. Add it to the repo-root .env.")
    try:
        result = get_agent().invoke({"messages": [{"role": "user", "content": body.message}]})
        # The final assistant message is the last item in the message trace.
        return ChatOut(reply=result["messages"][-1].content)
    except Exception as exc:  # keep the demo up even if the model call fails
        return ChatOut(reply=f"Agent error: {exc}")
