# -*- coding: utf-8 -*-
"""Generator for Day 3 Module 5 hands-on labs (12 notebooks).
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

Design: this is the "What is Agentic AI?" module, so the labs TEACH THE AGENT
MECHANICS by building a ReAct-style agent from scratch -- tools, the reason -> act
-> observe loop, ReAct parsing, tool routing, memory/scratchpad, guardrails,
plan-and-execute and reflection. Every GRADED cell uses ONLY the Python standard
library (no numpy/sklearn/transformers) driven by a deterministic rule-based
"mock LLM" policy, so the labs run and verify with NO network and NO installs.
Each Advanced lab adds ONE optional, non-graded, guarded cell that swaps the
rule-based policy for a REAL LLM via LangChain (Ollama llama3.2:1b, or Groq) --
it degrades gracefully if absent and never affects verification.
The calculator tool uses a small AST-based safe evaluator -- never bare eval()."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day3-module5-what-is-agentic-ai.html"
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
WORK = "/tmp/biaa-lab-05-{nn:02d}"
os.makedirs(WORK, exist_ok=True)
print("Working dir:", WORK){extra}''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 5.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 3 &middot; Module 5 &mdash; What is Agentic AI?**

### What you'll do
{g}

> **How this lab works (experiential flow):** read the **Concept**, run the **Demo** to see it work, then complete **Your Turn** by replacing every `___` placeholder. Run the **grader** cell at the end &mdash; it prints `[PASS]` / `[FAIL]` / `[TODO]` and a final `Score`. Aim for a full score.

**Reference:** [Module 5 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 5 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 5 labs](./index.html) &nbsp;&middot;&nbsp; [Module 5 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def optional_llm(intro, body):
    """An OPTIONAL, non-graded cell that swaps the rule-based policy for a REAL LLM."""
    return [md(f'''## Optional &mdash; swap the rule-based policy for a REAL LLM (not graded)
{intro} Safe to skip &mdash; it needs a local **Ollama** (`pip install langchain-ollama`, then
`ollama run llama3.2:1b`) or a **Groq** key (`pip install langchain-groq`, `GROQ_API_KEY`). If
neither is present the cell prints a friendly note and moves on. **The graded steps above run on a
deterministic rule-based policy, so the lab always verifies offline.**'''),
            code(body)]

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
     "Feel the core shift: a stateless model answers once; an agent takes an action toward a goal and can loop.",
     ["Stateless model", "Goal", "Action"])
def _l1(sol):
    return [
      header(1, "A Model that Answers vs an Agent that Acts", "Beginner", 20,
        ["See that a plain model is stateless: same input, same canned output, no memory",
         "Write a rule that DECIDES an action toward a goal",
         "Detect when the goal is met so the loop can stop"],
        "A model that answers &rarr; an agent that acts"),
      setup(1),
      md('''## Concept
A **language model** is a brilliant brain with no hands: give it a prompt, it returns text **once**,
then forgets. An **agent** wraps a model so it can take an **action toward a goal**, look at the
result, and **keep going** until the goal is met. In this lab we use a tiny rule as the "brain" to
feel that difference &mdash; the model just answers; the agent decides what to *do* next.'''),
      code('''# DEMO -- a stateless "model": same input always gives the same canned reply, no memory
def model_reply(prompt):
    canned = {"hello": "Hi there!", "what is 2+2": "I think it is 4."}
    return canned.get(prompt.lower().strip(), "I am not sure.")
print(model_reply("hello"))
print(model_reply("what is 2+2"))
print("Note: ask it twice, it has no idea you already asked -- it is stateless.")'''),
      md('''## Your Turn
An agent works toward a **goal**. Here the goal is a target number and `current` is where we are now.
Write `agent_decide` so it keeps acting until the target is reached, then signals it is done.'''),
      code(render([
        "def agent_decide(goal_target, current):",
        '    # return the ACTION the agent should take next',
        {"s": '    if ___:                    # TODO: have we reached or passed the target?',
         "a": '    if current >= goal_target:  # reached the goal'},
        {"s": '        return ___             # TODO: the action name when the goal is met',
         "a": '        return "done"'},
        {"s": '    return ___                 # TODO: the action that makes progress',
         "a": '    return "increment"'},
        "",
        "# A tiny loop that uses the decision rule (the agent 'acts' until done)",
        "def run(goal_target, max_steps=20):",
        "    current, steps = 0, 0",
        "    while steps < max_steps:",
        "        action = agent_decide(goal_target, current)",
        "        if action == 'done':",
        "            return current, steps",
        "        current += 1; steps += 1",
        "    return current, steps",
        "",
        "try:",
        "    print('agent reached', run(3), '(value, steps)')",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("agent returns an action string", lambda: agent_decide(3, 0) in {"increment", "done"})
expect_true("keeps acting while below the goal", lambda: agent_decide(3, 0) == "increment")
expect_true("detects the goal is met", lambda: agent_decide(3, 3) == "done")
expect_true("the loop actually reaches the goal", lambda: run(3)[0] == 3)
expect_true("the model is stateless / canned", lambda: model_reply("hello") == "Hi there!")'''),
      footer(1, "A model **answers**; an agent **acts toward a goal in a loop**. Everything else in this module &mdash; tools, memory, guardrails &mdash; hangs off that single shift."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-build-a-tool", "Beginner",
     "Build a Tool: Give the Agent Hands", 20,
     "Define tools as {name, description, fn}, register them, and wire up a SAFE calculator and a lookup tool.",
     ["Tool schema", "Registry", "Safe calculator"])
def _l2(sol):
    return [
      header(2, "Build a Tool: Give the Agent Hands", "Beginner", 20,
        ["Represent a tool as a dict with a name, a description and a function",
         "Build a registry that maps tool names to tools",
         "Implement a SAFE calculator (no bare eval) and a lookup tool"],
        "Tools turn an LLM into an agent"),
      setup(2),
      md('''## Concept
A model alone only emits **text**. A **tool** is a plain function you expose to it, described by a
**name**, a **description** (which the model reads to decide when to use it) and the **function**
itself. We collect tools in a **registry** keyed by name. Two staples: a **calculator** (LLMs are
bad at exact math &mdash; offload it) and a **lookup** over a small fixed knowledge base.

> **Safety:** never run bare `eval()` on free text. Our calculator uses a tiny **AST-based** safe
> evaluator that only allows numbers and arithmetic operators.'''),
      code(SAFE_CALC + '''
print("safe_calc('2+2') =", safe_calc("2+2"), "| safe_calc('3*(4+1)') =", safe_calc("3*(4+1)"))
# A bare eval() would happily run safe_calc("__import__('os').system('rm -rf /')") -- ours refuses.'''),
      md('''## Your Turn
Implement the two tool functions, then build the registry mapping each tool's name to its dict.'''),
      code(render([
        SAFE_CALC,
        "",
        'KNOWLEDGE = {"capital of france": "Paris", "population of metropolis": "120000"}',
        "",
        "def calculator_fn(expr):",
        {"s": '    return ___    # TODO: evaluate expr with the safe calculator',
         "a": '    return safe_calc(expr)'},
        "",
        "def lookup_fn(key):",
        {"s": '    return ___    # TODO: look key up in KNOWLEDGE (lowercased/stripped), default "unknown"',
         "a": '    return KNOWLEDGE.get(key.lower().strip(), "unknown")'},
        "",
        'calculator = {"name": "calculator", "description": "evaluate arithmetic like 2+2", "fn": calculator_fn}',
        'lookup     = {"name": "lookup", "description": "look up a known fact by key", "fn": lookup_fn}',
        "",
        "def build_registry(tools):",
        {"s": '    return ___    # TODO: a dict mapping each tool\'s name to the tool',
         "a": '    return {t["name"]: t for t in tools}'},
        "",
        "REGISTRY = {}",
        "try:",
        "    REGISTRY = build_registry([calculator, lookup])",
        "    print('tools:', list(REGISTRY))",
        "    print('calculator(2+2) =', REGISTRY['calculator']['fn']('2+2'))",
        "    print('lookup(capital of france) =', REGISTRY['lookup']['fn']('capital of france'))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("registry holds both tools", lambda: set(REGISTRY) >= {"calculator", "lookup"})
expect_true("each tool has name/description/fn", lambda: all({"name","description","fn"} <= set(t) for t in REGISTRY.values()))
expect_true("calculator tool computes 2+2 == 4", lambda: REGISTRY["calculator"]["fn"]("2+2") == 4)
expect_true("lookup tool finds a known key", lambda: REGISTRY["lookup"]["fn"]("capital of france") == "Paris")
expect_true("lookup returns 'unknown' for a missing key", lambda: REGISTRY["lookup"]["fn"]("price of gold") == "unknown")'''),
      footer(2, "A tool is just `{name, description, fn}` in a registry. That description is what a real LLM reads to choose a tool &mdash; next we make the agent route to the right one."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-the-agent-loop", "Beginner",
     "The Agent Loop: Reason, Act, Observe", 20,
     "Implement the reason -> act -> observe loop with a stop condition and a max_steps cap.",
     ["Agent loop", "Stop condition", "max_steps"])
def _l3(sol):
    return [
      header(3, "The Agent Loop: Reason, Act, Observe", "Beginner", 20,
        ["Run the reason -> act -> observe cycle driven by a rule-based policy",
         "Stop when the policy returns a final answer",
         "Cap the loop with max_steps so it can never run forever"],
        "The agent loop"),
      setup(3),
      md('''## Concept
Every agent runs the same cycle: **Reason** (decide the next step), **Act** (call a tool),
**Observe** (read the result), then **repeat** &mdash; until it can **stop** and answer. That is
**ReAct** (Reason + Act). Two non-negotiables: a **stop condition** (the policy says "final") and a
**max_steps** cap so a stuck agent cannot loop forever.'''),
      code('''# DEMO -- a rule-based "mock LLM" policy and one tool (increment)
def policy(goal, last_obs):
    # goal = {"target": N}. Count up until we reach the target, then finish.
    if last_obs is not None and last_obs >= goal["target"]:
        return ("final", "reached " + str(last_obs))
    return ("increment", (last_obs or 0))

TOOLS = {"increment": lambda x: x + 1}
print("policy first move:", policy({"target": 3}, None))'''),
      md('''## Your Turn
Implement `run_loop`: ask the policy, stop on a final answer, otherwise run the tool and observe.'''),
      code(render([
        "def run_loop(goal, max_steps=10):",
        "    last_obs, steps = None, 0",
        "    for _ in range(max_steps):",
        {"s": '        action, arg = ___   # TODO: ask the policy for the next (action, arg)',
         "a": '        action, arg = policy(goal, last_obs)'},
        "        steps += 1",
        {"s": '        if ___:             # TODO: stop when the policy says we are done',
         "a": '        if action == "final":'},
        '            return {"answer": arg, "steps": steps, "stopped": "final"}',
        {"s": '        last_obs = ___      # TODO: run the chosen tool on arg (act + observe)',
         "a": '        last_obs = TOOLS[action](arg)'},
        '    return {"answer": None, "steps": steps, "stopped": "max_steps"}',
        "",
        "try:",
        "    print(run_loop({'target': 3}))",
        "    print(run_loop({'target': 999}, max_steps=5))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("loop returns a final answer", lambda: run_loop({"target": 3})["answer"] is not None)
expect_true("loop terminates via 'final' (not max_steps)", lambda: run_loop({"target": 3})["stopped"] == "final")
expect_true("answer reflects the reached target", lambda: "reached 3" in run_loop({"target": 3})["answer"])
expect_true("respects max_steps on an impossible goal", lambda: run_loop({"target": 999}, max_steps=5)["steps"] == 5)
expect_true("an impossible goal stops at the cap", lambda: run_loop({"target": 999}, max_steps=5)["stopped"] == "max_steps")'''),
      footer(3, "Reason -> act -> observe, repeat, with a stop condition and a step cap. That loop IS the agent &mdash; everything from here makes each step smarter and safer."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-react-step-parsing", "Beginner",
     "Parsing a ReAct Step", 20,
     "Parse a ReAct-formatted string into Thought / Action / Action Input / Final Answer.",
     ["ReAct format", "Parsing", "Final Answer"])
def _l4(sol):
    return [
      header(4, "Parsing a ReAct Step", "Beginner", 20,
        ["Read the ReAct text format an LLM produces",
         "Extract the Action name and its Action Input",
         "Detect when the step is a Final Answer"],
        "Tools &amp; function-calling &mdash; a ReAct trace"),
      setup(4),
      md('''## Concept
A ReAct agent's LLM emits **structured text**: a `Thought:`, then either an `Action:` + `Action
Input:` (call a tool) or a `Final Answer:` (stop). The orchestrator must **parse** that text to know
what to do next. Here we parse it with pure string handling &mdash; no model needed.'''),
      code('''# DEMO -- the two kinds of step an agent produces
SAMPLE = """Thought: I need the population, so I should look it up.
Action: lookup
Action Input: population of metropolis"""

FINAL = """Thought: I now have everything I need.
Final Answer: 120000"""
print(SAMPLE)
print("---")
print(FINAL)'''),
      md('''## Your Turn
Write `field(text, label)` to read the text after a `Label:` line, then detect a Final Answer.'''),
      code(render([
        'SAMPLE = """Thought: I need the population, so I should look it up.',
        "Action: lookup",
        'Action Input: population of metropolis"""',
        "",
        'FINAL = """Thought: I now have everything I need.',
        'Final Answer: 120000"""',
        "",
        "def field(text, label):",
        "    for line in text.splitlines():",
        {"s": '        if line.strip().startswith(___):   # TODO: the label followed by a colon',
         "a": '        if line.strip().startswith(label + ":"):'},
        {"s": '            return ___    # TODO: the text after the first colon, stripped',
         "a": '            return line.split(":", 1)[1].strip()'},
        "    return None",
        "",
        "def is_final(text):",
        {"s": '    return ___    # TODO: True if a Final Answer line is present',
         "a": '    return field(text, "Final Answer") is not None'},
        "",
        "try:",
        "    print('action      =', field(SAMPLE, 'Action'))",
        "    print('action input=', field(SAMPLE, 'Action Input'))",
        "    print('SAMPLE final?', is_final(SAMPLE), '| FINAL final?', is_final(FINAL))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("extracts the action name", lambda: field(SAMPLE, "Action") == "lookup")
expect_true("extracts the action input", lambda: field(SAMPLE, "Action Input") == "population of metropolis")
expect_true("'Action' does not accidentally grab 'Action Input'", lambda: field(SAMPLE, "Action") != "population of metropolis")
expect_true("no Final Answer in the action step", lambda: is_final(SAMPLE) is False)
expect_true("detects a Final Answer", lambda: is_final(FINAL) is True)
expect_true("extracts the final answer text", lambda: field(FINAL, "Final Answer") == "120000")'''),
      footer(4, "The orchestrator turns the model's text into structured steps. Real LangChain output parsers do exactly this &mdash; now you know what they are reading."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-tool-routing", "Beginner",
     "Tool Routing: Dispatch an Action to a Tool", 20,
     "Route an action name to the right tool, run it, capture the observation, and handle unknown tools safely.",
     ["Routing", "Observation", "Error handling"])
def _l5(sol):
    return [
      header(5, "Tool Routing: Dispatch an Action to a Tool", "Beginner", 20,
        ["Look a tool up by name in the registry",
         "Run it and capture the observation the agent will read next",
         "Handle an unknown tool (and a failing tool) without crashing"],
        "Anatomy of an agent"),
      setup(5),
      md('''## Concept
Once the agent has chosen an **action name**, the orchestrator must **route** it to the matching
tool, run it, and wrap the result as an **observation**. Real agents hallucinate tool names, so
routing must fail **safely**: an unknown tool returns a message, not a crash.'''),
      code(SAFE_CALC + '''
KNOWLEDGE = {"capital of france": "Paris", "population of metropolis": "120000"}
REGISTRY = {
    "calculator": {"name": "calculator", "fn": safe_calc},
    "lookup":     {"name": "lookup", "fn": lambda k: KNOWLEDGE.get(k.lower().strip(), "unknown")},
}
print("registry:", list(REGISTRY))'''),
      md('''## Your Turn
Implement `route`: find the tool, run it, return a dict; handle unknown tools and tool errors.'''),
      code(render([
        "def route(registry, action, arg):",
        {"s": '    tool = ___    # TODO: get the tool by name (None if it is not registered)',
         "a": '    tool = registry.get(action)'},
        "    if tool is None:",
        {"s": '        return {"ok": False, "observation": ___}   # TODO: a message naming the unknown tool',
         "a": '        return {"ok": False, "observation": "unknown tool: " + action}'},
        "    try:",
        {"s": '        result = ___   # TODO: run the tool function on arg',
         "a": '        result = tool["fn"](arg)'},
        '        return {"ok": True, "observation": result}',
        "    except Exception as e:",
        '        return {"ok": False, "observation": "tool error: " + type(e).__name__}',
        "",
        "try:",
        "    print(route(REGISTRY, 'calculator', '10/2'))",
        "    print(route(REGISTRY, 'lookup', 'capital of france'))",
        "    print(route(REGISTRY, 'no_such_tool', 'x'))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("routes the calculator correctly", lambda: route(REGISTRY, "calculator", "10/2")["observation"] == 5.0)
expect_true("routes the lookup correctly", lambda: route(REGISTRY, "lookup", "capital of france")["observation"] == "Paris")
expect_true("ok flag is True on success", lambda: route(REGISTRY, "calculator", "2+2")["ok"] is True)
expect_true("unknown tool handled without crashing", lambda: route(REGISTRY, "no_such_tool", "x")["ok"] is False)
expect_true("unknown tool message names the tool", lambda: "no_such_tool" in route(REGISTRY, "no_such_tool", "x")["observation"])'''),
      footer(5, "Routing turns a chosen action into a real observation &mdash; safely. The split between deciding (the policy) and executing (the router) is what makes agents debuggable."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-memory-scratchpad", "Beginner",
     "Memory: the Agent's Scratchpad", 20,
     "Append (thought, action, observation) steps to memory, format a running scratchpad, and detect when to stop.",
     ["Short-term memory", "Scratchpad", "Stop detection"])
def _l6(sol):
    return [
      header(6, "Memory: the Agent's Scratchpad", "Beginner", 20,
        ["Append each (thought, action, observation) step to a memory list",
         "Format the memory into a running scratchpad string",
         "Detect when a Final Answer has been reached so the loop stops"],
        "Memory &mdash; short-term &amp; long-term"),
      setup(6),
      md('''## Concept
The agent's **short-term memory** is a **scratchpad**: the running transcript of every Thought,
Action and Observation so far. It is how the agent knows **what it already tried**. We store steps
in a list and format them back into the text the model re-reads each turn.'''),
      code('''# DEMO -- one step is just a small dict
step = {"thought": "I need the population", "action": "lookup", "observation": "120000"}
print(step)'''),
      md('''## Your Turn
Implement `remember`, `scratchpad`, and `should_stop`.'''),
      code(render([
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
        "",
        "try:",
        "    m = make_memory()",
        "    remember(m, 'I need the population', 'lookup', '120000')",
        "    print(scratchpad(m))",
        "    print('stop?', should_stop(m))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("memory grows by one per step", lambda: len(remember(make_memory(), "t", "a", "o")) == 1)
expect_true("a step stores its observation", lambda: remember(make_memory(), "t", "lookup", "120000")[0]["observation"] == "120000")
expect_true("scratchpad mentions the action", lambda: "lookup" in scratchpad(remember(make_memory(), "t", "lookup", "Paris")))
expect_true("scratchpad has one line per step", lambda: scratchpad(remember(remember(make_memory(), "t", "lookup", "x"), "t", "calculator", "y")).count(chr(10)) == 1)
expect_true("stop detected on a final step", lambda: should_stop(remember(make_memory(), "t", "final", "done")) is True)
expect_true("no stop before a final step", lambda: should_stop(remember(make_memory(), "t", "lookup", "x")) is False)'''),
      footer(6, "The scratchpad is the agent's working memory for one task. Long-term memory (a vector store) comes with RAG later &mdash; but every loop needs this short-term notebook."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-rule-based-react-agent", "Intermediate",
     "A Rule-Based ReAct Agent (two-step task)", 30,
     "Combine tools + loop + memory + a policy to solve a two-step task: look up a fact, then compute on it.",
     ["ReAct agent", "Tool chaining", "Two-step task"])
def _l7(sol):
    return [
      header(7, "A Rule-Based ReAct Agent (two-step task)", "Intermediate", 30,
        ["Wire tools + memory + a loop + a policy into one working agent",
         "Solve a TWO-step task: look up the population, then double it",
         "Confirm both tools were used and the loop terminated"],
        "The agent loop"),
      setup(7),
      md('''## Concept
Now we assemble the pieces from Labs 2&ndash;6 into a real **ReAct agent**. The task &mdash;
*"twice the population of Metropolis"* &mdash; needs **two** tools chained: first **lookup** the
population, then **calculator** to double it. The rule-based **policy** reads the memory to decide
what is still missing and what to do next.'''),
      code(SAFE_CALC + '''
KNOWLEDGE = {"population of metropolis": "120000", "capital of france": "Paris"}
TOOLS = {
    "lookup":     {"fn": lambda k: KNOWLEDGE.get(k.lower().strip(), "unknown")},
    "calculator": {"fn": safe_calc},
}
print("tools ready:", list(TOOLS))'''),
      md('''## Your Turn
Fill the policy's two-step reasoning. `run_agent` (provided) runs the loop and memory for you.'''),
      code(render([
        "def policy(goal, memory):",
        '    seen = [s["action"] for s in memory]',
        '    if "lookup" not in seen:',
        {"s": '        return ("lookup", ___)   # TODO: the key to look up the population',
         "a": '        return ("lookup", "population of metropolis")'},
        '    pop = int([s["observation"] for s in memory if s["action"] == "lookup"][0])',
        '    if "calculator" not in seen:',
        {"s": '        return ("calculator", ___)   # TODO: an expression for twice the population',
         "a": '        return ("calculator", str(pop) + "*2")'},
        '    answer = [s["observation"] for s in memory if s["action"] == "calculator"][0]',
        {"s": '    return (___, str(answer))   # TODO: the action name that ENDS the loop',
         "a": '    return ("final", str(answer))'},
        "",
        "def run_agent(goal, max_steps=8):",
        "    memory = []",
        "    for _ in range(max_steps):",
        "        action, arg = policy(goal, memory)",
        "        if action == 'final':",
        "            return {'answer': arg, 'memory': memory}",
        "        obs = TOOLS[action]['fn'](arg)",
        "        memory.append({'action': action, 'observation': obs})",
        "    return {'answer': None, 'memory': memory}",
        "",
        "try:",
        "    out = run_agent('twice the population of metropolis')",
        "    print('answer:', out['answer'])",
        "    print('actions used:', [s['action'] for s in out['memory']])",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("final answer is twice the population", lambda: run_agent("twice the population of metropolis")["answer"] == "240000")
expect_true("the lookup tool was used", lambda: any(s["action"] == "lookup" for s in run_agent("x")["memory"]))
expect_true("the calculator tool was used", lambda: any(s["action"] == "calculator" for s in run_agent("x")["memory"]))
expect_true("tools ran in order: lookup then calculator", lambda: [s["action"] for s in run_agent("x")["memory"]] == ["lookup", "calculator"])
expect_true("the loop terminated with an answer", lambda: run_agent("x")["answer"] is not None)'''),
      footer(7, "Tools + memory + loop + policy = a working ReAct agent that chains two tools. Swap the rule-based policy for an LLM and you have the real thing (Module 6)."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-guardrails", "Intermediate",
     "Guardrails: Keep the Agent Safe", 30,
     "Add a max_steps cap, a tool allow-list, repeated-action loop detection, and input validation.",
     ["Allow-list", "Loop detection", "Input validation"])
def _l8(sol):
    return [
      header(8, "Guardrails: Keep the Agent Safe", "Intermediate", 30,
        ["Allow-list the tools an agent may call",
         "Detect a runaway loop (the same action repeated)",
         "Validate tool input and stop a runaway agent safely"],
        "Guardrails &amp; human-in-the-loop"),
      setup(8),
      md('''## Concept
Autonomy needs **guardrails**. Four cheap, essential ones: a **max_steps** cap (already in the
loop), a **tool allow-list** (only call permitted tools), **loop detection** (stop if the same
action repeats), and **input validation** (reject dangerous tool inputs). Together they stop an
agent that hallucinates a tool, gets stuck, or is fed garbage.'''),
      code('''# DEMO
ALLOWED = {"lookup", "calculator"}
ALLOWED_CHARS = set("0123456789+-*/(). ")
print("allowed tools:", ALLOWED)
print("'rm -rf /' allowed as a tool?", "rm_rf" in ALLOWED)'''),
      md('''## Your Turn
Implement the three guards, then see them stop a deliberately runaway agent.'''),
      code(render([
        'ALLOWED = {"lookup", "calculator"}',
        'ALLOWED_CHARS = set("0123456789+-*/(). ")',
        "",
        "def is_allowed(action):",
        {"s": '    return ___    # TODO: True only if action is in the allow-list',
         "a": '    return action in ALLOWED'},
        "",
        "def detect_loop(memory, k=3):",
        '    actions = [s["action"] for s in memory]',
        {"s": '    return len(actions) >= k and ___   # TODO: True if the last k actions are all identical',
         "a": '    return len(actions) >= k and len(set(actions[-k:])) == 1'},
        "",
        "def is_valid_calc_input(expr):",
        {"s": '    return all(c in ALLOWED_CHARS for c in expr) and ___   # TODO: require at least one digit',
         "a": '    return all(c in ALLOWED_CHARS for c in expr) and any(c.isdigit() for c in expr)'},
        "",
        "# A guarded runner that uses the guards above (provided)",
        "def safe_run(policy, max_steps=10):",
        "    memory = []",
        "    for i in range(max_steps):",
        "        action, arg = policy(memory)",
        "        if not is_allowed(action):",
        "            return {'stopped': 'blocked_tool', 'steps': i}",
        "        if detect_loop(memory + [{'action': action}]):",
        "            return {'stopped': 'loop_detected', 'steps': i}",
        "        memory.append({'action': action, 'observation': '...'})",
        "    return {'stopped': 'max_steps', 'steps': max_steps}",
        "",
        "try:",
        "    print('runaway (always lookup):', safe_run(lambda m: ('lookup', 'x')))",
        "    print('bad tool (rm_rf):       ', safe_run(lambda m: ('rm_rf', '/')))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("allow-list permits a known tool", lambda: is_allowed("calculator") is True)
expect_true("allow-list blocks an unknown tool", lambda: is_allowed("delete_database") is False)
expect_true("loop detector fires on 3 repeats", lambda: detect_loop([{"action": "lookup"}] * 3) is True)
expect_true("loop detector tolerates varied actions", lambda: detect_loop([{"action": "lookup"}, {"action": "calculator"}, {"action": "lookup"}]) is False)
expect_true("valid calc input accepted", lambda: is_valid_calc_input("2 + 2*3") is True)
expect_true("dangerous calc input rejected", lambda: is_valid_calc_input("__import__('os')") is False)
expect_true("a runaway agent is stopped, not infinite", lambda: safe_run(lambda m: ("lookup", "x"))["stopped"] in {"loop_detected", "max_steps"})
expect_true("a disallowed tool is blocked at step 0", lambda: safe_run(lambda m: ("rm_rf", "/"))["stopped"] == "blocked_tool")'''),
      footer(8, "Allow-list, loop detection and input validation turn an autonomous agent from a liability into a tool you can trust. Day 5 goes deeper on responsible agents."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-tool-selection", "Intermediate",
     "Tool Selection: Pick the Right Tool", 30,
     "With a larger tool set, select the right tool per sub-goal across several tasks and measure accuracy.",
     ["Tool selection", "Routing rules", "Accuracy"])
def _l9(sol):
    return [
      header(9, "Tool Selection: Pick the Right Tool", "Intermediate", 30,
        ["Choose the correct tool from a larger set for each request",
         "Write selection rules keyed on the request text",
         "Measure selection accuracy across a suite of tasks"],
        "Tools turn an LLM into an agent"),
      setup(9),
      md('''## Concept
With more than two tools, the agent must **select** the right one for each sub-goal &mdash; the
hardest part of tool use. A real agent reads each tool's **description**; here we use simple keyword
rules and **measure** how often the choice is right. Good selection is the difference between a
useful agent and a confused one.'''),
      code('''# DEMO -- four tools, several tagged tasks
TOOLSET = {"calculator", "weather", "translate", "lookup"}
TASKS = [
    {"text": "what is 12 * 8", "tool": "calculator"},
    {"text": "today's weather in tokyo", "tool": "weather"},
    {"text": "translate hello to french", "tool": "translate"},
    {"text": "capital of france", "tool": "lookup"},
    {"text": "what is 100 / 4", "tool": "calculator"},
    {"text": "weather in paris", "tool": "weather"},
]
print("tools:", TOOLSET, "| tasks:", len(TASKS))'''),
      md('''## Your Turn
Write `select_tool` so it picks the right tool for each task, then compute selection accuracy.'''),
      code(render([
        'TOOLSET = {"calculator", "weather", "translate", "lookup"}',
        "TASKS = [",
        '    {"text": "what is 12 * 8", "tool": "calculator"},',
        '    {"text": "today\'s weather in tokyo", "tool": "weather"},',
        '    {"text": "translate hello to french", "tool": "translate"},',
        '    {"text": "capital of france", "tool": "lookup"},',
        '    {"text": "what is 100 / 4", "tool": "calculator"},',
        '    {"text": "weather in paris", "tool": "weather"},',
        "]",
        "",
        "def select_tool(text):",
        "    t = text.lower()",
        {"s": '    if ___:               # TODO: a weather request mentions weather',
         "a": '    if "weather" in t:'},
        '        return "weather"',
        '    if "translate" in t:',
        '        return "translate"',
        {"s": '    if ___:               # TODO: any digit means an arithmetic task',
         "a": '    if any(ch.isdigit() for ch in t):'},
        {"s": '        return ___        # TODO: the calculator tool name',
         "a": '        return "calculator"'},
        '    return "lookup"',
        "",
        "def selection_accuracy():",
        {"s": '    correct = ___   # TODO: count tasks where select_tool matches the expected tool',
         "a": '    correct = sum(1 for task in TASKS if select_tool(task["text"]) == task["tool"])'},
        "    return correct / len(TASKS)",
        "",
        "try:",
        "    for task in TASKS:",
        "        print(task['tool'], '<-', select_tool(task['text']))",
        "    print('selection accuracy:', selection_accuracy())",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("'12 * 8' routes to calculator", lambda: select_tool("what is 12 * 8") == "calculator")
expect_true("a weather request routes to weather", lambda: select_tool("weather in paris") == "weather")
expect_true("'translate ...' routes to translate", lambda: select_tool("translate hello to french") == "translate")
expect_true("a plain fact routes to lookup", lambda: select_tool("capital of france") == "lookup")
expect_true("selection accuracy is 100% on the suite", lambda: selection_accuracy() == 1.0)'''),
      footer(9, "Selecting the right tool per sub-goal is the core skill of tool use. A real LLM does it from tool descriptions &mdash; the rule here makes the mechanism visible."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-plan-and-execute", "Advanced",
     "Plan-and-Execute (vs ReAct)", 40,
     "Draft a full plan up front, then execute each step's tool -- contrasting with step-by-step ReAct.",
     ["Planning", "Executor", "Plan vs ReAct"])
def _l10(sol):
    return [
      header(10, "Plan-and-Execute (vs ReAct)", "Advanced", 40,
        ["Write a planner that drafts all steps up front",
         "Write an executor that runs each step, feeding results forward",
         "Contrast plan-and-execute with step-by-step ReAct"],
        "Planning patterns at a glance"),
      setup(10),
      md('''## Concept
**ReAct** decides one step at a time. **Plan-and-execute** drafts the **whole plan first**, then
runs it &mdash; better for long, structured tasks. Here a `planner(goal)` returns a list of
`{tool, input}` steps and an `executor` runs them, substituting the previous result into the next
step. (The optional cell lets a real LLM write the plan.)'''),
      code(SAFE_CALC + '''
KNOWLEDGE = {"population of metropolis": "120000"}
TOOLS = {
    "lookup":     {"fn": lambda k: KNOWLEDGE.get(k.lower().strip(), "unknown")},
    "calculator": {"fn": safe_calc},
}
print("tools ready:", list(TOOLS))'''),
      md('''## Your Turn
Write the two-step plan, then the executor that substitutes the previous RESULT into each step.'''),
      code(render([
        "def planner(goal):",
        "    # draft ALL steps up front (a fixed plan for: twice the population of Metropolis)",
        "    return [",
        {"s": '        {"tool": "lookup", "input": ___},   # TODO: what to look up',
         "a": '        {"tool": "lookup", "input": "population of metropolis"},'},
        {"s": '        {"tool": ___, "input": "RESULT*2"},  # TODO: the tool that does arithmetic',
         "a": '        {"tool": "calculator", "input": "RESULT*2"},'},
        "    ]",
        "",
        "def executor(plan):",
        "    result, trace = None, []",
        "    for step in plan:",
        {"s": '        arg = ___   # TODO: replace RESULT in the input with the previous result (str), else use input as-is',
         "a": '        arg = step["input"].replace("RESULT", str(result)) if result is not None else step["input"]'},
        {"s": '        result = ___   # TODO: run this step tool on arg',
         "a": '        result = TOOLS[step["tool"]]["fn"](arg)'},
        '        trace.append((step["tool"], result))',
        "    return result, trace",
        "",
        "try:",
        "    plan = planner('twice the population of metropolis')",
        "    final, trace = executor(plan)",
        "    print('plan:', plan)",
        "    print('trace:', trace)",
        "    print('final:', final)",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("plan has two steps", lambda: len(planner("x")) == 2)
expect_true("first step uses lookup", lambda: planner("x")[0]["tool"] == "lookup")
expect_true("second step uses calculator", lambda: planner("x")[1]["tool"] == "calculator")
expect_true("executing the plan yields twice the population", lambda: executor(planner("x"))[0] == 240000)
expect_true("the trace records both tool runs", lambda: [t for t, _ in executor(planner("x"))[1]] == ["lookup", "calculator"])'''),
      *optional_llm(
        "Let a REAL LLM WRITE the plan; your executor above still runs the tools deterministically.",
        '''try:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.2:1b")
    prompt = ("List the 2 steps (each as tool + input) to find twice the population of Metropolis. "
              "Tools available: lookup, calculator. Be terse.")
    print("LLM plan:\\n", llm.invoke(prompt).content)
    print("A real LLM can author the plan; the executor pattern above is unchanged.")
except Exception as e:
    print("No local LLM available -- skipping (install langchain-ollama + `ollama run llama3.2:1b`,", type(e).__name__)
    print("or use Groq: `from langchain_groq import ChatGroq` with GROQ_API_KEY).")
    print("The rule-based planner above already produced and executed a correct plan offline.")'''),
      footer(10, "Plan-and-execute front-loads the thinking; ReAct interleaves it. Same tools, different control pattern &mdash; pick the one that fits the task's shape."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-reflection-self-critique", "Advanced",
     "Reflection: Self-Critique and Revise", 35,
     "Produce an answer, critique it against a rule, and revise -- seeded so reflection demonstrably fixes a wrong first try.",
     ["Reflection", "Critic", "Self-revision"])
def _l11(sol):
    return [
      header(11, "Reflection: Self-Critique and Revise", "Advanced", 35,
        ["Produce a (deliberately wrong) first answer",
         "Run a critic that checks the answer against a rule",
         "Revise when the critic objects, and confirm the fix"],
        "Planning patterns at a glance"),
      setup(11),
      md('''## Concept
**Reflection** has the agent **critique its own output** and improve it before answering. We seed a
**wrong first attempt** (it forgets to double the population), run a **critic** that catches the
mistake, and **revise**. Reflection trades extra work for higher quality &mdash; here it turns a
wrong answer into a right one.'''),
      code('''# DEMO -- the task: report TWICE the population of Metropolis (120000) => 240000
EXPECTED = 240000
def first_attempt(goal):
    # a naive agent that forgets to double -- deliberately wrong
    return 120000
print("naive first answer:", first_attempt("twice the population"), "(should be", EXPECTED, ")")'''),
      md('''## Your Turn
Implement the critic, the revision, and the reflect loop that revises only when the critic objects.'''),
      code(render([
        "EXPECTED = 240000",
        "def first_attempt(goal):",
        "    return 120000   # deliberately wrong (forgot to double)",
        "",
        "def critic(answer):",
        "    # return (ok, feedback)",
        {"s": '    if answer == ___:    # TODO: the expected (correct) value',
         "a": '    if answer == EXPECTED:'},
        '        return (True, "looks correct")',
        '    return (False, "you forgot to double the population")',
        "",
        "def revise(answer, feedback):",
        {"s": '    return ___    # TODO: double the answer to fix the mistake',
         "a": '    return answer * 2'},
        "",
        "def reflective_answer(goal):",
        "    ans = first_attempt(goal)",
        "    ok, feedback = critic(ans)",
        {"s": '    if ___:    # TODO: revise only when the critic REJECTED the answer',
         "a": '    if not ok:'},
        "        ans = revise(ans, feedback)",
        '    return {"final": ans, "critic_fired": not ok}',
        "",
        "try:",
        "    out = reflective_answer('twice the population of metropolis')",
        "    print('final:', out['final'], '| critic fired:', out['critic_fired'])",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("reflection corrects the final answer", lambda: reflective_answer("x")["final"] == 240000)
expect_true("the critic fired on the wrong first answer", lambda: reflective_answer("x")["critic_fired"] is True)
expect_true("critic accepts a correct answer", lambda: critic(240000)[0] is True)
expect_true("critic rejects a wrong answer", lambda: critic(120000)[0] is False)
expect_true("revise applies the fix", lambda: revise(120000, "double it") == 240000)'''),
      *optional_llm(
        "Let a REAL LLM be the critic; the answer -> critique -> revise loop above is identical.",
        '''try:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.2:1b")
    draft = "The answer is 120000."
    review = llm.invoke("The task was 'twice the population (120000) of Metropolis'. "
                        "Critique this answer in one line: " + draft).content
    print("LLM critic says:", review)
    print("A real LLM critic catches subtler mistakes; the reflect loop is unchanged.")
except Exception as e:
    print("No local LLM available -- skipping (install langchain-ollama + `ollama run llama3.2:1b`,", type(e).__name__)
    print("or use Groq: `from langchain_groq import ChatGroq` with GROQ_API_KEY).")
    print("The rule-based critic above already caught the wrong first answer and triggered a revision.")'''),
      footer(11, "Reflection = answer, critique, revise. It costs extra calls but lifts quality &mdash; reach for it when being right matters more than being fast."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-mini-agent", "Advanced",
     "Capstone: A Mini Autonomous Agent", 45,
     "Assemble tools + memory + guardrails + a reason/act/observe loop and run it over a small suite of tasks.",
     ["End-to-end agent", "Task suite", "Guardrails"])
def _l12(sol):
    return [
      header(12, "Capstone: A Mini Autonomous Agent", "Advanced", 45,
        ["Assemble the whole module: tools + memory + guardrails + the loop",
         "Run the agent over a SUITE of different tasks",
         "Score tasks solved / total and confirm guardrails hold"],
        "A day in the life of an agent"),
      setup(12),
      md('''## Concept
Capstone: a **mini autonomous agent** that brings together everything &mdash; a tool registry, a
reason/act/observe **loop**, **memory**, and a **guardrail** (only allowed tools) &mdash; and runs
it over a **suite** of tasks (a two-step lookup-and-compute, a fact lookup, and an arithmetic task).
The score reflects **tasks solved / total**. The optional cell swaps the rule-based policy for a
**real LangChain agent** &mdash; the bridge to Module 6.'''),
      code(SAFE_CALC + '''
KB = {"population of metropolis": "120000", "capital of france": "Paris"}
TOOLS = {"calculator": safe_calc, "lookup": lambda k: KB.get(k.lower().strip(), "unknown")}
ALLOWED = set(TOOLS)
print("tools:", list(TOOLS), "| allow-list:", ALLOWED)'''),
      md('''## Your Turn
Complete the policy routing, the guardrail check, and the suite evaluation. `run_agent` ties it together.'''),
      code(render([
        "def policy(goal, memory):",
        '    seen = [s["action"] for s in memory]',
        "    text = goal.lower()",
        '    if "population" in text and "twice" in text:',
        '        if "lookup" not in seen:',
        '            return ("lookup", "population of metropolis")',
        '        if "calculator" not in seen:',
        '            pop = int([s["observation"] for s in memory if s["action"] == "lookup"][0])',
        '            return ("calculator", str(pop) + "*2")',
        '        return ("final", str([s["observation"] for s in memory if s["action"] == "calculator"][0]))',
        '    if "capital" in text:',
        '        if "lookup" not in seen:',
        '            return ("lookup", "capital of france")',
        '        return ("final", [s["observation"] for s in memory if s["action"] == "lookup"][0])',
        '    if "compute" in text:',
        '        if "calculator" not in seen:',
        {"s": '            return ("calculator", ___)   # TODO: the math expression after the word "compute"',
         "a": '            return ("calculator", goal.split("compute")[-1].strip())'},
        '        return ("final", str([s["observation"] for s in memory if s["action"] == "calculator"][0]))',
        '    return ("final", "I cannot solve this")',
        "",
        "def run_agent(goal, max_steps=6):",
        "    memory = []",
        "    for _ in range(max_steps):",
        "        action, arg = policy(goal, memory)",
        "        if action == 'final':",
        "            return str(arg)",
        {"s": '        if action not in ___:   # TODO: the allow-list guardrail (only permitted tools)',
         "a": '        if action not in ALLOWED:'},
        "            return 'blocked'",
        "        obs = TOOLS[action](arg)",
        "        memory.append({'action': action, 'observation': obs})",
        "    return 'max_steps'",
        "",
        "SUITE = [",
        '    {"goal": "twice the population of metropolis", "answer": "240000"},',
        '    {"goal": "what is the capital of france", "answer": "Paris"},',
        '    {"goal": "compute 15*3", "answer": "45"},',
        "]",
        "def evaluate():",
        {"s": '    solved = ___   # TODO: count suite tasks the agent answers correctly',
         "a": '    solved = sum(1 for t in SUITE if run_agent(t["goal"]) == t["answer"])'},
        "    return solved, len(SUITE)",
        "",
        "try:",
        "    for t in SUITE:",
        "        print(t['goal'], '->', run_agent(t['goal']))",
        "    print('solved:', evaluate())",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("solves the two-step population task", lambda: run_agent("twice the population of metropolis") == "240000")
expect_true("solves the capital lookup task", lambda: run_agent("what is the capital of france") == "Paris")
expect_true("solves the arithmetic task", lambda: run_agent("compute 15*3") == "45")
expect_true("solves the whole suite (3/3)", lambda: evaluate() == (3, 3))
expect_true("handles an unsolvable goal without crashing", lambda: run_agent("xyzzy nonsense") == "I cannot solve this")
expect_true("never exceeds the step cap", lambda: run_agent("twice the population of metropolis") != "max_steps")'''),
      *optional_llm(
        "Swap the rule-based policy for a REAL LangChain agent (Ollama llama3.2:1b, or Groq) -- the bridge to Module 6.",
        '''try:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.2:1b")
    print(llm.invoke("In one sentence, what is an AI agent?").content)
    print("That reply came from a REAL local LLM -- in Module 6 you bind it to tools with LangChain")
    print("and let IT drive the loop, instead of the rule-based policy above.")
except Exception as e:
    print("No local LLM available -- skipping (install langchain-ollama + `ollama run llama3.2:1b`,", type(e).__name__)
    print("or use Groq: `from langchain_groq import ChatGroq` with GROQ_API_KEY).")
    print("The rule-based mini-agent above already solved the whole suite offline.")
    print("Next: Module 6 (Agent Frameworks) and your Day-3 labs -- a simple LangChain agent, then")
    print("connecting agents to external APIs (Google Search / Wolfram Alpha).")'''),
      footer(12, "You built a guardrailed mini-agent that solves a suite of tasks with tools, memory and a loop. That IS agentic AI &mdash; next, Module 6 hands the loop to a real LLM with LangChain."),
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
