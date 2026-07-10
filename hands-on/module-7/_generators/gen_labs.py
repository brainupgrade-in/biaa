# -*- coding: utf-8 -*-
"""Generator for Day 4 Module 7 hands-on labs (12 notebooks) -- NEAR-REAL design.
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

Design: this is the "Task Automation with AI Agents" module. Participants HAVE a GROQ_API_KEY in
the repo .env. So the labs are NEAR-REAL, not stubs: the DRAFT step and the assembled email agent
are driven by a REAL hosted model (ChatGroq "openai/gpt-oss-20b", reliable tool-calling via
create_agent), and the student reads the REAL output/message trace. There is NO auto-grader -- each
lab ends with "Run it for real -> Read the trace/output -> Your turn (open task)".

Kept real & deterministic (NOT LLM stand-ins): the automation pipeline, the extract/route/coerce
schema logic, validation, retry/idempotency, the draft-not-send gate, and the run log. These are
legitimate rule-based Python -- not stubs -- so they stay. What changed from the graded version:
the mock/scripted policy and the [PASS]/[FAIL]/Score grader are gone; the draft + agent labs now
call a REAL Groq model; tools ALWAYS catch their own exceptions and RETURN a string.

The withheld-tool guardrail stays and is checked as REAL structure: `send_email` is defined but
NEVER bound to the agent, so the email agent drafts but has no way to send -- a human approves.

Student robustness (no grader): cells that EXERCISE the blanks are wrapped by guard()/runguard()
so an unfilled `___` prints a friendly note instead of crashing -- a student notebook runs
top-to-bottom, and a solution notebook runs the real thing. runguard() also self-skips (with a
note) when GROQ_API_KEY is unset, and retries with backoff on Groq rate limits (HTTP 429)."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day4-module7-task-automation.html"
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
    """Guard a 'run it for real' cell: skip cleanly if there's no GROQ_API_KEY, and if a blank is unfilled."""
    return ('if not groq_ready():\n'
            '    print("No GROQ_API_KEY -- add it to the repo .env (free key at console.groq.com), then re-run this cell.")\n'
            'else:\n'
            '    try:\n' + _indent(exercise, 8) +
            '\n    except Exception as e:\n        print("(Fill the ___ blanks above, then re-run.)", type(e).__name__)')

def setup(nn):
    return code(f'''# Setup -- run me first
import os, time, socket, pathlib
from dotenv import load_dotenv
load_dotenv(pathlib.Path("{REPO}/.env"), override=True)   # GROQ_API_KEY (+ other keys)

WORK = "/tmp/biaa-lab-07-{nn:02d}"
os.makedirs(WORK, exist_ok=True)

def groq_ready():
    """True if a GROQ_API_KEY is configured -- the 'Run it for real' cells self-skip if not."""
    return bool(os.environ.get("GROQ_API_KEY"))

from langchain_groq import ChatGroq
# Day-4 provider: a REAL hosted model with reliable tool-calling via create_agent.
MODEL = "openai/gpt-oss-20b"
llm = ChatGroq(model=MODEL, temperature=0) if groq_ready() else None

def with_backoff(fn, tries=4):
    """Run fn(); retry with backoff on Groq rate limits (HTTP 429). Other errors propagate."""
    last = None
    for attempt in range(tries):
        try:
            return fn()
        except Exception as e:
            last = e
            if "429" in str(e) or "rate limit" in str(e).lower() or "rate_limit" in str(e).lower():
                wait = 5 * (attempt + 1)
                print(f"(rate-limited -- retrying in {{wait}}s)")
                time.sleep(wait)
                continue
            raise
    raise last

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
    print("Groq ready | model:", MODEL, "| WORK:", WORK)
else:
    print("GROQ_API_KEY not set -- add it to the repo .env (free key at console.groq.com).")
    print("(The 'Run it for real' cells will print this note instead of crashing.)  WORK:", WORK)''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 7.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 4 &middot; Module 7 &mdash; Task Automation with AI Agents**

### What you'll do
{g}

> **How this lab works (near-real):** you have a `GROQ_API_KEY` in the repo `.env`. Read the **Concept**, fill the real `___` blanks in **Build it** (real pipeline logic, real tool bodies, the real draft/`create_agent` call), then **Run it for real** &mdash; a real Groq model drives the step over real tools &mdash; and **read the output/trace**. Finish with an open **Your turn**. There is **no auto-grader**; the goal is a working email agent and a trace you can read.

> **Framework note:** these labs use the **real** LangChain 1.x (`langchain`, `langchain-core`, `langchain-groq`) and a **real hosted model** (`ChatGroq("openai/gpt-oss-20b")` &mdash; reliable tool-calling via `create_agent`). If `GROQ_API_KEY` is unset, the run cells print how to set it instead of crashing. A `@tool` must **catch its own errors and return a string** &mdash; a tool that *raises* can abort the whole agent run. You are building the **email-drafting agent** (the client's Lab 4.1): it **drafts but never sends** &mdash; `send_email` is withheld and a human approves.

**Reference:** [Module 7 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 7 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 7 labs](./index.html) &nbsp;&middot;&nbsp; [Module 7 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def concept(text):   return md("## Concept\n" + text)
def buildmd(text):   return md("## Build it\n" + text)
def runmd(text):     return md("## Run it for real &amp; read the trace\n" + text + "\n\n_This calls the real `openai/gpt-oss-20b` via Groq. If `GROQ_API_KEY` is unset the cell prints how to set it instead of crashing._")
def noticemd(text):  return md("## What to notice\n" + text)
def yourturn(text):  return md("## Your turn (open task &mdash; no grader)\n" + text)

# ---- shared building blocks -----------------------------------------------------------------

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
    """A code cell = real-library imports/fixtures + a runnable demo."""
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
    DEFS = [
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
    ]
    EX = '''print("after trigger ->", next_stage("trigger"))
print("after act     ->", next_stage("act"))
print("full run:", run_pipeline())
print("checkpoint at approve?", is_checkpoint("approve"))'''
    return [
      header(1, "The Automation Pipeline", "Beginner", 20,
        ["Walk the six pipeline stages in order, from trigger to act",
         "See where the Day-3 loop lives (inside reason/draft)",
         "Mark the approval checkpoint that guards the irreversible act"],
        "The task-automation pipeline"),
      setup(1),
      concept('''Every task-automation agent, however complex, follows the **same pipeline** (deck slide 5):
**trigger** &rarr; **gather** &rarr; **draft** &rarr; **validate** &rarr; **approve** &rarr; **act**.
The Day-3 ReAct loop lives inside *reason/draft*; the outer stages &mdash; gather, validate,
approve &mdash; are what make it **reliable** and **safe**. The **approve** stage is a human
checkpoint that guards the one irreversible step: **act**. (This lab is pure Python &mdash; it's the
scaffold the real Groq-driven steps in later labs slot into.)'''),
      code('''PIPELINE = ["trigger", "gather", "draft", "validate", "approve", "act"]
print("the shape of every automation:")
print(" -> ".join(PIPELINE))'''),
      buildmd('''Implement `next_stage` (what follows each stage) and `is_checkpoint` (the human gate before the
irreversible act); `run_pipeline` then walks the whole thing.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- `run_pipeline()` walks all six stages in order &mdash; that ordering is the contract every later lab honours.
- `is_checkpoint("approve")` marks the one **human** gate; everything before it is autonomous, everything after it is irreversible.
- The `draft` stage is where the real model runs (Lab 6); `gather` is where real tools run (Lab 2).'''),
      yourturn('''Add a seventh stage &mdash; e.g. `"log"` after `act` &mdash; and re-run `run_pipeline()`. **What good looks
like:** the walk includes your new stage in the right place and `next_stage` still terminates at `"done"`.
Then ask yourself: which of your stages are reversible, and which one truly needs the human gate?'''),
      footer(1, "Trigger -> gather -> draft -> validate -> approve -> act. The outer stages are what turn a demo agent into an automation. Next: the gather stage -- grounding the task in real data with real tools."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-gather-context", "Beginner",
     "Gather Context with Tools", 20,
     "Wrap lookup_order and get_template as real @tools, then watch a real Groq agent gather context before drafting.",
     ["Gather-first", "Real tools", "Real agent"])
def _l2(sol):
    DEFS = [
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
    ]
    EX = '''print("order 4471 :", lookup_order.invoke("4471"))
print("unknown    :", lookup_order.invoke("9999"))
print("gathered   :", gather("4471", "delivery_delay"))'''
    RUN = '''from langchain.agents import create_agent
agent = create_agent(llm, tools=[lookup_order, get_template])
result = with_backoff(lambda: agent.invoke(
    {"messages": [("user", "Gather the status and ETA of order 4471 for a delivery update. Do not send anything.")]},
    config={"recursion_limit": 8}))
print_trace(result)'''
    return [
      header(2, "Gather Context with Tools", "Beginner", 20,
        ["Wrap lookup_order and get_template as @tool functions",
         "Gather the order + the reply template BEFORE drafting",
         "Watch a real Groq agent call YOUR gather tools from the trace"],
        "Grounding the task in real data"),
      setup(2),
      concept('''A general model doesn't know **your** client's order or **your** reply templates &mdash; so the agent
must **gather context first, then draft** (deck slide 6). Gathering happens through **tools** over
your systems: an orders DB, a template store, the CRM. An agent that drafts before it gathers
**hallucinates specifics**; one that grounds every claim in retrieved context is accurate and
auditable. Here you build real `@tool`s and watch a **real agent** call them.'''),
      realcell([TOOL_IMPORT, EMAIL_FIXTURE],
        '''print("orders on file :", list(ORDERS))
print("templates on file:", list(TEMPLATES))'''),
      buildmd('''Complete the two gather tools and the `gather` step that pulls both **before** any drafting.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Bind your two gather tools to a real Groq agent and ask it to gather order 4471. Read the trace: the model calls YOUR functions to ground itself before answering."),
      code(runguard(RUN)),
      noticemd('''- The trace shows **`TOOL CALL: lookup_order {'order_id': '4471'}`** &mdash; the real model chose to call your Python.
- Each **`OBS:`** line is what your tool returned; the model reads it, then answers with grounded specifics.
- Gather-first is why the reply can say "due Friday" truthfully &mdash; it retrieved that, it didn't invent it.'''),
      yourturn('''Ask the agent about an order that isn't on file (e.g. `9999`), or add a third gather tool (say
`order_history(order_id)`), bind it, and re-run. **What good looks like:** for the unknown order the tool
returns `{"status": "unknown"}` and the agent says so honestly instead of inventing an ETA.'''),
      footer(2, "Gather first, draft second. These are just tools pointed at a real job -- and a real Groq agent calls them to ground itself before it writes a word."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-structured-output", "Beginner",
     "Structured Output, Not Prose", 20,
     "Return a machine-readable record (a defined shape) instead of prose, and check it is well-formed.",
     ["Structured output", "Schema", "Machine-readable"])
def _l3(sol):
    DEFS = [
      'SCHEMA = {',
      '    "order_id": {"type": str, "default": None},',
      '    "intent":   {"type": str, "default": "other"},',
      '    "urgency":  {"type": str, "default": "low"},',
      '    "attempts": {"type": int, "default": 0},',
      '}',
      'REQUIRED = ("order_id", "intent")',
      "",
      "def coerce(raw):",
      "    out = {}",
      "    for field, spec in SCHEMA.items():",
      '        typ, default = spec["type"], spec["default"]',
      "        if field not in raw:",
      {"s": '            out[field] = ___   # TODO: a missing field takes its declared default',
       "a": '            out[field] = default'},
      "            continue",
      "        val = raw[field]",
      {"s": '        if ___:   # TODO: the value is present but NOT of the declared type',
       "a": '        if not isinstance(val, typ):'},
      "            try:",
      {"s": '                val = ___   # TODO: coerce val to the declared type',
       "a": '                val = typ(val)'},
      "            except (ValueError, TypeError):",
      "                val = default",
      "        out[field] = val",
      "    return out",
      "",
      "def is_valid(rec):",
      '    # required fields must be present AND non-None after coercion',
      {"s": '    return all(___ for f in REQUIRED)   # TODO: each REQUIRED field is present and not None',
       "a": '    return all(rec.get(f) is not None for f in REQUIRED)'},
    ]
    EX = '''print("coerced   :", coerce({"order_id": 4471, "urgency": "high"}))
print("defaults  :", coerce({"order_id": "5090"}))
print("valid?    :", is_valid(coerce({"order_id": "4471", "intent": "refund"})))
print("missing id:", is_valid(coerce({"intent": "refund"})))'''
    return [
      header(3, "Structured Output, Not Prose", "Beginner", 20,
        ["Define a SCHEMA: each field's declared type and default",
         "Coerce a messy record -- fill missing fields, fix wrong types",
         "Validate that the required fields ended up present"],
        "Structured output, not prose"),
      setup(3),
      concept('''Structured output is only useful if it's **well-shaped** &mdash; every field present, every value the
right type (deck slide 7). Downstream code (route, draft, validate) indexes `rec["order_id"]` and
`rec["intent"]`, so a record that's **missing a field** or carries a **wrong-typed value** breaks the
pipeline. The fix is a **schema**: declare each field's **type** and **default**, then **coerce** any
raw record into that shape &mdash; fill missing fields from their defaults, and convert wrong types (a
numeric `order_id` becomes the **string** the orders DB is keyed by). This is real, deterministic
plumbing &mdash; the model's messy output is what you'll coerce.'''),
      code('''raw = {"order_id": 4471, "urgency": "high"}   # order_id is an int; intent & attempts are missing
print("raw (messy, from an upstream extract):", raw)
print("we want a COMPLETE, correctly-typed record out.")'''),
      buildmd('''Complete `coerce` (fill defaults for missing fields; coerce wrong-typed values) and `is_valid`
(the required fields must end up present and non-None).'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- A wrong-typed `order_id` (the int `4471`) is coerced to the **string** `"4471"` &mdash; the type the orders DB is keyed by.
- Missing fields fall back to their **declared defaults**, so downstream `rec["attempts"]` never `KeyError`s.
- `is_valid` is the gate: a record still missing a required field is rejected before it can break a later stage.'''),
      yourturn('''Add a new field to `SCHEMA` (e.g. `"channel": {"type": str, "default": "email"}`) and feed `coerce`
records that omit it or give it the wrong type. **What good looks like:** the coerced record always has
your field, correctly typed, and `is_valid` still guards the required set.'''),
      footer(3, "A schema of typed fields with defaults turns a messy, half-filled record into something the pipeline can trust. Coerce first, validate second -- next we produce records by extraction."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-extract-fields", "Beginner",
     "Extract: Mess In, Structure Out", 25,
     "Pull order_id, intent and sentiment out of a messy client email into a tight schema; handle missing data.",
     ["Extract", "Tight schema", "Missing data"])
def _l4(sol):
    DEFS = [
      'INTENTS = ("refund", "delivery", "cancel", "other")',
      "",
      "def extract(email):",
      "    text = email.lower()",
      '    # order id: the digits in the message, or None if there are none',
      '    digits = "".join(ch for ch in email if ch.isdigit())',
      {"s": '    order_id = ___   # TODO: the digits as-is if we found any, else None (keep order_id a STRING -- the orders DB is keyed by strings)',
       "a": '    order_id = digits if digits else None'},
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
    ]
    EX = '''print(extract("my order 4471 still hasn't arrived, getting frustrated"))
print(extract("please cancel my subscription"))
print(extract("I want a refund"))
print(extract("where is my stuff?"))'''
    return [
      header(4, "Extract: Mess In, Structure Out", "Beginner", 25,
        ["Pull defined fields out of an unstructured email",
         "Use a closed set of intents; handle a missing order id",
         "Return the tight schema the rest of the pipeline consumes"],
        "Extract — mess in, structure out"),
      setup(4),
      concept('''**Extract** turns unstructured input into structured data (deck slide 10): an email *"my order from
last Tuesday still hasn't arrived, ref 4471, getting frustrated"* becomes
`{"order_id": "4471", "intent": "delivery", "sentiment": "negative"}`. Keys: a **tight schema** (only
the fields you'll use, intents from a **closed set**), **handle missing data** (return `None`, don't
invent an id), and **type consistency** &mdash; `order_id` is a **string** because the orders DB is
keyed by strings. Extract is usually the **first step** in the chain &mdash; extract &rarr; route
&rarr; draft. (A keyword extractor is deterministic and auditable; a model can extract too, but you
must still validate its output against a closed schema.)'''),
      code('''sample = "Hi, my order from last Tuesday still hasn't arrived, ref 4471, getting frustrated."
print("unstructured in:", sample)
print("we want out    : {order_id, intent, sentiment}")'''),
      buildmd('''Complete `extract`: pull the order id (digits), classify the intent from a closed set, and read a
rough sentiment.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- The order id comes out a **string** (`"4471"`), matching the DB key; a message with no digits yields `None`, not a made-up id.
- `intent` is always one of the **closed set** &mdash; that's what makes the label safe to branch on in the router.
- The keyword rules mis-read some phrasings (e.g. "never showed up") &mdash; a real, visible failure mode you'll see again in the capstone.'''),
      yourturn('''Feed `extract` a few of your own emails &mdash; especially awkward ones like *"my parcel never showed up"*
(no keyword hit) &mdash; and see where it mislabels. **What good looks like:** you can name exactly which
phrasings slip past the keywords, which tells you where a model-based extractor would earn its keep.'''),
      footer(4, "Extract is the workhorse: it turns email, chat and forms into rows your systems can process. A tight schema plus missing-data handling is what makes it reliable enough to build on."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-route-the-query", "Beginner",
     "Route: Decide What Happens Next", 20,
     "Route an extracted query to the right team from a closed label set, and escalate hard cases to a human.",
     ["Route", "Closed labels", "Escalate"])
def _l5(sol):
    DEFS = [
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
    ]
    EX = '''print("refund   ->", route({"intent": "refund", "sentiment": "neutral"}))
print("delivery ->", route({"intent": "delivery", "sentiment": "negative"}))
print("unknown  ->", route({"intent": "mystery", "sentiment": "neutral"}))'''
    return [
      header(5, "Route: Decide What Happens Next", "Beginner", 20,
        ["Map an intent to a team from a fixed set (with an escape hatch)",
         "Escalate negative or unknown cases to a human",
         "Emit a label that drives the next branch of the workflow"],
        "Route — decide what happens next"),
      setup(5),
      concept('''**Route** decides what happens next and emits a **label from a fixed set** that drives a branch
(deck slide 11): which team, how urgent, auto-handle or escalate. The **closed list** is the trick
that makes an LLM a reliable classifier &mdash; include an **escape hatch** (`other` / `unsure`), and
a **fallback path** that routes low-confidence or high-stakes cases to a human. (Deterministic
routing here; routing to a specialist *agent* is Module 8.)'''),
      code('''TEAMS = {"refund": "billing", "delivery": "logistics", "cancel": "billing", "other": "general"}
print("closed label set -> team:", TEAMS)'''),
      buildmd('''Complete `route`: pick the team from the closed map, and decide when to **escalate** to a human.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- An unknown intent falls back to `general` via the **escape hatch** &mdash; the router never crashes on a label it hasn't seen.
- A **negative** sentiment escalates to a human even when the team is known &mdash; the high-stakes fallback path.
- The emitted `{team, escalate}` is the label the rest of the workflow branches on; keep it small and closed.'''),
      yourturn('''Add a new intent/team pair (e.g. `"billing_query": "billing"`) or a stricter escalation rule (escalate
any `refund` over a threshold). **What good looks like:** known intents route deterministically, unknowns
fall to `general`, and the cases you'd want a human to see are the ones that get `escalate=True`.'''),
      footer(5, "Routing makes one agent the front door to a whole system. Routing to the right specialist AGENT is the bridge to Module 8 -- for now it's the label that drives the branch."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-draft-a-reply", "Beginner",
     "Draft: Generate a Grounded Reply", 25,
     "Ground a prompt in real order fields and call a REAL Groq model to draft an on-tone reply that invents nothing.",
     ["Draft", "Grounding", "Real model"])
def _l6(sol):
    DEFS = [
      "from langchain_core.prompts import PromptTemplate",
      "",
      "DRAFT_PROMPT = PromptTemplate.from_template(",
      '    "You are a customer-support agent. Using ONLY these order facts, write a short, polite reply.\\n"',
      '    "Invent no date or fact that is not given below.\\n"',
      '    "Customer name: {name}\\nOrder id: {id}\\nStatus: {status}\\nETA: {eta}\\nReply:")',
      "",
      "def build_prompt(order):",
      '    # ground the draft in the REAL order fields -- never invent anything',
      {"s": '    return DRAFT_PROMPT.format(name=___, id=___, status=___, eta=___)   # TODO: from order',
       "a": '    return DRAFT_PROMPT.format(name=order["name"], id=order["id"], status=order["status"], eta=order["eta"])'},
      "",
      "def draft_reply(order):",
      '    """Ask the REAL Groq model to draft a reply, grounded in this order."""',
      {"s": '    return ___   # TODO: with_backoff(lambda: llm.invoke(build_prompt(order)).content)',
       "a": '    return with_backoff(lambda: llm.invoke(build_prompt(order)).content)'},
    ]
    EX = '''# No model call here -- just inspect the grounded prompt the model will receive:
print(build_prompt(ORDERS["4471"]))'''
    RUN = '''reply = draft_reply(ORDERS["4471"])
print(reply)
print("---")
print("mentions the id? ", "4471" in reply)
print("grounded ETA?    ", "Friday" in reply)'''
    return [
      header(6, "Draft: Generate a Grounded Reply", "Beginner", 25,
        ["Build a prompt grounded in the gathered order fields",
         "Call a REAL Groq model to draft the reply",
         "Check the draft is grounded -- it uses only fields you gave it"],
        "Draft — generate a work product"),
      setup(6),
      concept('''**Draft** turns gathered context into a work product a human will review (deck slide 9): a reply, a
summary, a proposal. Three keys: **ground it** (feed the real order so it's specific, not generic),
**give it a voice** (tone, format, limits &mdash; set in the prompt), and **keep the human** (a draft
is a suggestion, not a sent message). The failure mode to avoid: a draft that **invents** a date or a
policy because it wasn't grounded. Here a **real Groq model** writes the draft &mdash; grounded in the
order fields you pass in.'''),
      realcell([PROMPT_IMPORT, EMAIL_FIXTURE],
        '''print("order to ground on:", ORDERS["4471"])'''),
      buildmd('''Complete `build_prompt` (fill the grounded prompt from the order &mdash; never invent a field) and
`draft_reply` (call the real model on it).'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Call the real Groq model through `draft_reply()` and read the reply it writes &mdash; grounded in the order you gave it."),
      code(runguard(RUN)),
      noticemd('''- The reply is written by the **real model**, yet it names the real order id and the real ETA (`Friday`) &mdash; because the prompt grounded it.
- Nothing in the prompt says "Friday" is optional; the instruction *"invent no date not given"* is the guardrail against a hallucinated promise.
- Change the ETA in `ORDERS["4471"]` and re-run: the draft follows the data. That's grounding, not luck.'''),
      yourturn('''Change the **voice** in `DRAFT_PROMPT` &mdash; make it warmer, add a sign-off, cap it at two sentences,
or draft in another language &mdash; and re-run `draft_reply()`. **What good looks like:** the style changes
with your prompt while the **facts stay grounded** (id and ETA still correct). Try feeding `ORDERS["5090"]`
(a different order) and confirm the draft tracks *its* fields.'''),
      footer(6, "A grounded draft is specific and correct; an ungrounded one invents facts. Draft agents are high-value and low-risk because the human still holds the pen -- which is why the email agent is the canonical first real-world lab."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-validate-output", "Intermediate",
     "Validate Before You Act", 30,
     "Never act on unchecked output: verify required fields, allowed values, and that the reply invents no dates.",
     ["Validation", "Allowed values", "No invented promises"])
def _l7(sol):
    DEFS = [
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
    ]
    EX = '''ORDER = {"id": "4471", "eta": "Friday"}
print("valid  ->", validate({"order_id": "4471", "intent": "delivery", "reply": "due Friday"}, ORDER))
print("invalid->", validate({"order_id": None, "intent": "sing", "reply": "due Monday"}, ORDER))'''
    return [
      header(7, "Validate Before You Act", "Intermediate", 30,
        ["Check the structured record has its required fields",
         "Reject values outside the allowed set",
         "Catch an ungrounded reply (an invented date) before it goes out"],
        "Reliability: validate, then act"),
      setup(7),
      concept('''The line between a demo and production is **validation** (deck slide 12): never trust the model
blindly. Check the record **parses**, the **required fields** are present, the values are in the
**allowed set**, and &mdash; crucially for a drafted reply &mdash; that it **invents no promises**
(the ETA in the reply must match the real order). If it fails validation, **don't act**. This runs on
the real model's draft output &mdash; it's the safety net under the LLM.'''),
      code('''ALLOWED_INTENTS = {"refund", "delivery", "cancel", "other"}
good = {"order_id": "4471", "intent": "delivery", "reply": "...due Friday..."}
print("we will check records like:", good)'''),
      buildmd('''Complete `validate`: collect problems for a missing id, a bad intent, and an ungrounded ETA.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- The **ungrounded eta** check is the important one: it catches a draft that promised "Monday" when the order says "Friday".
- Because `ok` is just *no problems*, one failing check is enough to **stop the act** &mdash; fail-closed, not fail-open.
- Run this on the real draft from Lab 6 and you have a model-agnostic guard: it doesn't trust the LLM, it checks it.'''),
      yourturn('''Take a real reply from Lab 6's `draft_reply` and validate it against the order. Then deliberately corrupt
it (swap the ETA) and re-validate. **What good looks like:** the honest draft passes; the tampered one is
caught as `ungrounded eta`. Add one more check of your own &mdash; e.g. reject a reply that's suspiciously long.'''),
      footer(7, "Validate parses, fields, ranges, and grounding BEFORE you act. An automation that acts on unchecked output is a liability; one that validates first is something you can trust to run."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-retry-idempotency", "Intermediate",
     "Retry & Idempotency", 30,
     "Wrap a flaky call in a capped retry, and key each send so a re-run never double-sends.",
     ["Retry", "Cap", "Idempotency"])
def _l8(sol):
    DEFS = [
      "import hashlib",
      "",
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
      "def send_key(order_id, draft):",
      '    # the idempotency key ties the EXACT draft to its order -- re-sending the same one is a no-op',
      '    h = hashlib.sha256(draft.encode()).hexdigest()[:8]',
      {"s": '    return ___   # TODO: combine the order id and the draft hash h into one key string',
       "a": '    return f"{order_id}:{h}"'},
      "",
      "def send_once(key, sent):",
      '    # idempotent: sending the same key twice must NOT double-send',
      {"s": '    if ___:   # TODO: this key was already sent',
       "a": '    if key in sent:'},
      '        return "already_sent"',
      "    sent.add(key)",
      '    return "sent"',
    ]
    EX = '''print("first try ok   :", with_retry(flaky_lookup("4471", 0))["status"])
print("after 2 fails  :", with_retry(flaky_lookup("4471", 2), 3)["status"])
print("exhausted raises:", raises(lambda: with_retry(flaky_lookup("4471", 5), 3)))
k = send_key("4471", "Hi Priya, your order 4471 is due Friday.")
print("send key        :", k)
sent = set()
print("send (1st)      :", send_once(k, sent))
print("send (2nd)      :", send_once(k, sent))'''
    return [
      header(8, "Retry & Idempotency", "Intermediate", 30,
        ["Retry a flaky order lookup, but cap the attempts so it can't loop forever",
         "Make sending idempotent with an order+draft key, so a re-run is safe",
         "See why idempotency matters most for money & messages"],
        "Reliability: retry & idempotency"),
      setup(8),
      concept('''Models and tools are flaky, so wrap calls in a **retry** &mdash; but **cap** the attempts (deck slide
12). And design for **idempotency**: key each action so running the same task twice is **safe** and
never **double-sends** an email or **double-charges** a card. This is the subtlest and most important
discipline for anything that touches **money or messages**. (Note: the `with_backoff` in your Setup
cell is exactly this pattern applied to Groq's rate limits.)'''),
      code('''# A flaky order lookup: the network hiccups n_fail times, then returns the order.
import hashlib
def flaky_lookup(order_id, n_fail):
    calls = {"n": 0}
    def f():
        calls["n"] += 1
        if calls["n"] <= n_fail:
            raise RuntimeError("transient network error")
        return {"id": order_id, "status": "shipped", "eta": "Friday"}
    return f
def raises(fn):
    try: fn(); return False
    except Exception: return True
print("helpers ready: flaky_lookup(id, n) fails n times, then returns the order dict")'''),
      buildmd('''Complete `with_retry` (capped), `send_key` (the idempotency key from the order id + a draft hash),
and `send_once` (idempotent via the key set).'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- `with_retry` succeeds *after* transient failures but **raises once the cap is hit** &mdash; bounded, never an infinite loop.
- `send_key` ties the **exact draft** to its order; a different draft yields a different key, so an edited reply is a new send.
- `send_once` makes the second identical send a **no-op** &mdash; the property that lets an automation re-run safely.'''),
      yourturn('''Change `send_key` to ignore the draft (key on `order_id` alone) and watch what breaks: a legitimately
*revised* reply to the same order would now be suppressed. **What good looks like:** you can articulate why
the key must include the draft hash &mdash; idempotency should block *duplicates*, not *revisions*.'''),
      footer(8, "Retry with a cap, and key every irreversible action so a re-run is safe. Assume every step can fail -- and make failure safe and visible. Idempotency is what lets an automation run unattended."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-human-in-the-loop", "Intermediate",
     "Human-in-the-Loop: Draft ≠ Send", 30,
     "Separate drafting from sending: the agent emits a needs-approval draft and never holds a send tool.",
     ["Draft not send", "Approval gate", "Withhold the tool"])
def _l9(sol):
    DEFS = [
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
    ]
    EX = '''d = make_draft("Hi Priya, your order 4471 is due Friday.")
print("draft   :", d)
print("approve ->", gate(d, True))
print("reject  ->", gate(d, False))
print("agent can send?", agent_can_send())'''
    return [
      header(9, "Human-in-the-Loop: Draft ≠ Send", "Intermediate", 30,
        ["Make the agent's output a DRAFT with a needs-approval flag",
         "Build the approval gate: approve -> send, reject -> revise",
         "Apply the strongest guardrail: withhold the send tool entirely"],
        "Human-in-the-loop: draft ≠ send"),
      setup(9),
      concept('''The golden rule for real-world agents: **separate drafting from sending** (deck slides 13, 16). The
agent gathers, reasons and drafts **autonomously** &mdash; none of that is irreversible &mdash; but the
**send** pauses for a human. The simplest, strongest guardrail is to **withhold the `send_email`
tool**: the agent literally **cannot send**, so a human always does that after approving.
**Draft is not send.** (In Lab 11 you'll enforce this on the *real* Groq agent by never binding
`send_email`.)'''),
      code('''# The agent's toolset -- notice what is deliberately MISSING.
CANDIDATE_TOOLS = ["lookup_order", "get_template", "send_email"]  # send_email must NOT be given
print("what the agent COULD be given:", CANDIDATE_TOOLS)'''),
      buildmd('''Complete the draft flag, the approval gate, and the gather-only toolset (no send tool).'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- The draft carries **`needs_approval`**, never `sent` &mdash; the output shape itself encodes "a human must look".
- `gate` routes approve&rarr;send / reject&rarr;revise; the *send* only ever happens on the far side of a human.
- `agent_can_send()` is **False**: the strongest guardrail is structural &mdash; the tool simply isn't in the list.'''),
      yourturn('''Add a third state to `gate` &mdash; e.g. `"edit"` when a human tweaks the reply before sending &mdash; and
decide what `status` an edited draft carries. **What good looks like:** every path still ends with a human
action for the send, and there is no code path where the agent sends on its own.'''),
      footer(9, "The strongest human-in-the-loop guardrail is the simplest: don't give the agent the send tool. It gathers and drafts all day -- and a human keeps the send. Draft is not send."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-observability", "Advanced",
     "Observability: Log Every Run", 40,
     "Log every stage of a run (trigger, tools, draft, validation, decision) and measure the approval rate.",
     ["Observability", "Run log", "Metrics"])
def _l10(sol):
    DEFS = [
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
    ]
    EX = '''log = RunLog()
log.record("trigger", "email 4471")
log.record("gather", "lookup_order -> shipped")
log.record("draft", "due Friday")
log.record("validate", "ok")
log.record("approve", "send")
print("trace stages:", log.stages())
print("approval rate:", approval_rate(["send", "revise", "send", "send"]))'''
    return [
      header(10, "Observability: Log Every Run", "Advanced", 40,
        ["Record every stage of a run in an auditable log",
         "Read back the ordered trace for debugging",
         "Measure quality over a batch (the approval rate)"],
        "Failure modes & observability"),
      setup(10),
      concept('''You can't run unattended what you can't see (deck slide 18). **Observability** means logging every
run &mdash; the **trigger**, each **tool call &amp; observation**, the **draft**, the **validation**
result, and the **human decision**. That log lets you **debug** a bad output, **audit** what
happened, and **measure** quality over time (approval rate, edit rate). Real stacks &mdash;
**LangSmith / Langfuse** &mdash; capture exactly this via LangChain callbacks; here you build the
minimal offline version, and it drops straight onto the real agent trace from Lab 11.'''),
      code('''# One run produces a sequence of stage events; a batch of runs produces a metric.
print("we log: trigger -> gather -> draft -> validate -> approve, plus the human decision")'''),
      buildmd('''Complete the `RunLog` (record + read back the stages) and `approval_rate` over a batch.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- `stages()` reads the run back in order &mdash; the same shape as an agent's message trace, which is your #1 debugging surface.
- `approval_rate` turns a pile of runs into **one number** you can track; a falling rate means the drafts are getting worse.
- LangChain's real `BaseCallbackHandler` fires on every tool start/end &mdash; the same events, captured automatically by LangSmith/Langfuse.'''),
      yourturn('''Extend `RunLog` to also record the *tool arguments* on each `gather` event, then run it over a couple of
Lab 6 drafts and compute the approval rate you'd assign. **What good looks like:** from the log alone you
can reconstruct exactly what each run did &mdash; and you have a metric that would tell you if quality slipped.'''),
      footer(10, "Log every run's trigger, tools, draft, validation and decision -- that's how you debug, audit and MEASURE an automation. Once you can measure it (approval rate), you can improve it. Day 5 goes deeper."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-assemble-email-agent", "Advanced",
     "Assemble the Email Agent", 35,
     "Bind gather-only tools into a REAL Groq create_agent that can draft a grounded reply but has no way to send.",
     ["create_agent", "Gather-only", "needs_approval"])
def _l11(sol):
    DEFS = [
      "from langchain.agents import create_agent",
      "",
      "def gather_tools():",
      {"s": '    return ___   # TODO: gather-only -- lookup_order & get_template, NEVER send_email',
       "a": '    return [lookup_order, get_template]'},
      "",
      "def make_email_agent():",
      '    # bind the REAL Groq model to the gather-only tools',
      {"s": '    return create_agent(llm, ___)   # TODO: bind the gather-only tools',
       "a": '    return create_agent(llm, gather_tools())'},
      "",
      "def handle_email(draft, tools_used):",
      '    # never auto-send: wrap the drafted reply as a result a human must approve',
      {"s": '    return {"draft": draft, "status": ___, "tools_used": tools_used}   # TODO: the needs-approval flag',
       "a": '    return {"draft": draft, "status": "needs_approval", "tools_used": tools_used}'},
    ]
    EX = '''# Structure checks -- no model call needed:
print("bound tools :", [t.name for t in gather_tools()])
print("can it send?:", "send_email" in [t.name for t in gather_tools()])
print("send_email still EXISTS as a capability, just unbound:", send_email.name)
demo = handle_email("Hi Priya, your order 4471 is due Friday.", ["lookup_order"])
print("wrapped     :", demo["status"], "| tools:", demo["tools_used"])'''
    RUN = '''from langchain_core.messages import AIMessage
def tools_used(messages):
    return [tc["name"] for m in messages for tc in (getattr(m, "tool_calls", None) or [])]

agent = make_email_agent()
result = with_backoff(lambda: agent.invoke(
    {"messages": [("user",
        "Look up order 4471, then draft a one-line status reply for the customer. Do not send anything.")]},
    config={"recursion_limit": 8}))
print_trace(result)
print("---")
out = handle_email(result["messages"][-1].content, tools_used(result["messages"]))
print("tools used:", out["tools_used"])
print("status    :", out["status"], "(the agent has no send tool, so it cannot auto-send)")'''
    return [
      header(11, "Assemble the Email Agent", "Advanced", 35,
        ["Bind gather-only tools into a real Groq agent with create_agent",
         "Withhold send_email so the agent cannot auto-send",
         "Run it for real: it gathers & drafts, and you wrap it needs_approval"],
        "The email-drafting agent, end to end"),
      setup(11),
      concept('''Now assemble the email agent (deck slides 14&ndash;16): `@tool` gather tools bound with
**`create_agent`** (a runnable `CompiledStateGraph`) over a **real Groq model**. The agent gathers
(`lookup_order`, `get_template`) then drafts a reply. The key design choice: the tools list is
**gather-only** &mdash; `send_email` is **defined but not bound** &mdash; and the run's output is
wrapped as a **`needs_approval`** draft. The agent did the tedious 90%; the human keeps the send.'''),
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
      buildmd('''The guardrail here is what's **missing**: build the agent with **gather-only** tools (no `send_email`),
and wrap whatever it drafts as a **`needs_approval`** result.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Run the gather-only agent for real: it looks up the order and drafts a reply &mdash; and it has no send tool, so it cannot auto-send."),
      code(runguard(RUN)),
      noticemd('''- The trace shows **`TOOL CALL: lookup_order`** then a drafted reply &mdash; a real Groq agent doing the gather-then-draft job.
- The bound list is **gather-only**: `send_email` is defined (it exists as a capability) but never passed to `create_agent`, so the agent **cannot send**.
- The output is wrapped **`needs_approval`** &mdash; the agent did the work; a human still holds the send.'''),
      yourturn('''Try (carefully) *adding* `send_email` to `gather_tools()` and re-running &mdash; then put it back. **What good
looks like:** you can see that binding the send tool is the ONLY thing standing between "drafts for a human"
and "sends on its own", which is exactly why the guardrail is *withhold the tool*. Restore the gather-only list.'''),
      footer(11, "The guardrail is what's MISSING from the tools list -- send_email is never bound, so the real agent gathers and drafts but cannot send. Next: run the whole pipeline over a suite."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-email-drafting-agent", "Advanced",
     "Capstone: The Email-Drafting Agent", 45,
     "Chain extract -> route -> gather -> draft (real Groq) -> validate over a suite of client emails; never auto-send.",
     ["End-to-end pipeline", "Task suite", "Draft-not-send"])
def _l12(sol):
    DEFS = [
      "def process(email):",
      "    rec    = extract(email)",
      "    routed = route(rec)",
      '    # gather via the SAME tool the Lab 7.11 agent is built from (reuse, not re-implement)',
      '    found  = lookup_order.invoke(rec["order_id"]) if rec["order_id"] else {}',
      '    order  = found if found.get("id") else {"id": rec["order_id"], "name": "there", "status": "unknown", "eta": "soon"}',
      {"s": '    reply  = ___   # TODO: draft a grounded reply for this order with the REAL model (draft(order))',
       "a": '    reply  = draft(order)'},
      "    ok     = validate(reply, order)",
      '    # never auto-send: a valid draft awaits approval; an invalid one needs a fix',
      {"s": '    status = ___   # TODO: "needs_approval" if ok else "needs_fix"',
       "a": '    status = "needs_approval" if ok else "needs_fix"'},
      '    return {"team": routed["team"], "escalate": routed["escalate"],',
      '            "draft": reply, "status": status}',
      "",
      "SUITE = [",
      '    "Where is my order 4471? It\'s late.",',
      '    "Please refund order 5090",',
      '    "I want to cancel order 4471, I\'m so frustrated",',
      "]",
    ]
    EX = '''# Structure check (no model call): the capstone reuses the Lab 7.11 gather-only agent.
print("agent type      :", type(make_email_agent()).__name__)
print("still withholds send_email:", "send_email" not in [t.name for t in gather_tools()])'''
    RUN = '''for email in SUITE:
    r = process(email)
    print("EMAIL:", email)
    print("  team:", r["team"], "| escalate:", r["escalate"], "| status:", r["status"])
    print("  draft:", r["draft"][:140].replace(chr(10), " "))
    print()
print("Every result is needs_approval / needs_fix -- the agent NEVER auto-sends.")'''
    return [
      header(12, "Capstone: The Email-Drafting Agent", "Advanced", 45,
        ["Chain the pipeline: extract, route, gather, draft (real Groq), validate",
         "Never auto-send -- every result is a needs_approval draft",
         "Run it over a SUITE of client emails and read the real drafts"],
        "Now build it — Module 7 labs"),
      setup(12),
      concept('''Capstone: the **email-drafting agent** (the client's Lab 4.1), end to end. It **extracts** the
query's fields, **routes** it to a team, **gathers** the order via the **gather-only tool** the Lab
7.11 agent is built from (`send_email` still withheld), **drafts** a grounded reply with the **real
Groq model**, **validates** it, and returns a **`needs_approval`** draft &mdash; it **never
auto-sends**. You run it over a **suite of client emails** and read the real drafts. The helpers below
are the ones you built through the module; you assemble them into `process`.'''),
      realcell([PROMPT_IMPORT, EMAIL_FIXTURE],
        '''from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain.agents import create_agent

# --- The pipeline pieces you built this module (provided so you can assemble the whole agent) ---
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

DRAFT_PROMPT = PromptTemplate.from_template(
    "You are a customer-support agent. Using ONLY these order facts, write a short, polite reply.\\n"
    "Invent no date or fact that is not given below.\\n"
    "Customer name: {name}\\nOrder id: {id}\\nStatus: {status}\\nETA: {eta}\\nReply:")
def draft(order):
    # the DRAFT step calls the REAL Groq model, grounded in the order
    return with_backoff(lambda: llm.invoke(DRAFT_PROMPT.format(
        name=order["name"], id=order["id"], status=order["status"], eta=order["eta"])).content)
def validate(reply, order):
    return order["eta"] in reply

# --- The gather-only agent you assembled in Lab 7.11 (send_email WITHHELD) -- reused here ---
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
def gather_tools():
    return [lookup_order, get_template]                 # gather-only -- send_email is NOT bound
def make_email_agent():
    return create_agent(llm, gather_tools())
print("helpers ready: extract, route, draft (real model), validate + the gather-only agent")'''),
      buildmd('''Assemble `process`: chain the pipeline, gather via the agent's tool, draft with the **real model**, and
never send &mdash; every result is `needs_approval` or `needs_fix`.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Run the whole pipeline over a suite of client emails. Each `draft` is written by the real Groq model, grounded in the gathered order; nothing is ever sent."),
      code(runguard(RUN)),
      noticemd('''- Each row runs the **real pipeline**: keyword extract &rarr; route &rarr; gather (real order) &rarr; **real Groq draft** &rarr; validate.
- Every `status` is `needs_approval` or `needs_fix` &mdash; **never** `sent`. The agent has no send tool; a human decides.
- Read the drafts: for a known order they name the real ETA (grounded); for an unknown order the model can only work with what it was given.'''),
      yourturn('''Add an awkward email the keyword extractor mis-reads (e.g. *"my package never showed up and I'm furious"*,
which has no id and no delivery keyword) and re-run. **What good looks like:** you can see exactly where the
*rule-based* extract fails the model &mdash; and you can argue for swapping in an LLM-based extractor (with a
closed-schema validator) as the fix. That's the honest edge of the system, and the bridge to Module 8.'''),
      footer(12, "You built the email-drafting agent end to end -- extract, route, gather, draft (real model), validate -- and it never sends on its own. That's an agent that does a job you'd pay for. Next: Module 8 orchestrates a team of them."),
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
