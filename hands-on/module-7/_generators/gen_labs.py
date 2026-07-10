# -*- coding: utf-8 -*-
"""Generator for Day 4 Module 7 hands-on labs (12 notebooks).
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

Design: this is the "Task Automation with AI Agents" module -- the labs build the
EMAIL-DRAFTING AGENT (the client's Lab 4.1) piece by piece, exactly as the deck teaches:
the automation pipeline (trigger -> gather -> draft -> validate -> approve -> act), the three
patterns (draft / extract / route), structured output, reliability (validate / retry /
idempotency), and the draft-not-send human-in-the-loop guardrail. To keep the course's verify
discipline (every GRADED cell runs offline & deterministically -- no live LLM, no keys, no
network), the graded cells are pure Python stdlib, and the agent-assembly labs reuse the SAME
compact LangChain-shaped shim as Module 6 (names & shapes mirror real LangChain), driven by a
deterministic scripted "FakeChatModel". Each Advanced lab (10-12) adds ONE optional, non-graded,
guarded cell that runs the SAME shapes against the REAL library and degrades gracefully.
The calculator/compute tools use a small AST-based safe evaluator -- never bare eval()."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day4-module7-task-automation.html"
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
import os, socket
WORK = "/tmp/biaa-lab-07-{nn:02d}"
os.makedirs(WORK, exist_ok=True)
def ollama_up(host="127.0.0.1", port=11434):
    """True if a local Ollama server is listening -- the optional live cells self-skip when it isn't."""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False
print("Working dir:", WORK, "| Ollama reachable:", ollama_up()){extra}''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 7.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 4 &middot; Module 7 &mdash; Task Automation with AI Agents**

### What you'll do
{g}

> **How this lab works (experiential flow):** read the **Concept**, run the **Demo** to see it work, then complete **Your Turn** by replacing every `___` placeholder. Run the **grader** cell at the end &mdash; it prints `[PASS]` / `[FAIL]` / `[TODO]` and a final `Score`. Aim for a full score.

> **Framework note:** these labs use the **real** LangChain (`langchain`, `langchain-core`, `langchain-ollama`). The **graded** cells assert only on the deterministic parts you build &mdash; tool wiring, prompt formatting, agent structure, and the pipeline logic &mdash; and never call an LLM, so the lab always verifies offline. Cells marked **Optional &mdash; run it for real** call a live local model (`ollama run llama3.2:1b`, or Groq) and self-skip if none is reachable. You are building the **email-drafting agent** &mdash; the client's Lab 4.1.

**Reference:** [Module 7 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 7 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 7 labs](./index.html) &nbsp;&middot;&nbsp; [Module 7 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def live(intro, body):
    """An OPTIONAL, non-graded cell that runs REAL LangChain against a live local LLM (or self-skips)."""
    return [md(f'''## Optional &mdash; run it for real (not graded)
{intro} This calls a **real** local model via `ChatOllama("llama3.2:1b")` &mdash; start it with
`ollama run llama3.2:1b` (or swap in `ChatGroq` with a `GROQ_API_KEY`). If none is reachable the cell
prints a note and moves on. **The graded cells above never call an LLM, so the lab always verifies offline.**
*(llama3.2:1b is tiny &mdash; tool-calling can be hit-or-miss; the point is to see a real invocation.)*'''),
            code(body)]

def optional_real(intro, body):
    """An OPTIONAL, non-graded cell that shows a REAL LangChain interface (no live model call needed)."""
    return [md(f'''## Optional &mdash; the real LangChain interface (not graded)
{intro} It needs only `pip install langchain-core` (already in the course env) and makes **no** network
call. **The graded steps above never call an LLM, so the lab always verifies offline.**'''),
            code(body)]

# ---- shared building blocks (pure stdlib) -------------------------------------------------

# AST-based safe arithmetic -- never bare eval() on free text.
SAFE_CALC = '''import ast, operator
# safe arithmetic: walk a parsed AST of numbers + (+ - * / ** unary-minus) -- never bare eval()
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.USub: operator.neg, ast.Pow: operator.pow}
def safe_calc(expr):
    def ev(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp):
            return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp):
            return _OPS[type(node.op)](ev(node.operand))
        raise ValueError("unsupported expression")
    return ev(ast.parse(expr, mode="eval").body)'''

# Real-LangChain import snippets (dropped into the cells that need them).
TOOL_IMPORT = "from langchain_core.tools import tool"
PROMPT_IMPORT = "from langchain_core.prompts import PromptTemplate"

# The shared email-domain fixtures used across the module (orders + reply templates).
EMAIL_FIXTURE = '''# The email agent's context sources: a small orders DB and a set of reply templates.
ORDERS = {
    "4471": {"id": "4471", "name": "Priya", "status": "shipped",    "eta": "Friday",    "carrier": "BlueDart"},
    "5090": {"id": "5090", "name": "Sam",   "status": "processing", "eta": "next week", "carrier": "-"},
}
TEMPLATES = {
    "delivery_delay": "Hi {name}, your order {id} has {status} and is due {eta}. Thanks for your patience.",
    "refund":         "Hi {name}, we've started the refund for order {id}. It will reflect in 5-7 days.",
}'''

def realcell(parts, demo):
    """A code cell = real-library imports/fixtures + a runnable demo (replaces the old shimcell)."""
    return code("\n\n".join(parts) + "\n\n" + demo)

NB = {}
def lab(nn, slug, level, title, mins, summary, concepts):
    def deco(fn):
        NB[nn] = dict(slug=slug, level=level, title=title, mins=mins,
                      summary=summary, concepts=concepts, build=fn)
        return fn
    return deco

# ============================================================ LAB 01
@lab(1, "lab-01-the-automation-pipeline", "Beginner",
     "The Automation Pipeline", 20,
     "Model the pipeline every task automation follows: trigger, gather, draft, validate, approve, act.",
     ["Pipeline", "Stages", "Checkpoint"])
def _l1(sol):
    return [
      header(1, "The Automation Pipeline", "Beginner", 20,
        ["Walk the six pipeline stages in order, from trigger to act",
         "See where the Day-3 loop lives (inside reason/draft)",
         "Mark the approval checkpoint that guards the irreversible act"],
        "The task-automation pipeline"),
      setup(1),
      md('''## Concept
Every task-automation agent, however complex, follows the **same pipeline** (deck slide 5):
**trigger** &rarr; **gather** &rarr; **draft** &rarr; **validate** &rarr; **approve** &rarr; **act**.
The Day-3 ReAct loop lives inside *reason/draft*; the outer stages &mdash; gather, validate,
approve &mdash; are what make it **reliable** and **safe**. The **approve** stage is a human
checkpoint that guards the one irreversible step: **act**.'''),
      code('''PIPELINE = ["trigger", "gather", "draft", "validate", "approve", "act"]
print("the shape of every automation:")
print(" -> ".join(PIPELINE))'''),
      md('''## Your Turn
Implement `next_stage` (what follows each stage) and `is_checkpoint` (the human gate before the
irreversible act), then `run_pipeline` walks the whole thing.'''),
      code(render([
        'PIPELINE = ["trigger", "gather", "draft", "validate", "approve", "act"]',
        "",
        "def next_stage(current):",
        "    i = PIPELINE.index(current)",
        {"s": '    return ___   # TODO: "done" if this is the last stage, else the next stage',
         "a": '    return "done" if i == len(PIPELINE) - 1 else PIPELINE[i + 1]'},
        "",
        "def is_checkpoint(stage):",
        '    # the human approval gate: a person must approve before the irreversible act',
        {"s": '    return ___   # TODO: True only for the "approve" stage',
         "a": '    return stage == "approve"'},
        "",
        "def run_pipeline():",
        '    order, stage = [], "trigger"',
        '    while stage != "done":',
        "        order.append(stage)",
        "        stage = next_stage(stage)",
        "    return order",
        "",
        "try:",
        "    print('after trigger ->', next_stage('trigger'))",
        "    print('after act     ->', next_stage('act'))",
        "    print('full run:', run_pipeline())",
        "    print('checkpoint at approve?', is_checkpoint('approve'))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("gather follows trigger", lambda: next_stage("trigger") == "gather")
expect_true("act is the last stage (-> done)", lambda: next_stage("act") == "done")
expect_true("the run walks all six stages in order", lambda: run_pipeline() == PIPELINE)
expect_true("approve is the human checkpoint", lambda: is_checkpoint("approve") is True)
expect_true("gather is not a checkpoint", lambda: is_checkpoint("gather") is False)'''),
      footer(1, "Trigger -> gather -> draft -> validate -> approve -> act. The outer stages are what turn a demo agent into an automation. Next: the gather stage -- grounding the task in real data."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-gather-context", "Beginner",
     "Gather Context with Tools", 20,
     "Ground the task first: wrap lookup_order and get_template as tools and gather context before drafting.",
     ["Gather-first", "Tools", "Grounding"])
def _l2(sol):
    return [
      header(2, "Gather Context with Tools", "Beginner", 20,
        ["Wrap lookup_order and get_template as @tool functions",
         "Gather the order + the reply template BEFORE drafting",
         "See why gather-first prevents hallucinated specifics"],
        "Grounding the task in real data"),
      setup(2),
      md('''## Concept
A general model doesn't know **your** client's order or **your** reply templates &mdash; so the agent
must **gather context first, then draft** (deck slide 6). Gathering happens through **tools** over
your systems: an orders DB, a template store, the CRM. An agent that drafts before it gathers
**hallucinates specifics**; one that grounds every claim in retrieved context is accurate and
auditable.'''),
      realcell([TOOL_IMPORT, EMAIL_FIXTURE],
        '''print("orders on file :", list(ORDERS))
print("templates on file:", list(TEMPLATES))'''),
      md('''## Your Turn
Complete the two gather tools and the `gather` step that pulls both before any drafting.'''),
      code(render([
        "from langchain_core.tools import tool",
        "",
        "@tool",
        "def lookup_order(order_id: str) -> dict:",
        '    """Look up an order\'s status, ETA and carrier by id."""',
        {"s": '    return ___   # TODO: the order dict for order_id, or {"status": "unknown"} if not found',
         "a": '    return ORDERS.get(order_id, {"status": "unknown"})'},
        "",
        "@tool",
        "def get_template(kind: str) -> str:",
        '    """Fetch a reply template by kind, e.g. delivery_delay or refund."""',
        {"s": '    return ___   # TODO: the template string for kind, or "" if none',
         "a": '    return TEMPLATES.get(kind, "")'},
        "",
        "def gather(order_id, kind):",
        '    # gather FIRST: pull the order AND the template before we draft anything',
        {"s": '    return {"order": ___, "template": ___}   # TODO: invoke each tool',
         "a": '    return {"order": lookup_order.invoke(order_id), "template": get_template.invoke(kind)}'},
        "",
        "try:",
        "    print('order 4471 :', lookup_order.invoke('4471'))",
        "    print('unknown    :', lookup_order.invoke('9999'))",
        "    ctx = gather('4471', 'delivery_delay')",
        "    print('gathered   :', ctx)",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("lookup_order finds a real order", lambda: lookup_order.invoke("4471")["status"] == "shipped")
expect_true("an unknown order degrades to 'unknown'", lambda: lookup_order.invoke("9999")["status"] == "unknown")
expect_true("get_template returns the delivery template", lambda: "{name}" in get_template.invoke("delivery_delay"))
expect_true("gather returns BOTH order and template", lambda: set(gather("4471", "delivery_delay")) == {"order", "template"})
expect_true("gather grounds on real data (ETA Friday)", lambda: gather("4471", "delivery_delay")["order"]["eta"] == "Friday")'''),
      footer(2, "Gather first, draft second. These are just Module-6 tools pointed at a real job -- the order and the template are the ground truth the draft will stand on."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-structured-output", "Beginner",
     "Structured Output, Not Prose", 20,
     "Return a machine-readable record (a defined shape) instead of prose, and check it is well-formed.",
     ["Structured output", "Schema", "Machine-readable"])
def _l3(sol):
    return [
      header(3, "Structured Output, Not Prose", "Beginner", 20,
        ["Turn a decision into a defined shape (a dict / JSON record)",
         "See why a machine can act on fields but not on a paragraph",
         "Check a record is well-formed before trusting it"],
        "Structured output, not prose"),
      setup(3),
      md('''## Concept
Prose is great for a human but terrible for automation &mdash; your code can't reliably act on it
(deck slide 7). The fix is **structured output**: ask for a **defined shape** (a record with fixed
fields) instead of a sentence. *"I think we should refund them, seems urgent"* becomes
`{"intent": "refund", "urgency": "high", "order_id": 4471}` &mdash; machine-readable, **validatable**,
composable. The mantra: **prose for humans, JSON for machines**.'''),
      code('''prose = "I think we should refund them, and it seems fairly urgent -- order 4471."
print("prose (a human reads this):", prose)
print("...but your code cannot reliably act on a paragraph.")'''),
      md('''## Your Turn
Build a **record** (the structured shape) and an `is_wellformed` check for the required fields.'''),
      code(render([
        'REQUIRED = ("order_id", "intent", "urgency")',
        "",
        "def as_record(order_id, intent, urgency):",
        '    # a machine-readable record instead of a prose sentence',
        {"s": '    return ___   # TODO: a dict with keys order_id, intent, urgency',
         "a": '    return {"order_id": order_id, "intent": intent, "urgency": urgency}'},
        "",
        "def is_wellformed(rec):",
        '    # well-formed = every required field is present AND order_id is not None',
        {"s": '    return all(k in rec for k in REQUIRED) and ___   # TODO: order_id must not be None',
         "a": '    return all(k in rec for k in REQUIRED) and rec["order_id"] is not None'},
        "",
        "try:",
        '    rec = as_record(4471, "refund", "high")',
        "    print('record   :', rec)",
        "    print('field    :', rec['intent'])",
        "    print('wellformed:', is_wellformed(rec))",
        '    print(\'missing id:\', is_wellformed({"order_id": None, "intent": "x", "urgency": "low"}))',
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("as_record builds all three fields", lambda: as_record(4471, "refund", "high") == {"order_id": 4471, "intent": "refund", "urgency": "high"})
expect_true("the record is machine-readable (a dict)", lambda: isinstance(as_record(1, "a", "b"), dict))
expect_true("fields are addressable by key", lambda: as_record(4471, "refund", "high")["intent"] == "refund")
expect_true("a full record is well-formed", lambda: is_wellformed(as_record(4471, "refund", "high")) is True)
expect_true("a record with a missing id is rejected", lambda: is_wellformed({"order_id": None, "intent": "x", "urgency": "low"}) is False)'''),
      footer(3, "A defined shape can be validated and fed to the next step; a paragraph can't. Structured output is the backbone of every reliable automation -- next we produce one by extraction."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-extract-fields", "Beginner",
     "Extract: Mess In, Structure Out", 25,
     "Pull order_id, intent and sentiment out of a messy client email into a tight schema; handle missing data.",
     ["Extract", "Tight schema", "Missing data"])
def _l4(sol):
    return [
      header(4, "Extract: Mess In, Structure Out", "Beginner", 25,
        ["Pull defined fields out of an unstructured email",
         "Use a closed set of intents; handle a missing order id",
         "Return the tight schema the rest of the pipeline consumes"],
        "Extract — mess in, structure out"),
      setup(4),
      md('''## Concept
**Extract** turns unstructured input into structured data (deck slide 10): an email *"my order from
last Tuesday still hasn't arrived, ref 4471, getting frustrated"* becomes
`{"order_id": 4471, "intent": "delivery", "sentiment": "negative"}`. Keys: a **tight schema** (only
the fields you'll use, intents from a **closed set**), **handle missing data** (return `None`, don't
invent an id), and it's usually the **first step** in the chain &mdash; extract &rarr; route &rarr;
draft.'''),
      code('''sample = "Hi, my order from last Tuesday still hasn't arrived, ref 4471, getting frustrated."
print("unstructured in:", sample)
print("we want out    : {order_id, intent, sentiment}")'''),
      md('''## Your Turn
Complete `extract`: pull the order id (digits), classify the intent from a closed set, and read a
rough sentiment.'''),
      code(render([
        'INTENTS = ("refund", "delivery", "cancel", "other")',
        "",
        "def extract(email):",
        "    text = email.lower()",
        '    # order id: the digits in the message, or None if there are none',
        '    digits = "".join(ch for ch in email if ch.isdigit())',
        {"s": '    order_id = ___   # TODO: int(digits) if we found any, else None',
         "a": '    order_id = int(digits) if digits else None'},
        '    # intent: map keywords to a label from the CLOSED set INTENTS',
        '    if "refund" in text or "money back" in text:',
        '        intent = "refund"',
        {"s": '    elif ___:   # TODO: a delivery-ish message (deliver / arrive / late / where is)',
         "a": '    elif any(w in text for w in ("deliver", "arrive", "late", "where is", "hasn\'t")):'},
        '        intent = "delivery"',
        '    elif "cancel" in text:',
        '        intent = "cancel"',
        "    else:",
        '        intent = "other"',
        '    # sentiment: negative if the customer sounds unhappy',
        {"s": '    sentiment = ___   # TODO: "negative" if any unhappy word is present, else "neutral"',
         "a": '    sentiment = "negative" if any(w in text for w in ("frustrated", "angry", "late", "still", "unhappy")) else "neutral"'},
        '    return {"order_id": order_id, "intent": intent, "sentiment": sentiment}',
        "",
        "try:",
        '    print(extract("my order 4471 still hasn\'t arrived, getting frustrated"))',
        '    print(extract("please cancel my subscription"))',
        '    print(extract("I want a refund"))',
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("pulls the order id from the text", lambda: extract("ref 4471 please")["order_id"] == 4471)
expect_true("a message with no id -> order_id is None", lambda: extract("where is my stuff?")["order_id"] is None)
expect_true("detects a delivery intent", lambda: extract("my order hasn't arrived, it's late")["intent"] == "delivery")
expect_true("detects a refund intent", lambda: extract("I want a refund")["intent"] == "refund")
expect_true("intent is always from the closed set", lambda: extract("hello there")["intent"] in ("refund", "delivery", "cancel", "other"))
expect_true("reads a negative sentiment", lambda: extract("I am frustrated, still no order")["sentiment"] == "negative")'''),
      footer(4, "Extract is the workhorse: it turns email, chat and forms into rows your systems can process. A tight schema plus missing-data handling is what makes it reliable enough to build on."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-route-the-query", "Beginner",
     "Route: Decide What Happens Next", 20,
     "Route an extracted query to the right team from a closed label set, and escalate hard cases to a human.",
     ["Route", "Closed labels", "Escalate"])
def _l5(sol):
    return [
      header(5, "Route: Decide What Happens Next", "Beginner", 20,
        ["Map an intent to a team from a fixed set (with an escape hatch)",
         "Escalate negative or unknown cases to a human",
         "Emit a label that drives the next branch of the workflow"],
        "Route — decide what happens next"),
      setup(5),
      md('''## Concept
**Route** decides what happens next and emits a **label from a fixed set** that drives a branch
(deck slide 11): which team, how urgent, auto-handle or escalate. The **closed list** is the trick
that makes an LLM a reliable classifier &mdash; include an **escape hatch** (`other` / `unsure`), and
a **fallback path** that routes low-confidence or high-stakes cases to a human.'''),
      code('''TEAMS = {"refund": "billing", "delivery": "logistics", "cancel": "billing", "other": "general"}
print("closed label set -> team:", TEAMS)'''),
      md('''## Your Turn
Complete `route`: pick the team from the closed map, and decide when to **escalate** to a human.'''),
      code(render([
        'TEAMS = {"refund": "billing", "delivery": "logistics", "cancel": "billing", "other": "general"}',
        "",
        "def route(record):",
        '    intent = record.get("intent", "other")',
        {"s": '    team = ___   # TODO: the team for intent, defaulting to "general" (the escape hatch)',
         "a": '    team = TEAMS.get(intent, "general")'},
        '    # escalate to a human when the customer is unhappy OR the intent is unknown',
        {"s": '    escalate = ___   # TODO: True if sentiment is negative or intent not in TEAMS',
         "a": '    escalate = record.get("sentiment") == "negative" or intent not in TEAMS'},
        '    return {"team": team, "escalate": escalate}',
        "",
        "try:",
        '    print("refund   ->", route({"intent": "refund", "sentiment": "neutral"}))',
        '    print("delivery ->", route({"intent": "delivery", "sentiment": "negative"}))',
        '    print("unknown  ->", route({"intent": "mystery", "sentiment": "neutral"}))',
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("a refund routes to billing", lambda: route({"intent": "refund", "sentiment": "neutral"})["team"] == "billing")
expect_true("a delivery routes to logistics", lambda: route({"intent": "delivery", "sentiment": "neutral"})["team"] == "logistics")
expect_true("an unknown intent falls back to general (escape hatch)", lambda: route({"intent": "mystery", "sentiment": "neutral"})["team"] == "general")
expect_true("a negative sentiment escalates to a human", lambda: route({"intent": "delivery", "sentiment": "negative"})["escalate"] is True)
expect_true("a neutral known case does not escalate", lambda: route({"intent": "refund", "sentiment": "neutral"})["escalate"] is False)'''),
      footer(5, "Routing makes one agent the front door to a whole system. Routing to the right specialist AGENT is the bridge to Module 8 -- for now it's the label that drives the branch."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-draft-a-reply", "Beginner",
     "Draft: Generate a Grounded Reply", 25,
     "Fill a grounded template with real order fields to draft an on-tone reply that invents nothing.",
     ["Draft", "Grounding", "Voice"])
def _l6(sol):
    return [
      header(6, "Draft: Generate a Grounded Reply", "Beginner", 25,
        ["Fill a reply template with the gathered order fields",
         "Keep it grounded -- use only fields you actually have",
         "Give the reply a consistent voice (tone & sign-off)"],
        "Draft — generate a work product"),
      setup(6),
      md('''## Concept
**Draft** turns gathered context into a work product a human will review (deck slide 9): a reply, a
summary, a proposal. Three keys: **ground it** (feed the real order &amp; template so it's specific,
not generic), **give it a voice** (tone, format, limits), and **keep the human** (a draft is a
suggestion, not a sent message). The failure mode to avoid: a draft that **invents** a date or a
policy because it wasn't grounded.'''),
      realcell([PROMPT_IMPORT, EMAIL_FIXTURE],
        '''print("template:", TEMPLATES["delivery_delay"])'''),
      md('''## Your Turn
Complete `draft_reply`: fill the grounded template from the order &mdash; never invent a field.'''),
      code(render([
        "from langchain_core.prompts import PromptTemplate",
        "",
        "def draft_reply(order, kind):",
        '    template = PromptTemplate.from_template(TEMPLATES[kind])',
        '    # ground the draft in the REAL order fields -- do not invent anything',
        {"s": '    return template.format(name=___, id=___, status=___, eta=___)   # TODO: from order',
         "a": '    return template.format(name=order["name"], id=order["id"], status=order["status"], eta=order["eta"])'},
        "",
        "try:",
        "    reply = draft_reply(ORDERS['4471'], 'delivery_delay')",
        "    print(reply)",
        "    print('---')",
        "    print('mentions the id? ', '4471' in reply)",
        "    print('grounded ETA?    ', 'Friday' in reply)",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the draft greets the customer by name", lambda: "Priya" in draft_reply(ORDERS["4471"], "delivery_delay"))
expect_true("the draft names the order id", lambda: "4471" in draft_reply(ORDERS["4471"], "delivery_delay"))
expect_true("the draft is grounded in the real ETA", lambda: "Friday" in draft_reply(ORDERS["4471"], "delivery_delay"))
expect_true("the draft invents no other date", lambda: "Monday" not in draft_reply(ORDERS["4471"], "delivery_delay"))
expect_true("the draft keeps its voice (a sign-off)", lambda: "Thanks" in draft_reply(ORDERS["4471"], "delivery_delay"))'''),
      footer(6, "A grounded draft is specific and correct; an ungrounded one invents facts. Draft agents are high-value and low-risk because the human still holds the pen -- which is why the email agent is the canonical first real-world lab."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-validate-output", "Intermediate",
     "Validate Before You Act", 30,
     "Never act on unchecked output: verify required fields, allowed values, and that the reply invents no dates.",
     ["Validation", "Allowed values", "No invented promises"])
def _l7(sol):
    return [
      header(7, "Validate Before You Act", "Intermediate", 30,
        ["Check the structured record has its required fields",
         "Reject values outside the allowed set",
         "Catch an ungrounded reply (an invented date) before it goes out"],
        "Reliability: validate, then act"),
      setup(7),
      md('''## Concept
The line between a demo and production is **validation** (deck slide 12): never trust the model
blindly. Check the record **parses**, the **required fields** are present, the values are in the
**allowed set**, and &mdash; crucially for a drafted reply &mdash; that it **invents no promises**
(the ETA in the reply must match the real order). If it fails validation, **don't act**.'''),
      code('''ALLOWED_INTENTS = {"refund", "delivery", "cancel", "other"}
good = {"order_id": 4471, "intent": "delivery", "reply": "...due Friday..."}
print("we will check records like:", good)'''),
      md('''## Your Turn
Complete `validate`: collect problems for a missing id, a bad intent, and an ungrounded ETA.'''),
      code(render([
        'ALLOWED_INTENTS = {"refund", "delivery", "cancel", "other"}',
        "",
        "def validate(rec, order):",
        "    problems = []",
        {"s": '    if ___:   # TODO: order_id is missing (None)',
         "a": '    if rec.get("order_id") is None:'},
        '        problems.append("missing order_id")',
        {"s": '    if ___:   # TODO: intent is not in the allowed set',
         "a": '    if rec.get("intent") not in ALLOWED_INTENTS:'},
        '        problems.append("bad intent")',
        '    # no invented promise: the real ETA must actually appear in the reply text',
        {"s": '    if ___:   # TODO: the order ETA is NOT present in rec["reply"]',
         "a": '    if order["eta"] not in rec.get("reply", ""):'},
        '        problems.append("ungrounded eta")',
        {"s": '    return {"ok": ___, "problems": problems}   # TODO: ok = no problems',
         "a": '    return {"ok": len(problems) == 0, "problems": problems}'},
        "",
        'ORDER = {"id": "4471", "eta": "Friday"}',
        "try:",
        '    ok = validate({"order_id": 4471, "intent": "delivery", "reply": "due Friday"}, ORDER)',
        '    bad = validate({"order_id": None, "intent": "sing", "reply": "due Monday"}, ORDER)',
        "    print('valid  ->', ok)",
        "    print('invalid->', bad)",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("a well-grounded record passes", lambda: validate({"order_id": 4471, "intent": "delivery", "reply": "due Friday"}, {"id": "4471", "eta": "Friday"})["ok"] is True)
expect_true("a missing order_id is caught", lambda: "missing order_id" in validate({"order_id": None, "intent": "delivery", "reply": "due Friday"}, {"id": "4471", "eta": "Friday"})["problems"])
expect_true("a bad intent is caught", lambda: "bad intent" in validate({"order_id": 1, "intent": "sing", "reply": "due Friday"}, {"id": "4471", "eta": "Friday"})["problems"])
expect_true("an invented date (wrong ETA) is caught", lambda: "ungrounded eta" in validate({"order_id": 1, "intent": "delivery", "reply": "due Monday"}, {"id": "4471", "eta": "Friday"})["problems"])
expect_true("ok is True only when there are no problems", lambda: validate({"order_id": 1, "intent": "delivery", "reply": "Friday"}, {"id": "4471", "eta": "Friday"})["ok"] and not validate({"order_id": None, "intent": "delivery", "reply": "Friday"}, {"id": "4471", "eta": "Friday"})["ok"])'''),
      footer(7, "Validate parses, fields, ranges, and grounding BEFORE you act. An automation that acts on unchecked output is a liability; one that validates first is something you can trust to run."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-retry-idempotency", "Intermediate",
     "Retry & Idempotency", 30,
     "Wrap a flaky call in a capped retry, and key each send so a re-run never double-sends.",
     ["Retry", "Cap", "Idempotency"])
def _l8(sol):
    return [
      header(8, "Retry & Idempotency", "Intermediate", 30,
        ["Retry a flaky call, but cap the attempts so it can't loop forever",
         "Make sending idempotent with a key, so a re-run is safe",
         "See why idempotency matters most for money & messages"],
        "Reliability: retry & idempotency"),
      setup(8),
      md('''## Concept
Models and tools are flaky, so wrap calls in a **retry** &mdash; but **cap** the attempts (deck slide
12). And design for **idempotency**: key each action so running the same task twice is **safe** and
never **double-sends** an email or **double-charges** a card. This is the subtlest and most important
discipline for anything that touches **money or messages**.'''),
      code('''# A helper that fails n_fail times, then succeeds -- to exercise the retry deterministically.
def flaky(n_fail):
    calls = {"n": 0}
    def f():
        calls["n"] += 1
        if calls["n"] <= n_fail:
            raise RuntimeError("transient")
        return "ok"
    return f
def raises(fn):
    try: fn(); return False
    except Exception: return True
print("helpers ready: flaky(n) fails n times then returns 'ok'")'''),
      md('''## Your Turn
Complete `with_retry` (capped) and `send_once` (idempotent via a key set).'''),
      code(render([
        "def with_retry(fn, max_attempts=3):",
        '    # call fn(); on failure retry up to max_attempts; raise the last error if all fail',
        "    last = None",
        "    for attempt in range(max_attempts):",
        "        try:",
        {"s": '            return ___   # TODO: call fn() and return its result',
         "a": '            return fn()'},
        "        except Exception as e:",
        "            last = e",
        {"s": '    raise ___   # TODO: re-raise the last error after the cap is hit',
         "a": '    raise last'},
        "",
        "def send_once(key, sent):",
        '    # idempotent: sending the same key twice must NOT double-send',
        {"s": '    if ___:   # TODO: this key was already sent',
         "a": '    if key in sent:'},
        '        return "already_sent"',
        "    sent.add(key)",
        '    return "sent"',
        "",
        "try:",
        "    print('first try ok   :', with_retry(flaky(0)))",
        "    print('after 2 fails  :', with_retry(flaky(2), 3))",
        "    print('exhausted raises:', raises(lambda: with_retry(flaky(5), 3)))",
        "    sent = set()",
        "    print('send 4471 (1st):', send_once('4471', sent))",
        "    print('send 4471 (2nd):', send_once('4471', sent))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("returns the result when the call succeeds", lambda: with_retry(flaky(0)) == "ok")
expect_true("succeeds after transient failures", lambda: with_retry(flaky(2), 3) == "ok")
expect_true("raises once attempts are exhausted", lambda: raises(lambda: with_retry(flaky(5), 3)))
expect_true("the first send goes out", lambda: send_once("4471", set()) == "sent")
expect_true("a duplicate send is suppressed (idempotent)", lambda: (lambda s: (send_once("4471", s), send_once("4471", s))[1])(set()) == "already_sent")'''),
      footer(8, "Retry with a cap, and key every irreversible action so a re-run is safe. Assume every step can fail -- and make failure safe and visible. Idempotency is what lets an automation run unattended."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-human-in-the-loop", "Intermediate",
     "Human-in-the-Loop: Draft ≠ Send", 30,
     "Separate drafting from sending: the agent emits a needs-approval draft and never holds a send tool.",
     ["Draft not send", "Approval gate", "Withhold the tool"])
def _l9(sol):
    return [
      header(9, "Human-in-the-Loop: Draft ≠ Send", "Intermediate", 30,
        ["Make the agent's output a DRAFT with a needs-approval flag",
         "Build the approval gate: approve -> send, reject -> revise",
         "Apply the strongest guardrail: withhold the send tool entirely"],
        "Human-in-the-loop: draft ≠ send"),
      setup(9),
      md('''## Concept
The golden rule for real-world agents: **separate drafting from sending** (deck slides 13, 16). The
agent gathers, reasons and drafts **autonomously** &mdash; none of that is irreversible &mdash; but the
**send** pauses for a human. The simplest, strongest guardrail is to **withhold the `send_email`
tool**: the agent literally **cannot send**, so a human always does that after approving.
**Draft is not send.**'''),
      code('''# The agent's toolset -- notice what is deliberately MISSING.
CANDIDATE_TOOLS = ["lookup_order", "get_template", "send_email"]  # send_email must NOT be given
print("what the agent COULD be given:", CANDIDATE_TOOLS)'''),
      md('''## Your Turn
Complete the draft flag, the approval gate, and the gather-only toolset (no send tool).'''),
      code(render([
        "def make_draft(reply):",
        '    # the agent\'s output is a DRAFT + a needs-approval flag -- never a sent mail',
        {"s": '    return {"reply": reply, "status": ___}   # TODO: the needs-approval flag',
         "a": '    return {"reply": reply, "status": "needs_approval"}'},
        "",
        "def gate(draft, approved):",
        '    # the human-in-the-loop gate: approve -> send, reject -> revise',
        '    if draft["status"] != "needs_approval":',
        '        return "invalid"',
        {"s": '    return ___   # TODO: "send" if approved else "revise"',
         "a": '    return "send" if approved else "revise"'},
        "",
        "def agent_tools():",
        '    # gather-only: the agent must NOT be given a send tool',
        {"s": '    return ___   # TODO: the two gather tools, WITHOUT send_email',
         "a": '    return ["lookup_order", "get_template"]'},
        "",
        "def agent_can_send():",
        '    return "send_email" in agent_tools()',
        "",
        "try:",
        '    d = make_draft("Hi Priya, your order 4471 is due Friday.")',
        "    print('draft   :', d)",
        "    print('approve ->', gate(d, True))",
        "    print('reject  ->', gate(d, False))",
        "    print('agent can send?', agent_can_send())",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the draft carries a needs-approval flag", lambda: make_draft("hi")["status"] == "needs_approval")
expect_true("the draft is never already 'sent'", lambda: make_draft("hi")["status"] != "sent")
expect_true("approval routes to send", lambda: gate(make_draft("hi"), True) == "send")
expect_true("rejection routes to revise", lambda: gate(make_draft("hi"), False) == "revise")
expect_true("the agent is NOT given a send tool", lambda: agent_can_send() is False)'''),
      footer(9, "The strongest human-in-the-loop guardrail is the simplest: don't give the agent the send tool. It gathers and drafts all day -- and a human keeps the send. Draft is not send."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-observability", "Advanced",
     "Observability: Log Every Run", 40,
     "Log every stage of a run (trigger, tools, draft, validation, decision) and measure the approval rate.",
     ["Observability", "Run log", "Metrics"])
def _l10(sol):
    return [
      header(10, "Observability: Log Every Run", "Advanced", 40,
        ["Record every stage of a run in an auditable log",
         "Read back the ordered trace for debugging",
         "Measure quality over a batch (the approval rate)"],
        "Failure modes & observability"),
      setup(10),
      md('''## Concept
You can't run unattended what you can't see (deck slide 18). **Observability** means logging every
run &mdash; the **trigger**, each **tool call &amp; observation**, the **draft**, the **validation**
result, and the **human decision**. That log lets you **debug** a bad output, **audit** what
happened, and **measure** quality over time (approval rate, edit rate). Real stacks &mdash;
**LangSmith / Langfuse** &mdash; capture exactly this; here you build the offline version.'''),
      code('''# One run produces a sequence of stage events; a batch of runs produces a metric.
print("we log: trigger -> gather -> draft -> validate -> approve, plus the human decision")'''),
      md('''## Your Turn
Complete the `RunLog` (record + read back the stages) and `approval_rate` over a batch.'''),
      code(render([
        "class RunLog:",
        "    def __init__(self):",
        "        self.events = []",
        "    def record(self, stage, detail):",
        {"s": '        ___   # TODO: append (stage, detail) to self.events',
         "a": '        self.events.append((stage, detail))'},
        "    def stages(self):",
        {"s": '        return ___   # TODO: just the stage names, in order',
         "a": '        return [s for s, _ in self.events]'},
        "",
        "def approval_rate(decisions):",
        '    # the fraction of runs a human approved ("send")',
        {"s": '    return ___   # TODO: count of "send" divided by the number of decisions',
         "a": '    return sum(1 for d in decisions if d == "send") / len(decisions)'},
        "",
        "try:",
        "    log = RunLog()",
        "    log.record('trigger', 'email 4471')",
        "    log.record('gather', 'lookup_order -> shipped')",
        "    log.record('draft', 'due Friday')",
        "    log.record('validate', 'ok')",
        "    log.record('approve', 'send')",
        "    print('trace stages:', log.stages())",
        "    print('approval rate:', approval_rate(['send', 'revise', 'send', 'send']))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("record appends an event", lambda: (lambda l: (l.record("trigger", "x"), len(l.events))[1])(RunLog()) == 1)
expect_true("a full run logs five stages", lambda: (lambda l: [l.record(s, "d") for s in ("trigger","gather","draft","validate","approve")] and len(l.events))(RunLog()) == 5)
expect_true("stages() returns them in order", lambda: (lambda l: [l.record(s, "d") for s in ("trigger","gather","draft")] and l.stages())(RunLog()) == ["trigger","gather","draft"])
expect_true("approval_rate is 0.5 on [send, revise]", lambda: approval_rate(["send", "revise"]) == 0.5)
expect_true("approval_rate is 1.0 when all approve", lambda: approval_rate(["send", "send"]) == 1.0)''')
      ,
      *optional_real(
        "See the REAL callback interface LangChain exposes (LangSmith / Langfuse capture full traces).",
        '''try:
    from langchain_core.callbacks import BaseCallbackHandler
    class PrintHandler(BaseCallbackHandler):
        def on_tool_end(self, output, **kw):
            print("tool ->", output)
    print("Real LangChain calls handlers like PrintHandler on every model/tool event.")
    print("For full run traces: set LANGCHAIN_TRACING_V2=true + LANGCHAIN_API_KEY (LangSmith),")
    print("or run Langfuse (this course's stack) and attach its callback handler.")
except Exception as e:
    print("Install langchain-core to use real callbacks -- skipping:", type(e).__name__)
print("The RunLog above already traced every stage offline.")'''),
      footer(10, "Log every run's trigger, tools, draft, validation and decision -- that's how you debug, audit and MEASURE an automation. Once you can measure it (approval rate), you can improve it. Day 5 goes deeper."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-assemble-email-agent", "Advanced",
     "Assemble the Email Agent", 35,
     "Bind gather-only tools into a real create_agent that can draft a grounded reply but has no way to send.",
     ["create_agent", "Gather-only", "needs_approval"])
def _l11(sol):
    return [
      header(11, "Assemble the Email Agent", "Advanced", 35,
        ["Bind gather-only tools into an agent with create_agent",
         "Withhold send_email so the agent cannot auto-send",
         "Wrap the draft as needs_approval, with its tool trace"],
        "The email-drafting agent, end to end"),
      setup(11),
      md('''## Concept
Now assemble the email agent from Module 6's pieces (deck slides 14&ndash;16): `@tool` gather tools bound
with **`create_agent`** (a runnable `CompiledStateGraph`). The agent gathers (`lookup_order`,
`get_template`) then drafts a reply. The key design choice: the tools list is **gather-only** &mdash;
`send_email` is **not** bound &mdash; and the run's output is wrapped as a **`needs_approval`** draft.
The agent did the tedious 90%; the human keeps the send.'''),
      realcell([TOOL_IMPORT, EMAIL_FIXTURE],
        '''from langchain_core.tools import tool

@tool
def lookup_order(order_id: str) -> dict:
    """Look up an order's status, ETA and carrier by id."""
    return ORDERS.get(order_id, {"status": "unknown"})
@tool
def get_template(kind: str) -> str:
    """Fetch a reply template by kind."""
    return TEMPLATES.get(kind, "")
@tool
def send_email(to: str, body: str) -> str:
    """Send an email. (Defined to show the capability -- but DELIBERATELY WITHHELD from the agent.)"""
    return "SENT"
print("gather tools ready:", lookup_order.name, "&", get_template.name, "| withheld:", send_email.name)'''),
      md('''## Your Turn
The guardrail here is what's **missing**: build the agent with **gather-only** tools (no `send_email`),
and wrap whatever it drafts as a **`needs_approval`** result. The draft text comes from the model at
run time (the optional cell), so the graded steps check the **wiring and the guardrail**, not the prose.'''),
      code(render([
        "from langchain_ollama import ChatOllama",
        "from langchain.agents import create_agent",
        "",
        "def gather_tools():",
        {"s": '    return ___   # TODO: gather-only -- lookup_order & get_template, NEVER send_email',
         "a": '    return [lookup_order, get_template]'},
        "",
        "def make_email_agent():",
        '    model = ChatOllama(model="llama3.2:1b")',
        {"s": '    return create_agent(model, ___)   # TODO: bind the gather-only tools',
         "a": '    return create_agent(model, gather_tools())'},
        "",
        "def handle_email(draft, tools_used):",
        '    # never auto-send: wrap the drafted reply as a result a human must approve',
        {"s": '    return {"draft": draft, "status": ___, "tools_used": tools_used}   # TODO: the needs-approval flag',
         "a": '    return {"draft": draft, "status": "needs_approval", "tools_used": tools_used}'},
        "",
        "try:",
        "    print('bound tools :', [t.name for t in gather_tools()])",
        "    print('can it send?:', 'send_email' in [t.name for t in gather_tools()])",
        "    print('agent type  :', type(make_email_agent()).__name__)",
        '    demo = handle_email("Hi Priya, your order 4471 is due Friday.", ["lookup_order", "get_template"])',
        "    print('wrapped     :', demo['status'], '| tools:', demo['tools_used'])",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the agent is a runnable CompiledStateGraph", lambda: type(make_email_agent()).__name__ == "CompiledStateGraph")
expect_true("it binds exactly the two gather tools", lambda: [t.name for t in gather_tools()] == ["lookup_order", "get_template"])
expect_true("the send tool is WITHHELD (the guardrail)", lambda: "send_email" not in [t.name for t in gather_tools()])
expect_true("send_email still EXISTS as a capability, just unbound", lambda: send_email.name == "send_email")
expect_true("a draft is wrapped as needs_approval, never sent", lambda: handle_email("d", [])["status"] == "needs_approval")
expect_true("the wrapper preserves the tool trace", lambda: handle_email("d", ["lookup_order"])["tools_used"] == ["lookup_order"])'''),
      *live(
        "Run the gather-only agent for real: it can look up and draft, but it has no way to send.",
        '''from langchain_core.messages import AIMessage
def tools_used(messages):
    return [tc["name"] for m in messages for tc in (getattr(m, "tool_calls", None) or [])]
try:
    if ollama_up():
        agent = make_email_agent()
        result = agent.invoke({"messages": [{"role": "user",
                 "content": "Look up order 4471, then draft a one-line status reply. Do not send anything."}]},
                 config={"recursion_limit": 8})
        draft = result["messages"][-1].content
        out = handle_email(draft, tools_used(result["messages"]))
        print("tools used:", out["tools_used"])
        print("status    :", out["status"], "(the agent has no send tool, so it cannot auto-send)")
        print("draft     :", out["draft"])
    else:
        print("No Ollama reachable -- skipping the live run. The gather-only wiring above is what matters:")
        print("send_email is defined but never bound, so the agent gathers & drafts but cannot send.")
except Exception as e:
    print("Live run skipped:", type(e).__name__)'''),
      footer(11, "The guardrail is what's MISSING from the tools list -- send_email is never bound, so the agent gathers and drafts but cannot send. Next: run the whole pipeline over a suite."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-email-drafting-agent", "Advanced",
     "Capstone: The Email-Drafting Agent", 45,
     "Chain extract -> route -> gather -> draft -> validate -> approval over a suite of client emails, and score it.",
     ["End-to-end pipeline", "Task suite", "Draft-not-send"])
def _l12(sol):
    return [
      header(12, "Capstone: The Email-Drafting Agent", "Advanced", 45,
        ["Chain the whole pipeline: extract, route, gather, draft, validate",
         "Never auto-send -- every result is a needs_approval draft",
         "Run it over a SUITE of client emails and score the outcomes"],
        "Now build it — Module 7 labs"),
      setup(12),
      md('''## Concept
Capstone: the **email-drafting agent** (the client's Lab 4.1), end to end. It **extracts** the
query's fields, **routes** it to a team, **gathers** the order + template, **drafts** a grounded
reply, **validates** it, and returns a **`needs_approval`** draft &mdash; it **never auto-sends**. You
run it over a **suite** of incoming emails and score the outcomes. The helpers below are the ones you
built through the module; you assemble them into `process` and score with `evaluate`.'''),
      realcell([PROMPT_IMPORT, EMAIL_FIXTURE],
        '''from langchain_core.prompts import PromptTemplate
# The pieces you built this module, provided here so you can assemble the whole agent.
def extract(email):
    text = email.lower()
    digits = "".join(ch for ch in email if ch.isdigit())
    order_id = digits if digits else None
    if "refund" in text: intent = "refund"
    elif any(w in text for w in ("deliver", "arrive", "late", "where is")): intent = "delivery"
    elif "cancel" in text: intent = "cancel"
    else: intent = "other"
    sentiment = "negative" if any(w in text for w in ("frustrated", "angry", "late", "still")) else "neutral"
    return {"order_id": order_id, "intent": intent, "sentiment": sentiment}

TEAMS = {"refund": "billing", "delivery": "logistics", "cancel": "billing", "other": "general"}
def route(rec):
    return {"team": TEAMS.get(rec["intent"], "general"),
            "escalate": rec["sentiment"] == "negative" or rec["intent"] not in TEAMS}

TEMPLATE_FOR = {"delivery": "delivery_delay", "refund": "refund"}
def draft(order, intent):
    kind = TEMPLATE_FOR.get(intent, "delivery_delay")
    return PromptTemplate.from_template(TEMPLATES[kind]).format(
        name=order["name"], id=order["id"], status=order["status"], eta=order["eta"])
def validate(reply, order):
    return order["eta"] in reply
print("helpers ready: extract, route, draft, validate + ORDERS/TEMPLATES")'''),
      md('''## Your Turn
Assemble `process` (chain the pipeline; never send) and `evaluate` (score the suite).'''),
      code(render([
        "def process(email):",
        "    rec    = extract(email)",
        "    routed = route(rec)",
        '    order  = ORDERS.get(rec["order_id"], {"id": rec["order_id"], "name": "there", "status": "unknown", "eta": "soon"})',
        {"s": '    reply  = ___   # TODO: draft a grounded reply for this order & intent',
         "a": '    reply  = draft(order, rec["intent"])'},
        "    ok     = validate(reply, order)",
        '    # never auto-send: a valid draft awaits approval; an invalid one needs a fix',
        {"s": '    status = ___   # TODO: "needs_approval" if ok else "needs_fix"',
         "a": '    status = "needs_approval" if ok else "needs_fix"'},
        '    return {"team": routed["team"], "escalate": routed["escalate"],',
        '            "draft": reply, "status": status}',
        "",
        "SUITE = [",
        '    {"email": "Where is my order 4471? It\'s late.", "team": "logistics"},',
        '    {"email": "Please refund order 5090",           "team": "billing"},',
        "]",
        "",
        "def evaluate():",
        '    # count suite emails routed to the expected team AND left as a draft (never sent)',
        {"s": '    solved = ___   # TODO: sum 1 per email where team matches and status starts with "needs_"',
         "a": '    solved = sum(1 for t in SUITE if process(t["email"])["team"] == t["team"] and process(t["email"])["status"].startswith("needs_"))'},
        "    return solved, len(SUITE)",
        "",
        "try:",
        "    for t in SUITE:",
        "        r = process(t['email'])",
        "        print(t['email'][:28], '->', r['team'], '|', r['status'])",
        "    print('score:', evaluate())",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("a delivery email routes to logistics", lambda: process("Where is my order 4471? It's late.")["team"] == "logistics")
expect_true("a refund email routes to billing", lambda: process("Please refund order 5090")["team"] == "billing")
expect_true("the delivery draft is grounded (ETA present)", lambda: "Friday" in process("Where is my order 4471? It's late.")["draft"])
expect_true("NO email is ever auto-sent (always needs_*)", lambda: all(process(t["email"])["status"].startswith("needs_") for t in SUITE))
expect_true("a frustrated customer is escalated", lambda: process("I am frustrated, order 4471 still late")["escalate"] is True)
expect_true("evaluate solves the whole suite", lambda: evaluate() == (2, 2))'''),
      *live(
        "Swap the template draft for a REAL model draft (Ollama / Groq) -- the bridge to Module 8.",
        '''try:
    if ollama_up():
        from langchain_ollama import ChatOllama
        llm = ChatOllama(model="llama3.2:1b")
        email = "Where is my order 4471? It's late."
        reply = llm.invoke("You are a support agent. Draft a short, polite reply (do NOT send): " + email).content
        print("REAL drafted reply:\\n", reply)
        print("\\nProduction shape: extract -> route -> gather (tools) -> draft (llm) -> validate -> human approves -> send.")
    else:
        print("No Ollama reachable -- skipping the live draft. The offline pipeline above already ran the whole suite")
        print("(extract -> route -> draft -> validate) and returned needs_approval drafts, never auto-sent.")
    print("Next: Module 8 -- when one agent isn't enough, route to specialist AGENTS (the customer-service chatbot).")
except Exception as e:
    print("Live draft skipped:", type(e).__name__)'''),
      footer(12, "You built the email-drafting agent end to end -- extract, route, gather, draft, validate -- and it never sends on its own. That's an agent that does a job you'd pay for. Next: Module 8 orchestrates a team of them."),
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
        banner = md(f'''> ## SOLUTION / ANSWER KEY &mdash; Lab 7.{nn}
> This is the **completed** notebook (all `___` blanks filled). For the student version, open
> [`../{info['slug']}.ipynb`](../{info['slug']}.ipynb). Trainer use &mdash; or self-check after you've tried it yourself.''')
        with open(os.path.join(SOL_DIR, fname), "w") as f:
            json.dump(notebook([banner] + info["build"](True)), f, indent=1, ensure_ascii=False)

print(f"Wrote {len(NB)} notebooks to {OUT_DIR}" + (f" and solutions to {SOL_DIR}" if SOL_DIR else ""))

with open(os.path.join(_HERE, "_meta.json"), "w") as f:
    json.dump({str(nn): {k: NB[nn][k] for k in ("slug","level","title","mins","summary","concepts")}
               for nn in NB}, f, indent=1)
