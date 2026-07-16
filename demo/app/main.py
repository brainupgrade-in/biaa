"""biaa demo app — one FastAPI process that serves the chat UI AND the /chat API.

No Node, no Expo: the "app" is a mobile-styled web page (demo/app/index.html) that
calls /chat. Launch with any of:
    uvicorn demo.app.main:app --host 0.0.0.0 --port 8000
    python -m demo.app
    docker compose -f demo/docker-compose.yml up
"""
import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Load the repo-root .env when present (local / Codespace dev). In a container the
# key arrives via the environment (docker-compose env_file), so a missing file is fine.
load_dotenv(find_dotenv(usecwd=True))

from demo.app.agents import registry  # noqa: E402 (after load_dotenv)

HERE = Path(__file__).resolve().parent

app = FastAPI(title="biaa demo app", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ChatIn(BaseModel):
    message: str
    agent: str = registry.DEFAULT


@app.get("/")
def index():
    return FileResponse(HERE / "index.html")


@app.get("/health")
def health() -> dict:
    return {"ok": True, "has_key": bool(os.getenv("GROQ_API_KEY")), "agents": registry.list_agents()}


@app.get("/agents")
def agents() -> list:
    return registry.list_agents()


@app.post("/chat")
def chat(body: ChatIn) -> dict:
    return registry.run_agent(body.agent, body.message)
