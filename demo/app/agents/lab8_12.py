"""Module-8 lab 8.12 packaged as a demo agent — the customer-service TEAM.

route -> real billing/tech specialists -> vote-on-dispute -> synthesise -> refund gate.
Lifted from hands-on/module-8/solutions/lab-12-capstone-customer-service-chatbot.ipynb
(cells 2 + 6), dropping the notebook-only bits.

Guardrail preserved: the specialists have NO refund tool, so a refund request comes
back as status "needs_approval" — in a real app that's a human-approval screen.

Contract: run(message) -> {"reply", "status", "agents", "conflict"}.
"""
import os
from collections import Counter

MODEL = "openai/gpt-oss-20b"

# --- lab data ----------------------------------------------------------------
INVOICES = {
    "4471": [{"amount": 50, "date": "Jul 01"}, {"amount": 50, "date": "Jul 01"}],  # duplicate charge
    "5090": [{"amount": 30, "date": "Jul 02"}],
}
KNOWN_ISSUES = {
    "crash": {"bug": "BUG-231", "fix": "update to v4.2"},
    "login": {"bug": "BUG-118", "fix": "reset your password"},
}


# --- pure team logic (no LLM) ------------------------------------------------
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


# --- real specialists (built lazily on first use) ----------------------------
_agents = None


def _build_agents():
    from langchain.agents import create_agent
    from langchain_core.tools import tool
    from langchain_groq import ChatGroq

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

    llm = ChatGroq(model=MODEL, temperature=0)
    return {
        "billing": build_specialist(llm, [lookup_invoice], "billing"),
        "tech": build_specialist(llm, [known_issues], "tech"),
    }


def run(message: str) -> dict:
    if not os.getenv("GROQ_API_KEY"):
        return {"reply": "No GROQ_API_KEY set — add it to .env (or a Codespaces secret).",
                "status": "error", "agents": [], "conflict": False}
    global _agents
    try:
        if _agents is None:
            _agents = _build_agents()
        return process(message, _agents)
    except Exception as exc:  # keep the demo up if a model call fails
        return {"reply": f"Agent error: {exc}", "status": "error", "agents": [], "conflict": False}
