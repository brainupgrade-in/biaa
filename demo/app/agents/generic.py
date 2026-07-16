"""Generic single-agent example (word_count tool).

The template for packaging a single-agent lab (M7 email, M9 insight, ...):
swap the body of _build() for the lab's tools + prompt + model.

Contract: run(message) -> {"reply", "status", "agents", "conflict"}.
"""
import os

MODEL = "openai/gpt-oss-20b"
_agent = None


def _build():
    from langchain.agents import create_agent
    from langchain_core.tools import tool
    from langchain_groq import ChatGroq

    @tool
    def word_count(text: str) -> str:
        """Return the number of words in the given text."""
        return str(len(text.split()))

    return create_agent(ChatGroq(model=MODEL, temperature=0), [word_count])


def run(message: str) -> dict:
    if not os.getenv("GROQ_API_KEY"):
        return {"reply": "No GROQ_API_KEY set — add it to .env (or a Codespaces secret).",
                "status": "error", "agents": [], "conflict": False}
    global _agent
    try:
        if _agent is None:
            _agent = _build()
        result = _agent.invoke({"messages": [{"role": "user", "content": message}]})
        return {"reply": result["messages"][-1].content, "status": "auto_ok", "agents": ["generic"], "conflict": False}
    except Exception as exc:
        return {"reply": f"Agent error: {exc}", "status": "error", "agents": [], "conflict": False}
