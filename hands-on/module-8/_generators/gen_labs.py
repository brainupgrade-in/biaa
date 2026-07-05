# -*- coding: utf-8 -*-
"""Generator for Day 4 Module 8 hands-on labs (12 notebooks).
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

Design: this is the "Multi-Agent Collaboration & Decision Making" module -- the labs build the
MULTI-AGENT CUSTOMER-SERVICE CHATBOT (the client's Lab 4.2) piece by piece, exactly as the deck
teaches: specialist roles, the supervisor/router, message passing & shared state, the orchestration
shapes (sequential pipeline, parallel fan-out, explicit handoff), the decision mechanisms (voting,
critique/debate, synthesis), observability, and the assembled chatbot. To keep the course's verify
discipline (every GRADED cell runs offline & deterministically -- no live LLM, no keys, no network),
the graded cells are pure Python stdlib; the two agent-assembly labs (11-12) reuse the SAME compact
LangChain-shaped shim as Modules 6-7 (names & shapes mirror real LangChain), driven by a
deterministic scripted "FakeChatModel". Each Advanced lab (10-12) adds ONE optional, non-graded,
guarded cell that runs the SAME shapes against the REAL library (LangChain / LangGraph) and degrades
gracefully. Tools use a small AST-based safe evaluator where needed -- never bare eval()."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day4-module8-multi-agent-collaboration.html"
OUTLINE = "../../course-outline-building-intelligent-ai-agents.html"

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

GRADER_HEAD = '''# === Auto-grader: run after filling the blanks above ===
_results = []
def _rec(label, status, extra=""):
    _results.append(status); print(f"[{status}] {label}" + (f" -- {extra}" if extra else ""))
def expect(label, got, want):
    if got == "___" or got is None: _rec(label, "TODO")
    elif got == want: _rec(label, "PASS")
    else: _rec(label, "FAIL", f"got {got!r}")
def expect_true(label, fn):
    try: _rec(label, "PASS" if fn() else "FAIL")
    except Exception as e: _rec(label, "TODO", type(e).__name__)
'''
GRADER_TAIL = '''_p = _results.count("PASS")
print(f"\\nScore: {_p}/{len(_results)}")
print("All checks passed -- lab complete!" if _p == len(_results) else "Keep going: fill the blanks marked ___ and re-run.")'''

def grader(body):
    return code(GRADER_HEAD + "\n" + body.strip() + "\n\n" + GRADER_TAIL)

def setup(nn, extra=""):
    return code(f'''# Setup -- run me first
import os
WORK = "/tmp/biaa-lab-08-{nn:02d}"
os.makedirs(WORK, exist_ok=True)
print("Working dir:", WORK){extra}''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 8.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 4 &middot; Module 8 &mdash; Multi-Agent Collaboration &amp; Decision Making**

### What you'll do
{g}

> **How this lab works (experiential flow):** read the **Concept**, run the **Demo** to see it work, then complete **Your Turn** by replacing every `___` placeholder. Run the **grader** cell at the end &mdash; it prints `[PASS]` / `[FAIL]` / `[TODO]` and a final `Score`. Aim for a full score.

> **Framework note:** the graded steps are **offline &amp; deterministic** (pure Python stdlib); the agent-assembly labs reuse the **LangChain-shaped shim** from Modules 6&ndash;7. Advanced labs end with an **optional** cell that runs the **real** library. You are building the **multi-agent customer-service chatbot** &mdash; the client's Lab 4.2.

**Reference:** [Module 8 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 8 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 8 labs](./index.html) &nbsp;&middot;&nbsp; [Module 8 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def optional_real(intro, body):
    """An OPTIONAL, non-graded cell that runs the SAME shapes against the REAL LangChain / LangGraph."""
    return [md(f'''## Optional &mdash; run this against the REAL LangChain / LangGraph (not graded)
{intro} Safe to skip &mdash; it needs `pip install langchain langchain-ollama langgraph` (then
`ollama run llama3.2:1b`) or `langchain-groq` with a `GROQ_API_KEY`. If a package, model or key is
missing the cell prints a friendly note and moves on.
**The graded steps above are offline &amp; deterministic, so the lab always verifies without a model.**'''),
            code(body)]

# ---- shared building blocks (pure stdlib) -------------------------------------------------

# A tiny LangChain-SHAPED shim (same as Modules 6-7). Names & shapes mirror real LangChain.
LC_TOOL = '''# --- LangChain-SHAPED shim: a tool has .name, .description (from the docstring), .args, .invoke() ---
import inspect
class Tool:
    def __init__(self, fn, name=None, description=None):
        self.fn = fn
        self.name = name or fn.__name__
        self.description = (description or inspect.getdoc(fn) or "").strip()
        self.args = list(inspect.signature(fn).parameters)
    def invoke(self, value):
        return self.fn(**value) if isinstance(value, dict) else self.fn(value)
    def __repr__(self):
        return "Tool(name=%r)" % self.name
def tool(fn):
    """The @tool decorator -- wrap a plain function into a Tool (mirrors langchain_core.tools.tool)."""
    return Tool(fn)'''

LC_MODEL = '''class AIMessage:
    def __init__(self, content): self.content = content
class FakeChatModel:
    """Deterministic stand-in for ChatOllama / ChatGroq: replays a scripted list of replies.
    Real code: from langchain_ollama import ChatOllama; model = ChatOllama(model="llama3.2:1b").
    Like the real thing, .invoke(prompt) returns a message whose text is in .content."""
    def __init__(self, script): self.script = list(script); self.i = 0
    def invoke(self, prompt):
        reply = self.script[min(self.i, len(self.script) - 1)]; self.i += 1
        return AIMessage(reply)'''

LC_PROMPT = '''class PromptTemplate:
    """Mirrors LangChain: PromptTemplate.from_template(...).format(input=..., ...)."""
    def __init__(self, template): self.template = template
    @classmethod
    def from_template(cls, template): return cls(template)
    def format(self, **kw):
        s = self.template
        for k, v in kw.items():
            s = s.replace("{" + k + "}", str(v))
        return s'''

LC_EXEC = '''def create_react_agent(model, tools, prompt):
    """Bind model + tools + prompt into a ReAct agent (mirrors langchain.agents.create_react_agent)."""
    return {"model": model, "tools": {t.name: t for t in tools}, "prompt": prompt}
def parse_react(text):
    """Turn the model's ReAct text into ('final', answer) or ('action', name, input)."""
    action = inp = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("Final Answer:"): return ("final", s.split(":", 1)[1].strip())
        if s.startswith("Action Input:"): inp = s.split(":", 1)[1].strip()
        elif s.startswith("Action:"):      action = s.split(":", 1)[1].strip()
    return ("action", action, inp)
class AgentExecutor:
    """Runs the loop: ask model -> parse -> run tool -> observe -> repeat, capped by max_iterations
    (mirrors langchain.agents.AgentExecutor). verbose=True prints the ReAct trace."""
    def __init__(self, agent, tools=None, verbose=False, max_iterations=6):
        self.agent = agent
        self.tools = agent["tools"] if tools is None else {t.name: t for t in tools}
        self.model = agent["model"]; self.prompt = agent["prompt"]
        self.verbose = verbose; self.max_iterations = max_iterations
    def invoke(self, inputs):
        scratch, steps = "", []
        for _ in range(self.max_iterations):
            text = self.model.invoke(self.prompt.format(input=inputs["input"], scratchpad=scratch)).content
            if self.verbose: print(text)
            parsed = parse_react(text)
            if parsed[0] == "final":
                return {"output": parsed[1], "intermediate_steps": steps}
            name, arg = parsed[1], parsed[2]
            obs = self.tools[name].invoke(arg) if name in self.tools else ("unknown tool: %s" % name)
            if self.verbose: print("Observation:", obs)
            steps.append((name, arg, obs)); scratch += text + "\\nObservation: " + str(obs) + "\\n"
        return {"output": None, "intermediate_steps": steps}'''

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

def shimcell(parts, demo):
    return code("\n\n".join(parts) + "\n\n" + demo)

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
     "Build two specialists -- billing and tech -- each with a focused tool set and clear scope boundaries.",
     ["Specialist roles", "Separation of concerns", "Boundaries"])
def _l1(sol):
    return [
      header(1, "Specialist Agents (Separation of Concerns)", "Beginner", 20,
        ["Model a specialist as a role + a small, focused tool set",
         "Give billing and tech agents distinct, non-overlapping tools",
         "Add a scope check so each agent knows what it handles"],
        "Specialist roles: separation of concerns"),
      setup(1),
      md('''## Concept
A multi-agent system is **decomposition applied to agents** (deck slide 5). The payoff comes from each
agent being **good at one thing**: a **focused role**, a **small tool set**, and **clear boundaries**.
A billing specialist handles charges and refunds with billing tools; a tech specialist troubleshoots
with tech tools. Small prompts get followed; small tool sets keep selection accurate; boundaries make
behaviour predictable &mdash; and you can improve one without touching the other.'''),
      code('''# A specialist = a name + the tools it owns + the topics it handles.
print("we will build two specialists: billing and tech")'''),
      md('''## Your Turn
Give each specialist its own **focused tool set** and topic **keywords**, and complete the `in_scope`
check.'''),
      code(render([
        "class Specialist:",
        "    def __init__(self, name, tools, keywords):",
        "        self.name = name",
        "        self.tools = tools",
        "        self.keywords = keywords",
        "    def in_scope(self, message):",
        "        m = message.lower()",
        {"s": '        return ___   # TODO: True if ANY of this role\'s keywords is in the message',
         "a": '        return any(k in m for k in self.keywords)'},
        "",
        {"s": 'billing = Specialist("billing", ___, ["charge", "refund", "invoice", "billed"])   # TODO: billing tools',
         "a": 'billing = Specialist("billing", ["lookup_invoice", "refund_request"], ["charge", "refund", "invoice", "billed"])'},
        {"s": 'tech    = Specialist("tech", ["known_issues", "restart_service"], ___)   # TODO: tech keywords',
         "a": 'tech    = Specialist("tech", ["known_issues", "restart_service"], ["crash", "error", "login", "bug", "broken"])'},
        "",
        "try:",
        "    print('billing tools:', billing.tools)",
        "    print('tech tools   :', tech.tools)",
        "    print('billing handles a charge? ', billing.in_scope('I was charged twice'))",
        "    print('tech handles a crash?     ', tech.in_scope('the app keeps crashing'))",
        "    print('billing handles a crash?  ', billing.in_scope('the app keeps crashing'))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("billing has its own focused tool set", lambda: billing.tools == ["lookup_invoice", "refund_request"])
expect_true("tech's tools do not overlap billing's", lambda: set(tech.tools).isdisjoint(billing.tools))
expect_true("billing handles a charge query", lambda: billing.in_scope("I was charged twice") is True)
expect_true("tech handles a crash query", lambda: tech.in_scope("the app keeps crashing") is True)
expect_true("billing stays in its lane (not a crash)", lambda: billing.in_scope("the app keeps crashing") is False)'''),
      footer(1, "Each specialist is a focused role with a small tool set and clear boundaries. That separation of concerns is the whole payoff of multi-agent -- next, a supervisor decides who handles what."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-the-supervisor", "Beginner",
     "The Supervisor (Router)", 20,
     "Build a supervisor that classifies a message and routes it to the right specialist -- or to several.",
     ["Supervisor", "Routing", "Multi-intent"])
def _l2(sol):
    return [
      header(2, "The Supervisor (Router)", "Beginner", 20,
        ["Route a message to the specialist(s) whose scope it matches",
         "Handle a message with TWO intents -> route to both",
         "Fall back to a general agent when nothing matches"],
        "The supervisor (router) pattern"),
      setup(2),
      md('''## Concept
The **supervisor** (router) is the backbone of a multi-agent system (deck slide 6): it receives the
message, decides **which specialist** should handle it, and routes there. It is exactly Module 7's
**route** pattern &mdash; but the destinations are **agents**, not code branches. A message can have
**two intents** (a billing problem *and* a crash), so routing returns a **list**; and an unmatched
message falls back to a **general** agent (the escape hatch).'''),
      shimcell([],
        '''class Specialist:
    def __init__(self, name, keywords): self.name = name; self.keywords = keywords
    def in_scope(self, message):
        m = message.lower()
        return any(k in m for k in self.keywords)
billing = Specialist("billing", ["charge", "refund", "invoice", "billed"])
tech    = Specialist("tech", ["crash", "error", "login", "bug", "broken"])
SPECIALISTS = [billing, tech]
print("specialists ready:", [s.name for s in SPECIALISTS])'''),
      md('''## Your Turn
Complete `route`: collect every specialist whose scope matches, and fall back to `general`.'''),
      code(render([
        "def route(message, specialists):",
        {"s": '    hits = ___   # TODO: the .name of every specialist whose scope matches the message',
         "a": '    hits = [s.name for s in specialists if s.in_scope(message)]'},
        {"s": '    return hits if hits else ___   # TODO: fall back to ["general"] when nothing matches',
         "a": '    return hits if hits else ["general"]'},
        "",
        "try:",
        "    print('charge msg :', route('I was charged twice', SPECIALISTS))",
        "    print('crash msg  :', route('the app keeps crashing', SPECIALISTS))",
        "    print('both       :', route('charged twice and the app crashes', SPECIALISTS))",
        "    print('unknown    :', route('what are your hours?', SPECIALISTS))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("a billing message routes to billing", lambda: route("I was charged twice", SPECIALISTS) == ["billing"])
expect_true("a tech message routes to tech", lambda: route("the app keeps crashing", SPECIALISTS) == ["tech"])
expect_true("a two-intent message routes to BOTH", lambda: set(route("charged twice and the app crashes", SPECIALISTS)) == {"billing", "tech"})
expect_true("an unmatched message falls back to general", lambda: route("what are your hours?", SPECIALISTS) == ["general"])
expect_true("route always returns a list", lambda: isinstance(route("hi", SPECIALISTS), list))'''),
      footer(2, "The supervisor is Module 7's route pattern -- but routing to AGENTS. Returning a list lets one message reach several specialists; the general fallback keeps it safe. Next: how those agents share what they find."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-shared-state", "Beginner",
     "Shared State & Message Passing", 20,
     "Give the team a shared state object where each agent records its finding and the running log is kept.",
     ["Shared state", "Message passing", "Findings"])
def _l3(sol):
    return [
      header(3, "Shared State & Message Passing", "Beginner", 20,
        ["Record each agent's finding into a shared state",
         "Keep an ordered log of who said what",
         "Expose a small, relevant context for the next agent"],
        "Message passing & shared state"),
      setup(3),
      md('''## Concept
Agents coordinate by **communicating** (deck slide 7): they pass **messages** or read/write a **shared
state** &mdash; a common object carrying the conversation, each agent's findings, and the plan.
**LangGraph** uses this: the state flows through every node. Two rules keep it sane: keep the shared
context **small &amp; relevant** (don't dump everything to everyone), and make handoffs **explicit**.'''),
      code('''# One finding is just (agent_name, what it found).
print("a finding:", ("billing", "duplicate charge on 4471"))'''),
      md('''## Your Turn
Complete `SharedState`: record findings (keyed by agent), keep an ordered log, and return a small
context.'''),
      code(render([
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
        "",
        "try:",
        "    st = SharedState('charged twice and the app crashes')",
        "    st.record('billing', 'duplicate charge on 4471')",
        "    st.record('tech', 'matches BUG-231')",
        "    print('findings:', st.context())",
        "    print('log     :', st.log)",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("record stores a finding by agent", lambda: (lambda s: (s.record("billing", "x"), s.findings.get("billing"))[1])(SharedState("m")) == "x")
expect_true("two agents' findings coexist", lambda: (lambda s: (s.record("billing", "a"), s.record("tech", "b"), set(s.findings))[2])(SharedState("m")) == {"billing", "tech"})
expect_true("the log preserves order", lambda: (lambda s: (s.record("billing", "a"), s.record("tech", "b"), s.log)[2])(SharedState("m")) == [("billing", "a"), ("tech", "b")])
expect_true("context returns the findings", lambda: (lambda s: (s.record("tech", "b"), s.context())[1])(SharedState("m")) == {"tech": "b"})
expect_true("context stays small (only recorded agents)", lambda: (lambda s: (s.record("tech", "b"), len(s.context()))[1])(SharedState("m")) == 1)'''),
      footer(3, "Shared state is how a team stays coherent -- each agent writes its finding, the next reads the context. Keep it small and let handoffs be explicit, or agents talk past each other."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-sequential-pipeline", "Beginner",
     "Sequential Pipeline of Specialists", 25,
     "Chain agents in a fixed order so each transforms the previous one's output -- research, write, edit.",
     ["Sequential", "Pipeline", "Stages"])
def _l4(sol):
    return [
      header(4, "Sequential Pipeline of Specialists", "Beginner", 25,
        ["Run a list of stage-agents in a fixed order",
         "Feed each stage the previous stage's output",
         "See why a clean, focused input makes each stage reliable"],
        "Sequential — a pipeline of specialists"),
      setup(4),
      md('''## Concept
The simplest collaboration is the **sequential pipeline** (deck slide 9): agents run in a **fixed
order**, each transforming the previous output &mdash; researcher &rarr; writer &rarr; editor. It's a
relay where the baton is the growing state. Each agent gets a **clean, focused input** (the prior
stage's output), so each does its narrow job well &mdash; and you can swap any stage independently.
(Watch out: errors **propagate**, and it's **serial**, so latency adds up.)'''),
      code('''# Each stage is an agent that takes the running text and returns it, extended.
print("pipeline: research -> write -> edit")'''),
      md('''## Your Turn
Complete `run_pipeline` so each stage receives the previous stage's output.'''),
      code(render([
        "def run_pipeline(text, stages):",
        "    steps = []",
        "    for stage in stages:",
        {"s": '        text = ___   # TODO: run this stage on the CURRENT text (its input is the prior output)',
         "a": '        text = stage(text)'},
        "        steps.append(text)",
        '    return {"result": text, "steps": steps}',
        "",
        "STAGES = [",
        '    lambda t: t + " -> researched",',
        '    lambda t: t + " -> written",',
        '    lambda t: t + " -> edited",',
        "]",
        "",
        "try:",
        "    out = run_pipeline('topic: refunds', STAGES)",
        "    print('result:', out['result'])",
        "    print('steps :', out['steps'])",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the text passes through all three stages", lambda: run_pipeline("x", STAGES)["result"] == "x -> researched -> written -> edited")
expect_true("one step is recorded per stage", lambda: len(run_pipeline("x", STAGES)["steps"]) == 3)
expect_true("each stage builds on the previous output", lambda: run_pipeline("x", STAGES)["steps"][1].startswith(run_pipeline("x", STAGES)["steps"][0]))
expect_true("the final step is the result", lambda: run_pipeline("x", STAGES)["steps"][-1] == run_pipeline("x", STAGES)["result"])
expect_true("a single-stage pipeline works", lambda: run_pipeline("x", [lambda t: t + "!"])["result"] == "x!")'''),
      footer(4, "A pipeline is the multi-agent version of Module 7's automation pipeline -- each stage a specialist. Clean hand-offs make each stage reliable; just remember errors propagate downstream."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-parallel-fanout", "Beginner",
     "Parallel Fan-Out", 20,
     "Run several agents on the SAME input for coverage, and collect all their results together.",
     ["Parallel", "Fan-out", "Coverage"])
def _l5(sol):
    return [
      header(5, "Parallel Fan-Out", "Beginner", 20,
        ["Give the same input to several agents at once",
         "Collect one result per agent for coverage",
         "See how independent lenses catch what one would miss"],
        "Parallel — fan-out for coverage & speed"),
      setup(5),
      md('''## Concept
In the **parallel** (fan-out) shape, several agents work the **same input** at once and their outputs
are combined (deck slide 10). Two uses: **coverage** (different lenses on one question &mdash; security,
performance, style reviewers) and **diverse attempts** (several solutions, pick the best). Independent
views don't share a blind spot. But fan-out creates a new problem &mdash; you now have **several
outputs and need one** &mdash; which is the decision-making you'll build next.'''),
      code('''# Three reviewers, each a different lens on the same code snippet.
print("fan-out: run every reviewer on the same input")'''),
      md('''## Your Turn
Complete `fan_out` so every agent runs on the same input and you collect all results.'''),
      code(render([
        "def fan_out(text, agents):",
        {"s": '    return ___   # TODO: a list with each agent\'s result on the SAME text',
         "a": '    return [agent(text) for agent in agents]'},
        "",
        "REVIEWERS = [",
        '    lambda t: "security: " + ("risk" if "eval" in t else "ok"),',
        '    lambda t: "perf: " + ("slow" if "loop" in t else "ok"),',
        '    lambda t: "style: ok",',
        "]",
        "",
        "try:",
        "    print(fan_out('for x in loop: eval(x)', REVIEWERS))",
        "    print(fan_out('clean code', REVIEWERS))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("fan_out runs every agent", lambda: len(fan_out("x", REVIEWERS)) == 3)
expect_true("one result per agent", lambda: len(fan_out("x", REVIEWERS)) == len(REVIEWERS))
expect_true("every agent saw the same input", lambda: fan_out("eval loop", REVIEWERS)[0] == "security: risk" and fan_out("eval loop", REVIEWERS)[1] == "perf: slow")
expect_true("a clean input flags nothing", lambda: fan_out("clean", REVIEWERS) == ["security: ok", "perf: ok", "style: ok"])
expect_true("different input, different results", lambda: fan_out("eval", REVIEWERS) != fan_out("clean", REVIEWERS))'''),
      footer(5, "Fan-out buys coverage and speed -- latency is the slowest agent, not the sum. But now you have several outputs and need one: that convergence is decision making, coming up."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-handoff", "Beginner",
     "Explicit Handoff (Capped)", 25,
     "Let agents hand off to each other explicitly, walk the handoff path, and cap it to stop loops.",
     ["Handoff", "Loop cap", "Coordination"])
def _l6(sol):
    return [
      header(6, "Explicit Handoff (Capped)", "Beginner", 25,
        ["Let each agent return the next agent, or 'done'",
         "Walk the handoff path from a starting agent",
         "Cap total handoffs so two agents can't loop forever"],
        "Message passing & shared state"),
      setup(6),
      md('''## Concept
Agents coordinate by **explicit handoffs**: an agent signals *&ldquo;done&rdquo;* or *&ldquo;this needs
the tech agent&rdquo;*, and control passes on. The danger is a **handoff loop** &mdash; A hands to B,
B hands back to A, forever (deck slide 19) &mdash; so you **cap total handoffs**, exactly like
`max_iterations`. Explicit handoffs plus a cap are what keep a team from becoming a mob.'''),
      code('''# Each agent is a function returning the NEXT agent's name, or "done".
print("handoff: supervisor -> billing -> tech -> done")'''),
      md('''## Your Turn
Complete `run_handoffs`: stop at `"done"`, otherwise follow the handoff, all under a cap.'''),
      code(render([
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
        "",
        "try:",
        "    print('path :', run_handoffs('supervisor', AGENTS))",
        "    print('loop :', run_handoffs('a', LOOP, max_handoffs=4))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the handoff path is walked in order", lambda: run_handoffs("supervisor", AGENTS) == ["supervisor", "billing", "tech"])
expect_true("it stops at 'done'", lambda: run_handoffs("supervisor", AGENTS)[-1] == "tech")
expect_true("the cap stops an infinite loop", lambda: len(run_handoffs("a", LOOP, max_handoffs=4)) == 4)
expect_true("a lower cap stops sooner", lambda: len(run_handoffs("a", LOOP, max_handoffs=2)) == 2)
expect_true("an immediate 'done' yields a single step", lambda: run_handoffs("x", {"x": lambda: "done"}) == ["x"])'''),
      footer(6, "Explicit handoffs plus a cap are the multi-agent version of the agent loop with max_iterations. Without the cap, two polite agents hand back and forth forever."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-voting", "Intermediate",
     "Voting & Consensus", 30,
     "Converge several agents' comparable answers by majority vote, and escalate a split decision to a human.",
     ["Voting", "Consensus", "Escalate"])
def _l7(sol):
    return [
      header(7, "Voting & Consensus", "Intermediate", 30,
        ["Take the majority answer from several agents",
         "Require a clear majority above a threshold",
         "Escalate a split (no majority) to a human"],
        "Voting & consensus"),
      setup(7),
      md('''## Concept
When agents produce **comparable answers**, take a **vote** (deck slide 12). Independent errors
cancel: if each agent is 70% right with uncorrelated mistakes, the **majority** is far better. But a
**split vote** is a *signal* &mdash; escalate to a human rather than force a call. (And beware a
**shared blind spot**: agents that reason alike will confidently agree on the same wrong answer.)'''),
      code('''from collections import Counter
print("three agents voted:", ["refund", "refund", "deny"], "-> majority?")'''),
      md('''## Your Turn
Complete `vote` (the majority) and `decide` (escalate unless a clear majority).'''),
      code(render([
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
        "",
        "try:",
        "    print('vote  :', vote(['refund', 'refund', 'deny']))",
        "    print('clear :', decide(['refund', 'refund', 'deny']))",
        "    print('split :', decide(['refund', 'deny', 'wait']))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("vote returns the majority answer", lambda: vote(["refund", "refund", "deny"]) == "refund")
expect_true("vote handles a unanimous set", lambda: vote(["ok", "ok", "ok"]) == "ok")
expect_true("a clear majority is decided", lambda: decide(["refund", "refund", "deny"])["decision"] == "refund")
expect_true("a three-way split escalates", lambda: decide(["refund", "deny", "wait"])["escalate"] is True)
expect_true("a bare majority (2/3) passes the threshold", lambda: decide(["a", "a", "b"])["escalate"] is False)'''),
      footer(7, "Voting converges comparable answers, and a split vote is information -- escalate, don't force it. Use it for checkable answers; watch for a shared blind spot that makes agents agree on the same mistake."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-critique-debate", "Intermediate",
     "Critique & Debate", 30,
     "Add an independent critic that reviews an answer; loop propose -> critique -> revise, capped.",
     ["Critique", "Reflection", "Capped loop"])
def _l8(sol):
    return [
      header(8, "Critique & Debate", "Intermediate", 30,
        ["Run a propose -> critique -> revise loop",
         "Let an independent critic gate on quality",
         "Cap the loop so two agents can't argue forever"],
        "Critique & debate"),
      setup(8),
      md('''## Concept
Instead of averaging, **stress-test** one answer (deck slide 13): one agent **proposes**, an
independent **critic** tries to find what's wrong, the proposer **revises** &mdash; repeat until the
critic approves or a **cap** is hit. Generating and evaluating are **different skills**, so a separate
skeptic catches the author's blind spots (just like code review). Always **cap** the loop.'''),
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
      md('''## Your Turn
Complete `critique_loop`: get the critic's verdict and stop when it approves (or at the cap).'''),
      code(render([
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
        "",
        "try:",
        "    print('approved:', critique_loop(proposer, critic))",
        "    print('capped  :', critique_loop(proposer, critic_never))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the loop returns an approved answer", lambda: critique_loop(proposer, critic)["approved"] is True)
expect_true("it approves in the expected round (2)", lambda: critique_loop(proposer, critic)["rounds"] == 2)
expect_true("a never-satisfied critic hits the cap", lambda: critique_loop(proposer, critic_never, max_rounds=3)["rounds"] == 3)
expect_true("a capped run is marked not approved", lambda: critique_loop(proposer, critic_never)["approved"] is False)
expect_true("the critic actually gates the result", lambda: "grounded" in critique_loop(proposer, critic)["answer"])'''),
      footer(8, "A separate critic raises quality because evaluating is a different skill from generating -- and the cap keeps the debate from running forever. Use it when being right beats being fast."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-synthesis", "Intermediate",
     "Synthesis: One Coherent Reply", 30,
     "Combine several agents' findings into one grounded, coherent reply -- resolving, not concatenating.",
     ["Synthesis", "Grounded", "One voice"])
def _l9(sol):
    return [
      header(9, "Synthesis: One Coherent Reply", "Intermediate", 30,
        ["Combine multiple agents' findings into one reply",
         "Keep it grounded -- built only from the findings",
         "Detect a conflict instead of pasting contradictions"],
        "Synthesis — combine the parts"),
      setup(9),
      md('''## Concept
Voting is for comparable **whole answers**; **synthesis** is for complementary **parts** (deck slide
14). When the billing agent found the refund status and the tech agent diagnosed the bug, a
**synthesiser** weaves both into one coherent reply. Keys: **resolve conflicts** (don't just
concatenate contradictions), **stay grounded** (build only from what agents found), and **own one
voice**.'''),
      code('''# findings: a dict of agent -> what it found.
print("synthesise:", {"billing": "duplicate charge -> refund", "tech": "BUG-231 -> update to v4.2"})'''),
      md('''## Your Turn
Complete `synthesize` (combine, stable order) and `is_grounded` (every finding must appear).'''),
      code(render([
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
        "",
        "try:",
        "    F = {'billing': 'duplicate charge -> refund', 'tech': 'BUG-231 -> update to v4.2'}",
        "    reply = synthesize(F)",
        "    print(reply)",
        "    print('grounded?', is_grounded(reply, F))",
        "    print('conflict?', has_conflict({'a': 'issue refund', 'b': 'no refund allowed'}))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("synthesis includes every finding", lambda: all(v in synthesize({"billing": "X-charge", "tech": "Y-bug"}) for v in ("X-charge", "Y-bug")))
expect_true("the result is one coherent string", lambda: isinstance(synthesize({"a": "one"}), str))
expect_true("findings are combined in stable (sorted) order", lambda: synthesize({"tech": "T", "billing": "B"}).index("B") < synthesize({"tech": "T", "billing": "B"}).index("T"))
expect_true("a grounded reply passes", lambda: is_grounded(synthesize({"a": "alpha", "b": "beta"}), {"a": "alpha", "b": "beta"}) is True)
expect_true("a reply missing a finding is not grounded", lambda: is_grounded("only alpha here", {"a": "alpha", "b": "beta"}) is False)'''),
      footer(9, "Synthesis reconciles complementary parts into one grounded reply in a single voice -- the last step before the customer sees an answer. Vote to converge, critique to harden, synthesise to combine."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-observability", "Advanced",
     "Observability for a Team", 40,
     "Trace every agent, message and handoff; count calls per agent; and detect a runaway handoff loop.",
     ["Observability", "Agent trace", "Loop detection"])
def _l10(sol):
    return [
      header(10, "Observability for a Team", "Advanced", 40,
        ["Log every agent action into an auditable trace",
         "Count calls per agent to find the busy/faulty one",
         "Detect a handoff loop so a runaway team is caught"],
        "Failure modes & observability"),
      setup(10),
      md('''## Concept
A multi-agent system fails in new ways &mdash; **handoff loops**, agents **talking past** each other,
**cost blow-ups**, and **lost accountability** (deck slide 19). The defence is **observability**: log
every agent, message, handoff and decision so you can **replay** the conversation, find the **faulty
agent**, and watch **cost**. **LangSmith / Langfuse** do this for graphs; here you build the offline
version.'''),
      code('''from collections import Counter
print("we log (agent, action, detail) events and watch for loops")'''),
      md('''## Your Turn
Complete the `AgentTrace` (log + read back) and `detect_loop` (a runaway handoff).'''),
      code(render([
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
        "",
        "try:",
        "    tr = AgentTrace()",
        "    tr.log('supervisor', 'route', 'billing+tech')",
        "    tr.log('billing', 'tool', 'lookup_invoice')",
        "    tr.log('tech', 'tool', 'known_issues')",
        "    print('involved :', tr.agents_involved())",
        "    print('calls    :', dict(tr.calls_per_agent()))",
        "    print('loop?    :', detect_loop(['a', 'b', 'a', 'b', 'a', 'b']))",
        "    print('healthy? :', detect_loop(['supervisor', 'billing', 'tech']))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("log records an event", lambda: (lambda t: (t.log("a", "x", "y"), len(t.events))[1])(AgentTrace()) == 1)
expect_true("agents_involved lists them in order", lambda: (lambda t: [t.log(a, "x", "y") for a in ("supervisor", "billing", "tech")] and t.agents_involved())(AgentTrace()) == ["supervisor", "billing", "tech"])
expect_true("calls_per_agent counts each agent", lambda: (lambda t: [t.log("billing", "x", "y") for _ in range(3)] and t.calls_per_agent()["billing"])(AgentTrace()) == 3)
expect_true("detect_loop catches a runaway handoff", lambda: detect_loop(["a", "b", "a", "b", "a", "b"]) is True)
expect_true("detect_loop clears a healthy path", lambda: detect_loop(["supervisor", "billing", "tech"]) is False)''')
      ,
      *optional_real(
        "See the REAL callback / tracing interface LangChain exposes (LangSmith / Langfuse capture full graphs).",
        '''try:
    from langchain_core.callbacks import BaseCallbackHandler
    class AgentHandler(BaseCallbackHandler):
        def on_chain_end(self, outputs, **kw):
            print("agent/chain finished ->", outputs)
    print("Real LangChain/LangGraph call handlers like AgentHandler on every agent & tool event.")
    print("For full multi-agent run traces: set LANGCHAIN_TRACING_V2=true + LANGCHAIN_API_KEY (LangSmith),")
    print("or run Langfuse (this course's stack) and attach its callback handler to the graph.")
except Exception as e:
    print("Install langchain-core to use real callbacks -- skipping:", type(e).__name__)
print("The AgentTrace above already logged every agent, action and detail offline.")'''),
      footer(10, "Log every agent, message, handoff and decision so you can replay the conversation, find the faulty agent and watch cost. A multi-agent system is only as trustworthy as it is observable."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-assemble-chatbot", "Advanced",
     "Assemble the Customer-Service Chatbot", 35,
     "Wire a supervisor to billing & tech specialist agents, run the matching ones, and synthesise one reply.",
     ["Multi-agent", "Specialist executors", "needs_approval"])
def _l11(sol):
    return [
      header(11, "Assemble the Customer-Service Chatbot", "Advanced", 35,
        ["Build billing & tech specialists as real agent executors",
         "Route a message and run only the matching specialists",
         "Synthesise one reply, flagged needs_approval for the refund"],
        "The multi-agent customer-service chatbot"),
      setup(11),
      md('''## Concept
Now assemble the chatbot from Modules 6&ndash;7 pieces (deck slides 15&ndash;17): each specialist is a
`create_react_agent` + `AgentExecutor` with its **own** prompt and **own** small tool set. The
**supervisor** routes the message; the matching specialists run (each grounded by its tool); their
findings are **synthesised** into one reply. Because a refund is **irreversible**, the reply is flagged
**`needs_approval`** &mdash; draft-not-send, now at the team level.'''),
      shimcell([LC_TOOL, LC_MODEL, LC_PROMPT, LC_EXEC, CS_FIXTURE],
        '''@tool
def lookup_invoice(order_id):
    """Look up the charges on an order by id."""
    return INVOICES.get(order_id, [])
@tool
def known_issues(symptom):
    """Look up a known technical issue by symptom keyword."""
    for k, v in KNOWN_ISSUES.items():
        if k in symptom.lower():
            return v
    return {}
def synthesize(findings):
    return " ".join(findings[k] for k in sorted(findings)) if findings else "No findings."
print("tools & synthesise ready:", lookup_invoice.name, "&", known_issues.name)'''),
      md('''## Your Turn
Complete `run_specialist` (build & run one specialist agent) and `handle_message` (route, run,
synthesise, flag).'''),
      code(render([
        "BILLING_SCRIPT = [",
        '    "Thought: check the charges.\\nAction: lookup_invoice\\nAction Input: 4471",',
        '    "Thought: two charges -- a duplicate.\\nFinal Answer: On billing: duplicate charge on 4471, refund warranted.",',
        "]",
        "TECH_SCRIPT = [",
        '    "Thought: look up the symptom.\\nAction: known_issues\\nAction Input: crash",',
        '    "Thought: known bug.\\nFinal Answer: On the app: matches BUG-231, fix is update to v4.2.",',
        "]",
        "",
        "def run_specialist(script, tools):",
        "    model  = FakeChatModel(script)",
        '    prompt = PromptTemplate.from_template("Message: {input}\\n{scratchpad}")',
        {"s": '    agent  = create_react_agent(model, ___, prompt)   # TODO: this specialist\'s own tools',
         "a": '    agent  = create_react_agent(model, tools, prompt)'},
        "    return AgentExecutor(agent, max_iterations=6)",
        "",
        "def handle_message(message):",
        "    m = message.lower()",
        "    findings = {}",
        '    if any(k in m for k in ("charg", "refund", "invoice", "billed")):',
        {"s": '        findings["billing"] = ___   # TODO: run the billing specialist, take its "output"',
         "a": '        findings["billing"] = run_specialist(BILLING_SCRIPT, [lookup_invoice]).invoke({"input": message})["output"]'},
        '    if any(k in m for k in ("crash", "bug", "login", "broken")):',
        '        findings["tech"] = run_specialist(TECH_SCRIPT, [known_issues]).invoke({"input": message})["output"]',
        {"s": '    return {"reply": synthesize(findings), "status": ___, "agents": sorted(findings)}   # TODO: needs_approval',
         "a": '    return {"reply": synthesize(findings), "status": "needs_approval", "agents": sorted(findings)}'},
        "",
        "try:",
        "    out = handle_message('I was charged twice for 4471 and the app keeps crashing')",
        "    print('agents:', out['agents'])",
        "    print('status:', out['status'])",
        "    print('reply :', out['reply'])",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the billing specialist reports the duplicate", lambda: "billing" in handle_message("I was charged twice for 4471")["reply"].lower() or "duplicate" in handle_message("I was charged twice for 4471")["reply"].lower())
expect_true("a two-intent message engages BOTH specialists", lambda: handle_message("charged twice for 4471 and the app keeps crashing")["agents"] == ["billing", "tech"])
expect_true("the reply synthesises both findings", lambda: (lambda r: "refund" in r.lower() and "bug-231" in r.lower())(handle_message("charged twice and crashing")["reply"]))
expect_true("a pure tech message engages only tech", lambda: handle_message("the app keeps crashing")["agents"] == ["tech"])
expect_true("the reply is needs_approval (refund is irreversible)", lambda: handle_message("charged twice")["status"] == "needs_approval")'''),
      *optional_real(
        "Swap the scripted specialists for REAL LangChain agents behind a supervisor (LangGraph, or two agents by hand).",
        '''try:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.2:1b")
    billing = llm.invoke("You are a BILLING agent. In one line, handle: charged twice on order 4471.").content
    tech    = llm.invoke("You are a TECH agent. In one line, handle: the app keeps crashing.").content
    print("REAL billing agent:", billing)
    print("REAL tech agent   :", tech)
    print("In production: give each its own tools via create_react_agent, and wire them behind a")
    print("LangGraph StateGraph supervisor -- then synthesise, and gate the refund on human approval.")
except Exception as e:
    print("No local LLM available -- skipping (pip install langchain langchain-ollama langgraph +")
    print("`ollama run llama3.2:1b`, or langchain-groq with GROQ_API_KEY):", type(e).__name__)
    print("The offline chatbot above already routed to both specialists and synthesised one needs_approval reply.")'''),
      footer(11, "Same executors as Module 6, now a TEAM: a supervisor routes, specialists gather with their own tools, a synthesiser makes one reply -- and the refund waits for a human. Next: run it over a whole suite."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-customer-service-chatbot", "Advanced",
     "Capstone: The Multi-Agent Chatbot", 45,
     "Run the full multi-agent chatbot over a suite of customer messages: route, specialists, synthesise, approve.",
     ["End-to-end team", "Task suite", "Human approval"])
def _l12(sol):
    return [
      header(12, "Capstone: The Multi-Agent Chatbot", "Advanced", 45,
        ["Chain route -> specialists -> synthesise into one handler",
         "Gate any irreversible action (a refund) on human approval",
         "Run the chatbot over a SUITE of messages and score it"],
        "The multi-agent customer-service chatbot"),
      setup(12),
      md('''## Concept
Capstone: the **multi-agent customer-service chatbot** (the client's Lab 4.2), end to end. A
**supervisor** routes each message to the matching **specialists**; each returns a grounded finding; a
**synthesiser** composes one reply; and anything **irreversible** (a refund) is flagged
**`needs_approval`** for a human &mdash; never auto-done. You run it over a **suite** of messages and
score the outcomes. The pieces below are the ones you built through the module; you assemble them.'''),
      shimcell([],
        '''# The pieces you built this module, provided here so you can assemble the whole chatbot.
SPECIALISTS = {
    "billing": ["charge", "refund", "invoice", "billed"],
    "tech":    ["crash", "bug", "login", "broken"],
}
def route(message):
    m = message.lower()
    hits = [name for name, kws in SPECIALISTS.items() if any(k in m for k in kws)]
    return hits if hits else ["general"]

def billing_agent(message):  return "On billing: duplicate charge -> refund warranted."
def tech_agent(message):     return "On the app: matches BUG-231 -> update to v4.2."
def general_agent(message):  return "On your query: forwarded to a human agent."
AGENTS = {"billing": billing_agent, "tech": tech_agent, "general": general_agent}

def synthesize(findings):
    return " ".join(findings[k] for k in sorted(findings)) if findings else "No findings."
print("route, agents & synthesise ready")'''),
      md('''## Your Turn
Assemble `process` (route -> run each specialist -> synthesise -> gate the refund) and `evaluate`.'''),
      code(render([
        "def process(message):",
        "    involved = route(message)",
        {"s": '    findings = ___   # TODO: {name: AGENTS[name](message) for each involved specialist}',
         "a": '    findings = {name: AGENTS[name](message) for name in involved}'},
        "    reply = synthesize(findings)",
        '    # irreversible action? a refund needs a human before anything happens',
        {"s": '    needs_human = ___   # TODO: True if any finding mentions "refund"',
         "a": '    needs_human = any("refund" in f.lower() for f in findings.values())'},
        '    status = "needs_approval" if needs_human else "auto_ok"',
        '    return {"agents": sorted(findings), "reply": reply, "status": status}',
        "",
        "SUITE = [",
        '    {"message": "charged twice for 4471 and the app keeps crashing", "agents": ["billing", "tech"], "status": "needs_approval"},',
        '    {"message": "the app keeps crashing on login",                  "agents": ["tech"],            "status": "auto_ok"},',
        '    {"message": "please refund my invoice",                         "agents": ["billing"],         "status": "needs_approval"},',
        "]",
        "",
        "def evaluate():",
        {"s": '    solved = ___   # TODO: count suite items where agents AND status both match',
         "a": '    solved = sum(1 for t in SUITE if process(t["message"])["agents"] == t["agents"] and process(t["message"])["status"] == t["status"])'},
        "    return solved, len(SUITE)",
        "",
        "try:",
        "    for t in SUITE:",
        "        r = process(t['message'])",
        "        print(r['agents'], '|', r['status'], '->', r['reply'][:48])",
        "    print('score:', evaluate())",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("a two-intent message engages both specialists", lambda: process("charged twice and the app keeps crashing")["agents"] == ["billing", "tech"])
expect_true("a pure tech message engages only tech", lambda: process("the app keeps crashing")["agents"] == ["tech"])
expect_true("the reply is synthesised from the findings", lambda: (lambda r: "refund" in r.lower() and "bug-231" in r.lower())(process("charged twice and crashing")["reply"]))
expect_true("a refund is gated on human approval", lambda: process("please refund my invoice")["status"] == "needs_approval")
expect_true("a non-irreversible case is auto_ok", lambda: process("the app keeps crashing")["status"] == "auto_ok")
expect_true("the chatbot solves the whole suite", lambda: evaluate() == (3, 3))'''),
      *optional_real(
        "Swap the scripted team for a REAL LangGraph multi-agent supervisor (Ollama / Groq) -- the bridge to Day 5.",
        '''try:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.2:1b")
    msg = "I was charged twice and the app keeps crashing."
    intents = llm.invoke("List the intents (billing/tech) in one line: " + msg).content
    print("REAL supervisor intents:", intents)
    print("\\nProduction shape (LangGraph): supervisor node routes to billing & tech agent nodes,")
    print("findings flow through shared state to a synthesise node, and the refund waits on human approval.")
    print("Next: Day 5 -- agents in industry (finance / health / cyber) and responsible AI.")
except Exception as e:
    print("No local LLM available -- skipping (pip install langchain langchain-ollama langgraph +")
    print("`ollama run llama3.2:1b`, or langchain-groq with GROQ_API_KEY):", type(e).__name__)
    print("The offline multi-agent chatbot above already ran the whole suite -- routed, synthesised,")
    print("and gated every refund on human approval. Next: Day 5 -- agents in industry & responsible AI.")'''),
      footer(12, "You built a multi-agent customer-service chatbot end to end -- specialists coordinated by a supervisor, findings synthesised into one reply, refunds gated on a human. That completes Day 4. Next: Day 5 -- agents in the real world, responsibly."),
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
