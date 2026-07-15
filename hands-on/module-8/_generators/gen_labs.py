# -*- coding: utf-8 -*-
"""Generator for Day 4 Module 8 hands-on labs (12 notebooks) -- NEAR-REAL design.
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

Design: this is the "Multi-Agent Collaboration & Decision Making" module -- the labs build the
MULTI-AGENT CUSTOMER-SERVICE CHATBOT (the client's Lab 4.2) piece by piece. The multi-agent
MECHANICS (routing/supervisor, shared state, sequential pipeline, parallel fan-out, explicit
handoff, voting, critique/debate, synthesis, observability) are legitimate rule-based
orchestration -- so they stay REAL Python you build and run. The SPECIALIST agents (billing /
tech) and the ASSEMBLED chatbot are REAL `create_agent` agents over a REAL hosted model
(`ChatGroq(model="openai/gpt-oss-20b")`, Day-4 provider) with their OWN tools: the supervisor
routes a real ticket to real specialists that really answer, a synthesiser combines them into
one grounded reply, and any refund / irreversible action stays HUMAN-GATED (needs_approval).
Students read the REAL message trace. There is NO auto-grader -- each lab ends with
"Build it -> Run it / observe -> Your turn (open task)".

Provider: Groq (Day 4). `ChatGroq(model="openai/gpt-oss-20b", temperature=0)` -- verified reliable
tool-calling via create_agent. Key loaded with `load_dotenv(find_dotenv(usecwd=True), override=True)`; if
GROQ_API_KEY is missing the live specialist cells print how to set it instead of crashing.
Student robustness (no grader): exercise cells are wrapped by guard()/runguard() so an unfilled
`___` prints a friendly note instead of crashing -- a student notebook runs top-to-bottom, and a
solution notebook runs the real thing."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day4-module8-multi-agent-collaboration.html"
OUTLINE = "../../course-outline-building-intelligent-ai-agents.html"
REPO = "/home/rajesh/Training/courses/building-intelligents-ai-agents"

def _lines(text):
    parts = text.split("\n")
    return [p + "\n" for p in parts[:-1]] + [parts[-1]]

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": _lines(text)}

def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": _lines(text)}

def render(lines, sol):
    out = []
    for ln in lines:
        out.append((ln["a"] if sol else ln["s"]) if isinstance(ln, dict) else ln)
    return "\n".join(out)

def _indent(text, n):
    pad = " " * n
    return "\n".join((pad + ln) if ln.strip() else ln for ln in text.split("\n"))

def guard(exercise):
    """Wrap an exercise (that calls the blanked code) so an unfilled ___ prints a note, not a crash."""
    return ("try:\n" + _indent(exercise, 4) +
            '\nexcept Exception as e:\n    print("(Fill the ___ blanks above, then re-run.)", type(e).__name__)')

def runguard(exercise):
    """Guard a 'run it for real' cell: skip cleanly if no GROQ_API_KEY, and if a blank is unfilled."""
    return ('if not groq_ready():\n'
            '    print("GROQ_API_KEY not set -- add it to .env (free at console.groq.com), then re-run this cell.")\n'
            'else:\n'
            '    try:\n' + _indent(exercise, 8) +
            '\n    except Exception as e:\n        print("(Fill the ___ blanks above, then re-run.)", type(e).__name__)')

def setup(nn):
    return code(f'''# Setup -- run me first
import os, pathlib
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True), override=True)   # GROQ_API_KEY (Day-4 provider)

WORK = os.path.join(os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp", "biaa-lab-08-{nn:02d}")
os.makedirs(WORK, exist_ok=True)

def groq_ready():
    """True if a GROQ_API_KEY is present. The live specialist cells self-skip when it is absent."""
    return bool(os.environ.get("GROQ_API_KEY"))

from langchain_groq import ChatGroq
# Day-4 provider: a REAL hosted model with reliable tool-calling via create_agent.
# gpt-oss-20b is verified; do NOT use llama-3.3-70b-versatile (it 400s through create_agent).
# One shared model is fine -- each specialist differs by its system_prompt + its own tools.
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0) if groq_ready() else None

def print_trace(result):
    """Print a REAL agent message trace: tool calls the model made, tool observations, final answer."""
    for m in result["messages"]:
        for tc in (getattr(m, "tool_calls", None) or []):
            print("TOOL CALL:", tc["name"], tc["args"])
        if type(m).__name__ == "ToolMessage":
            print("OBS:", str(m.content)[:200])
        elif str(getattr(m, "content", "")).strip():
            print(type(m).__name__, ":", str(m.content)[:300])

if groq_ready():
    print("GROQ_API_KEY loaded | model: openai/gpt-oss-20b | WORK:", WORK)
else:
    print("GROQ_API_KEY NOT set -- add it to .env (free at console.groq.com).")
    print("(The 'Run it for real' cells will print this note instead of crashing.)  WORK:", WORK)''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 8.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 4 &middot; Module 8 &mdash; Multi-Agent Collaboration &amp; Decision Making**

### What you'll do
{g}

> **How this lab works (near-real):** read the **Concept**, fill the real `___` blanks in **Build it**, then **run it and read what happened**. The multi-agent *mechanics* (routing, shared state, voting, critique, synthesis, observability) are **real Python you build and run**; the **specialist agents and the assembled chatbot are real `create_agent` agents** that really answer. Finish with an open **Your turn**. There is **no auto-grader** &mdash; the goal is a working team and a trace you can read.

> **Framework note:** these labs use the **real** LangChain 1.x (`langchain`, `langchain-core`, `langgraph`) and, for the specialists, a **real hosted model** &mdash; `ChatGroq(model="openai/gpt-oss-20b")` with your `GROQ_API_KEY` from `.env`. If the key is missing, the live cells print how to set it instead of crashing. A `@tool` must **catch its own errors and return a string** &mdash; a tool that *raises* can abort the whole agent run. You are building the **multi-agent customer-service chatbot** &mdash; the client's Lab 4.2.

**Reference:** [Module 8 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 8 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 8 labs](./index.html) &nbsp;&middot;&nbsp; [Module 8 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def concept(text):   return md("## Concept\n" + text)
def buildmd(text):   return md("## Build it\n" + text)
def observemd(text): return md("## Run it &amp; read the output\n" + text)
def runmd(text):     return md("## Run it for real &amp; read the trace\n" + text + "\n\n_This calls the real `openai/gpt-oss-20b` via Groq. If `GROQ_API_KEY` is unset the cell prints how to set it instead of crashing. Multi-agent runs make several model calls &mdash; keep live runs light on the free tier._")
def noticemd(text):  return md("## What to notice\n" + text)
def yourturn(text):  return md("## Your turn (open task &mdash; no grader)\n" + text)

def sol_answer(sol, code_text):
    """Solution-only worked reference for the open 'Your turn' task above (empty in the student notebook)."""
    if not sol:
        return []
    body = code_text
    # A groq_ready()-guarded reference cell is a LIVE cell (it calls the real model, directly
    # or via a helper like process()/draft()). A model-side error (a rate limit, or gpt-oss
    # emitting a stray built-in tool call -> Groq 400) must never crash Run All. Wrap it so it
    # degrades to a note, exactly like the Build-it "run it for real" cells do.
    if "groq_ready()" in code_text:
        body = ("try:\n" + _indent(code_text, 4) +
                '\nexcept Exception as e:\n    print("(Live model hiccup -- a rate limit or a stray built-in tool call. Re-run in a moment.)", type(e).__name__)')
    return [code("# --- Reference answer (ONE good way to do the 'Your turn' task -- compare with your own) ---\n" + body)]

# Real-LangChain import snippets (dropped into the cells that need them).
TOOL_IMPORT = "from langchain_core.tools import tool"

# The customer-service domain fixtures used across the module.
CS_FIXTURE = '''# The chatbot's context sources: invoices (order 4471 has a DUPLICATE charge) and known issues.
INVOICES = {
    "4471": [{"amount": 50, "date": "Jul 01"}, {"amount": 50, "date": "Jul 01"}],
    "5090": [{"amount": 30, "date": "Jul 02"}],
}
KNOWN_ISSUES = {
    "crash": {"bug": "BUG-231", "fix": "update to v4.2"},
    "login": {"bug": "BUG-118", "fix": "reset your password"},
}'''

# Real specialist tools, reused across the assembly labs.
SPECIALIST_TOOLS = '''@tool
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
    return "no known issue matched"'''

NB = {}
def lab(nn, slug, level, title, mins, summary, concepts):
    def deco(fn):
        NB[nn] = dict(slug=slug, level=level, title=title, mins=mins,
                      summary=summary, concepts=concepts, build=fn)
        return fn
    return deco

# ============================================================ LAB 01
@lab(1, "lab-01-specialist-agents", "Beginner",
     "Specialist Agents (Separation of Concerns)", 20,
     "Build two REAL create_agent specialists -- billing and tech -- each with its own focused tool, and watch one really answer.",
     ["Specialist roles", "create_agent", "Real trace"])
def _l1(sol):
    DEFS = [
      TOOL_IMPORT,
      "from langchain.agents import create_agent",
      "",
      CS_FIXTURE,
      "",
      SPECIALIST_TOOLS,
      "",
      "def build_specialist(tools, role):",
      '    """A specialist = the shared model + its OWN small tool set + a role system prompt."""',
      {"s": '    return create_agent(llm, ___, system_prompt=f"You are the {role} specialist. Use ONLY your own tools; answer in one sentence.")   # TODO: bind this role\'s tools',
       "a": '    return create_agent(llm, tools, system_prompt=f"You are the {role} specialist. Use ONLY your own tools; answer in one sentence.")'},
    ]
    EX = '''# These run offline -- they only inspect the tools (no model call yet):
print("billing tool:", lookup_invoice.name, "->", lookup_invoice.invoke("4471"))
print("tech tool   :", known_issues.name, "->", known_issues.invoke("the app keeps crashing"))
print("build_specialist ready:", callable(build_specialist))'''
    RUN = '''billing_agent = build_specialist([lookup_invoice], "billing")
tech_agent    = build_specialist([known_issues], "tech")
print("billing agent:", type(billing_agent).__name__, "| nodes:", set(billing_agent.nodes) - {"__start__"})

# Run the REAL billing specialist on a billing ticket and read its trace:
result = billing_agent.invoke(
    {"messages": [("user", "I was charged twice for order 4471 -- is that right?")]},
    config={"recursion_limit": 8})
print_trace(result)'''
    return [
      header(1, "Specialist Agents (Separation of Concerns)", "Beginner", 20,
        ["Model a specialist as a role + a small, focused tool set",
         "Build billing and tech agents as real create_agent agents",
         "Run one specialist for real and read the trace"],
        "Specialist roles: separation of concerns"),
      setup(1),
      concept('''A multi-agent system is **decomposition applied to agents** (deck slide 5). The payoff comes from each
agent being **good at one thing**: a **focused role**, a **small tool set**, and **clear boundaries**. A
**billing** specialist handles charges/refunds with billing tools; a **tech** specialist troubleshoots with
tech tools. In LangChain each specialist is a **`create_agent`** &mdash; the SAME building block from Module
6/7, but scoped to one job. Small prompts get followed; small tool sets keep selection accurate; and you can
improve one specialist without touching the other.'''),
      code('''# A specialist = a role + the tools it owns, wrapped as a real create_agent.
print("we will build two real specialists: billing (lookup_invoice) and tech (known_issues)")'''),
      buildmd('''Complete `build_specialist` so it binds **this role's own tools** to the shared `llm` with `create_agent`.
The two `@tool`s are already written for you (they catch their own errors and return a string).'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Build both specialists, then run the **real** billing specialist on a billing ticket. Read the trace: it calls *its own* tool and answers in its lane."),
      code(runguard(RUN)),
      noticemd('''- Each specialist is a real **`CompiledStateGraph`** with **`model`** + **`tools`** nodes &mdash; the same shape as any `create_agent` agent, scoped to one job.
- The trace shows the billing specialist calling **`lookup_invoice`** (its own tool) and nothing else &mdash; that focus is the point of specialisation.
- A tech ticket would engage `tech_agent` instead. Deciding *which* specialist gets a ticket is the **supervisor's** job &mdash; next lab.'''),
      yourturn('''Run the **tech** specialist for real on *"the app keeps crashing on login"* &mdash; read its trace and confirm
it calls `known_issues`, not a billing tool. Then give one specialist the *other's* tool and re-run: **what
good looks like** is that a focused specialist stays in its lane, and blurring the tool sets makes tool
selection worse. Sharpen a docstring if a specialist ignores its tool.'''),
      *sol_answer(sol, r'''if groq_ready():
    tech_agent = build_specialist([known_issues], "tech")   # a focused tech specialist
    result = tech_agent.invoke(
        {"messages": [("user", "the app keeps crashing on login")]},
        config={"recursion_limit": 8})
    print_trace(result)          # it calls known_issues (its own tool), not a billing tool
else:
    print("(add GROQ_API_KEY to .env)")'''),
      footer(1, "Each specialist is a real create_agent with a focused role, a small tool set, and clear boundaries. That separation of concerns is the whole payoff of multi-agent -- next, a supervisor decides who handles what."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-the-supervisor", "Beginner",
     "The Supervisor (Router)", 20,
     "Build a real StateGraph whose supervisor conditional-routes a ticket to real create_agent specialists -- one, several, or a general fallback.",
     ["StateGraph router", "Conditional edges", "Real specialists"])
def _l2(sol):
    DEFS = [
      "from typing import Annotated, TypedDict",
      "from operator import add",
      "from langgraph.graph import StateGraph, START, END",
      TOOL_IMPORT,
      "from langchain.agents import create_agent",
      "",
      CS_FIXTURE,
      "",
      SPECIALIST_TOOLS,
      "",
      "class TeamState(TypedDict):",
      "    message: str",
      "    findings: Annotated[list, add]        # reducer: each specialist APPENDS; nobody overwrites",
      "",
      "def build_specialist(tools, role):",
      '    return create_agent(llm, tools, system_prompt=f"You are the {role} specialist. Use ONLY your own tools; answer in one sentence.")',
      "",
      "def specialist_node(role, tools):",
      '    """Wrap a REAL create_agent specialist as a graph node that appends its finding."""',
      "    agent = build_specialist(tools, role)",
      "    def node(state):",
      '        r = agent.invoke({"messages": [("user", state["message"])]}, config={"recursion_limit": 8})',
      '        text = r["messages"][-1].content',
      '        return {"findings": [f"{role}: {text}"]}',
      "    return node",
      "",
      "def general_node(state):",
      '    return {"findings": ["general: forwarded to a human agent"]}',
      "",
      "def supervise(state):",
      '    """The supervisor: classify the message, name the specialist(s) it needs."""',
      "    m = state[\"message\"].lower()",
      "    hits = []",
      '    if any(k in m for k in ("charg", "refund", "invoice", "billed")): hits.append("billing")',
      '    if any(k in m for k in ("crash", "bug", "login", "broken")): hits.append("tech")',
      {"s": '    return ___   # TODO: the matching specialists (a LIST routes to all of them), or "general" when none match',
       "a": '    return hits or "general"'},
      "",
      "# Workflow (StateGraph) -- a supervisor conditional-routes to specialist node(s):",
      "#",
      "#                    START",
      "#                      |",
      "#                [ supervisor ]        (router: one, several, or general)",
      "#                 /    |    \\",
      "#           billing   tech   general   (each a real create_agent)",
      "#                 \\    |    /",
      "#                     END",
      "def build_team():",
      "    g = StateGraph(TeamState)",
      '    g.add_node("supervisor", lambda s: s)                       # its only job is to route',
      '    g.add_node("billing", specialist_node("billing", [lookup_invoice]))',
      '    g.add_node("tech", specialist_node("tech", [known_issues]))',
      '    g.add_node("general", general_node)',
      '    g.add_edge(START, "supervisor")',
      {"s": '    ___   # TODO: conditional edges out of "supervisor", routed by supervise, to ["billing","tech","general"]',
       "a": '    g.add_conditional_edges("supervisor", supervise, ["billing", "tech", "general"])'},
      '    for n in ("billing", "tech", "general"):',
      '        g.add_edge(n, END)',
      "    return g.compile()",
    ]
    EX = '''# The router itself is pure classification -- run it offline (no model call):
for msg in ["I was charged twice", "the app keeps crashing",
            "charged twice and it crashes", "what are your hours?"]:
    print(f"{msg:34} -> {supervise({'message': msg})}")'''
    RUN = '''team = build_team()
print("graph nodes:", sorted(set(team.get_graph().nodes) - {"__start__", "__end__"}))

# A two-intent ticket: the supervisor routes it to BOTH real specialists, which really answer.
state = team.invoke(
    {"message": "I was charged twice for order 4471 and the app keeps crashing on login.", "findings": []},
    config={"recursion_limit": 12})
print("\\nfindings gathered into shared state:")
for f in state["findings"]:
    print(" -", f)'''
    return [
      header(2, "The Supervisor (Router)", "Beginner", 20,
        ["Express the supervisor as a StateGraph with conditional edges",
         "Route a two-intent ticket to BOTH real create_agent specialists",
         "Fall back to a general node when nothing matches"],
        "The supervisor (router) pattern"),
      setup(2),
      concept('''The **supervisor** is the backbone of a multi-agent system (deck slide 6): it reads the message and decides
**which specialist** handles it. In LangGraph you express this with a **`StateGraph`** and **conditional
edges** &mdash; `add_conditional_edges` sends control from the supervisor node to the specialist node(s) a
routing function names. Returning a **list** routes to **several** specialists at once (a billing *and* a
tech problem); an unmatched message falls back to a **general** node &mdash; the router never drops a ticket.
Each specialist node is a **real `create_agent`**, so the supervisor dispatches to agents that really answer,
and a **reducer** (`Annotated[list, add]`) gathers their findings into shared state.'''),
      code('''# supervisor node -> conditional edges -> real billing/tech specialist nodes (or general)
print("we build a real StateGraph: a supervisor routes each ticket to the specialist(s) it needs")'''),
      buildmd('''Complete `supervise` (return the matching specialists, or `"general"`) and the **conditional edges** in
`build_team`. The specialist nodes are real `create_agent` agents, already wired for you.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Build the graph, then route a real two-intent ticket. The supervisor fans it to **both** real specialists; the reducer collects what each found."),
      code(runguard(RUN)),
      noticemd('''- `add_conditional_edges` turns the supervisor into a real **router**: a two-intent ticket routes to **both** `billing` and `tech`, and the reducer merges their findings &mdash; **no join code needed**, the framework does it.
- Each specialist node is a real `create_agent` (a `CompiledStateGraph`); each calls **its own** tool to answer in its lane.
- An unmatched message routes to `general` &mdash; the safe fallback. In Lab 8.11 this same graph gains synthesis and a refund gate.'''),
      yourturn('''Add a third specialist &mdash; an **`account`** node (keywords `"password"`, `"email"`, `"cancel"`) with its own
`@tool` &mdash; to `build_team` and to `supervise`, then send it a matching ticket. **What good looks like:**
`add_conditional_edges` now reaches `account` too, a two-intent message still fans to both owners, and anything
unmatched still falls back to `general`. (Each live ticket makes a model call per engaged specialist &mdash; run a
couple on the free tier.)'''),
      *sol_answer(sol, r'''if groq_ready():
    @tool
    def account_status(query: str) -> str:
        """Look up an account action such as a password reset or cancellation."""
        return "password reset link sent" if "password" in query.lower() else "account action logged"

    def supervise3(state):
        m = state["message"].lower(); hits = []
        if any(k in m for k in ("charg", "refund", "invoice", "billed")): hits.append("billing")
        if any(k in m for k in ("crash", "bug", "login", "broken")): hits.append("tech")
        if any(k in m for k in ("password", "email", "cancel")): hits.append("account")
        return hits or "general"

    g = StateGraph(TeamState)
    g.add_node("supervisor", lambda s: s)
    g.add_node("billing", specialist_node("billing", [lookup_invoice]))
    g.add_node("tech", specialist_node("tech", [known_issues]))
    g.add_node("account", specialist_node("account", [account_status]))
    g.add_node("general", general_node)
    g.add_edge(START, "supervisor")
    g.add_conditional_edges("supervisor", supervise3, ["billing", "tech", "account", "general"])
    for n in ("billing", "tech", "account", "general"): g.add_edge(n, END)
    team3 = g.compile()

    out = team3.invoke({"message": "please reset my password and refund the duplicate charge on 4471", "findings": []},
                       config={"recursion_limit": 12})
    for f in out["findings"]: print(" -", f)
else:
    print("(add GROQ_API_KEY to .env)")'''),
      footer(2, "The supervisor is a real StateGraph router: add_conditional_edges dispatches one ticket to one, several, or a fallback specialist -- each a real create_agent -- and a reducer gathers their findings. Next: the shared state that reducer writes to."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-shared-state", "Beginner",
     "Shared State & Message Passing", 20,
     "Replace a hand-rolled state class with LangGraph's real state schema: a TypedDict + reducers that MERGE each node's partial update.",
     ["StateGraph state", "Reducers", "Message passing"])
def _l3(sol):
    DEFS = [
      "from typing import Annotated, TypedDict",
      "from operator import add",
      "from langgraph.graph import StateGraph, START, END",
      "",
      "# LangGraph's state IS the shared blackboard. Declare it once as a typed schema;",
      "# a REDUCER says how each node's partial update is merged into it.",
      "class TeamState(TypedDict):",
      "    message: str",
      {"s": '    findings: Annotated[list, ___]   # TODO: the reducer that MERGES successive/parallel updates (hint: operator.add)',
       "a": '    findings: Annotated[list, add]'},
      "    log: Annotated[list, add]",
      "",
      "def billing_node(state):",
      '    """A node reads shared state and returns a PARTIAL update -- the reducer merges it in."""',
      '    return {"findings": ["billing: duplicate charge on 4471"], "log": [("billing", "looked up 4471")]}',
      "",
      "def tech_node(state):",
      {"s": '    return ___   # TODO: return tech\'s finding + a log entry, the same shape as billing_node',
       "a": '    return {"findings": ["tech: matches BUG-231"], "log": [("tech", "matched BUG-231")]}'},
      "",
      "# Workflow (StateGraph) -- each node returns a partial update; the reducer merges it:",
      "#",
      "#   START -> billing -> tech -> END   (both nodes' findings accumulate in shared state)",
      "def build_graph():",
      "    g = StateGraph(TeamState)",
      '    g.add_node("billing", billing_node)',
      '    g.add_node("tech", tech_node)',
      '    g.add_edge(START, "billing")',
      '    g.add_edge("billing", "tech")',
      '    g.add_edge("tech", END)',
      "    return g.compile()",
    ]
    EX = '''# A REAL StateGraph runs offline (no model call): the reducer accumulates both nodes' findings.
app = build_graph()
final = app.invoke({"message": "charged twice and the app crashes", "findings": [], "log": []})
print("findings:", final["findings"])
print("log     :", final["log"])'''
    return [
      header(3, "Shared State & Message Passing", "Beginner", 20,
        ["Declare the team's shared state as a typed StateGraph schema",
         "Use a reducer so each node's partial update MERGES, not overwrites",
         "Run a real graph and watch both findings accumulate"],
        "Message passing & shared state"),
      setup(3),
      concept('''Agents coordinate by sharing state (deck slide 7). In LangGraph the **state is a typed schema** you declare
once &mdash; a `TypedDict` &mdash; and it flows through every node. The key framework idea is the
**reducer**: annotate a field with `Annotated[list, add]` and LangGraph **merges** each node's partial update
instead of overwriting it. So two nodes can each return `{"findings": [...]}` and **both survive** &mdash; no
bespoke state class, no manual dict-merging. Keep the shared context **small &amp; relevant**; the reducer
does the plumbing every LangGraph agent relies on.'''),
      code('''# state = a typed schema; a reducer (Annotated[list, add]) merges each node's update.
print("no hand-rolled class -- the framework's StateGraph + reducers ARE the shared state")'''),
      buildmd('''Complete the **reducer** on `findings` and the `tech_node` update. Then a real `StateGraph` runs
`billing -> tech` and the reducer accumulates both findings &mdash; no API key needed.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- `findings` is `Annotated[list, add]` &mdash; the **reducer**. Each node returns only its *partial* update `{"findings": [...]}`, and LangGraph merges them, so **nobody overwrites anybody**.
- This is the framework doing what a hand-rolled shared-state class used to do &mdash; but it's the real mechanism *every* LangGraph agent uses.
- The `log` (also reduced) preserves order &mdash; the seed of observability (Lab 8.10). Change the reducer and you change how updates combine.'''),
      yourturn('''Add a `status` field with a **custom reducer** &mdash; a function `(old, new) -> merged` that keeps only the
latest value &mdash; and a node that sets it. **What good looks like:** each node still returns a small partial
update, and your reducer decides how the shared state combines them (append vs overwrite) &mdash; the raw material
a synthesiser (Lab 8.9) turns into one reply.'''),
      *sol_answer(sol, r'''def keep_last(old, new):        # a custom reducer: overwrite instead of append
    return new

class TeamState2(TypedDict):
    message: str
    findings: Annotated[list, add]
    status: Annotated[str, keep_last]

def triage2(state): return {"status": "triaged"}
def close2(state):  return {"status": "closed", "findings": ["case closed"]}

g = StateGraph(TeamState2)
g.add_node("triage", triage2); g.add_node("close", close2)
g.add_edge(START, "triage"); g.add_edge("triage", "close"); g.add_edge("close", END)
final = g.compile().invoke({"message": "x", "findings": [], "status": ""})
print("findings (appended):", final["findings"])
print("status  (last only):", final["status"])'''),
      footer(3, "LangGraph's typed state + reducers ARE the shared blackboard -- each node returns a small partial update and the reducer merges it. That replaces any hand-rolled state class, and it's the real mechanism every graph uses."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-sequential-pipeline", "Beginner",
     "Sequential Pipeline of Specialists", 25,
     "Wire a real StateGraph triage -> billing -> tech, each node a stage over shared state, with billing/tech as real create_agent specialists.",
     ["Sequential graph", "Nodes & edges", "Real specialist stage"])
def _l4(sol):
    DEFS = [
      "from typing import Annotated, TypedDict",
      "from operator import add",
      "from langgraph.graph import StateGraph, START, END",
      TOOL_IMPORT,
      "from langchain.agents import create_agent",
      "",
      CS_FIXTURE,
      "",
      SPECIALIST_TOOLS,
      "",
      "class CaseState(TypedDict):",
      "    message: str",
      "    findings: Annotated[list, add]",
      "",
      "def build_specialist(tools, role):",
      '    return create_agent(llm, tools, system_prompt=f"You are the {role} specialist. Use ONLY your own tools; answer in one sentence.")',
      "",
      "def specialist_node(role, tools):",
      '    """Wrap a REAL create_agent specialist as a pipeline stage."""',
      "    agent = build_specialist(tools, role)",
      "    def node(state):",
      '        r = agent.invoke({"messages": [("user", state["message"])]}, config={"recursion_limit": 8})',
      '        return {"findings": [f"{role}: " + r["messages"][-1].content]}',
      "    return node",
      "",
      "def triage_node(state):",
      '    """Stage 1 (deterministic): sort the ticket before the specialists see it."""',
      '    return {"findings": ["triage: billing + tech needed"]}',
      "",
      "# Workflow (StateGraph) -- specialists run in a fixed order, each adding to the case:",
      "#",
      "#   START -> triage -> billing -> tech -> END   (billing/tech are real create_agent nodes)",
      "def build_pipeline():",
      "    g = StateGraph(CaseState)",
      '    g.add_node("triage", triage_node)',
      '    g.add_node("billing", specialist_node("billing", [lookup_invoice]))',
      '    g.add_node("tech", specialist_node("tech", [known_issues]))',
      '    g.add_edge(START, "triage")',
      {"s": '    ___   # TODO: chain the stages in order -- triage -> billing, then billing -> tech',
       "a": '    g.add_edge("triage", "billing")\n    g.add_edge("billing", "tech")'},
      '    g.add_edge("tech", END)',
      "    return g.compile()",
    ]
    EX = '''# Offline sanity (no model call): the deterministic triage stage + the intended order.
print("triage stage:", triage_node({"message": "charged twice, app crashing"}))
print("pipeline order: START -> triage -> billing -> tech -> END")'''
    RUN = '''pipe = build_pipeline()
print("graph nodes:", sorted(set(pipe.get_graph().nodes) - {"__start__", "__end__"}))

final = pipe.invoke(
    {"message": "I was charged twice for order 4471 and the app keeps crashing on login.", "findings": []},
    config={"recursion_limit": 12})
print("\\ncase, stage by stage:")
for f in final["findings"]:
    print("  •", f)'''
    return [
      header(4, "Sequential Pipeline of Specialists", "Beginner", 25,
        ["Wire a StateGraph triage -> billing -> tech with edges",
         "Run billing and tech as real create_agent specialist nodes",
         "See how one edge fixes the order and each stage adds to shared state"],
        "Sequential — a pipeline of specialists"),
      setup(4),
      concept('''The simplest collaboration is the **sequential pipeline** (deck slide 9): specialists run in a **fixed
order**, each adding to the case &mdash; for support that's **triage &rarr; billing &rarr; tech**. In LangGraph
you express order with **edges**: `add_edge("triage", "billing")` makes billing run *after* triage. Each stage
reads shared state and appends its finding, so a later stage sees everything so far. Here `triage` is
deterministic and `billing`/`tech` are **real `create_agent` specialists** &mdash; a real pipeline of agents.
(Trade-off: it's serial, so latency adds up, and an early error flows downstream.)'''),
      code('''# Each stage is a node; edges fix the order. billing/tech are real create_agent specialists.
print("pipeline graph: triage -> billing(real) -> tech(real)")'''),
      buildmd('''Complete the **edges** that chain `triage -> billing -> tech`. The triage node is written; `billing` and
`tech` are real specialist nodes.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Build the graph and run one ticket through it. Each stage adds its finding to shared state in the wired order."),
      code(runguard(RUN)),
      noticemd('''- The `add_edge` chain fixes the **order**: triage, then billing, then tech &mdash; each a real node appending to shared `findings`.
- Swap or insert a stage by rewiring **one edge** &mdash; the framework sequences the team, not a bespoke loop.
- Because it's serial, latency is the **sum** of stages and an early error propagates downstream &mdash; the price of a clean ordered hand-off. Fan-out (Lab 8.5) trades that for parallelism.'''),
      yourturn('''Insert a **`policy`** node between billing and tech (a deterministic stage, e.g. returns
`"policy: refund within 30 days"`) and rewire the two edges around it. **What good looks like:** the new stage runs
in order, every stage's finding is in the final state, and removing it cleanly shortens the graph &mdash; no other
node changes.'''),
      *sol_answer(sol, r'''if groq_ready():
    def policy_node(state):
        return {"findings": ["policy: refund within 30 days"]}
    g = StateGraph(CaseState)
    g.add_node("triage", triage_node)
    g.add_node("billing", specialist_node("billing", [lookup_invoice]))
    g.add_node("policy", policy_node)
    g.add_node("tech", specialist_node("tech", [known_issues]))
    g.add_edge(START, "triage")
    g.add_edge("triage", "billing")
    g.add_edge("billing", "policy")     # NEW stage: one edge in, one edge out
    g.add_edge("policy", "tech")
    g.add_edge("tech", END)
    pipe = g.compile()
    final = pipe.invoke({"message": "charged twice on 4471 and the app keeps crashing", "findings": []},
                        config={"recursion_limit": 12})
    for f in final["findings"]: print("  •", f)
else:
    print("(add GROQ_API_KEY to .env)")'''),
      footer(4, "A sequential pipeline is a StateGraph edge-chain: add_edge fixes the order and each node -- a real specialist -- adds to shared state. Clean ordered hand-offs, at the cost of serial latency. Next: run specialists in parallel."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-parallel-fanout", "Beginner",
     "Parallel Fan-Out", 20,
     "Fan one ticket to several nodes at once with a real StateGraph, merge their findings with a reducer, and survive a branch that fails.",
     ["Parallel fan-out", "Reducer merge", "Fault tolerance"])
def _l5(sol):
    DEFS = [
      "from typing import Annotated, TypedDict",
      "from operator import add",
      "from langgraph.graph import StateGraph, START, END",
      TOOL_IMPORT,
      "from langchain.agents import create_agent",
      "",
      CS_FIXTURE,
      "",
      SPECIALIST_TOOLS,
      "",
      "class FanState(TypedDict):",
      "    message: str",
      {"s": '    findings: Annotated[list, ___]   # TODO: the reducer that MERGES the parallel branches (hint: operator.add)',
       "a": '    findings: Annotated[list, add]'},
      "    summary: str",
      "",
      "def build_specialist(tools, role):",
      '    return create_agent(llm, tools, system_prompt=f"You are the {role} specialist. Use ONLY your own tools; answer in one sentence.")',
      "",
      "def specialist_node(role, tools):",
      "    agent = build_specialist(tools, role)",
      "    def node(state):",
      '        r = agent.invoke({"messages": [("user", state["message"])]}, config={"recursion_limit": 8})',
      '        return {"findings": [f"{role}: " + r["messages"][-1].content]}',
      "    return node",
      "",
      "def policy_node(state):",
      '    """A third branch that is DOWN. It must CATCH its own error -- a raising node aborts the whole graph."""',
      "    try:",
      '        raise RuntimeError("policy service unavailable")',
      "    except Exception as e:",
      {"s": '        return ___   # TODO: return an ERROR-marker finding (include type(e).__name__) so the fan-out survives',
       "a": '        return {"findings": [f"policy: ERROR: {type(e).__name__}"]}'},
      "",
      "def join_node(state):",
      '    """Fan-in: combine whatever the branches produced into one summary."""',
      '    return {"summary": " | ".join(sorted(state["findings"]))}',
      "",
      "# Workflow (StateGraph) -- fan OUT from START to parallel branches, fan IN to join:",
      "#",
      "#              START",
      "#            /   |   \\",
      "#     billing   tech   policy   (run in parallel; policy is DOWN -> ERROR marker)",
      "#            \\   |   /",
      "#           [ join ]            (reducer merged all findings)",
      "#               |",
      "#              END",
      "def build_fanout():",
      "    g = StateGraph(FanState)",
      '    g.add_node("billing", specialist_node("billing", [lookup_invoice]))',
      '    g.add_node("tech", specialist_node("tech", [known_issues]))',
      '    g.add_node("policy", policy_node)',
      '    g.add_node("join", join_node)',
      {"s": '    for n in ("billing", "tech", "policy"):\n        ___   # TODO: fan OUT from START to each branch, and fan each branch IN to "join"',
       "a": '    for n in ("billing", "tech", "policy"):\n        g.add_edge(START, n)\n        g.add_edge(n, "join")'},
      '    g.add_edge("join", END)',
      "    return g.compile()",
    ]
    EX = '''# Offline sanity (no model call): the down branch degrades to a marker, and the fan-out plan.
print("down branch ->", policy_node({"message": "x"}))
print("plan: START -> {billing, tech, policy} in parallel -> join -> END")'''
    RUN = '''fan = build_fanout()
print("graph nodes:", sorted(set(fan.get_graph().nodes) - {"__start__", "__end__"}))

final = fan.invoke(
    {"message": "I was charged twice on 4471 and the app keeps crashing on login.", "findings": [], "summary": ""},
    config={"recursion_limit": 12})
print("\\nfindings (merged by the reducer):")
for f in sorted(final["findings"]):
    print("  •", f)
print("\\njoined summary:", final["summary"][:300])'''
    return [
      header(5, "Parallel Fan-Out", "Beginner", 20,
        ["Fan a ticket from START to several nodes that run in parallel",
         "Merge their findings with a reducer and fan in to a join node",
         "Survive a branch that fails -- fault tolerance in a fan-out"],
        "Parallel — fan-out for coverage & speed"),
      setup(5),
      concept('''In the **parallel** (fan-out) shape several agents work the **same input** at once and their outputs are
combined (deck slide 10). In LangGraph you fan out by adding edges from **`START` to several nodes** &mdash;
they run in **one superstep, concurrently** &mdash; and fan in by pointing them all at a **join** node. The
**reducer** (`Annotated[list, add]`) merges their findings no matter the finish order. Two rules the framework
makes easy: keep each result **tagged** with its agent, and make branches **fault-tolerant** &mdash; a node
that *raises* aborts the whole graph, so a down branch must **catch its own error** and return a marker.'''),
      code('''# Three branches on the SAME ticket: billing/tech are real specialists; policy is DOWN.
print("fan-out: START -> billing, tech, policy (parallel) -> join")'''),
      buildmd('''Complete the **reducer** on `findings`, the down-branch **error marker** in `policy_node`, and the
**fan-out / fan-in edges**. `billing` and `tech` are real specialist nodes.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Build the graph and fan one ticket out. Watch the reducer merge findings from branches that finished in any order, and the down branch degrade to a marker."),
      code(runguard(RUN)),
      noticemd('''- Three branches run from `START` in **one superstep** &mdash; real parallel execution; latency is the **slowest** branch, not the sum.
- The **reducer** merges all three findings regardless of finish order; the down `policy` branch caught its error and returned a **marker**, so the graph survived.
- You now hold **several** findings and need **one** &mdash; the `join` node starts that; vote/synthesis (Labs 8.7&ndash;8.9) finish it.'''),
      yourturn('''Add a fourth branch &mdash; a `billing_review` node that returns a *contradicting* verdict
(e.g. `"billing_review: no refund due"`). **What good looks like:** all four run in parallel, the reducer merges
them (the down branch still degrades to a marker), and you now have a genuine **conflict** to resolve with a vote
(Lab 8.7).'''),
      *sol_answer(sol, r'''if groq_ready():
    def billing_review_node(state):
        return {"findings": ["billing_review: no refund due"]}    # CONTRADICTS the billing branch
    g = StateGraph(FanState)
    g.add_node("billing", specialist_node("billing", [lookup_invoice]))
    g.add_node("tech", specialist_node("tech", [known_issues]))
    g.add_node("billing_review", billing_review_node)
    g.add_node("policy", policy_node)
    g.add_node("join", join_node)
    for n in ("billing", "tech", "billing_review", "policy"):
        g.add_edge(START, n)
        g.add_edge(n, "join")
    g.add_edge("join", END)
    fan = g.compile()
    final = fan.invoke({"message": "charged twice on 4471 and the app keeps crashing", "findings": [], "summary": ""},
                       config={"recursion_limit": 12})
    for f in sorted(final["findings"]): print("  •", f)
else:
    print("(add GROQ_API_KEY to .env)")'''),
      footer(5, "Fan-out is edges from START to several nodes running in one superstep; a reducer merges their findings and a join fans them back in. A down branch that catches its own error keeps the team alive -- and now you have several outputs to converge."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-handoff", "Beginner",
     "Explicit Handoff (Capped)", 25,
     "Hand off between nodes with Command(goto=...) in a real StateGraph, run a real specialist between handoffs, and cap loops with recursion_limit.",
     ["Command handoff", "Recursion cap", "Coordination"])
def _l6(sol):
    DEFS = [
      "from typing import Annotated, TypedDict",
      "from operator import add",
      "from langgraph.graph import StateGraph, START, END",
      "from langgraph.types import Command",
      TOOL_IMPORT,
      "from langchain.agents import create_agent",
      "",
      CS_FIXTURE,
      "",
      SPECIALIST_TOOLS,
      "",
      "class FlowState(TypedDict):",
      "    message: str",
      "    findings: Annotated[list, add]",
      "",
      "def build_specialist(tools, role):",
      '    return create_agent(llm, tools, system_prompt=f"You are the {role} specialist. Use ONLY your own tools; answer in one sentence.")',
      "",
      "def handoff_node(role, tools, goto):",
      '    """A specialist node that does its work, then HANDS OFF to the next node (or END)."""',
      "    agent = build_specialist(tools, role)",
      "    def node(state):",
      '        r = agent.invoke({"messages": [("user", state["message"])]}, config={"recursion_limit": 8})',
      '        return Command(goto=goto, update={"findings": [f"{role}: " + r["messages"][-1].content]})',
      "    return node",
      "",
      "# Workflow (Command handoffs -- routed at RUNTIME, not static edges):",
      "#",
      "#   START -> billing --Command(goto)--> tech --Command(goto)--> END",
      "#   (a runaway ping <-> pong pair is stopped by recursion_limit)",
      "def build_flow():",
      "    g = StateGraph(FlowState)",
      '    g.add_node("billing", handoff_node("billing", [lookup_invoice], goto="tech"))   # billing -> tech',
      {"s": '    g.add_node("tech", handoff_node("tech", [known_issues], goto=___))          # TODO: tech is last -> hand off to END',
       "a": '    g.add_node("tech", handoff_node("tech", [known_issues], goto=END))'},
      '    g.add_edge(START, "billing")',
      "    return g.compile()",
    ]
    EX = '''# The runaway guard is deterministic -- demo it offline (no model call).
# A polite looping pair would hand back and forth forever; recursion_limit stops it.
def ping(state) -> Command: return Command(goto="pong", update={"findings": ["ping"]})
def pong(state) -> Command: return Command(goto="ping", update={"findings": ["pong"]})
loop = StateGraph(FlowState)
loop.add_node("ping", ping); loop.add_node("pong", pong); loop.add_edge(START, "ping")
try:
    loop.compile().invoke({"message": "x", "findings": []}, config={"recursion_limit": 5})
except Exception as e:
    print("looping pair stopped by recursion_limit ->", type(e).__name__)'''
    RUN = '''flow = build_flow()
state = flow.invoke(
    {"message": "I was charged twice for 4471 and the app keeps crashing on login.", "findings": []},
    config={"recursion_limit": 8})
print("handoff chain findings:")
for f in state["findings"]:
    print(" -", f)'''
    return [
      header(6, "Explicit Handoff (Capped)", "Beginner", 25,
        ["Hand off between nodes with Command(goto=...)",
         "Run a real create_agent specialist between handoffs",
         "Cap runaway loops with recursion_limit (the multi-agent max_iterations)"],
        "Failure modes & observability"),
      setup(6),
      concept('''Agents also coordinate by **explicit handoffs**: a node finishes its part and passes control on. LangGraph
expresses this with **`Command`** &mdash; a node returns `Command(goto="tech", update={...})` to both **update
shared state** and **route** to the next node in one move. The danger is a **handoff loop** (A &rarr; B &rarr;
A forever, deck slide 19), so every graph runs under a **`recursion_limit`** &mdash; the multi-agent
`max_iterations`. Here each handoff node runs a **real `create_agent` specialist**, then hands off; a
deliberately looping pair shows the cap stopping a runaway team.'''),
      code('''# Each node returns Command(goto=..., update=...): state update + routing in one step.
print("handoff: billing (real) -> tech (real) -> END, all under a recursion_limit")'''),
      buildmd('''Complete the final handoff: `tech` is the last specialist, so it hands off to **`END`**. Each node runs a real
specialist, then returns a `Command`.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Build the flow and run one ticket: billing does its part and hands off to tech, which hands off to END. Read the findings each node contributed."),
      code(runguard(RUN)),
      noticemd('''- Each node returns `Command(goto=..., update=...)` &mdash; **state update and routing in one step**; `billing` hands to `tech`, `tech` hands to `END`.
- The looping `ping`/`pong` pair is stopped by **`recursion_limit`** (a `GraphRecursionError`) &mdash; the framework's built-in runaway guard, no manual counter.
- Lower the cap and it stops sooner: `recursion_limit` is your dial between *let the team finish* and *never run away*.'''),
      yourturn('''Make `billing` hand off **conditionally** &mdash; return `Command(goto="tech")` for a two-intent ticket but
`Command(goto=END)` for a billing-only one (branch on `state["message"]`). **What good looks like:** a normal ticket
terminates under the cap, while the `ping`/`pong` loop is *always* stopped by `recursion_limit` &mdash; no polite
pair of nodes hands back and forth forever.'''),
      *sol_answer(sol, r'''if groq_ready():
    def billing_cond_node(state):
        agent = build_specialist([lookup_invoice], "billing")
        r = agent.invoke({"messages": [("user", state["message"])]}, config={"recursion_limit": 8})
        m = state["message"].lower()
        nxt = "tech" if any(k in m for k in ("crash", "bug", "login", "broken")) else END
        return Command(goto=nxt, update={"findings": ["billing: " + r["messages"][-1].content]})

    g = StateGraph(FlowState)
    g.add_node("billing", billing_cond_node)
    g.add_node("tech", handoff_node("tech", [known_issues], goto=END))
    g.add_edge(START, "billing")
    flow = g.compile()
    for msg in ["I was charged twice on 4471", "charged twice on 4471 and the app keeps crashing"]:
        out = flow.invoke({"message": msg, "findings": []}, config={"recursion_limit": 8})
        print(f"{msg[:34]:36} -> handed to:", [f.split(':')[0] for f in out["findings"]])
else:
    print("(add GROQ_API_KEY to .env)")'''),
      footer(6, "Command(goto=...) updates state and routes in one step -- the framework's handoff -- and recursion_limit caps runaway loops without a manual counter. Explicit handoffs plus a cap keep a team from becoming a mob. Next: deciding when specialists disagree."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-voting", "Intermediate",
     "Voting & Consensus", 30,
     "Converge several agents' comparable answers by majority vote, and escalate a split decision to a human.",
     ["Voting", "Consensus", "Escalate"])
def _l7(sol):
    DEFS = [
      "from collections import Counter",
      "",
      "def vote(answers):",
      "    counts = Counter(answers)",
      {"s": '    top, n = ___   # TODO: the single most common (answer, count)',
       "a": '    top, n = counts.most_common(1)[0]'},
      "    return top",
      "",
      "def decide(answers, threshold=0.5):",
      "    counts = Counter(answers)",
      "    top, n = counts.most_common(1)[0]",
      {"s": '    if ___:   # TODO: a CLEAR majority -- more than `threshold` of the votes',
       "a": '    if n / len(answers) > threshold:'},
      '        return {"decision": top, "escalate": False}',
      '    return {"decision": None, "escalate": True}   # split -> escalate to a human',
    ]
    EX = '''print("vote  :", vote(["refund", "refund", "deny"]))
print("clear :", decide(["refund", "refund", "deny"]))
print("split :", decide(["refund", "deny", "wait"]))'''
    return [
      header(7, "Voting & Consensus", "Intermediate", 30,
        ["Take the majority answer from several agents",
         "Require a clear majority above a threshold",
         "Escalate a split (no majority) to a human"],
        "Voting & consensus"),
      setup(7),
      concept('''When agents produce **comparable answers**, take a **vote** (deck slide 12). Independent errors cancel: if
each agent is 70% right with uncorrelated mistakes, the **majority** is far better. But a **split vote** is a
*signal* &mdash; escalate to a human rather than force a call. (And beware a **shared blind spot**: agents
that reason alike will confidently agree on the same wrong answer.)'''),
      code('''from collections import Counter
print("three agents voted:", ["refund", "refund", "deny"], "-> majority?")'''),
      buildmd('''Complete `vote` (the majority) and `decide` (escalate unless a clear majority).'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- `vote` returns the **majority** answer; a bare 2/3 majority clears the default `threshold` and is decided.
- A three-way **split** returns `escalate: True` &mdash; the system *knows it doesn't know* and hands off to a human.
- This same `decide` is wired into the capstone (Lab 8.12) to resolve a **disputed refund** &mdash; a real place a split must escalate.'''),
      yourturn('''Raise the `threshold` to `0.66` and re-run over `["refund", "refund", "deny"]`. **What good looks like:** a
2/3 majority now *fails* the stricter bar and escalates &mdash; showing the threshold is your dial between
*trust the majority* and *only act on strong consensus*. Pick the bar to match how costly a wrong call is.'''),
      *sol_answer(sol, r'''print("strict 2/3:", decide(["refund", "refund", "deny"], threshold=0.66))   # fails the bar -> escalate
print("unanimous :", decide(["refund", "refund", "refund"], threshold=0.66)) # clears it -> decided'''),
      footer(7, "Voting converges comparable answers, and a split vote is information -- escalate, don't force it. Use it for checkable answers; watch for a shared blind spot that makes agents agree on the same mistake."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-critique-debate", "Intermediate",
     "Critique & Debate", 30,
     "Add an independent critic that reviews an answer; loop propose -> critique -> revise, capped.",
     ["Critique", "Reflection", "Capped loop"])
def _l8(sol):
    DEFS = [
      "def critique_loop(proposer, critic, max_rounds=3):",
      "    answer = None",
      "    for r in range(max_rounds):",
      "        answer = proposer(answer)",
      {"s": '        verdict = ___   # TODO: ask the critic to review this answer',
       "a": '        verdict = critic(answer)'},
      {"s": '        if ___:   # TODO: the critic approved',
       "a": '        if verdict == "approve":'},
      '            return {"answer": answer, "rounds": r + 1, "approved": True}',
      '    return {"answer": answer, "rounds": max_rounds, "approved": False}',
    ]
    EX = '''print("approved:", critique_loop(proposer, critic))
print("capped  :", critique_loop(proposer, critic_never))'''
    return [
      header(8, "Critique & Debate", "Intermediate", 30,
        ["Run a propose -> critique -> revise loop",
         "Let an independent critic gate on quality",
         "Cap the loop so two agents can't argue forever"],
        "Critique & debate"),
      setup(8),
      concept('''Instead of averaging, **stress-test** one answer (deck slide 13): one agent **proposes**, an independent
**critic** tries to find what's wrong, the proposer **revises** &mdash; repeat until the critic approves or a
**cap** is hit. Generating and evaluating are **different skills**, so a separate skeptic catches the
author's blind spots (just like code review). Always **cap** the loop.'''),
      code('''# proposer improves its draft each round; critic approves only a GROUNDED answer.
def proposer(prev):
    if prev is None: return "draft v1"
    if "v1" in prev: return "draft v2 grounded"
    return prev
def critic(answer):
    return "approve" if "grounded" in answer else "revise"
def critic_never(answer):
    return "revise"
print("proposer & critics ready")'''),
      buildmd('''Complete `critique_loop`: get the critic's verdict and stop when it approves (or at the cap).'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- The loop approves in **round 2** &mdash; the proposer's revision earns the critic's OK, and the result carries the `"grounded"` answer.
- A **never-satisfied** critic hits the **cap** and returns `approved: False` &mdash; the loop can argue, but not forever.
- The critic **gates** the outcome: quality comes from the separate skeptic, not from the proposer marking its own work.'''),
      yourturn('''Write a stricter `critic` that also requires the word *"cited"*, and a `proposer` that only adds it on round 3.
**What good looks like:** approval now takes an extra round (and a higher `max_rounds` to reach it), proving the
critic &mdash; not the proposer &mdash; sets the quality bar. Drop the cap too low and a good answer never
lands: tune the cap to the task.'''),
      *sol_answer(sol, r'''def proposer_cite(prev):
    if prev is None: return "draft v1"
    if "v1" in prev: return "draft v2 grounded"
    return "draft v3 grounded cited"                      # only adds "cited" on the 3rd round
def critic_cite(answer):
    return "approve" if ("grounded" in answer and "cited" in answer) else "revise"
print("reaches cited:", critique_loop(proposer_cite, critic_cite, max_rounds=4))  # approves in round 3
print("cap too low  :", critique_loop(proposer_cite, critic_cite, max_rounds=2))  # good answer never lands'''),
      footer(8, "A separate critic raises quality because evaluating is a different skill from generating -- and the cap keeps the debate from running forever. Use it when being right beats being fast."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-synthesis", "Intermediate",
     "Synthesis: One Coherent Reply", 30,
     "Combine several agents' findings into one grounded, coherent reply -- resolving, not concatenating.",
     ["Synthesis", "Grounded", "One voice"])
def _l9(sol):
    DEFS = [
      "def synthesize(findings):",
      '    # combine the findings, in a stable order, into ONE reply',
      {"s": '    ordered = ___   # TODO: each finding\'s value, in sorted-key order',
       "a": '    ordered = [findings[k] for k in sorted(findings)]'},
      '    return "Here is what we found: " + "; ".join(ordered) + "."',
      "",
      "def is_grounded(reply, findings):",
      '    # grounded = every finding actually appears in the reply (nothing dropped or invented)',
      {"s": '    return ___   # TODO: True if every finding value is in the reply',
       "a": '    return all(v in reply for v in findings.values())'},
      "",
      "def has_conflict(findings):",
      '    joined = " ".join(findings.values()).lower()',
      '    return "refund" in joined and "no refund" in joined',
    ]
    EX = '''F = {"billing": "duplicate charge -> refund", "tech": "BUG-231 -> update to v4.2"}
reply = synthesize(F)
print(reply)
print("grounded?", is_grounded(reply, F))
print("conflict?", has_conflict({"a": "issue refund", "b": "no refund allowed"}))'''
    return [
      header(9, "Synthesis: One Coherent Reply", "Intermediate", 30,
        ["Combine multiple agents' findings into one reply",
         "Keep it grounded -- built only from the findings",
         "Detect a conflict instead of pasting contradictions"],
        "Synthesis — combine the parts"),
      setup(9),
      concept('''Voting is for comparable **whole answers**; **synthesis** is for complementary **parts** (deck slide 14).
When the billing agent found the refund status and the tech agent diagnosed the bug, a **synthesiser** weaves
both into one coherent reply. Keys: **resolve conflicts** (don't just concatenate contradictions), **stay
grounded** (build only from what agents found), and **own one voice**.'''),
      code('''# findings: a dict of agent -> what it found.
print("synthesise:", {"billing": "duplicate charge -> refund", "tech": "BUG-231 -> update to v4.2"})'''),
      buildmd('''Complete `synthesize` (combine, stable order) and `is_grounded` (every finding must appear).'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- The reply is **one string** in a **stable (sorted) order**, and `is_grounded` confirms **every** finding survived into it &mdash; nothing dropped or invented.
- A reply missing a finding fails `is_grounded` &mdash; the same grounding check the assembled chatbot uses so it never invents facts.
- `has_conflict` catches a *"refund"* vs *"no refund"* contradiction &mdash; a cue to **vote** (Lab 8.7) instead of pasting both.'''),
      yourturn('''Extend `synthesize` to **prefix each finding with its agent name** (e.g. `"billing: ..."`). **What good looks
like:** the reply still passes `is_grounded` (the finding text is intact), and now a reader can see *which*
specialist said *what* &mdash; the one-voice reply that the customer-service chatbot (Lab 8.11) will return.'''),
      *sol_answer(sol, r'''def synthesize_tagged(findings):
    ordered = [f"{k}: {findings[k]}" for k in sorted(findings)]   # prefix each with its agent name
    return "Here is what we found: " + "; ".join(ordered) + "."

F = {"billing": "duplicate charge -> refund", "tech": "BUG-231 -> update to v4.2"}
reply = synthesize_tagged(F)
print(reply)
print("grounded?", is_grounded(reply, F))    # finding text intact -> still grounded'''),
      footer(9, "Synthesis reconciles complementary parts into one grounded reply in a single voice -- the last step before the customer sees an answer. Vote to converge, critique to harden, synthesise to combine."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-observability", "Advanced",
     "Observability for a Team", 40,
     "Trace every agent, message and handoff; count calls per agent; and detect a runaway handoff loop.",
     ["Observability", "Agent trace", "Loop detection"])
def _l10(sol):
    DEFS = [
      "from collections import Counter",
      "",
      "class AgentTrace:",
      "    def __init__(self):",
      "        self.events = []",
      "    def log(self, agent, action, detail):",
      {"s": '        ___   # TODO: append (agent, action, detail) to self.events',
       "a": '        self.events.append((agent, action, detail))'},
      "    def agents_involved(self):",
      {"s": '        return ___   # TODO: the agent of each event, in order',
       "a": '        return [a for a, _, _ in self.events]'},
      "    def calls_per_agent(self):",
      "        return Counter(a for a, _, _ in self.events)",
      "",
      "def detect_loop(path, limit=2):",
      '    # a runaway loop: some agent appears MORE than `limit` times (a normal 2x back-and-forth is fine)',
      {"s": '    return ___   # TODO: True if any agent count in path exceeds limit',
       "a": '    return any(c > limit for c in Counter(path).values())'},
    ]
    EX = '''tr = AgentTrace()
tr.log("supervisor", "route", "billing+tech")
tr.log("billing", "tool", "lookup_invoice")
tr.log("tech", "tool", "known_issues")
print("involved :", tr.agents_involved())
print("calls    :", dict(tr.calls_per_agent()))
print("loop?    :", detect_loop(["a", "b", "a", "b", "a", "b"]))
print("healthy? :", detect_loop(["supervisor", "billing", "tech"]))'''
    LIVE = '''# The SAME idea, but reading a REAL create_agent trace: build one specialist, run it,
# and log every tool call the model actually made. (Lab 8.1's specialist, observed.)
from langchain_core.tools import tool
from langchain.agents import create_agent
INVOICES = {"4471": [{"amount": 50, "date": "Jul 01"}, {"amount": 50, "date": "Jul 01"}]}

@tool
def lookup_invoice(order_id: str) -> str:
    """Look up the charges on an order by its id. Use for billing / charge questions."""
    return str(INVOICES.get(order_id.strip(), [])) or "no charges"

billing_agent = create_agent(llm, [lookup_invoice],
    system_prompt="You are the billing specialist. Use ONLY your own tools; answer in one sentence.")
result = billing_agent.invoke(
    {"messages": [("user", "Was I double-charged on order 4471?")]}, config={"recursion_limit": 8})

tr = AgentTrace()
for m in result["messages"]:
    for tc in (getattr(m, "tool_calls", None) or []):
        tr.log("billing", "tool_call", tc["name"])         # log the REAL tool calls from the trace
print("real agent events :", tr.events)
print("calls per agent   :", dict(tr.calls_per_agent()))
print("runaway loop?     :", detect_loop(tr.agents_involved()))'''
    return [
      header(10, "Observability for a Team", "Advanced", 40,
        ["Log every agent action into an auditable trace",
         "Count calls per agent to find the busy/faulty one",
         "Read a REAL agent trace and detect a runaway handoff loop"],
        "Failure modes & observability"),
      setup(10),
      concept('''A multi-agent system fails in new ways &mdash; **handoff loops**, agents **talking past** each other,
**cost blow-ups**, and **lost accountability** (deck slide 19). The defence is **observability**: log every
agent, message, handoff and decision so you can **replay** the conversation, find the **faulty agent**, and
watch **cost**. **LangSmith / Langfuse** do this for real graphs; here you build the offline version, then
point it at a **real** agent trace.'''),
      code('''from collections import Counter
print("we log (agent, action, detail) events and watch for loops")'''),
      buildmd('''Complete the `AgentTrace` (log + read back) and `detect_loop` (a runaway handoff).'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Now feed your `AgentTrace` a **real** `create_agent` run: build one specialist, invoke it, and log every tool call it actually made. Your loop-detector reads a real path."),
      code(runguard(LIVE)),
      noticemd('''- `agents_involved` and `calls_per_agent` read straight off the log &mdash; your #1 way to spot the busy or faulty agent.
- `detect_loop` allows a normal 2x back-and-forth but flags anything hotter &mdash; a runaway team caught before it burns tokens.
- The **live** cell logged the *real* tool calls from a real trace &mdash; exactly what LangSmith / Langfuse capture, in miniature.'''),
      yourturn('''Extend `AgentTrace` with a `cost` field per event (e.g. a token estimate) and a `total_cost()` method, then log a
few events. **What good looks like:** you can now answer *"which agent cost the most?"* from the trace &mdash; the
accountability a multi-agent system needs. Feed `detect_loop` a hand-built looping path to confirm it fires.'''),
      *sol_answer(sol, r'''class CostTrace(AgentTrace):
    def log(self, agent, action, detail, cost=0):
        self.events.append((agent, action, detail, cost))     # add a per-event cost
    def agents_involved(self):
        return [e[0] for e in self.events]
    def total_cost(self):
        return sum(e[3] for e in self.events)

ct = CostTrace()
ct.log("supervisor", "route", "billing+tech", cost=5)
ct.log("billing", "tool", "lookup_invoice", cost=12)
ct.log("tech", "tool", "known_issues", cost=9)
print("total cost:", ct.total_cost(), "| involved:", ct.agents_involved())
print("loop?     :", detect_loop(["a", "b", "a", "b", "a"]))   # hand-built runaway -> True'''),
      footer(10, "Log every agent, message, handoff and decision so you can replay the conversation, find the faulty agent and watch cost. A multi-agent system is only as trustworthy as it is observable."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-assemble-chatbot", "Advanced",
     "Assemble the Customer-Service Chatbot", 35,
     "Route a real ticket to REAL billing & tech create_agent specialists, synthesise one reply, and gate the refund on a human.",
     ["Multi-agent", "Real specialists", "needs_approval"])
def _l11(sol):
    DEFS = [
      TOOL_IMPORT,
      "from langchain.agents import create_agent",
      "",
      CS_FIXTURE,
      "",
      SPECIALIST_TOOLS,
      "",
      "def build_specialist(tools, role):",
      {"s": '    return create_agent(llm, ___, system_prompt=f"You are the {role} specialist. Use ONLY your own tools; answer in one sentence.")   # TODO: bind this role\'s tools',
       "a": '    return create_agent(llm, tools, system_prompt=f"You are the {role} specialist. Use ONLY your own tools; answer in one sentence.")'},
      "",
      "def route(message):",
      "    m = message.lower()",
      "    engaged = []",
      '    if any(k in m for k in ("charg", "refund", "invoice", "billed")):',
      '        engaged.append("billing")',
      '    if any(k in m for k in ("crash", "bug", "login", "broken")):',
      {"s": '        engaged.append(___)   # TODO: the tech specialist',
       "a": '        engaged.append("tech")'},
      "    return engaged or [\"general\"]",
      "",
      "def refund_intent(message):",
      '    return any(k in message.lower() for k in ("refund", "charged twice", "duplicate", "dispute"))',
      "",
      "def synthesize(findings):",
      '    return " ".join(f"[{k}] {findings[k]}" for k in sorted(findings)) if findings else "forwarded to a human agent"',
      "",
      "def specialist_reply(agent, message):",
      '    """Invoke a REAL specialist and return its final answer text."""',
      '    result = agent.invoke({"messages": [("user", message)]}, config={"recursion_limit": 8})',
      '    return result["messages"][-1].content',
      "",
      "def assemble_reply(findings, involved, message):",
      '    reply = synthesize(findings)',
      '    # a refund is irreversible -> a human approves it (draft-not-send, at the team level)',
      {"s": '    needs_human = ___   # TODO: True when billing is involved AND the message is a refund intent',
       "a": '    needs_human = "billing" in involved and refund_intent(message)'},
      '    return {"reply": reply, "status": "needs_approval" if needs_human else "auto_ok", "agents": sorted(findings) or involved}',
    ]
    EX = '''# These run offline (no model call): routing + the refund gate are rule-based.
print("route (two-intent):", route("charged twice for 4471 and the app keeps crashing"))
print("route (hours)     :", route("what are your hours?"))
print("refund intent?    :", refund_intent("please refund my invoice"))
demo = assemble_reply({"billing": "duplicate charge -> refund warranted", "tech": "BUG-231"},
                      ["billing", "tech"], "please refund the duplicate charge")
print("assembled status  :", demo["status"], "| agents:", demo["agents"])'''
    RUN = '''# Build the REAL specialists and route a real two-intent ticket to them.
billing_agent = build_specialist([lookup_invoice], "billing")
tech_agent    = build_specialist([known_issues], "tech")
AGENTS = {"billing": billing_agent, "tech": tech_agent}

msg = "I was charged twice for order 4471 and the app keeps crashing on login."
involved = route(msg)
print("supervisor routed to:", involved)

# Show ONE real specialist trace, then collect every engaged specialist's finding:
print("\\n-- billing specialist trace --")
print_trace(billing_agent.invoke({"messages": [("user", msg)]}, config={"recursion_limit": 8}))

findings = {name: specialist_reply(AGENTS[name], msg) for name in involved if name in AGENTS}
out = assemble_reply(findings, involved, msg)
print("\\nagents :", out["agents"])
print("status :", out["status"], "(refund is irreversible -> a human approves)")
print("reply  :", out["reply"])'''
    return [
      header(11, "Assemble the Customer-Service Chatbot", "Advanced", 35,
        ["Build billing & tech specialists as real create_agent agents",
         "Route a real ticket to only the matching specialists, who really answer",
         "Synthesise one reply, flagged needs_approval for the refund"],
        "The multi-agent customer-service chatbot"),
      setup(11),
      concept('''Now assemble the chatbot from your Module 6&ndash;8 pieces (deck slides 15&ndash;17): each specialist is a
**real `create_agent`** with its **own** small tool set. The **supervisor** (`route`) sends the ticket to
only the matching specialists; each **really answers** over its tool; a **synthesiser** weaves their findings
into one reply. Because a refund is **irreversible**, the reply is flagged **`needs_approval`** &mdash;
draft-not-send, now at the *team* level. The routing, synthesis and refund gate are rule-based (they run
offline); the specialists run for real against Groq.'''),
      code('''# The pieces: two @tools (billing/tech), a router, a synthesiser, and a refund gate.
print("assembling: supervisor -> {billing, tech} specialists -> synthesise -> human-gate the refund")'''),
      buildmd('''Complete `build_specialist` (bind each role's tools), `route` (add the tech specialist), and
`assemble_reply` (flag the refund `needs_approval`). The tools and `synthesize` are written for you.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Build the real specialists, route a real two-intent ticket, show one specialist's **real trace**, then collect both findings, synthesise, and gate the refund."),
      code(runguard(RUN)),
      noticemd('''- The supervisor routed the two-intent ticket to **both** `billing` and `tech`; each is a real `CompiledStateGraph` that **called its own tool** (see the trace).
- The findings are **synthesised into one reply** tagged by specialist &mdash; one voice, grounded in what each agent actually found.
- Because billing + a refund intent are present, the reply is **`needs_approval`** &mdash; the irreversible action waits for a human. That is the team-level draft-not-send gate.'''),
      yourturn('''Send a **pure tech** ticket (*"the app keeps crashing on login"*) through the same flow. **What good looks like:**
only `tech` is engaged, its trace calls `known_issues`, the reply is `auto_ok` (no refund, no human needed).
Then send a refund ticket and confirm it flips to `needs_approval`. (Each live ticket makes a few model calls &mdash;
run a couple, not the whole world, on the free tier.)'''),
      *sol_answer(sol, r'''if groq_ready():
    AGENTS = {"billing": build_specialist([lookup_invoice], "billing"),
              "tech":    build_specialist([known_issues], "tech")}
    for msg in ["the app keeps crashing on login",              # pure tech -> auto_ok
                "please refund the duplicate charge on 4471"]:   # refund -> needs_approval
        involved = route(msg)
        findings = {n: specialist_reply(AGENTS[n], msg) for n in involved if n in AGENTS}
        out = assemble_reply(findings, involved, msg)
        print(msg[:36], "->", out["status"], "| agents:", out["agents"])
else:
    print("(add GROQ_API_KEY to .env)")'''),
      footer(11, "A TEAM: a supervisor routes, real specialists (each a create_agent with its own tools) gather, a synthesiser makes one reply -- and the refund waits for a human. Next: run it over a whole suite."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-customer-service-chatbot", "Advanced",
     "Capstone: The Multi-Agent Chatbot", 45,
     "Run the full chatbot -- route to REAL specialists, vote on a conflict, synthesise, gate every refund -- and read a real trace.",
     ["End-to-end team", "Real specialists", "Vote + human approval"])
def _l12(sol):
    DEFS = [
      TOOL_IMPORT,
      "from langchain.agents import create_agent",
      "from collections import Counter",
      "",
      CS_FIXTURE,
      "",
      SPECIALIST_TOOLS,
      "",
      "def build_specialist(tools, role):",
      {"s": '    return create_agent(llm, ___, system_prompt=f"You are the {role} specialist. Use ONLY your own tools; answer in one sentence.")   # TODO: bind this role\'s tools',
       "a": '    return create_agent(llm, tools, system_prompt=f"You are the {role} specialist. Use ONLY your own tools; answer in one sentence.")'},
      "",
      "def route(message):",
      "    m = message.lower()",
      '    kws = {"billing": ("charg", "refund", "invoice", "billed"), "tech": ("crash", "bug", "login", "broken")}',
      "    hits = [name for name, ks in kws.items() if any(k in m for k in ks)]",
      '    return hits if hits else ["general"]',
      "",
      "def refund_intent(message):",
      '    return any(k in message.lower() for k in ("refund", "charged twice", "duplicate", "dispute"))',
      "def is_dispute(message):",
      '    return "dispute" in message.lower()',
      "def decide(verdicts, threshold=0.5):                    # Lab 8.7's vote",
      "    top, n = Counter(verdicts).most_common(1)[0]",
      {"s": '    if ___:   # TODO: a CLEAR majority -- more than `threshold` of the verdicts',
       "a": '    if n / len(verdicts) > threshold:'},
      '        return {"decision": top, "escalate": False}',
      '    return {"decision": None, "escalate": True}',
      "",
      "def synthesize(findings):",
      '    return " ".join(f"[{k}] {findings[k]}" for k in sorted(findings)) if findings else "forwarded to a human agent"',
      "",
      "def specialist_reply(agent, message):",
      '    result = agent.invoke({"messages": [("user", message)]}, config={"recursion_limit": 8})',
      '    return result["messages"][-1].content',
      "",
      "def process(message, agents):",
      '    """Route -> run each REAL specialist -> vote on a dispute -> synthesise -> gate the refund."""',
      "    involved = route(message)",
      {"s": '    findings = ___   # TODO: {name: specialist_reply(agents[name], message)} for each involved specialist that has an agent',
       "a": '    findings = {name: specialist_reply(agents[name], message) for name in involved if name in agents}'},
      "    conflict = None",
      '    if "billing" in involved and is_dispute(message):',
      '        conflict = decide(["refund", "deny"])          # a disputed charge -> reviewers SPLIT',
      '        findings["billing"] = "reviewers split -> escalate to a human" if conflict["escalate"] else findings.get("billing", "")',
      {"s": '    needs_human = ___   # TODO: True if billing is involved AND a refund intent, OR the conflict vote escalated',
       "a": '    needs_human = ("billing" in involved and refund_intent(message)) or bool(conflict and conflict["escalate"])'},
      '    return {"agents": sorted(findings) or involved,',
      '            "reply": synthesize(findings),',
      '            "status": "needs_approval" if needs_human else "auto_ok",',
      '            "conflict": bool(conflict)}',
    ]
    EX = '''# Offline sanity of the deterministic team logic (no model call yet):
print("route two-intent :", route("charged twice and the app keeps crashing"))
print("route hours      :", route("what are your hours?"))
print("dispute vote     :", decide(["refund", "deny"]))       # split -> escalate
print("refund intent?   :", refund_intent("please refund me"))'''
    RUN = '''# Build the REAL specialists ONCE, then process ONE representative ticket end to end.
AGENTS = {"billing": build_specialist([lookup_invoice], "billing"),
          "tech":    build_specialist([known_issues], "tech")}

msg = "I was charged twice for order 4471 and the app keeps crashing on login."
print("route:", route(msg))
print("\\n-- one real specialist trace (billing) --")
print_trace(AGENTS["billing"].invoke({"messages": [("user", msg)]}, config={"recursion_limit": 8}))

out = process(msg, AGENTS)          # runs the engaged REAL specialists, then applies vote/synthesis/gate
print("\\nagents  :", out["agents"])
print("status  :", out["status"], "| conflict:", out["conflict"])
print("reply   :", out["reply"][:300])'''
    return [
      header(12, "Capstone: The Multi-Agent Chatbot", "Advanced", 45,
        ["Route a real ticket to real create_agent specialists that answer",
         "Run a VOTE when a charge is disputed; gate any refund on a human",
         "Assemble it into one process() and read a real end-to-end trace"],
        "The multi-agent customer-service chatbot"),
      setup(12),
      concept('''Capstone: the **multi-agent customer-service chatbot** (the client's Lab 4.2), end to end. A **supervisor**
routes each message to the matching **specialists** (the **real `create_agent`** agents from Lab 8.1/8.11);
each **really answers** over its own tool. When a charge is **disputed**, you don't paste a contradiction &mdash;
you run the **vote** from Lab 8.7 and **escalate a split** to a human. A **synthesiser** composes one reply,
and anything **irreversible** (a refund) is flagged **`needs_approval`** &mdash; never auto-done. Routing, the
vote, synthesis and the refund gate are rule-based (offline); the specialists run for real against Groq.'''),
      code('''# One process() ties it all together: route -> real specialists -> vote-on-dispute -> synthesise -> gate.
print("capstone flow: supervisor -> real specialists -> vote (on dispute) -> synthesise -> human-gate refund")'''),
      buildmd('''Complete `build_specialist` (bind the tools), `decide` (the clear-majority test), `process` (collect each
engaged specialist's real finding), and the `needs_human` refund gate.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Build the real specialists once, then run **`process()`** on one representative two-intent ticket. It routes, invokes the real specialists, synthesises, and gates the refund &mdash; read the real trace."),
      code(runguard(RUN)),
      noticemd('''- `process()` routed to **both** real specialists, each of which **called its own tool** (see the trace), then synthesised **one** grounded reply.
- The ticket carries a refund intent, so `status` is **`needs_approval`** &mdash; the irreversible action waits for a human, exactly as the deck demands.
- Swap in a message containing *"dispute"* and the **vote** fires: a split escalates &mdash; the team knows when *not* to decide alone.'''),
      yourturn('''Build a **suite** of tickets (a pure-tech one, a general *"what are your hours?"*, a *"dispute the charge on 4471"*)
and run `process()` over each &mdash; then check every outcome: only-tech is `auto_ok`, general falls back, and the
dispute both `conflict` and escalates to `needs_approval`. **What good looks like:** every ticket is routed to the
right specialists, refunds and splits are gated on a human, and no reply invents a fact its specialists didn't
find. (Each two-intent ticket makes several live calls &mdash; run the suite a few tickets at a time on the free tier.)'''),
      *sol_answer(sol, r'''if groq_ready():
    AGENTS = {"billing": build_specialist([lookup_invoice], "billing"),
              "tech":    build_specialist([known_issues], "tech")}
    suite = ["the app keeps crashing on login",         # only tech -> auto_ok
             "what are your hours?",                     # general fallback
             "I want to dispute the charge on 4471"]     # dispute -> vote splits -> needs_approval
    for msg in suite:
        out = process(msg, AGENTS)
        print(f"{msg[:34]:36} -> status={out['status']:14} conflict={out['conflict']} agents={out['agents']}")
else:
    print("(add GROQ_API_KEY to .env)")'''),
      footer(12, "You built a multi-agent customer-service chatbot end to end -- real specialists coordinated by a supervisor, a vote when they conflict, findings synthesised into one reply, refunds gated on a human. That completes Day 4. Next: Day 5 -- agents in the real world, responsibly."),
    ]

# ============================================================ WRITE NOTEBOOKS
def notebook(cells):
    for i, c in enumerate(cells):
        c["id"] = f"cell{i:02d}"
    return {"cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                         "language_info": {"name": "python", "version": "3.x"}},
            "nbformat": 4, "nbformat_minor": 5}

for nn in sorted(NB):
    info = NB[nn]
    fname = f"{info['slug']}.ipynb"
    with open(os.path.join(OUT_DIR, fname), "w") as f:
        json.dump(notebook(info["build"](False)), f, indent=1, ensure_ascii=False)
    if SOL_DIR:
        banner = md(f'''> ## SOLUTION / ANSWER KEY &mdash; Lab 8.{nn}
> This is the **completed** notebook (all `___` blanks filled). For the student version, open
> [`../{info['slug']}.ipynb`](../{info['slug']}.ipynb). Trainer use &mdash; or self-check after you've tried it yourself.''')
        with open(os.path.join(SOL_DIR, fname), "w") as f:
            json.dump(notebook([banner] + info["build"](True)), f, indent=1, ensure_ascii=False)

print(f"Wrote {len(NB)} notebooks to {OUT_DIR}" + (f" and solutions to {SOL_DIR}" if SOL_DIR else ""))

with open(os.path.join(_HERE, "_meta.json"), "w") as f:
    json.dump({str(nn): {k: NB[nn][k] for k in ("slug","level","title","mins","summary","concepts")}
               for nn in NB}, f, indent=1)
