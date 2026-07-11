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

WORK = "/tmp/biaa-lab-08-{nn:02d}"
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
      footer(1, "Each specialist is a real create_agent with a focused role, a small tool set, and clear boundaries. That separation of concerns is the whole payoff of multi-agent -- next, a supervisor decides who handles what."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-the-supervisor", "Beginner",
     "The Supervisor (Router)", 20,
     "Build a supervisor that classifies a message and routes it to the right specialist -- or to several.",
     ["Supervisor", "Routing", "Multi-intent"])
def _l2(sol):
    DEFS = [
      "class Specialist:",
      "    def __init__(self, name, keywords): self.name = name; self.keywords = keywords",
      "    def in_scope(self, message):",
      "        return any(k in message.lower() for k in self.keywords)",
      "",
      'billing = Specialist("billing", ["charge", "refund", "invoice", "billed"])',
      'tech    = Specialist("tech", ["crash", "error", "login", "bug", "broken"])',
      "SPECIALISTS = [billing, tech]",
      "",
      "def route(message, specialists):",
      {"s": '    hits = ___   # TODO: the .name of every specialist whose scope matches the message',
       "a": '    hits = [s.name for s in specialists if s.in_scope(message)]'},
      {"s": '    return hits if hits else ___   # TODO: fall back to ["general"] when nothing matches',
       "a": '    return hits if hits else ["general"]'},
    ]
    EX = '''print("charge msg :", route("I was charged twice", SPECIALISTS))
print("crash msg  :", route("the app keeps crashing", SPECIALISTS))
print("both       :", route("charged twice and the app crashes", SPECIALISTS))
print("unknown    :", route("what are your hours?", SPECIALISTS))'''
    return [
      header(2, "The Supervisor (Router)", "Beginner", 20,
        ["Route a message to the specialist(s) whose scope it matches",
         "Handle a message with TWO intents -> route to both",
         "Fall back to a general agent when nothing matches"],
        "The supervisor (router) pattern"),
      setup(2),
      concept('''The **supervisor** (router) is the backbone of a multi-agent system (deck slide 6): it receives the
message, decides **which specialist** should handle it, and routes there. It is exactly Module 7's **route**
pattern &mdash; but the destinations are **agents**, not code branches. A message can carry **two intents**
(a billing problem *and* a crash), so routing returns a **list**; and an unmatched message falls back to a
**general** agent (the escape hatch). This classification is genuine rule-based plumbing &mdash; no LLM
needed to decide who owns a ticket.'''),
      code('''# A tiny Specialist just knows its name + the keywords that put a message in its scope.
print("we will route to whichever specialists a message is in scope for -- possibly several")'''),
      buildmd('''Complete `route`: collect every specialist whose scope matches, and fall back to `["general"]`.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- A billing message routes to `["billing"]`, a crash to `["tech"]`, and a **two-intent** message to **both** &mdash; routing returns a *list*.
- An unmatched message falls back to `["general"]` &mdash; the router never drops a ticket on the floor.
- In Lab 8.11 these names become the keys into a dict of **real** specialist agents; here you just decide *who*.'''),
      yourturn('''Add a **third** specialist (e.g. `account` with keywords like `"password"`, `"email"`, `"cancel"`) to
`SPECIALISTS` and re-run over a message that hits it. **What good looks like:** the router now sends
account-related tickets to `account`, two-intent messages reach both owners, and anything unmatched still
falls back to `general`. That is the supervisor whose destinations you'll wire to real agents later.'''),
      footer(2, "The supervisor is Module 7's route pattern -- but routing to AGENTS. Returning a list lets one message reach several specialists; the general fallback keeps it safe. Next: how those agents share what they find."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-shared-state", "Beginner",
     "Shared State & Message Passing", 20,
     "Give the team a shared state object where each agent records its finding and the running log is kept.",
     ["Shared state", "Message passing", "Findings"])
def _l3(sol):
    DEFS = [
      "class SharedState:",
      "    def __init__(self, message):",
      "        self.message = message",
      "        self.findings = {}",
      "        self.log = []",
      "    def record(self, agent, finding):",
      {"s": '        ___   # TODO: store the finding under self.findings[agent]',
       "a": '        self.findings[agent] = finding'},
      "        self.log.append((agent, finding))",
      "    def context(self):",
      '        # small & relevant: just the findings gathered so far',
      {"s": '        return ___   # TODO: the findings dict',
       "a": '        return self.findings'},
    ]
    EX = '''st = SharedState("charged twice and the app crashes")
st.record("billing", "duplicate charge on 4471")
st.record("tech", "matches BUG-231")
print("findings:", st.context())
print("log     :", st.log)'''
    return [
      header(3, "Shared State & Message Passing", "Beginner", 20,
        ["Record each agent's finding into a shared state",
         "Keep an ordered log of who said what",
         "Expose a small, relevant context for the next agent"],
        "Message passing & shared state"),
      setup(3),
      concept('''Agents coordinate by **communicating** (deck slide 7): they pass **messages** or read/write a **shared
state** &mdash; a common object carrying the conversation, each agent's findings, and the plan. **LangGraph**
works exactly this way: the state flows through every node. Two rules keep it sane: keep the shared context
**small &amp; relevant** (don't dump everything to everyone), and make handoffs **explicit**.'''),
      code('''# One finding is just (agent_name, what it found).
print("a finding:", ("billing", "duplicate charge on 4471"))'''),
      buildmd('''Complete `SharedState`: record findings (keyed by agent), keep an ordered log, and return a small
context.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- Two agents' findings **coexist** in `findings`, keyed by who found them &mdash; nobody overwrites anybody.
- The **`log`** preserves order, so you can replay *who said what, when* &mdash; the seed of observability (Lab 8.10).
- `context()` stays **small** &mdash; only what's been recorded &mdash; so the next agent isn't drowned in irrelevant state.'''),
      yourturn('''Add a `summary()` method that returns a one-line string joining every finding (e.g.
`"billing: ...; tech: ..."`), and call it after recording two findings. **What good looks like:** the summary
reads back in a stable order and contains every recorded finding &mdash; the raw material a **synthesiser**
(Lab 8.9) will turn into one reply.'''),
      footer(3, "Shared state is how a team stays coherent -- each agent writes its finding, the next reads the context. Keep it small and let handoffs be explicit, or agents talk past each other."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-sequential-pipeline", "Beginner",
     "Sequential Pipeline of Specialists", 25,
     "Chain specialists in a fixed order so each adds to a customer case -- triage, then billing, then tech.",
     ["Sequential", "Pipeline", "Stages"])
def _l4(sol):
    DEFS = [
      "def run_pipeline(ticket, stages):",
      "    case = ticket",
      "    trail = []",
      "    for stage in stages:",
      {"s": '        case = ___   # TODO: run this stage on the CURRENT case (its input is the previous stage output)',
       "a": '        case = stage(case)'},
      "        trail.append(case)",
      '    return {"case": case, "trail": trail}',
      "",
      "STAGES = [",
      '    lambda c: c + " | triage -> billing+tech",',
      '    lambda c: c + " | billing: duplicate charge on 4471",',
      '    lambda c: c + " | tech: matches BUG-231",',
      "]",
    ]
    EX = '''out = run_pipeline("ticket: charged twice, app crashing", STAGES)
print("final case:", out["case"])
for step in out["trail"]:
    print("  step:", step)'''
    return [
      header(4, "Sequential Pipeline of Specialists", "Beginner", 25,
        ["Run the CS specialists in a fixed order over one customer ticket",
         "Feed each stage the previous stage's accumulated case",
         "See why a clean, ordered hand-off keeps each stage reliable"],
        "Sequential — a pipeline of specialists"),
      setup(4),
      concept('''The simplest collaboration is the **sequential pipeline** (deck slide 9): agents run in a **fixed order**,
each transforming the running case &mdash; for a support ticket that is **triage &rarr; billing &rarr;
tech**. It's a relay where the baton is the growing case. Each stage gets a **clean, focused input** (the
prior stage's output), so each does its narrow job well &mdash; and you can swap any stage independently.
(Watch out: errors **propagate** downstream, and it's **serial**, so latency adds up.)'''),
      code('''# Each stage is a specialist that takes the running case and returns it, extended with its note.
print("pipeline: triage -> billing -> tech")'''),
      buildmd('''Complete `run_pipeline` so each stage receives the previous stage's output.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- The ticket passes through **every stage in order**; each `trail` entry **builds on** the previous one.
- Triage runs before the specialists, so the specialists get a pre-sorted case &mdash; a clean, focused input.
- Because stages are just functions of the running case, you can **swap** any one independently. Errors, though, propagate downstream.'''),
      yourturn('''Insert a new **`policy`** stage between billing and tech (e.g. `lambda c: c + " | policy: refund within 30 days"`)
and re-run. **What good looks like:** the new stage appears in order in the trail, the final case carries every
stage's note, and removing a stage cleanly shortens the pipeline &mdash; no other stage needs to change.'''),
      footer(4, "A pipeline is the multi-agent version of Module 7's automation pipeline -- each stage a specialist over the same ticket. Clean, ordered hand-offs make each stage reliable; just remember errors propagate downstream."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-parallel-fanout", "Beginner",
     "Parallel Fan-Out", 20,
     "Fan one ticket out to several specialists at once, collect results by agent, and survive one that fails.",
     ["Parallel", "Fan-out", "Coverage"])
def _l5(sol):
    DEFS = [
      "def fan_out(ticket, specialists):",
      "    results = {}",
      "    for name, agent in specialists.items():",
      "        try:",
      {"s": '            results[name] = ___   # TODO: run THIS agent on the ticket (same input for all)',
       "a": '            results[name] = agent(ticket)'},
      "        except Exception as e:",
      {"s": '            results[name] = ___   # TODO: this agent is down -- record a marker string beginning "ERROR: " (include type(e).__name__) so the fan-out survives',
       "a": '            results[name] = f"ERROR: {type(e).__name__}"'},
      "    return results",
    ]
    EX = '''out = fan_out("charged twice and the app keeps crashing", SPECIALISTS)
for name, res in out.items():
    print(f"{name:8}: {res}")'''
    return [
      header(5, "Parallel Fan-Out", "Beginner", 20,
        ["Run every specialist on the SAME customer ticket at once",
         "Collect each result tagged with the agent that produced it",
         "Survive one agent failing -- fault tolerance in a fan-out"],
        "Parallel — fan-out for coverage & speed"),
      setup(5),
      concept('''In the **parallel** (fan-out) shape, several agents work the **same input** at once and their outputs are
combined (deck slide 10). For a support ticket you fan it out to the **billing, tech and policy** specialists
together &mdash; each an independent lens, so between them they catch what one alone would miss. Two practical
rules: keep each result **tagged with the agent** that produced it (you must know who said what), and make
the fan-out **fault-tolerant** &mdash; if one specialist is down, the others still return. Fan-out then
creates a new problem &mdash; **several outputs, and you need one** &mdash; which is the decision-making you
build next.'''),
      code('''# Three specialists, each a different lens on the SAME ticket -- and one of them is currently DOWN.
def billing_agent(t):
    return "duplicate charge on 4471" if "charg" in t.lower() else "no billing issue"
def tech_agent(t):
    return "matches BUG-231" if "crash" in t.lower() else "no tech issue"
def policy_agent(t):
    raise RuntimeError("policy service unavailable")   # this specialist is DOWN -> the fan-out must survive it
SPECIALISTS = {"billing": billing_agent, "tech": tech_agent, "policy": policy_agent}
print("fan-out targets:", list(SPECIALISTS))'''),
      buildmd('''Complete `fan_out`: run every specialist on the **same** ticket, tag each result by agent, and keep going
when one raises.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- Every specialist saw the **same ticket**; each result is **tagged** with who produced it &mdash; you always know who said what.
- The **down** `policy` agent yields an `"ERROR: ..."` marker instead of crashing the fan-out &mdash; the survivors still returned findings.
- You now hold **several** results and need **one** &mdash; that convergence (vote / synthesise) is the rest of the module.'''),
      yourturn('''Add a fourth specialist that returns a *contradicting* billing verdict (e.g. `"no refund due"`), then re-run
the fan-out. **What good looks like:** all four run, each tagged, the down agent still degrades to a marker &mdash;
and you now have a genuine **conflict** to resolve with a vote (Lab 8.7) or synthesis (Lab 8.9).'''),
      footer(5, "Fan-out buys coverage and speed -- latency is the slowest agent, not the sum -- and staying tagged + fault-tolerant means one agent going down doesn't take the team with it. But now you have several outputs and need one: that convergence is decision making, coming up."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-handoff", "Beginner",
     "Explicit Handoff (Capped)", 25,
     "Let agents hand off to each other explicitly, walk the handoff path, and cap it to stop loops.",
     ["Handoff", "Loop cap", "Coordination"])
def _l6(sol):
    DEFS = [
      "def run_handoffs(start, agents, max_handoffs=5):",
      "    current, path = start, []",
      "    for _ in range(max_handoffs):",
      "        path.append(current)",
      "        nxt = agents[current]()",
      {"s": '        if ___:   # TODO: the agent signalled it is finished',
       "a": '        if nxt == "done":'},
      "            break",
      {"s": '        current = ___   # TODO: hand off to the next agent',
       "a": '        current = nxt'},
      "    return path",
      "",
      'AGENTS = {"supervisor": lambda: "billing", "billing": lambda: "tech", "tech": lambda: "done"}',
      'LOOP   = {"a": lambda: "b", "b": lambda: "a"}   # two agents that would loop forever',
    ]
    EX = '''print("path :", run_handoffs("supervisor", AGENTS))
print("loop :", run_handoffs("a", LOOP, max_handoffs=4))'''
    return [
      header(6, "Explicit Handoff (Capped)", "Beginner", 25,
        ["Let each agent return the next agent, or 'done'",
         "Walk the handoff path from a starting agent",
         "Cap total handoffs so two agents can't loop forever"],
        "Message passing & shared state"),
      setup(6),
      concept('''Agents coordinate by **explicit handoffs**: an agent signals *&ldquo;done&rdquo;* or *&ldquo;this needs the
tech agent&rdquo;*, and control passes on. The danger is a **handoff loop** &mdash; A hands to B, B hands
back to A, forever (deck slide 19) &mdash; so you **cap total handoffs**, exactly like `max_iterations`.
Explicit handoffs plus a cap are what keep a team from becoming a mob.'''),
      code('''# Each agent is a function returning the NEXT agent's name, or "done".
print("handoff: supervisor -> billing -> tech -> done")'''),
      buildmd('''Complete `run_handoffs`: stop at `"done"`, otherwise follow the handoff, all under a cap.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- The handoff **path** is walked in order and stops at `"done"` &mdash; explicit control passing, not magic.
- Point it at `LOOP` (two agents that hand back and forth) and the **cap** stops it dead &mdash; the multi-agent `max_iterations`.
- A lower cap stops sooner: the cap is your dial between *let the team finish* and *never run away*.'''),
      yourturn('''Add an agent that hands off **conditionally** (returns `"tech"` sometimes and `"done"` other times), and walk
a few runs. **What good looks like:** normal runs terminate at `"done"` well under the cap, while a
deliberately looping set is always stopped by the cap &mdash; no polite pair of agents can hand back and forth
forever.'''),
      footer(6, "Explicit handoffs plus a cap are the multi-agent version of the agent loop with max_iterations. Without the cap, two polite agents hand back and forth forever."),
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
