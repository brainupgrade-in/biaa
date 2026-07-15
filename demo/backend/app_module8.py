"""
Worked example: package Module-8 lab 8.12 (capstone customer-service chatbot)
as a deployable HTTP service.

This lab is a multi-agent TEAM, not a single agent: process() routes a ticket to
real billing/tech specialists (create_agent + ChatGroq), votes on a disputed
charge, synthesises one reply, and GATES refunds to a human. So /chat returns the
team's structured verdict (reply + status + which agents ran), not just text.

The functions below are lifted almost verbatim from
  hands-on/module-8/solutions/lab-12-capstone-customer-service-chatbot.ipynb
(cells 2 + 6), with the notebook-only bits (offline sanity prints, print_trace,
the "Your turn" cell) dropped. The refund guardrail is preserved: specialists
have NO refund tool, so a refund request comes back as needs_approval.

Run (from repo root, venv active):
    pip install -r demo/backend/requirements.txt
    uvicorn demo.backend.app_module8:app --reload --host 0.0.0.0 --port 8000
    # POST /chat {"message": "I was charged twice for order 4471"}
"""
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_groq import ChatGroq

# Same repo-root .env the labs use (GROQ_API_KEY).
REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

import os  # noqa: E402  (after load_dotenv so the key is present)

MODEL = "openai/gpt-oss-20b"


def groq_ready() -> bool:
    return bool(os.environ.get("GROQ_API_KEY"))


# ---------------------------------------------------------------------------
# ---- Lab 8.12 logic (lifted from the solution notebook) -------------------
# ---------------------------------------------------------------------------
INVOICES = {
    "4471": [{"amount": 50, "date": "Jul 01"}, {"amount": 50, "date": "Jul 01"}],  # duplicate charge
    "5090": [{"amount": 30, "date": "Jul 02"}],
}
KNOWN_ISSUES = {
    "crash": {"bug": "BUG-231", "fix": "update to v4.2"},
    "login": {"bug": "BUG-118", "fix": "reset your password"},
}


@tool
def lookup_invoice(order_id: str) -> str:
    """Look up the charges on an order by its id, e.g. '4471'. Use for billing / charge / refund questions."""
    charges = INVOICES.get(order_id.strip(), [])
    return str(charges) if charges else "no charges found for that order"


@tool
def known_issues(symptom: str) -> str:
    """Look up a known technical issue by symptom keyword, e.g. 'crash' or 'login'. Use for tech problems."""
    for k, v in KNOWN_ISSUES.items():
        if k in symptom.lower():
            return v["bug"] + ": " + v["fix"]
    return "no known issue matched"


def build_specialist(llm, tools, role):
    return create_agent(llm, tools, system_prompt=f"You are the {role} specialist. Use ONLY your own tools; answer in one sentence.")


def route(message):
    m = message.lower()
    kws = {"billing": ("charg", "refund", "invoice", "billed"), "tech": ("crash", "bug", "login", "broken")}
    hits = [name for name, ks in kws.items() if any(k in m for k in ks)]
    return hits if hits else ["general"]


def refund_intent(message):
    return any(k in message.lower() for k in ("refund", "charged twice", "duplicate", "dispute"))


def is_dispute(message):
    return "dispute" in message.lower()


def decide(verdicts, threshold=0.5):
    top, n = Counter(verdicts).most_common(1)[0]
    if n / len(verdicts) > threshold:
        return {"decision": top, "escalate": False}
    return {"decision": None, "escalate": True}


def synthesize(findings):
    return " ".join(f"[{k}] {findings[k]}" for k in sorted(findings)) if findings else "forwarded to a human agent"


def specialist_reply(agent, message):
    result = agent.invoke({"messages": [("user", message)]}, config={"recursion_limit": 8})
    return result["messages"][-1].content


def process(message, agents):
    """Route -> run each REAL specialist -> vote on a dispute -> synthesise -> gate the refund."""
    involved = route(message)
    findings = {name: specialist_reply(agents[name], message) for name in involved if name in agents}
    conflict = None
    if "billing" in involved and is_dispute(message):
        conflict = decide(["refund", "deny"])
        findings["billing"] = "reviewers split -> escalate to a human" if conflict["escalate"] else findings.get("billing", "")
    needs_human = ("billing" in involved and refund_intent(message)) or bool(conflict and conflict["escalate"])
    return {
        "agents": sorted(findings) or involved,
        "reply": synthesize(findings),
        "status": "needs_approval" if needs_human else "auto_ok",
        "conflict": bool(conflict),
    }


# ---------------------------------------------------------------------------
# ---- HTTP layer -----------------------------------------------------------
# ---------------------------------------------------------------------------
app = FastAPI(title="biaa demo - Module 8 customer-service chatbot", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Build the real specialists ONCE, lazily (so /health works without a key).
_agents = None


def get_agents():
    global _agents
    if _agents is None:
        llm = ChatGroq(model=MODEL, temperature=0)
        _agents = {
            "billing": build_specialist(llm, [lookup_invoice], "billing"),
            "tech": build_specialist(llm, [known_issues], "tech"),
        }
    return _agents


class ChatIn(BaseModel):
    message: str


@app.get("/health")
def health() -> dict:
    return {"ok": True, "model": MODEL, "has_key": groq_ready()}


@app.post("/chat")
def chat(body: ChatIn) -> dict:
    if not groq_ready():
        return {"reply": "No GROQ_API_KEY set. Add it to the repo-root .env.", "status": "error", "agents": [], "conflict": False}
    try:
        return process(body.message, get_agents())
    except Exception as exc:  # keep the demo up if a model call fails
        return {"reply": f"Agent error: {exc}", "status": "error", "agents": [], "conflict": False}
