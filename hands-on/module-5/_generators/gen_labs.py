# -*- coding: utf-8 -*-
"""Generator for Day 3 Module 5 hands-on labs (12 notebooks) -- NEAR-REAL design.
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

Design: this is the "What is Agentic AI?" module, so the labs TEACH THE AGENT MECHANICS
by building a ReAct-style agent FROM SCRATCH -- the tools, the reason -> act -> observe
loop, ReAct text parsing, tool routing, the memory/scratchpad, and the guardrails. All of
that stays REAL Python that the student writes (genuine mechanics, not stubs). What changed:
the old deterministic "mock LLM policy" is REPLACED by a REAL local model. A real
`ChatOllama("llama3.1:8b")` does the *reasoning* -- it emits the ReAct text / picks the next
action -- and the student's OWN from-scratch code parses it, routes it, loops it, and real
tools run. The payoff: "you built the agent loop, and a REAL model drives it." Module 6 then
hands that same loop to `create_agent`.

Kept real & deterministic (NOT LLM stand-ins): the AST-safe calculator (wrapped in try/except,
never bare eval), the ReAct parser, the safe tool router, the scratchpad/memory, and every
guardrail/validator. Tools ALWAYS catch their own exceptions and RETURN a string -- a tool that
raises can abort the whole loop (a lesson taught in labs 5/8).

There is NO auto-grader. Each lab ends with "Run it for real -> Read the trace -> Your turn".
Student robustness: cells that EXERCISE the blanks are wrapped by guard()/runguard() so an
unfilled `___` prints a friendly note instead of crashing, and the run cells self-skip if
Ollama is down -- so a student notebook runs top-to-bottom and a solution runs the real thing."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day3-module5-what-is-agentic-ai.html"
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
    """Guard a 'run it for real' cell: skip cleanly if Ollama is down, and if a blank is unfilled."""
    return ('if not ollama_up():\n'
            '    print("Ollama not reachable -- start `ollama run llama3.1:8b`, then re-run this cell.")\n'
            'else:\n'
            '    try:\n' + _indent(exercise, 8) +
            '\n    except Exception as e:\n        print("(Fill the ___ blanks above, then re-run.)", type(e).__name__)')

def setup(nn):
    return code(f'''# Setup -- run me first
import os, socket, pathlib
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))   # GROQ/OPENAI keys, if you ever want a hosted alternative

WORK = os.path.join(os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp", "biaa-lab-05-{nn:02d}")
os.makedirs(WORK, exist_ok=True)

def ollama_up(host="127.0.0.1", port=11434):
    """True if a local Ollama server is listening. If it's down, start it with:  ollama run llama3.1:8b"""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False

from langchain_ollama import ChatOllama
# Day-3 provider: a REAL local model DRIVES the agent YOU build from scratch.
# Pin the host -- plain 'localhost' can give 'No route to host'.
llm = ChatOllama(model="llama3.1:8b", temperature=0, base_url="http://127.0.0.1:11434")

def llm_text(prompt):
    """Call the REAL model and return its text (the .content of the reply)."""
    return llm.invoke(prompt).content

if ollama_up():
    print("Ollama reachable at 127.0.0.1:11434 | model:", llm.model, "| WORK:", WORK)
else:
    print("Ollama NOT reachable -- start it with:  ollama run llama3.1:8b")
    print("(The 'Run it for real' cells will print this note instead of crashing.)  WORK:", WORK)''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 5.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 3 &middot; Module 5 &mdash; What is Agentic AI?**

### What you'll do
{g}

> **How this lab works (near-real):** you have a local Ollama running `llama3.1:8b`. In Module 5 you build the agent **from scratch** &mdash; the loop, the ReAct parser, the tool router, the memory, the guardrails &mdash; as **real Python**. What's new vs the old version: a **real local model** now does the *reasoning* (it emits the ReAct steps / picks the actions) while **your** code parses, routes and loops it, and **real tools** run. Read the **Concept**, fill the real `___` blanks in **Build it**, then **Run it for real** and **read the trace**. Finish with an open **Your turn**. There is **no auto-grader**.

> **Framework note:** these labs use a **real local model** (`ollama run llama3.1:8b`, pinned to `http://127.0.0.1:11434`) via `langchain-ollama`. Unlike Module 6, you do **not** hand the loop to a framework &mdash; you build it yourself and the model drives it. If Ollama is down, the run cells print how to start it instead of crashing. A tool must **catch its own errors and return a string** &mdash; a tool that *raises* can abort the whole loop (you'll see exactly this in Labs 5 and 8). A small model can pick a wrong tool or fumble a step now and then &mdash; that's real agent behaviour, and it's why you read the trace.

**Reference:** [Module 5 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 5 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 5 labs](./index.html) &nbsp;&middot;&nbsp; [Module 5 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def concept(text):   return md("## Concept\n" + text)
def buildmd(text):   return md("## Build it\n" + text)
def runmd(text):     return md("## Run it for real &amp; read the trace\n" + text + "\n\n_This calls the real `llama3.1:8b` via Ollama. If Ollama is down the cell prints how to start it instead of crashing._")
def noticemd(text):  return md("## What to notice\n" + text)
def yourturn(text):  return md("## Your turn (open task &mdash; no grader)\n" + text)

def sol_answer(sol, code_text):
    """Solution-only: a worked reference for the open 'Your turn' task above.
    Returns nothing in the student notebook (the task stays open); in the SOLUTION
    it appends one runnable cell so participants have something to compare against."""
    if not sol:
        return []
    return [code("# --- Reference answer (ONE good way to do the 'Your turn' task -- compare with your own) ---\n" + code_text)]

# A small AST-based safe arithmetic evaluator, reused by labs that expose a calculator tool.
# It NEVER calls bare eval() on free text -- it walks a parsed tree of numbers + operators only.
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

# The real tool set + safe router (rule-based plumbing you build; NOT an LLM stand-in).
TOOLS_BLOCK = SAFE_CALC + '''

KNOWLEDGE = {"population of metropolis": "120000", "capital of france": "Paris"}
def _lookup(key):
    return KNOWLEDGE.get(str(key).lower().strip(), "unknown")
def _calc(expr):
    try:
        return str(safe_calc(expr))
    except Exception:
        return "error: not a numeric expression"   # a tool must NEVER raise -- return a string
TOOLS = {"lookup": _lookup, "calculator": _calc}    # real from-scratch tools: name -> function

def run_tool(name, inp):
    """Route an action to a tool and return an OBSERVATION string -- never raises."""
    fn = TOOLS.get(str(name).strip().lower())
    if fn is None:
        return "unknown tool: " + str(name)
    arg = str(inp).strip().strip("'\\"").strip()   # tolerate a model that quotes its argument
    return fn(arg)'''

# The ReAct format spec the REAL model must follow + the prompt builder + the parser.
# REACT_SYS is what makes an 8b model emit Thought/Action/Action Input; parse_step reads it back.
REACT_BLOCK = '''REACT_SYS = (
    "You are a ReAct agent. Solve the task step by step using tools.\\n"
    "Tools:\\n"
    "- lookup: look up a known fact by key. Known keys: 'population of metropolis', 'capital of france'.\\n"
    "- calculator: do exact arithmetic, e.g. 120000*2.\\n"
    "Each step you output is EXACTLY:\\n"
    "Thought: <reasoning>\\n"
    "Action: lookup OR calculator\\n"
    "Action Input: <input to that tool>\\n"
    "You will then be shown an 'Observation:'. Use it to decide the next step.\\n"
    "When the observations are enough to answer, output instead:\\n"
    "Thought: <reasoning>\\n"
    "Final Answer: <the answer>\\n"
    "Give ONLY the next single step. Do NOT write 'Observation:' yourself."
)

def react_prompt(task, transcript):
    """The prompt sent to the REAL model each turn: the format spec + task + the transcript so far.
    The transcript keeps the model's OWN Thoughts/Actions + the tool Observations, so it can continue
    its reasoning instead of restarting."""
    return REACT_SYS + "\\n\\nTask: " + task + "\\n" + transcript

def parse_step(text):
    """Parse the model's REAL text into ('final', answer) | ('action', name, inp) | ('none', text)."""
    def field(label):
        for line in str(text).splitlines():
            if line.strip().lower().startswith(label.lower() + ":"):
                return line.split(":", 1)[1].strip()
        return None
    fin = field("Final Answer")
    if fin is not None:
        return ("final", fin)
    act = field("Action")
    if act:
        return ("action", act.strip().lower(), field("Action Input") or "")
    return ("none", str(text)[:80])'''

NB = {}
def lab(nn, slug, level, title, mins, summary, concepts):
    def deco(fn):
        NB[nn] = dict(slug=slug, level=level, title=title, mins=mins,
                      summary=summary, concepts=concepts, build=fn)
        return fn
    return deco

# ============================================================ LAB 01
@lab(1, "lab-01-agent-vs-model", "Beginner",
     "A Model that Answers vs an Agent that Acts", 20,
     "Give the REAL llama3.1:8b a fact then ask for it in a fresh call to feel it forget (stateless), then build a tiny goal-seeking agent loop that carries state.",
     ["Stateless model", "Goal loop", "Real model"])
def _l1(sol):
    DEFS = [
      "def decide(goal_target, current):",
      "    # the agent DECIDES the next action toward the goal",
      {"s": '    if ___:                     # TODO: have we reached (>=) the target?',
       "a": '    if current >= goal_target:'},
      {"s": '        return ___              # TODO: the action name that STOPS the loop',
       "a": '        return "done"'},
      {"s": '    return ___                  # TODO: the action that makes progress',
       "a": '    return "increment"'},
      "",
      "def run(goal_target, max_steps=20):",
      "    current, steps = 0, 0          # the loop CARRIES STATE across steps",
      "    while steps < max_steps:",
      '        if decide(goal_target, current) == "done":',
      '            return {"value": current, "steps": steps, "stopped": "goal"}',
      "        current += 1; steps += 1",
      '    return {"value": current, "steps": steps, "stopped": "max_steps"}',
    ]
    EX = 'print("agent reached", run(3))   # stateful: it remembers `current` and stops at the goal'
    RUN = '''# Two calls where the SECOND depends on the FIRST -- the real test of memory.
a1 = llm_text("Remember this number: 42. Reply with just 'OK'.")   # call 1: we give it a fact
a2 = llm_text("What number did I just ask you to remember?")       # call 2: a fresh call, ask for it
print("call 1 (we told it 42):", a1)
print("call 2 (ask it back)  :", a2)
print("---")
print("Call 2 is a brand-new request with NO access to call 1, so the model can't recall '42': STATELESS.")
print("(Same prompt twice would only show it's deterministic -- it's the FORGETTING across calls that proves statelessness.)")
print("Your run() loop, by contrast, carried state (`current`) across steps until the goal was met.")'''
    return [
      header(1, "A Model that Answers vs an Agent that Acts", "Beginner", 20,
        ["Give the model a fact then ask for it in a fresh call &mdash; and watch it forget (stateless)",
         "Write a rule that DECIDES an action toward a goal",
         "Wrap it in a loop that carries state and stops when the goal is met"],
        "A model that answers &rarr; an agent that acts"),
      setup(1),
      concept('''A **language model** is a brilliant brain with no hands: give it a prompt, it returns text **once**, then
forgets. An **agent** wraps a model so it can take an **action toward a goal**, look at the result, and
**keep going** until the goal is met &mdash; carrying **state** between steps. Below you'll feel both: the
real model answering statelessly, and a tiny agent loop that remembers where it is.'''),
      code('''# A model maps text -> text, once, with no memory. An agent wraps it in a loop with a goal + state.
# (We call the REAL model in the "Run it for real" cell below.)
print("model:  prompt -> text (stateless)")
print("agent:  goal + loop + state -> keeps acting until done")'''),
      buildmd('''Write `decide` (the action toward the goal) and note how `run` **carries state** (`current`) across
steps &mdash; the thing a bare model can't do.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Give the model a fact in one call, then ask for it back in a **fresh** call &mdash; and watch it have no memory of the first. Then compare to your stateful loop above."),
      code(runguard(RUN)),
      noticemd('''- Call 2 was a **brand-new request with no access to call 1**, so the model couldn't recall the number &mdash; stateless. (Repeating the *same* prompt would only show it's deterministic; it's the **forgetting across calls** that proves statelessness.)
- Your `run()` loop kept `current` between steps and **stopped at the goal** &mdash; that memory + loop is the seed of every agent.
- Everything else in this module &mdash; tools, the ReAct loop, memory, guardrails &mdash; hangs off that single shift.'''),
      yourturn('''Now give the model &ldquo;memory&rdquo; the only way you can &mdash; feed the fact **into** the prompt as context:
call `llm_text("Context: the number is 42.\\nQuestion: what is the number?")` and watch it answer correctly.
That manual carry-over is exactly what the loop (and, next lab, the scratchpad) automates.
**What good looks like:** stateless across calls, but you can *fake* memory by stuffing prior context into the prompt.'''),
      *sol_answer(sol, r'''if ollama_up():
    # Fake memory by putting the fact INTO the prompt as context -- now it can answer.
    print("with manual context:", llm_text("Context: the number is 42.\nQuestion: what is the number? Answer with just the number."))
else:
    print("(start Ollama to see the model answer once you hand it the context)")
print("run(target=7) ->", run(7))   # the loop still tracks its own state to the NEW goal'''),
      footer(1, "A model **answers**; an agent **acts toward a goal in a loop with state**. You just proved a real model is stateless -- now you'll give the loop tools, parsing, memory and guardrails."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-build-a-tool", "Beginner",
     "Build a Tool: Give the Agent Hands", 20,
     "Build real from-scratch tools (name/description/fn) + a SAFE calculator, then let the REAL model pick a tool by reading your descriptions.",
     ["Tool schema", "Registry", "Model picks tool"])
def _l2(sol):
    DEFS = [
      SAFE_CALC,
      "",
      'KNOWLEDGE = {"capital of france": "Paris", "population of metropolis": "120000"}',
      "",
      "def calculator_fn(expr):",
      {"s": '    return ___    # TODO: evaluate expr with the safe calculator (never bare eval)',
       "a": '    return safe_calc(expr)'},
      "",
      "def lookup_fn(key):",
      {"s": '    return ___    # TODO: look key up in KNOWLEDGE (lowercased/stripped), default "unknown"',
       "a": '    return KNOWLEDGE.get(key.lower().strip(), "unknown")'},
      "",
      'calculator = {"name": "calculator", "description": "Do exact arithmetic like 2+2 or 45*12.", "fn": calculator_fn}',
      'lookup     = {"name": "lookup", "description": "Look up a known fact by key, e.g. capital of france.", "fn": lookup_fn}',
      "",
      "def build_registry(tools):",
      {"s": '    return ___    # TODO: a dict mapping each tool\'s name to the tool',
       "a": '    return {t["name"]: t for t in tools}'},
    ]
    EX = '''REGISTRY = build_registry([calculator, lookup])
print("tools:", list(REGISTRY))
print("calculator(45*12) =", REGISTRY["calculator"]["fn"]("45*12"))
print("lookup(capital of france) =", REGISTRY["lookup"]["fn"]("capital of france"))'''
    RUN = '''catalog = "\\n".join("- " + t["name"] + ": " + t["description"] for t in REGISTRY.values())
question = "what is 45 * 12?"
prompt = ("You can use these tools:\\n" + catalog +
          "\\n\\nWhich ONE tool answers this question: '" + question + "'?\\n"
          "Reply with ONLY the tool name.")
choice = llm_text(prompt).strip().lower()
print("model read the descriptions and picked:", repr(choice))
name = next((n for n in REGISTRY if n in choice), None)   # match its pick to a REAL tool, safely
if name:
    print("running", name, "->", REGISTRY[name]["fn"]("45*12"))
else:
    print("(model didn't name a known tool -- that happens; sharpen the descriptions and retry.)")'''
    return [
      header(2, "Build a Tool: Give the Agent Hands", "Beginner", 20,
        ["Represent a tool as {name, description, fn} and build a registry",
         "Implement a SAFE calculator (no bare eval) and a lookup tool",
         "Let the REAL model pick a tool by reading your descriptions"],
        "Tools turn an LLM into an agent"),
      setup(2),
      concept('''A model alone only emits **text**. A **tool** is a plain function you expose to it, described by a
**name**, a **description** (which the model reads to decide when to use it) and the **function** itself.
Two staples: a **calculator** (LLMs are bad at exact math &mdash; offload it) and a **lookup**. The
description is the tool's real API: below, the **real model** picks a tool purely from your words.

> **Safety:** never run bare `eval()` on free text. Our calculator uses a tiny **AST-based** safe
> evaluator that only allows numbers and arithmetic operators.'''),
      code(SAFE_CALC + '''
print("safe_calc('2+2') =", safe_calc("2+2"), "| safe_calc('3*(4+1)') =", safe_calc("3*(4+1)"))
# A bare eval() would happily run "__import__('os').system('rm -rf /')" -- ours refuses.'''),
      buildmd('''Implement the two tool functions, then build the registry mapping each tool's name to its dict.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Show the real model the tool catalog and let *it* pick which tool answers a question &mdash; from the descriptions alone."),
      code(runguard(RUN)),
      noticemd('''- The model chose a tool by reading the **description** &mdash; it never saw your code. The docstring/description **is** the tool's API.
- We matched its free-text pick back to a real tool **safely** (`next(... , None)`) &mdash; if it names nothing valid, we say so instead of crashing.
- In Module 6 a framework wires this selection for you; here you saw the raw mechanism.'''),
      yourturn('''Add a **third** tool (e.g. a `weather` tool) with a clear description, rebuild the registry, and re-ask the
model with a weather question. **What good looks like:** the model picks your new tool from its description.
Make the description vague and watch it pick worse &mdash; proof that you write descriptions *for the model*.'''),
      *sol_answer(sol, r'''def weather_fn(city):
    return "sunny, 24C in " + str(city).strip()          # a stub; a real tool would call an API
weather = {"name": "weather", "description": "Current weather for a city, e.g. 'tokyo'.", "fn": weather_fn}
REGISTRY = build_registry([calculator, lookup, weather])
print("tools:", list(REGISTRY))
if ollama_up():
    catalog = "\n".join("- " + t["name"] + ": " + t["description"] for t in REGISTRY.values())
    q = "what's the weather in tokyo?"
    pick = llm_text("You can use these tools:\n" + catalog +
                    "\n\nWhich ONE tool answers: '" + q + "'?\nReply with ONLY the tool name.").strip().lower()
    name = next((n for n in REGISTRY if n in pick), None)
    print("model picked:", repr(pick), "->", REGISTRY[name]["fn"]("tokyo") if name else "(no known tool)")
else:
    print("(start Ollama to watch the model pick your new tool from its description)")'''),
      footer(2, "A tool is `{name, description, fn}` in a registry, and the description is what a REAL model reads to choose it. Next: give the agent a loop that calls the tool the model picks."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-the-agent-loop", "Beginner",
     "The Agent Loop: Reason, Act, Observe", 20,
     "Build the reason -> act -> observe loop from scratch and let a REAL model be the reasoner that drives your tools.",
     ["Agent loop", "Real reasoner", "max_steps"])
def _l3(sol):
    DEFS = [
      "def run_loop(task, max_steps=5):",
      '    transcript, trace = "", []',
      "    for step in range(max_steps):",
      {"s": '        text = ___                       # TODO: ask the REAL model for the next step: react_prompt(task, transcript)',
       "a": '        text = llm_text(react_prompt(task, transcript))'},
      "        kind = parse_step(text)",
      {"s": '        if ___:                          # TODO: stop when the model gave a Final Answer (kind[0] == "final")',
       "a": '        if kind[0] == "final":'},
      '            return {"answer": kind[1], "trace": trace, "steps": step + 1}',
      '        if kind[0] == "action":',
      "            name, inp = kind[1], kind[2]",
      {"s": '            obs = ___                    # TODO: run the chosen tool SAFELY: run_tool(name, inp)',
       "a": '            obs = run_tool(name, inp)'},
      '            trace.append((name, inp, obs))',
      '            transcript += text.strip() + "\\nObservation: " + obs + "\\n"',
      "        else:",
      '            transcript += text.strip() + "\\nObservation: (unparseable step)\\n"',
      '    return {"answer": None, "trace": trace, "steps": max_steps}',
    ]
    EX = 'print("prompt preview:\\n", react_prompt("twice the population of metropolis", "")[:220], "...")'
    RUN = '''out = run_loop("What is twice the population of metropolis?")
print("TRACE (a REAL model + YOUR loop):")
for name, inp, obs in out["trace"]:
    print("  ACTION:", name, "| INPUT:", inp, "-> OBS:", obs)
print("steps:", out["steps"], "| ANSWER:", out["answer"])'''
    return [
      header(3, "The Agent Loop: Reason, Act, Observe", "Beginner", 20,
        ["Run the reason -> act -> observe cycle, driven by a REAL model",
         "Stop when the model returns a Final Answer",
         "Cap the loop with max_steps so a confused model can never run forever"],
        "The agent loop"),
      setup(3),
      concept('''Every agent runs the same cycle: **Reason** (decide the next step), **Act** (call a tool), **Observe**
(read the result), then **repeat** &mdash; until it can **stop** and answer. That is **ReAct** (Reason +
Act). Here the **Reason** step is a **real `llama3.1:8b`** emitting ReAct text; **your** loop parses it,
runs the tool, feeds the observation back, and stops on a Final Answer or a **max_steps** cap. The
`react_prompt`, `parse_step` and `run_tool` plumbing is provided &mdash; you wire the **loop**.'''),
      code(TOOLS_BLOCK + "\n\n" + REACT_BLOCK + '''

print("tools:", list(TOOLS))
print("run_tool('lookup', 'population of metropolis') ->", run_tool("lookup", "population of metropolis"))
print("parse_step demo ->", parse_step("Thought: t\\nAction: calculator\\nAction Input: 2*3"))'''),
      buildmd('''Complete `run_loop`: each turn, ask the **real** model for a step, **stop** on a Final Answer, otherwise
**run** the tool and append the observation. (Labs 4 and 5 dig into the parser and the router you're using
here.)'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Run the loop on a two-step task. The real model reasons; your loop calls `lookup` then `calculator`. Read the trace."),
      code(runguard(RUN)),
      noticemd('''- Each `ACTION` line was **chosen by the real model** in ReAct text; your loop parsed it and ran your Python tool.
- **`max_steps`** is your one-line guardrail &mdash; even a model that never says "Final Answer" can't loop forever.
- If the model computed without looking up, or chose a different order, that's **real 8b behaviour** &mdash; the trace tells you the truth.'''),
      yourturn('''Change the task (e.g. *"what is the capital of france?"*, which needs only `lookup`) or add a tool to `TOOLS`
and mention it in `REACT_SYS`, then re-run. **What good looks like:** the trace shows the model calling the
right tool(s) and a sensible Final Answer; a task it can't do stops cleanly at the cap.'''),
      *sol_answer(sol, r'''if ollama_up():
    out = run_loop("What is the capital of france?")   # a ONE-tool task -> only lookup is needed
    print("TRACE (real model + your loop):")
    for name, inp, obs in out["trace"]:
        print("  ACTION:", name, "| INPUT:", inp, "-> OBS:", obs)
    print("steps:", out["steps"], "| ANSWER:", out["answer"])
else:
    print("(start Ollama:  ollama run llama3.1:8b)")'''),
      footer(3, "Reason -> act -> observe, repeat, with a stop condition and a step cap. That loop IS the agent -- and a REAL model is now the reasoner driving your tools."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-react-step-parsing", "Beginner",
     "Parsing a ReAct Step", 20,
     "Get REAL ReAct text from llama3.1:8b and parse Thought / Action / Action Input / Final Answer with your own parser.",
     ["ReAct format", "Parsing", "Real output"])
def _l4(sol):
    DEFS = [
      'SAMPLE = """Thought: I need the population, so I should look it up.',
      "Action: lookup",
      'Action Input: population of metropolis"""',
      "",
      'FINAL = """Thought: I now have everything I need.',
      'Final Answer: 120000"""',
      "",
      "def field(text, label):",
      "    for line in text.splitlines():",
      {"s": '        if line.strip().lower().startswith(___):   # TODO: the label + ":" (case-insensitive)',
       "a": '        if line.strip().lower().startswith(label.lower() + ":"):'},
      {"s": '            return ___    # TODO: the text after the first colon, stripped',
       "a": '            return line.split(":", 1)[1].strip()'},
      "    return None",
      "",
      "def is_final(text):",
      {"s": '    return ___    # TODO: True if a Final Answer line is present',
       "a": '    return field(text, "Final Answer") is not None'},
    ]
    EX = '''print("action      =", field(SAMPLE, "Action"))
print("action input=", field(SAMPLE, "Action Input"))
print("SAMPLE final?", is_final(SAMPLE), "| FINAL final?", is_final(FINAL))'''
    RUN = '''spec = ("Reply in EXACTLY this format and nothing else:\\n"
        "Thought: <one line of reasoning>\\n"
        "Action: lookup\\n"
        "Action Input: <the key>\\n\\n"
        "Task: find the population of metropolis.")
text = llm_text(spec)                 # REAL model output -- your parser reads it
print("MODEL EMITTED:\\n" + text)
print("---")
print("parsed Action      :", field(text, "Action"))
print("parsed Action Input:", field(text, "Action Input"))
print("is it a final answer?:", is_final(text))'''
    return [
      header(4, "Parsing a ReAct Step", "Beginner", 20,
        ["Read the ReAct text format a real model produces",
         "Extract the Action name and its Action Input",
         "Detect when a step is a Final Answer"],
        "Tools &amp; function-calling &mdash; a ReAct trace"),
      setup(4),
      concept('''A ReAct agent's LLM emits **structured text**: a `Thought:`, then either an `Action:` + `Action Input:`
(call a tool) or a `Final Answer:` (stop). The orchestrator must **parse** that text to know what to do
next. You'll build the parser on a fixed sample first (so you can test it with no model), then point it at
**real** `llama3.1:8b` output &mdash; the exact thing a LangChain output parser does under the hood.'''),
      code('''# DEMO -- the two kinds of step an agent produces
SAMPLE = """Thought: I need the population, so I should look it up.
Action: lookup
Action Input: population of metropolis"""

FINAL = """Thought: I now have everything I need.
Final Answer: 120000"""
print(SAMPLE); print("---"); print(FINAL)'''),
      buildmd('''Write `field(text, label)` to read the text after a `Label:` line, then `is_final` to detect a Final Answer.
Test them on the fixed strings first.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Now ask the **real** model to emit a ReAct step and parse *its* output with your `field` / `is_final`."),
      code(runguard(RUN)),
      noticemd('''- Your parser turned the **real** model's free text into a structured `(Action, Action Input)` step &mdash; exactly what an output parser does.
- `field("Action")` must not accidentally grab `Action Input` &mdash; the `+ ":"` match is what keeps them apart.
- Real models sometimes add stray lines; a tolerant parser (first match wins, returns `None` if absent) survives that instead of crashing.'''),
      yourturn('''Change `spec` to nudge the model toward a **Final Answer** (e.g. *"you already know it is 120000"*) and
re-run. **What good looks like:** `is_final` flips to `True` and `field(text, "Final Answer")` returns the
number. Try a deliberately messy instruction and confirm your parser still doesn't crash.'''),
      *sol_answer(sol, r'''if ollama_up():
    spec = ("Reply in EXACTLY this format and nothing else:\n"
            "Thought: <one line>\nFinal Answer: <the number>\n\n"
            "Task: the population of metropolis is 120000 -- report it.")
    text = llm_text(spec)                 # nudged toward a Final Answer
    print("MODEL EMITTED:\n" + text)
    print("is_final?", is_final(text), "| Final Answer:", field(text, "Final Answer"))
else:
    print("(start Ollama to parse a real Final Answer)")'''),
      footer(4, "The orchestrator turns the model's text into structured steps. You parsed REAL llama3.1:8b output -- now you know exactly what LangChain's output parsers are reading."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-tool-routing", "Beginner",
     "Tool Routing: Dispatch an Action to a Tool", 20,
     "Build a safe router, then feed it a real action the model chose -- surviving unknown and failing tools without crashing.",
     ["Routing", "Safe dispatch", "Real action"])
def _l5(sol):
    DEFS = [
      "def route(registry, action, arg):",
      {"s": '    tool = ___    # TODO: get the tool by name (None if it is not registered)',
       "a": '    tool = registry.get(action)'},
      "    if tool is None:",
      {"s": '        return {"ok": False, "observation": ___}   # TODO: a message naming the unknown tool',
       "a": '        return {"ok": False, "observation": "unknown tool: " + str(action)}'},
      "    try:",
      {"s": '        result = ___   # TODO: run the tool function on arg',
       "a": '        result = tool["fn"](arg)'},
      '        return {"ok": True, "observation": result}',
      "    except Exception as e:",
      '        return {"ok": False, "observation": "tool error: " + type(e).__name__}',
    ]
    EX = '''print(route(REGISTRY, "calculator", "10/2"))
print(route(REGISTRY, "weather", "tokyo"))
print(route(REGISTRY, "no_such_tool", "x"))       # a hallucinated name -> handled, no crash
print(route(REGISTRY, "calculator", "not math"))  # a tool that RAISES -> caught, no crash'''
    RUN = '''question = "what's the weather in Tokyo right now?"
ask = ("Tools you may use: calculator, lookup, weather.\\n"
       "For the task below reply EXACTLY two lines and nothing else:\\n"
       "TOOL: <one tool name>\\nINPUT: <the tool input>\\n\\n"
       "Task: " + question)
reply = llm_text(ask)
print("MODEL SAID:\\n" + reply)
def _line(txt, tag):
    for ln in txt.splitlines():
        if ln.strip().lower().startswith(tag.lower() + ":"):
            return ln.split(":", 1)[1].strip()
    return ""
action, arg = _line(reply, "TOOL").lower(), _line(reply, "INPUT")
print("---")
print("model chose action:", repr(action), "| input:", repr(arg))
print("routed through YOUR safe router ->", route(REGISTRY, action, arg))'''
    return [
      header(5, "Tool Routing: Dispatch an Action to a Tool", "Beginner", 20,
        ["Look a tool up by name in the registry and run it",
         "Handle an unknown tool AND a failing tool without crashing",
         "Route a REAL action the model chose through your safe dispatcher"],
        "Anatomy of an agent"),
      setup(5),
      concept('''Once the model has chosen an **action name**, the orchestrator must **route** it to the matching tool, run
it, and wrap the result as an **observation**. Real models hallucinate tool names and feed bad inputs, so
routing must fail **safely**: an unknown or failing tool returns a message, not a crash. The `try/except`
is what turns a crash into a recoverable observation &mdash; genuine plumbing, not an LLM stand-in.'''),
      code(SAFE_CALC + '''
KNOWLEDGE = {"capital of france": "Paris", "population of metropolis": "120000"}
REGISTRY = {
    "calculator": {"name": "calculator", "fn": safe_calc},
    "lookup":     {"name": "lookup", "fn": lambda k: KNOWLEDGE.get(k.lower().strip(), "unknown")},
    "weather":    {"name": "weather", "fn": lambda city: "sunny 24C in " + str(city).strip()},
}
print("registry:", list(REGISTRY))
# Note: safe_calc RAISES on non-math input -- your router must survive that, not crash.'''),
      buildmd('''Implement `route`: find the tool, run it, return a dict &mdash; surviving an **unknown** tool name and a
tool that **raises**. Test it on all three hazards first.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Let the **real** model pick a tool + input for a task, then route *its* real choice through your safe dispatcher."),
      code(runguard(RUN)),
      noticemd('''- Your router ran the model's **real** choice safely &mdash; and would return `"unknown tool: ..."` if the model hallucinated a name.
- Splitting **deciding** (the model) from **executing** (the router) is exactly what makes agents debuggable.
- If the model picked `calculator` for a weather question, the router still runs cleanly &mdash; wrong tool, but no crash. You catch that by reading the trace.'''),
      yourturn('''Change `question` so the model should route to `calculator` or `lookup`, and re-run. Then force a failure:
call `route(REGISTRY, "delete_db", "x")` and `route(REGISTRY, "calculator", "hello")` directly. **What good
looks like:** every case returns a clean `{"ok": ..., "observation": ...}` dict &mdash; never a stack trace.'''),
      *sol_answer(sol, r'''print("math task ->", route(REGISTRY, "calculator", "15*3"))          # routes and runs
print("fact task ->", route(REGISTRY, "lookup", "capital of france"))
print("unknown   ->", route(REGISTRY, "delete_db", "x"))              # hallucinated name -> clean dict
print("bad input ->", route(REGISTRY, "calculator", "hello"))        # tool RAISES -> caught, clean dict
# every case is a {"ok": ..., "observation": ...} dict -- never a stack trace'''),
      footer(5, "Routing turns a chosen action into a real observation -- safely. You fed a REAL model's choice through the dispatcher and it survived an unknown or failing tool."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-memory-scratchpad", "Beginner",
     "Memory: the Agent's Scratchpad", 20,
     "Build the scratchpad of Thought/Action/Observation steps, then feed it to the REAL model so it can decide the next step.",
     ["Scratchpad", "Short-term memory", "Real follow-up"])
def _l6(sol):
    DEFS = [
      "def make_memory():",
      "    return []",
      "",
      "def remember(memory, thought, action, observation):",
      {"s": '    memory.append(___)   # TODO: a dict with keys thought, action, observation',
       "a": '    memory.append({"thought": thought, "action": action, "observation": observation})'},
      "    return memory",
      "",
      "def scratchpad(memory):",
      "    parts = []",
      "    for s in memory:",
      {"s": '        t, a, o = ___   # TODO: pull thought, action, observation out of step s',
       "a": '        t, a, o = s["thought"], s["action"], s["observation"]'},
      '        parts.append("Thought: " + str(t) + " | Action: " + str(a) + " | Observation: " + str(o))',
      '    return "\\n".join(parts)',
      "",
      "def should_stop(memory):",
      {"s": '    return ___    # TODO: True if any step took the "final" action',
       "a": '    return any(s["action"] == "final" for s in memory)'},
    ]
    EX = '''m = make_memory()
remember(m, "I need the population", "lookup", "120000")
print(scratchpad(m))
print("stop?", should_stop(m))'''
    RUN = '''m = make_memory()
remember(m, "I need the population first", "lookup", "120000")
prompt = ("Here is the agent's scratchpad so far:\\n" + scratchpad(m) +
          "\\n\\nThe goal is to report TWICE the population. "
          "What is the next Action and Action Input? Reply in two short lines.")
print("MODEL'S NEXT STEP (it READ your scratchpad):\\n" + llm_text(prompt))'''
    return [
      header(6, "Memory: the Agent's Scratchpad", "Beginner", 20,
        ["Append each (thought, action, observation) step to memory",
         "Format the memory into the running scratchpad the model re-reads",
         "Feed the scratchpad to the REAL model and watch it continue from it"],
        "Memory &mdash; short-term &amp; long-term"),
      setup(6),
      concept('''The agent's **short-term memory** is a **scratchpad**: the running transcript of every Thought, Action and
Observation so far. It is how the agent knows **what it already tried** &mdash; you store steps in a list
and format them back into the text the model re-reads each turn. Below, you build it and then hand it to the
**real** model so it can decide the **next** step instead of restarting. (Long-term memory is a vector
store &mdash; the bridge to RAG.)'''),
      code('''# DEMO -- one step is just a small dict
step = {"thought": "I need the population", "action": "lookup", "observation": "120000"}
print(step)'''),
      buildmd('''Implement `remember`, `scratchpad`, and `should_stop`.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Put one step in memory, then hand the **scratchpad** to the real model and let it propose the next Action &mdash; it can only do that because it read the memory."),
      code(runguard(RUN)),
      noticemd('''- The model proposed the **next** step (calculator on 120000) because your **scratchpad** told it the population was already looked up.
- Delete the `remember(...)` line and re-run: with no memory the model has nothing to build on &mdash; that's the whole value of a scratchpad.
- In a framework this is a component you attach; here you built it and fed it to a real model by hand.'''),
      yourturn('''Add a second step to memory (the calculator result), re-format the scratchpad, and ask the model for a
**Final Answer**. **What good looks like:** with the fuller scratchpad the model closes out the task; strip
memory and its follow-ups fall apart.'''),
      *sol_answer(sol, r'''m = make_memory()
remember(m, "I need the population first", "lookup", "120000")
remember(m, "Now double it", "calculator", "240000")     # the SECOND step
print(scratchpad(m))
if ollama_up():
    prompt = ("Scratchpad so far:\n" + scratchpad(m) +
              "\n\nThe goal is TWICE the population. Give the Final Answer in one short line.")
    print("MODEL'S FINAL ANSWER (it read the fuller scratchpad):\n" + llm_text(prompt))
else:
    print("(start Ollama to watch the model close out the task from memory)")'''),
      footer(6, "The scratchpad is the agent's working memory for one task, and a REAL model reads it to continue. Long-term memory (a vector store) arrives with RAG later."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-rule-based-react-agent", "Intermediate",
     "A ReAct Agent (two-step task)", 30,
     "Assemble tools + loop + memory into a from-scratch ReAct agent and let the REAL model chain two tools: look up a fact, then compute on it.",
     ["ReAct agent", "Tool chaining", "Real model"])
def _l7(sol):
    DEFS = [
      "def run_agent(task, max_steps=6):",
      "    memory = []                       # a memory trail of (action, input, observation)",
      '    transcript = ""',
      "    for step in range(max_steps):",
      {"s": '        text = ___                   # TODO: the REAL model reasons about the next step',
       "a": '        text = llm_text(react_prompt(task, transcript))'},
      "        kind = parse_step(text)",
      {"s": '        if kind[0] == ___:           # TODO: the model produced a Final Answer -> stop',
       "a": '        if kind[0] == "final":'},
      '            return {"answer": kind[1], "memory": memory}',
      '        if kind[0] == "action":',
      "            name, inp = kind[1], kind[2]",
      {"s": '            obs = ___                # TODO: run the tool and capture the observation',
       "a": '            obs = run_tool(name, inp)'},
      '            memory.append({"action": name, "input": inp, "observation": obs})',
      '            transcript += text.strip() + "\\nObservation: " + obs + "\\n"',
      "        else:",
      '            transcript += text.strip() + "\\nObservation: (unparseable step)\\n"',
      '    return {"answer": None, "memory": memory}',
    ]
    EX = 'print("tools:", list(TOOLS), "| the agent will chain them, driven by the real model")'
    RUN = '''out = run_agent("What is twice the population of metropolis?")
print("actions used:", [s["action"] for s in out["memory"]])
for s in out["memory"]:
    print("  ", s["action"], "(", s["input"], ") ->", s["observation"])
print("ANSWER:", out["answer"])
print("chained lookup THEN calculator?:",
      [s["action"] for s in out["memory"]][:2] == ["lookup", "calculator"])'''
    return [
      header(7, "A ReAct Agent (two-step task)", "Intermediate", 30,
        ["Wire tools + memory + the loop into one working ReAct agent",
         "Let the REAL model chain TWO tools: look up the population, then double it",
         "Read the memory to confirm both tools were used and the loop terminated"],
        "The agent loop"),
      setup(7),
      concept('''Now assemble the pieces from Labs 2&ndash;6 into a real **ReAct agent**. The task &mdash; *"twice the
population of Metropolis"* &mdash; needs **two** tools chained: **lookup** the population, then
**calculator** to double it. The difference from the old version: the **policy is a real model**. It reads
the scratchpad, emits the next Thought/Action, and **your** loop parses, routes and remembers. If the model
does the steps out of order or fumbles, the memory + step cap keep you safe &mdash; that's real behaviour.'''),
      code(TOOLS_BLOCK + "\n\n" + REACT_BLOCK + '''

print("ready: tools =", list(TOOLS), "| react_prompt + parse_step provided")'''),
      buildmd('''Complete `run_agent`: ask the **real** model, **stop** on a Final Answer, else **run** the tool and record
it in memory. This is the same loop as Lab 3, now assembled as a named agent with a memory trail.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Run the agent on the two-step task and read the memory: the real model should chain `lookup` then `calculator`."),
      code(runguard(RUN)),
      noticemd('''- The memory shows a **real two-tool chain** decided by `llama3.1:8b`: lookup 120000, then calculator 120000*2 -> 240000.
- Each observation fed the next step &mdash; that's orchestration, and it's exactly where an agent beats a single model call.
- If the order differs or a step fumbles, that's real 8b behaviour; **Module 6's `create_agent` runs this exact loop for you.**'''),
      yourturn('''Give it a different two-step task (add a fact to `KNOWLEDGE` and mention it, or ask *"three times the
population"*) and re-run. **What good looks like:** the agent chains lookup -> calculator with the searched
number, and the answer reflects both steps. A task it can't do stops cleanly at the cap.'''),
      *sol_answer(sol, r'''if ollama_up():
    out = run_agent("What is three times the population of metropolis?")   # a different two-step task
    print("actions used:", [s["action"] for s in out["memory"]])
    for s in out["memory"]:
        print("  ", s["action"], "(", s["input"], ") ->", s["observation"])
    print("ANSWER:", out["answer"])
else:
    print("(start Ollama:  ollama run llama3.1:8b)")'''),
      footer(7, "Tools + memory + loop + a REAL model policy = a working ReAct agent that chains two tools. That policy used to be a mock; now it's a real model -- and Module 6 hands the loop to LangChain."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-guardrails", "Intermediate",
     "Guardrails: Keep the Agent Safe", 30,
     "Wrap a REAL model-driven agent in deterministic guardrails -- allow-list, loop detection, input validation -- and watch the allow-list refuse a tool the model asks for.",
     ["Allow-list", "Loop detection", "Input validation"])
def _l8(sol):
    DEFS = [
      'ALLOWED = {"lookup", "calculator"}',
      'ALLOWED_CHARS = set("0123456789+-*/(). ")',
      "",
      "def is_allowed(action):",
      {"s": '    return ___    # TODO: True only if action is in the allow-list',
       "a": '    return action in ALLOWED'},
      "",
      "def detect_loop(actions, k=3):",
      {"s": '    return len(actions) >= k and ___   # TODO: True if the last k actions are all identical',
       "a": '    return len(actions) >= k and len(set(actions[-k:])) == 1'},
      "",
      "def is_valid_calc_input(expr):",
      {"s": '    return all(c in ALLOWED_CHARS for c in expr) and ___   # TODO: require at least one digit',
       "a": '    return all(c in ALLOWED_CHARS for c in expr) and any(c.isdigit() for c in expr)'},
    ]
    EX = '''print("is_allowed(calculator):", is_allowed("calculator"), "| is_allowed(delete_db):", is_allowed("delete_db"))
print("detect_loop(3x lookup):", detect_loop(["lookup", "lookup", "lookup"]))
print("detect_loop(varied):   ", detect_loop(["lookup", "calculator", "lookup"]))
print("valid '2 + 2*3':", is_valid_calc_input("2 + 2*3"), "| valid '__import__':", is_valid_calc_input("__import__"))'''
    RUN = '''# A REAL model is TEMPTED with a disallowed tool; your deterministic allow-list refuses it.
catalog = "lookup, calculator, delete_all"     # delete_all is NOT in ALLOWED
reply = llm_text("Tools: " + catalog + ".\\nTask: delete all the customer records.\\n"
                 "Reply one line only:\\nTOOL: <the tool to use>")
raw = reply.split(":", 1)[-1].strip().lower() if ":" in reply else reply.strip().lower()
pick = next((t for t in ["delete_all", "lookup", "calculator"] if t in raw), raw)
print("model wanted tool:", repr(pick))
print("allow-list decision:", "RUN" if is_allowed(pick) else "BLOCKED (not on the allow-list)")
print("---")
print("A nondeterministic model asked for a dangerous tool; deterministic Python refused it.")'''
    return [
      header(8, "Guardrails: Keep the Agent Safe", "Intermediate", 30,
        ["Allow-list the tools an agent may call",
         "Detect a runaway loop (the same action repeated)",
         "Validate tool input, then watch the allow-list refuse a tool the REAL model asks for"],
        "Guardrails &amp; human-in-the-loop"),
      setup(8),
      concept('''Autonomy needs **guardrails**. Four cheap, essential ones: a **max_steps** cap (already in your loop), a
**tool allow-list** (only permitted tools run), **loop detection** (stop if the same action repeats), and
**input validation** (reject dangerous tool inputs). These are **deterministic Python wrapped around a
nondeterministic model** &mdash; the safety pattern. Below you build the guards, then watch the allow-list
**refuse a dangerous tool the real model asks for**.'''),
      code('''# DEMO
ALLOWED = {"lookup", "calculator"}
print("allowed tools:", ALLOWED)
print("'delete_all' allowed as a tool?", "delete_all" in ALLOWED)'''),
      buildmd('''Implement the three guards. Test them deterministically first (no model needed).'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Now tempt the **real** model with a disallowed `delete_all` tool and watch your allow-list refuse whatever it picks."),
      code(runguard(RUN)),
      noticemd('''- Even though the model *asked* for `delete_all`, your **deterministic** allow-list refused it &mdash; the model never gets to run an un-vetted tool.
- Loop detection + input validation + `max_steps` are the other cheap guards; together they stop an agent that hallucinates a tool, gets stuck, or is fed garbage.
- The guardrails are **real Python** you can reason about &mdash; that's why they're trustworthy around an unpredictable model.'''),
      yourturn('''Wrap your Lab-7 `run_agent` loop with `is_allowed` (refuse any action not on the list) and `detect_loop`
(bail if the last 3 actions repeat), then run it. **What good looks like:** a normal task completes, but a
disallowed or looping action is stopped &mdash; an autonomous agent you can actually trust.'''),
      *sol_answer(sol, r'''# Wrap a loop with the two guards you built: is_allowed + detect_loop.
def guarded_run(actions):
    seen = []
    for a in actions:
        if not is_allowed(a):
            return {"stopped": "blocked", "on": a, "trace": seen}   # allow-list refuses it
        seen.append(a)
        if detect_loop(seen):
            return {"stopped": "loop", "trace": seen}               # runaway loop caught
    return {"stopped": "done", "trace": seen}
print("normal    ->", guarded_run(["lookup", "calculator"]))            # completes
print("disallowed->", guarded_run(["lookup", "delete_all"]))           # allow-list stops it
print("looping   ->", guarded_run(["lookup", "lookup", "lookup"]))     # detect_loop stops it'''),
      footer(8, "Allow-list, loop detection and input validation are deterministic guards around a nondeterministic model. They turn an autonomous agent from a liability into something you can trust. Day 5 goes deeper."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-tool-selection", "Intermediate",
     "Tool Selection: Pick the Right Tool", 30,
     "Let the REAL model select the right tool from descriptions across a suite, and measure how often it is right (no grader -- you inspect and tune).",
     ["Tool selection", "Descriptions", "Accuracy"])
def _l9(sol):
    DEFS = [
      'TOOLSET = ["calculator", "weather", "translate", "lookup"]',
      'CATALOG = ("- calculator: exact arithmetic like 12*8\\n"',
      '           "- weather: current weather for a city\\n"',
      '           "- translate: translate English text to French\\n"',
      '           "- lookup: look up a known fact")',
      "",
      "def select_with_model(text):",
      {"s": '    prompt = ___   # TODO: show CATALOG and ask which ONE tool answers `text`; reply with only the name',
       "a": '    prompt = ("Tools:\\n" + CATALOG + "\\n\\nWhich ONE tool answers: \'" + text + "\'?\\nReply with ONLY the tool name.")'},
      "    reply = llm_text(prompt).lower()",
      {"s": '    return ___   # TODO: the first tool from TOOLSET whose name appears in the reply (else "lookup")',
       "a": '    return next((t for t in TOOLSET if t in reply), "lookup")'},
      "",
      "TASKS = [",
      '    {"text": "what is 12 * 8", "tool": "calculator"},',
      '    {"text": "current weather in tokyo", "tool": "weather"},',
      '    {"text": "translate hello to french", "tool": "translate"},',
      '    {"text": "capital of france", "tool": "lookup"},',
      '    {"text": "who was the 16th president", "tool": "lookup"},   # a digit, but NOT arithmetic',
      "]",
      "",
      "def measure(picks):",
      {"s": '    hits = ___   # TODO: count tasks where picks[i] matches TASKS[i]["tool"]',
       "a": '    hits = sum(1 for i, t in enumerate(TASKS) if picks[i] == t["tool"])'},
      "    return hits, len(TASKS)",
    ]
    EX = 'print("catalog the model will read:\\n" + CATALOG)'
    RUN = '''picks = []
for t in TASKS:
    pick = select_with_model(t["text"])          # REAL model selects from the descriptions
    picks.append(pick)
    print(("ok " if pick == t["tool"] else "XX "), t["text"], "-> model:", pick, "| expected:", t["tool"])
print("---")
print("selection accuracy:", measure(picks))
print("(No grader. If the model misroutes, inspect WHY and sharpen the tool descriptions.)")'''
    return [
      header(9, "Tool Selection: Pick the Right Tool", "Intermediate", 30,
        ["Ask the REAL model to choose a tool from descriptions for each request",
         "Run it across a suite of tasks (including a digit-but-not-math trap)",
         "Measure how often the choice is right -- and tune the descriptions"],
        "Tools turn an LLM into an agent"),
      setup(9),
      concept('''With more than two tools, the agent must **select** the right one for each sub-goal &mdash; the hardest
part of tool use. A real agent reads each tool's **description** and picks. Here the **real model** does the
selecting; you **measure** how often it's right across a suite. There's **no grader** &mdash; an 8b model
won't always be perfect (watch the *"16th president"* trap: a digit, but not arithmetic), and that's the
point: you inspect the misses and sharpen the descriptions, the goal-driven loop.'''),
      code('''# DEMO -- four tools; the model will choose from their descriptions
print("tools:", ["calculator", "weather", "translate", "lookup"])
print("Trap: 'the 16th president' has a digit but is a LOOKUP, not arithmetic.")'''),
      buildmd('''Write `select_with_model` (prompt the model with the catalog, parse its pick) and `measure` (accuracy over
the suite). Descriptions are the lever &mdash; the model reads *them*, not your code.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Run the real model over the whole suite and read where it routes well and where it slips."),
      code(runguard(RUN)),
      noticemd('''- Each pick came from the **real model** reading your **descriptions** &mdash; not a keyword rule you hardcoded.
- If it misroutes (e.g. sends *"16th president"* to calculator, or a terse task to lookup), that's real selection error &mdash; **no grader hides it**.
- The fix is almost always a sharper **description**, not more code &mdash; that's how you'd tune a real agent.'''),
      yourturn('''Improve a tool's description to fix a misroute (e.g. clarify calculator is for *arithmetic expressions*,
not any number), and re-run. **What good looks like:** accuracy climbs as your descriptions get clearer.
Add a fifth tool and a task for it and see if the model picks it.'''),
      *sol_answer(sol, r'''# Sharpen the calculator description (the misroute lever) and add a 5th tool + task, then re-measure.
CATALOG2 = ("- calculator: arithmetic EXPRESSIONS only, like 12*8 (NOT questions that merely contain a number)\n"
            "- weather: current weather for a city\n"
            "- translate: translate English text to French\n"
            "- lookup: look up a known fact, including history and people\n"
            "- define: give the dictionary definition of a single word")
TOOLSET2 = TOOLSET + ["define"]
def select2(text):
    reply = llm_text("Tools:\n" + CATALOG2 + "\n\nWhich ONE tool answers: '" + text +
                     "'?\nReply with ONLY the tool name.").lower()
    return next((t for t in TOOLSET2 if t in reply), "lookup")
if ollama_up():
    for t in TASKS + [{"text": "define serendipity", "tool": "define"}]:
        pick = select2(t["text"])
        print(("ok " if pick == t["tool"] else "XX "), t["text"], "-> model:", pick, "| expected:", t["tool"])
else:
    print("(start Ollama to re-measure with the sharper descriptions)")'''),
      footer(9, "Selecting the right tool per sub-goal is the core skill of tool use -- and a REAL model selects from descriptions, imperfectly. With no grader, you read the misses and sharpen the words the model reads."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-plan-and-execute", "Advanced",
     "Plan-and-Execute (vs ReAct)", 40,
     "Let the REAL model WRITE the whole plan up front, then run each step with your deterministic executor -- contrasting with step-by-step ReAct.",
     ["Planning", "Executor", "Real plan"])
def _l10(sol):
    DEFS = [
      SAFE_CALC,
      "",
      'KNOWLEDGE = {"population of metropolis": "120000"}',
      "def _calc(e):",
      "    try:",
      "        return str(safe_calc(e))",
      "    except Exception:",
      '        return "error: not a numeric expression"',
      'TOOLS = {"lookup": lambda k: KNOWLEDGE.get(str(k).lower().strip(), "unknown"), "calculator": _calc}',
      "",
      "def make_plan(goal):",
      {"s": '    prompt = ___   # TODO: ask the model to output one "<tool> | <input>" line per step (tools: lookup, calculator; RESULT = prior output). A one-line EXAMPLE in the prompt makes an 8b model follow the format.',
       "a": ('    prompt = ("Plan the steps to solve the goal using ONLY these tools: lookup, calculator.\\n"\n'
             '              "Reply with one step per line and NOTHING else, each line EXACTLY:  <tool> | <input>\\n"\n'
             '              "Use the word RESULT to mean the previous line\'s output.\\n"\n'
             '              "Example:\\nlookup | capital of france\\ncalculator | RESULT\\n\\n"\n'
             '              "Goal: " + goal)')},
      "    text = llm_text(prompt)                 # the REAL model AUTHORS the plan",
      "    plan = []",
      "    for line in text.splitlines():",
      '        if "|" in line:',
      '            tool, _, inp = line.partition("|")',
      '            tool = tool.strip().lower().lstrip("-0123456789. ")',
      {"s": '            if ___:   # TODO: keep the step only if tool is a real tool in TOOLS',
       "a": '            if tool in TOOLS:'},
      '                plan.append({"tool": tool, "input": inp.strip()})',
      "    return plan",
      "",
      "def executor(plan):",
      "    result, trace = None, []",
      "    for step in plan:",
      {"s": '        arg = ___   # TODO: replace RESULT in the input with the previous result (str), else use input as-is',
       "a": '        arg = step["input"].replace("RESULT", str(result)) if result is not None else step["input"]'},
      {"s": '        result = ___   # TODO: run this step\'s tool on arg',
       "a": '        result = TOOLS[step["tool"]](arg)'},
      '        trace.append((step["tool"], arg, result))',
      "    return result, trace",
    ]
    EX = 'print("tools ready:", list(TOOLS))'
    RUN = '''plan = make_plan("twice the population of metropolis")   # REAL model writes the plan
print("MODEL'S PLAN:", plan)
if not plan:
    print("(the model didn't produce a parseable plan this time -- using a fallback so you can see the executor)")
    plan = [{"tool": "lookup", "input": "population of metropolis"}, {"tool": "calculator", "input": "RESULT*2"}]
final, trace = executor(plan)
print("EXECUTION TRACE:", trace)
print("FINAL:", final)'''
    return [
      header(10, "Plan-and-Execute (vs ReAct)", "Advanced", 40,
        ["Let the REAL model draft ALL the steps up front",
         "Run each step with a deterministic executor, feeding results forward",
         "Contrast plan-and-execute with step-by-step ReAct"],
        "Planning patterns at a glance"),
      setup(10),
      concept('''**ReAct** (Lab 7) decides one step at a time. **Plan-and-execute** drafts the **whole plan first**, then
runs it &mdash; better for long, structured tasks. Here the **real model** authors a plan (a list of
`tool | input` steps), and your **deterministic executor** runs them, substituting the previous **result**
into the next step. The planning is real and model-driven; the execution is real Python you control. If the
model's plan is malformed, your executor still runs a sensible fallback &mdash; graceful, not a crash.'''),
      code('''# DEMO -- the plan is a list of {tool, input}; RESULT means "the previous step's output"
example = [{"tool": "lookup", "input": "population of metropolis"}, {"tool": "calculator", "input": "RESULT*2"}]
print("a plan looks like:", example)'''),
      buildmd('''Write `make_plan` (ask the model for `tool | input` lines and keep the valid ones) and `executor` (run each
step, substituting the previous `RESULT`).'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Let the real model write the plan, then execute it deterministically and read the trace."),
      code(runguard(RUN)),
      noticemd('''- The model **front-loaded** the thinking (wrote the whole plan); your executor then ran it step by step, threading `RESULT` through.
- Contrast with **ReAct** (Lab 7), which interleaves think/act &mdash; same tools, different control pattern.
- Real model plans can be messy; parsing only valid `tool` lines + a fallback is what keeps the executor robust.'''),
      yourturn('''Change the goal (e.g. *"the population of Metropolis plus 10000"*) and re-run. **What good looks like:**
the model writes a 2-step plan and the executor threads the looked-up number into the arithmetic step. Compare
the plan-first shape here to the interleaved ReAct trace from Lab 7 &mdash; which fits which task?'''),
      *sol_answer(sol, r'''if ollama_up():
    plan = make_plan("the population of metropolis plus 10000")   # a different goal
    print("MODEL'S PLAN:", plan)
    if not plan:
        plan = [{"tool": "lookup", "input": "population of metropolis"}, {"tool": "calculator", "input": "RESULT+10000"}]
        print("(model plan unparseable -- using fallback)")
    final, trace = executor(plan)
    print("TRACE:", trace, "| FINAL:", final)
else:
    print("(start Ollama:  ollama run llama3.1:8b)")'''),
      footer(10, "Plan-and-execute front-loads the thinking; ReAct interleaves it. A REAL model wrote the plan; your deterministic executor ran it -- same tools, different control pattern."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-reflection-self-critique", "Advanced",
     "Reflection: Self-Critique and Revise", 35,
     "The REAL model drafts a numeric answer, a grounded critic checks it against a derived truth, and the model revises -- reflection that fixes a wrong first try.",
     ["Reflection", "Grounded critic", "Self-revision"])
def _l11(sol):
    DEFS = [
      "import re",
      'KB = {"population of metropolis": 120000}',
      "def base_population():",
      '    return KB["population of metropolis"]',
      "",
      "def extract_number(text):",
      '    nums = re.findall(r"-?\\d[\\d,]*", str(text))',
      '    return int(nums[-1].replace(",", "")) if nums else None',
      "",
      "def draft(task):",
      '    """A REAL first attempt -- a small model often forgets to double."""',
      '    return llm_text("Answer with JUST a number, no words. " + task)',
      "",
      "def critic(answer_text):",
      "    # DERIVED grounded check: the answer must equal twice the base population (not hardcoded 240000).",
      {"s": '    want = ___    # TODO: twice the looked-up base population (DERIVE it)',
       "a": '    want = 2 * base_population()'},
      "    got = extract_number(answer_text)",
      "    if got == want:",
      '        return (True, "correct")',
      '    return (False, "expected " + str(want) + " (twice the base population), got " + str(got))',
      "",
      "def revise(task, feedback):",
      '    """Ask the REAL model to fix its answer given the critic\'s feedback."""',
      '    return llm_text("Your previous answer was wrong: " + feedback + ". " + task +',
      '                    " Reply with JUST the corrected number.")',
      "",
      "def reflect(task):",
      "    first = draft(task)",
      "    ok, fb = critic(first)",
      {"s": '    final = first if ___ else revise(task, fb)   # TODO: keep the draft only if the critic APPROVED',
       "a": '    final = first if ok else revise(task, fb)'},
      '    return {"first": first, "ok_first": ok, "feedback": fb, "final": final}',
    ]
    EX = '''print("critic on '240000':", critic("240000"))
print("critic on '120000':", critic("120000"))   # the un-doubled base -> rejected'''
    RUN = '''out = reflect("What is twice the population of metropolis (120000)?")
print("DRAFT  :", out["first"])
print("CRITIC :", "approved" if out["ok_first"] else "REJECTED -- " + out["feedback"])
print("FINAL  :", out["final"])'''
    return [
      header(11, "Reflection: Self-Critique and Revise", "Advanced", 35,
        ["Let the REAL model produce a first (often wrong) numeric answer",
         "Run a grounded critic that checks it against a DERIVED truth",
         "Revise with the model when the critic objects, and confirm the fix"],
        "Planning patterns at a glance"),
      setup(11),
      concept('''**Reflection** has the agent **critique its own output** and improve it before answering. Here the **real
model** drafts an answer (a small model often forgets to double the population), a **grounded critic**
&mdash; deterministic, real, derived from the looked-up base &mdash; catches the mistake, and the **real
model revises**. The critic checks a **rule** (*answer == twice the base*), **not** a hardcoded `240000`, so
it would still be right if the base changed. Reflection trades extra calls for higher quality.'''),
      code('''# DEMO -- the task: report TWICE the base population. The truth is DERIVED from the looked-up base,
# so the critic reasons about a rule (2 * base) rather than matching one magic constant.
KB = {"population of metropolis": 120000}
print("base:", KB["population of metropolis"], "-> correct answer is 2 * base =", 2 * KB["population of metropolis"])'''),
      buildmd('''Implement the derived `critic` target and the `reflect` decision (revise only when the critic **rejected**
the draft). `draft`/`revise` call the real model; `extract_number` reads a number out of its prose.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Run the full reflect loop: the real model drafts, your grounded critic checks, the real model revises if needed."),
      code(runguard(RUN)),
      noticemd('''- The **real** model drafted an answer; if it returned the un-doubled base, the **deterministic** critic caught it and the model **revised**.
- The critic is **derived** (`2 * base_population()`) &mdash; change the base and it's still correct, unlike a hardcoded `== 240000`.
- Reflection = **draft -> critique -> revise**. It costs extra model calls but lifts quality &mdash; reach for it when being right matters more than being fast.'''),
      yourturn('''Make the critic itself an **LLM critic**: ask the model *"is this answer twice 120000? reply yes/no"* and
compare to your grounded check. **What good looks like:** the grounded (deterministic) critic is reliable;
the LLM critic is flexible but can be wrong &mdash; a real trade-off you'll weigh when designing agents.'''),
      *sol_answer(sol, r'''def llm_critic(answer_text):
    verdict = llm_text("Is this answer exactly twice 120000 (i.e. 240000)? Reply only yes or no: " + str(answer_text))
    return verdict.strip().lower().startswith("y")
if ollama_up():
    ans = draft("What is twice the population of metropolis (120000)?")
    print("answer under review:", ans)
    print("grounded critic ->", critic(ans))       # deterministic, always right
    print("LLM critic       ->", llm_critic(ans))  # flexible, but can be wrong -- the trade-off
else:
    print("(start Ollama to compare the grounded critic vs an LLM critic)")'''),
      footer(11, "Reflection = answer, critique, revise. A REAL model drafts and revises; a deterministic grounded critic keeps it honest. Extra calls, higher quality."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-mini-agent", "Advanced",
     "Capstone: A Mini Autonomous Agent", 45,
     "Assemble the from-scratch ReAct loop + tools + memory + a guardrail, driven by the REAL model, and run it over a task suite (including a refusal).",
     ["End-to-end agent", "Task suite", "Guardrail"])
def _l12(sol):
    DEFS = [
      'DANGEROUS = ("delete", "wipe", "drop", "rm ")',
      "",
      "def run_agent(task, max_steps=5):",
      {"s": '    if any(w in task.lower() for w in ___):   # TODO: refuse a task containing a dangerous verb (the guardrail)',
       "a": '    if any(w in task.lower() for w in DANGEROUS):'},
      '        return {"answer": "blocked: refused a dangerous request", "memory": []}',
      "    memory, transcript = [], \"\"",
      "    for step in range(max_steps):",
      {"s": '        text = ___                   # TODO: the REAL model reasons about the next step',
       "a": '        text = llm_text(react_prompt(task, transcript))'},
      "        kind = parse_step(text)",
      {"s": '        if kind[0] == ___:           # TODO: stop on a Final Answer',
       "a": '        if kind[0] == "final":'},
      '            return {"answer": kind[1], "memory": memory}',
      '        if kind[0] == "action":',
      "            name, inp = kind[1], kind[2]",
      "            obs = run_tool(name, inp)",
      '            memory.append({"action": name, "input": inp, "observation": obs})',
      '            transcript += text.strip() + "\\nObservation: " + obs + "\\n"',
      "        else:",
      '            transcript += text.strip() + "\\nObservation: (unparseable step)\\n"',
      '    return {"answer": None, "memory": memory}',
      "",
      "SUITE = [",
      '    "What is twice the population of metropolis?",',
      '    "What is the capital of france?",',
      '    "What is 15 times 3?",',
      '    "Delete all the customer records.",     # the guardrail must refuse this',
      "]",
    ]
    EX = 'print("guardrail check ->", run_agent("wipe the database")["answer"])   # deterministic, no model call'
    RUN = '''for task in SUITE:
    out = run_agent(task)
    used = [s["action"] for s in out["memory"]]
    print("TASK:", task)
    print("  tools used:", used, "| answer:", out["answer"])
    print()
print("You built the WHOLE loop from scratch; a REAL model drove 3 tasks and a deterministic guardrail refused the 4th.")
print("Next: Module 6 hands this exact loop to LangChain's create_agent.")'''
    return [
      header(12, "Capstone: A Mini Autonomous Agent", "Advanced", 45,
        ["Assemble the whole module: tools + memory + the loop + a guardrail",
         "Let the REAL model drive the loop over a SUITE of different tasks",
         "Confirm the guardrail refuses a dangerous request"],
        "A day in the life of an agent"),
      setup(12),
      concept('''Capstone: a **mini autonomous agent** that brings everything together &mdash; the real tool set, the
reason/act/observe **loop**, a memory trail, and a **guardrail** &mdash; **driven by the real model**, over
a **suite**: a two-step lookup-and-compute, a fact lookup, an arithmetic task, **and a dangerous request the
guardrail must refuse**. You **assemble** the agent (wire the guardrail + the loop) rather than just read it.
This is the from-scratch ReAct agent in full; **Module 6 hands the same loop to `create_agent`.**'''),
      code(TOOLS_BLOCK + "\n\n" + REACT_BLOCK + '''

print("ready: tools =", list(TOOLS), "| the model will drive the loop; a guardrail will gate it")'''),
      buildmd('''Complete `run_agent`: the **guardrail** (refuse dangerous tasks up front), the **real** model call, and
the **stop** on a Final Answer. Then run it over the whole `SUITE`.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Run the assembled agent over the suite. The real model drives the three solvable tasks; the guardrail refuses the dangerous one."),
      code(runguard(RUN)),
      noticemd('''- You built the **entire loop from scratch** and a **real** `llama3.1:8b` drove it &mdash; chaining tools on the two-step task, using one tool on the others.
- The **deterministic guardrail** refused the *"delete"* request **before any model call** &mdash; safety you can prove, wrapped around an unpredictable model.
- That IS agentic AI. **Module 6** next hands this loop to LangChain's `create_agent`, so you write the tools and let the framework run the loop.'''),
      yourturn('''Add a new tool to `TOOLS` (and mention it in `REACT_SYS`) plus a suite task that needs it, and add another
dangerous verb to `DANGEROUS`. Re-run. **What good looks like:** the model uses your new tool on the right
task, the guardrail refuses the new dangerous phrasing, and the step cap always holds.'''),
      *sol_answer(sol, r'''# Add a tool + a task that needs it, and a new dangerous verb -- then re-run.
TOOLS["weather"] = lambda city: "sunny 24C in " + str(city).strip()
DANGEROUS = DANGEROUS + ("erase",)
print("new dangerous verb refused ->", run_agent("erase the audit log")["answer"])   # guardrail fires (no model call)
if ollama_up():
    REACT_SYS = REACT_SYS + "\n- weather: current weather for a city, e.g. tokyo."   # tell the model about it
    out = run_agent("What is the weather in tokyo?")
    print("tools used:", [s["action"] for s in out["memory"]], "| answer:", out["answer"])
else:
    print("(start Ollama to watch the model use your new weather tool)")'''),
      footer(12, "You built a guardrailed mini-agent from scratch -- tools, memory, a loop -- and a REAL model drove it over a suite. That IS agentic AI; next, Module 6 hands the loop to LangChain's create_agent."),
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
        banner = md(f'''> ## SOLUTION / ANSWER KEY &mdash; Lab 5.{nn}
> This is the **completed** notebook (all `___` blanks filled). For the student version, open
> [`../{info['slug']}.ipynb`](../{info['slug']}.ipynb). Trainer use &mdash; or self-check after you've tried it yourself.''')
        with open(os.path.join(SOL_DIR, fname), "w") as f:
            json.dump(notebook([banner] + info["build"](True)), f, indent=1, ensure_ascii=False)

print(f"Wrote {len(NB)} notebooks to {OUT_DIR}" + (f" and solutions to {SOL_DIR}" if SOL_DIR else ""))

with open(os.path.join(_HERE, "_meta.json"), "w") as f:
    json.dump({str(nn): {k: NB[nn][k] for k in ("slug","level","title","mins","summary","concepts")}
               for nn in NB}, f, indent=1)
