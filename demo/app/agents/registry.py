"""Agent registry — map a short id to a lab agent that answers one message.

To package ANY hands-on lab as a demo:
  1. Drop a module in this folder that exposes:
         run(message: str) -> dict     # the dict MUST contain a "reply" key;
                                        # may also carry status/agents/conflict/etc.
  2. Register it in REGISTRY below.
That's the whole contract — the web UI and /chat endpoint pick it up automatically.
"""
from importlib import import_module

# id -> (human label, dotted module path). The module must expose run(message)->dict.
REGISTRY = {
    "module8": ("Customer-service team — M8 lab 8.12", "demo.app.agents.lab8_12"),
    "generic": ("Generic tool agent — word count", "demo.app.agents.generic"),
}
DEFAULT = "module8"


def list_agents():
    return [{"id": k, "label": label} for k, (label, _mod) in REGISTRY.items()]


def run_agent(agent_id: str, message: str) -> dict:
    entry = REGISTRY.get(agent_id)
    if entry is None:
        return {"reply": f"Unknown agent '{agent_id}'.", "status": "error", "agents": [], "conflict": False}
    mod = import_module(entry[1])
    return mod.run(message)
