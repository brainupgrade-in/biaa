# -*- coding: utf-8 -*-
"""Generator for Day 3 Module 6 hands-on labs (12 notebooks).
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

Design: this is the "Frameworks for Building AI Agents" module, so the labs teach
the REAL LangChain workflow -- @tool, PromptTemplate, create_react_agent,
AgentExecutor (+ max_iterations), memory, a LangGraph-style state graph, guardrails
and observability. To keep the course's verify discipline (every GRADED cell runs
offline & deterministically -- no live LLM, no keys, no network), the graded cells
use a compact, stdlib-only shim whose NAMES AND SHAPES MIRROR real LangChain, driven
by a deterministic scripted "FakeChatModel". Each Advanced lab (10-12) adds ONE
optional, non-graded, guarded cell that runs the SAME shapes against the REAL
library (ChatOllama/Groq, Google Serper / Wolfram Alpha) and degrades gracefully.
The calculator/compute tools use a small AST-based safe evaluator -- never bare eval()."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day3-module6-frameworks-for-building-ai-agents.html"
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
WORK = "/tmp/biaa-lab-06-{nn:02d}"
os.makedirs(WORK, exist_ok=True)
print("Working dir:", WORK){extra}''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 6.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 3 &middot; Module 6 &mdash; Frameworks for Building AI Agents**

### What you'll do
{g}

> **How this lab works (experiential flow):** read the **Concept**, run the **Demo** to see it work, then complete **Your Turn** by replacing every `___` placeholder. Run the **grader** cell at the end &mdash; it prints `[PASS]` / `[FAIL]` / `[TODO]` and a final `Score`. Aim for a full score.

> **Framework note:** the graded steps use a tiny **LangChain-shaped shim** (same names &amp; shapes as real LangChain) so they run offline &amp; deterministically. Advanced labs end with an **optional** cell that runs the **real** library.

**Reference:** [Module 6 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 6 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 6 labs](./index.html) &nbsp;&middot;&nbsp; [Module 6 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def optional_real(intro, body):
    """An OPTIONAL, non-graded cell that runs the SAME shapes against the REAL LangChain."""
    return [md(f'''## Optional &mdash; run this against the REAL LangChain (not graded)
{intro} Safe to skip &mdash; it needs `pip install langchain langchain-ollama` (then
`ollama run llama3.2:1b`) or `langchain-groq` with a `GROQ_API_KEY`; external-API tools also need
their own keys. If a package, model or key is missing the cell prints a friendly note and moves on.
**The graded steps above use a deterministic LangChain-shaped shim, so the lab always verifies offline.**'''),
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

# A tiny LangChain-SHAPED shim. Names & shapes mirror real LangChain (Module 6 slides).
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
@lab(1, "lab-01-your-first-tool", "Beginner",
     "Your First Tool with @tool", 20,
     "Turn a plain function into a LangChain tool with @tool and read its name, description and args.",
     ["@tool", "Tool schema", "tool.invoke"])
def _l1(sol):
    return [
      header(1, "Your First Tool with @tool", "Beginner", 20,
        ["Wrap a function as a tool with the @tool decorator",
         "See the name, description (from the docstring) and args the model reads",
         "Call the tool with .invoke() and get a real result"],
        "Defining a tool"),
      setup(1),
      md('''## Concept
In Module 5 you built tools by hand as dicts. A framework does it for you: LangChain's **`@tool`**
decorator turns a plain function into a **Tool** with a **name**, a **description** (taken from the
**docstring** &mdash; the text the model reads to decide when to use it), an **args** schema, and an
**`.invoke()`** method. Same idea as before &mdash; one decorator instead of a dict.'''),
      shimcell([SAFE_CALC, LC_TOOL],
        '''@tool
def greet(name):
    """Say hello to someone by name."""
    return "Hello, " + name + "!"
print("name:", greet.name, "| description:", greet.description, "| args:", greet.args)
print("greet.invoke('Ada') ->", greet.invoke("Ada"))'''),
      md('''## Your Turn
Write two real tools &mdash; a **calculator** and a **lookup** &mdash; each with a clear docstring
(the description the model reads), then call them with `.invoke()`.'''),
      code(render([
        "@tool",
        "def calculator(expression):",
        {"s": '    ___    # TODO: a one-line docstring describing this tool (the model reads it)',
         "a": '    """Do exact arithmetic on an expression such as 2+2 or 120000/2."""'},
        {"s": '    return ___    # TODO: compute the expression with the safe calculator',
         "a": '    return safe_calc(expression)'},
        "",
        "@tool",
        "def lookup(key):",
        {"s": '    ___    # TODO: a one-line docstring: look up a known fact by its key',
         "a": '    """Look up a known fact by its key, for example capital of france."""'},
        '    facts = {"capital of france": "Paris", "population of metropolis": "120000"}',
        {"s": '    return ___    # TODO: return the fact for key (lowercased/stripped), else "unknown"',
         "a": '    return facts.get(key.lower().strip(), "unknown")'},
        "",
        "try:",
        "    print('calculator.name :', calculator.name)",
        "    print('calculator.args :', calculator.args)",
        "    print('calculator.invoke(\"120000/2\") =', calculator.invoke('120000/2'))",
        "    print('lookup.invoke(\"capital of france\") =', lookup.invoke('capital of france'))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("calculator is a Tool named 'calculator'", lambda: calculator.name == "calculator")
expect_true("its args schema is ['expression']", lambda: calculator.args == ["expression"])
expect_true("calculator.invoke computes 120000/2 == 60000.0", lambda: calculator.invoke("120000/2") == 60000.0)
expect_true("lookup finds a known fact", lambda: lookup.invoke("capital of france") == "Paris")
expect_true("lookup returns 'unknown' for a missing key", lambda: lookup.invoke("price of gold") == "unknown")'''),
      footer(1, "`@tool` turns a function into a Tool the agent can call. The docstring is the description the model reads -- next we see why that description is the tool's real API."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-tool-descriptions", "Beginner",
     "The Docstring Is the Tool's API", 20,
     "Give tools clear descriptions, render the catalog the model reads, and route a query to the right tool.",
     ["Descriptions", "Tool catalog", "Selection"])
def _l2(sol):
    return [
      header(2, "The Docstring Is the Tool's API", "Beginner", 20,
        ["Write descriptions that tell the model WHEN to use each tool",
         "Render the catalog (name + description) the model actually reads",
         "Route a request to the right tool from that catalog"],
        "Defining a tool"),
      setup(2),
      md('''## Concept
The model never sees your code &mdash; only each tool's **name**, **description** and **args**. So the
**docstring is the tool's real API**: a vague one makes the agent pick the wrong tool. Here you write
good descriptions, build the **catalog** the model is shown, and route a query to a tool from it.'''),
      shimcell([LC_TOOL],
        '''@tool
def clock(_):
    """Return the current time of day."""
    return "12:00"
print("the model is shown -> ", clock.name + ": " + clock.description)'''),
      md('''## Your Turn
Write three tools with clear descriptions, render the catalog, then complete `choose_tool`.'''),
      code(render([
        "@tool",
        "def weather(city):",
        {"s": '    ___   # TODO: description -- returns CURRENT weather for a city',
         "a": '    """Get the current weather for a city. Use for questions about current temperature or conditions."""'},
        '    return "sunny, 24C"',
        "",
        "@tool",
        "def calculator(expression):",
        {"s": '    ___   # TODO: description -- exact arithmetic / any calculation',
         "a": '    """Do exact arithmetic on a math expression. Use for any calculation with numbers."""'},
        '    return "(computed)"',
        "",
        "@tool",
        "def translate(text):",
        {"s": '    ___   # TODO: description -- translate text into French',
         "a": '    """Translate the given text into French."""'},
        '    return "(translated)"',
        "",
        "TOOLS = [weather, calculator, translate]",
        "",
        "def tool_catalog(tools):",
        "    # the text the MODEL is shown to choose a tool",
        {"s": '    return ___   # TODO: one "name: description" line per tool, newline-joined',
         "a": '    return "\\n".join(t.name + ": " + t.description for t in tools)'},
        "",
        "def choose_tool(query):",
        "    q = query.lower()",
        {"s": '    if ___:                          # TODO: a weather-ish query',
         "a": '    if "weather" in q or "temperature" in q:'},
        '        return "weather"',
        '    if "translate" in q:',
        '        return "translate"',
        {"s": '    if any(ch.isdigit() for ch in q):   # a query with numbers',
         "a": '    if any(ch.isdigit() for ch in q):'},
        {"s": '        return ___                   # TODO: the calculator tool name',
         "a": '        return "calculator"'},
        '    return "weather"',
        "",
        "try:",
        "    print(tool_catalog(TOOLS))",
        "    print('---')",
        "    for q in ['weather in tokyo', 'what is 12*8', 'translate hi to french']:",
        "        print(q, '->', choose_tool(q))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("catalog lists all three tool names", lambda: all(n in tool_catalog(TOOLS) for n in ("weather", "calculator", "translate")))
expect_true("catalog has one line per tool", lambda: tool_catalog(TOOLS).count(chr(10)) == 2)
expect_true("a weather query routes to weather", lambda: choose_tool("weather in paris") == "weather")
expect_true("a numeric query routes to calculator", lambda: choose_tool("what is 12*8") == "calculator")
expect_true("a translate query routes to translate", lambda: choose_tool("translate hello to french") == "translate")'''),
      footer(2, "The description is what the model reads to choose a tool -- write it for the model. Real LangChain selects from exactly this catalog; here you made it visible."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-model-and-prompt", "Beginner",
     "The Model Interface: Prompts & .invoke()", 20,
     "Build a PromptTemplate, format it, and call a model with .invoke() -- the one interface every provider shares.",
     ["ChatModel", "PromptTemplate", ".invoke"])
def _l3(sol):
    return [
      header(3, "The Model Interface: Prompts & .invoke()", "Beginner", 20,
        ["Build a PromptTemplate with an {input} slot and format it",
         "Call the model with .invoke() and read the reply from .content",
         "See that the SAME interface works for any model (model-agnostic)"],
        "LangChain's core building blocks"),
      setup(3),
      md('''## Concept
Every LangChain chat model shares **one interface**: `model.invoke(prompt)` returns a message whose
text is in **`.content`**. That is why swapping **`ChatOllama`** for **`ChatGroq`** is a one-line
change. A **`PromptTemplate`** fills slots like `{input}`. Here a deterministic `FakeChatModel`
stands in for a real model so the lab runs offline.'''),
      shimcell([LC_MODEL, LC_PROMPT],
        '''demo_model = FakeChatModel(["Hi! I am a stand-in model."])
demo_prompt = PromptTemplate.from_template("Say hi to {who}.")
print(demo_prompt.format(who="Ada"))
print("reply:", demo_model.invoke("anything").content)'''),
      md('''## Your Turn
Build a prompt with an `{input}` slot, then `ask` the model and return the reply text.'''),
      code(render([
        "def build_prompt(question):",
        {"s": '    template = PromptTemplate.from_template(___)   # TODO: a template with an {input} slot',
         "a": '    template = PromptTemplate.from_template("Answer concisely.\\nQuestion: {input}")'},
        {"s": '    return ___   # TODO: format the template with input=question',
         "a": '    return template.format(input=question)'},
        "",
        "def ask(model, question):",
        "    prompt = build_prompt(question)",
        {"s": '    message = ___   # TODO: call the model on the prompt',
         "a": '    message = model.invoke(prompt)'},
        {"s": '    return ___      # TODO: the reply text (a message has .content)',
         "a": '    return message.content'},
        "",
        "try:",
        "    print(build_prompt('what is an agent?'))",
        "    print('---')",
        '    print("reply:", ask(FakeChatModel(["An agent uses tools in a loop."]), "what is an agent?"))',
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the prompt fills in the question", lambda: "capital of france" in build_prompt("capital of france"))
expect_true("the prompt has a Question: slot", lambda: "Question:" in build_prompt("x"))
expect_true("ask reads the reply from .content", lambda: ask(FakeChatModel(["hi"]), "q") == "hi")
expect_true("the model returns a message with .content", lambda: hasattr(FakeChatModel(["x"]).invoke("p"), "content"))
expect_true("same interface, swappable model", lambda: ask(FakeChatModel(["A"]), "q") == "A" and ask(FakeChatModel(["B"]), "q") == "B")'''),
      footer(3, "One interface -- .invoke(prompt).content -- over every provider. That uniformity is what makes the Ollama<->Groq swap a single line."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-assemble-agent", "Beginner",
     "Assemble a ReAct Agent (the four pieces)", 20,
     "Bind model + tools + prompt with create_react_agent -- the four moves from the deck.",
     ["create_react_agent", "Binding tools", "Agent"])
def _l4(sol):
    return [
      header(4, "Assemble a ReAct Agent (the four pieces)", "Beginner", 20,
        ["Complete create_react_agent so it registers tools by name",
         "Assemble a model + a tools list + a prompt into one agent",
         "Inspect the bound agent: which tools and model it holds"],
        "Assemble a ReAct agent"),
      setup(4),
      md('''## Concept
A LangChain agent is four pieces bound together (deck slide 9): a **model**, a **tools** list, a
**prompt**, and **`create_react_agent(model, tools, prompt)`** that ties them into a reasoning core.
`create_react_agent` registers the tools **by name** so the loop can look each one up.'''),
      shimcell([LC_TOOL, LC_MODEL, LC_PROMPT],
        '''@tool
def calculator(expression):
    """Do exact arithmetic."""
    return "(computed)"
@tool
def lookup(key):
    """Look up a known fact by key."""
    return "(fact)"
print("two tools ready:", calculator.name, "&", lookup.name)'''),
      md('''## Your Turn
Finish `create_react_agent` (register tools by name), then assemble the agent in `build_agent`.'''),
      code(render([
        "def create_react_agent(model, tools, prompt):",
        '    """Bind model + tools + prompt into an agent (mirrors langchain.agents.create_react_agent)."""',
        {"s": '    return {"model": model, "tools": ___, "prompt": prompt}   # TODO: a name->tool dict',
         "a": '    return {"model": model, "tools": {t.name: t for t in tools}, "prompt": prompt}'},
        "",
        "def build_agent():",
        '    model  = FakeChatModel(["Final Answer: ok"])',
        '    prompt = PromptTemplate.from_template("{scratchpad}\\nQuestion: {input}")',
        {"s": '    tools  = ___   # TODO: a list of the two tools (calculator, lookup)',
         "a": '    tools  = [calculator, lookup]'},
        {"s": '    return create_react_agent(model, tools, ___)   # TODO: pass the prompt',
         "a": '    return create_react_agent(model, tools, prompt)'},
        "",
        "try:",
        "    agent = build_agent()",
        "    print('registered tools:', list(agent['tools']))",
        "    print('model bound      :', type(agent['model']).__name__)",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the agent binds model, tools and prompt", lambda: {"model", "tools", "prompt"} <= set(build_agent()))
expect_true("both tools are registered by name", lambda: set(build_agent()["tools"]) == {"calculator", "lookup"})
expect_true("a registered entry is a Tool", lambda: build_agent()["tools"]["calculator"].name == "calculator")
expect_true("the model is bound", lambda: build_agent()["model"] is not None)
expect_true("create_react_agent maps a single tool too", lambda: list(create_react_agent(FakeChatModel(["x"]), [calculator], None)["tools"]) == ["calculator"])'''),
      footer(4, "model + tools + prompt -> create_react_agent = a bound agent. It knows its tools by name; next, the executor runs the loop over them."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-agent-executor", "Beginner",
     "The AgentExecutor Loop & the Verbose Trace", 25,
     "Wrap an agent in AgentExecutor, invoke a goal, read the ReAct trace, and cap it with max_iterations.",
     ["AgentExecutor", "verbose trace", "max_iterations"])
def _l5(sol):
    return [
      header(5, "The AgentExecutor Loop & the Verbose Trace", "Beginner", 25,
        ["Wrap a bound agent in an AgentExecutor and invoke a goal",
         "Read the output and the intermediate_steps (the ReAct trace)",
         "Cap the loop with max_iterations so it can never run forever"],
        "The AgentExecutor loop, made visible"),
      setup(5),
      md('''## Concept
The **`AgentExecutor`** runs the loop for you: ask the model, parse its **Action**, run the tool,
feed back the **Observation**, repeat &mdash; until a **Final Answer**, or until **`max_iterations`**
stops it. `verbose=True` prints the ReAct trace (deck slide 10). Here a scripted `FakeChatModel`
plays the model so the trace is deterministic.'''),
      shimcell([SAFE_CALC, LC_TOOL, LC_MODEL, LC_PROMPT, LC_EXEC],
        '''@tool
def calculator(expression):
    """Do exact arithmetic on an expression."""
    return safe_calc(expression)
print("executor + a calculator tool are ready")'''),
      md('''## Your Turn
Complete `make_executor`: give the agent its tools and set the `max_iterations` guardrail. It builds
a fresh, scripted agent each call so the grader can re-run it cleanly.'''),
      code(render([
        "SCRIPT = [",
        '    "Thought: I should compute this.\\nAction: calculator\\nAction Input: 120000/2",',
        '    "Thought: I have the result.\\nFinal Answer: 60000.0",',
        "]",
        "",
        "def make_executor(max_iterations=6):",
        "    model  = FakeChatModel(SCRIPT)",
        '    prompt = PromptTemplate.from_template("Question: {input}\\n{scratchpad}")',
        {"s": '    agent  = create_react_agent(model, ___, prompt)   # TODO: the tools list (just calculator)',
         "a": '    agent  = create_react_agent(model, [calculator], prompt)'},
        {"s": '    return AgentExecutor(agent, verbose=False, max_iterations=___)   # TODO: the step cap',
         "a": '    return AgentExecutor(agent, verbose=False, max_iterations=max_iterations)'},
        "",
        "try:",
        "    ex = make_executor()",
        "    ex.verbose = True",
        '    result = ex.invoke({"input": "What is half of 120000?"})',
        "    print('---')",
        "    print('output:', result['output'])",
        "    print('steps :', result['intermediate_steps'])",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the executor returns the final answer", lambda: make_executor().invoke({"input": "x"})["output"] == "60000.0")
expect_true("the trace records the calculator call", lambda: make_executor().invoke({"input": "x"})["intermediate_steps"][0][0] == "calculator")
expect_true("the tool actually computed 60000.0", lambda: make_executor().invoke({"input": "x"})["intermediate_steps"][0][2] == 60000.0)
expect_true("a 1-step cap stops before the final answer", lambda: make_executor(max_iterations=1).invoke({"input": "x"})["output"] is None)
expect_true("with enough steps it reaches the answer", lambda: make_executor(max_iterations=6).invoke({"input": "x"})["output"] == "60000.0")'''),
      footer(5, "AgentExecutor absorbs the parse/route/observe/loop you hand-built in Module 5 -- and max_iterations is your guardrail in one line. verbose=True is your #1 debugging surface."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-tool-routing", "Beginner",
     "Routing an Action to a Tool (safely)", 20,
     "Dispatch a chosen action to the right tool with .invoke(), and handle unknown tools & errors without crashing.",
     ["Routing", "Observation", "Safe dispatch"])
def _l6(sol):
    return [
      header(6, "Routing an Action to a Tool (safely)", "Beginner", 20,
        ["Look a tool up by name in a registry and run it with .invoke()",
         "Wrap the result as the observation the agent reads next",
         "Handle an unknown tool and a failing tool without crashing"],
        "LangChain's core building blocks"),
      setup(6),
      md('''## Concept
Once the model picks an **action name**, the framework must **route** it to the matching tool, run it
via `.invoke()`, and wrap the result as an **observation**. Models hallucinate tool names, so routing
must fail **safely**: an unknown or failing tool returns a message, not a crash.'''),
      shimcell([SAFE_CALC, LC_TOOL],
        '''@tool
def calculator(expression):
    """Do exact arithmetic on an expression."""
    return safe_calc(expression)
@tool
def lookup(key):
    """Look up a known fact by key."""
    facts = {"capital of france": "Paris", "population of metropolis": "120000"}
    return facts.get(key.lower().strip(), "unknown")
@tool
def weather(city):
    """Get the current weather for a city."""
    return "sunny, 24C"
REGISTRY = {t.name: t for t in [calculator, lookup, weather]}
print("registry:", list(REGISTRY))'''),
      md('''## Your Turn
Implement `dispatch`: find the tool, run it via `.invoke()`, and handle the unknown/failing cases.'''),
      code(render([
        "def dispatch(registry, name, arg):",
        {"s": '    tool = ___   # TODO: get the tool by name (None if not registered)',
         "a": '    tool = registry.get(name)'},
        "    if tool is None:",
        {"s": '        return {"ok": False, "observation": ___}   # TODO: a message naming the unknown tool',
         "a": '        return {"ok": False, "observation": "unknown tool: " + name}'},
        "    try:",
        {"s": '        return {"ok": True, "observation": ___}   # TODO: run the tool on arg via .invoke',
         "a": '        return {"ok": True, "observation": tool.invoke(arg)}'},
        "    except Exception as e:",
        '        return {"ok": False, "observation": "tool error: " + type(e).__name__}',
        "",
        "try:",
        "    print(dispatch(REGISTRY, 'calculator', '10/2'))",
        "    print(dispatch(REGISTRY, 'lookup', 'capital of france'))",
        "    print(dispatch(REGISTRY, 'no_such_tool', 'x'))",
        "    print(dispatch(REGISTRY, 'calculator', 'not-math'))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("routes the calculator correctly", lambda: dispatch(REGISTRY, "calculator", "10/2")["observation"] == 5.0)
expect_true("routes the lookup correctly", lambda: dispatch(REGISTRY, "lookup", "capital of france")["observation"] == "Paris")
expect_true("ok is True on success", lambda: dispatch(REGISTRY, "weather", "tokyo")["ok"] is True)
expect_true("an unknown tool is handled, naming it", lambda: dispatch(REGISTRY, "no_such_tool", "x")["ok"] is False and "no_such_tool" in dispatch(REGISTRY, "no_such_tool", "x")["observation"])
expect_true("a failing tool does not crash", lambda: dispatch(REGISTRY, "calculator", "not-math")["ok"] is False)'''),
      footer(6, "Routing turns a chosen action into a real observation -- safely. The split between the model deciding and the executor running is what makes agents debuggable."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-conversation-memory", "Intermediate",
     "Memory: Conversation History", 30,
     "Give the agent conversation memory so a follow-up like 'and Osaka?' resolves against earlier turns.",
     ["Memory", "Chat history", "Follow-ups"])
def _l7(sol):
    return [
      header(7, "Memory: Conversation History", "Intermediate", 30,
        ["Store each turn (role, text) in a memory object",
         "Format the running history the model re-reads each turn",
         "Build a prompt that carries context so a follow-up resolves"],
        "Memory -- plugged in, not hand-built"),
      setup(7),
      md('''## Concept
A framework keeps **conversation memory** so follow-ups work: ask *"capital of France?"*, then
*"and Osaka?"* &mdash; the agent needs the earlier turns to resolve *"and"*. Memory is a component you
**attach**: it stores turns and re-injects the **history** into each prompt. (Long-term memory is a
vector store &mdash; the bridge to RAG.)'''),
      shimcell([LC_MODEL, LC_PROMPT],
        '''# one turn is just (role, text)
print("a turn:", ("user", "What is the capital of France?"))'''),
      md('''## Your Turn
Implement `ConversationMemory` (store + format the history) and a prompt that injects it.'''),
      code(render([
        "class ConversationMemory:",
        "    def __init__(self):",
        "        self.turns = []",
        "    def add(self, role, text):",
        {"s": '        self.turns.append(___)   # TODO: store the turn as (role, text)',
         "a": '        self.turns.append((role, text))'},
        "    def history(self):",
        {"s": '        return ___   # TODO: one "role: text" line per turn, newline-joined',
         "a": '        return "\\n".join(r + ": " + t for r, t in self.turns)'},
        "",
        "def build_prompt(memory, question):",
        '    template = PromptTemplate.from_template("Conversation so far:\\n{history}\\nUser: {input}")',
        {"s": '    return template.format(history=___, input=question)   # TODO: the running history',
         "a": '    return template.format(history=memory.history(), input=question)'},
        "",
        "try:",
        "    mem = ConversationMemory()",
        "    mem.add('user', 'What is the capital of France?')",
        "    mem.add('ai', 'Paris.')",
        "    followup = build_prompt(mem, 'And Osaka is in which country?')",
        "    print(followup)",
        "    print('carries prior context?', 'Paris' in followup)",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("memory stores each turn", lambda: (lambda m: (m.add("user", "hi"), len(m.turns))[1])(ConversationMemory()) == 1)
expect_true("history has one line per turn", lambda: (lambda m: (m.add("user", "a"), m.add("ai", "b"), m.history().count(chr(10)))[2])(ConversationMemory()) == 1)
expect_true("history formats role: text", lambda: (lambda m: (m.add("user", "hi"), m.history())[1])(ConversationMemory()) == "user: hi")
expect_true("the follow-up prompt carries prior context", lambda: "Paris" in (lambda m: (m.add("ai", "Paris."), build_prompt(m, "and Osaka?"))[1])(ConversationMemory()))
expect_true("the prompt includes the new question", lambda: "Osaka" in build_prompt(ConversationMemory(), "where is Osaka?"))'''),
      footer(7, "Memory carries context across turns so 'and Osaka?' just works. In a framework it's a component you attach -- not a scratchpad you hand-build."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-langgraph-state-machine", "Intermediate",
     "LangChain vs LangGraph: a State Graph", 30,
     "Model a branching agent as a small state graph with a human-approval node for risky actions.",
     ["State graph", "Routing", "Human-in-the-loop"])
def _l8(sol):
    return [
      header(8, "LangChain vs LangGraph: a State Graph", "Intermediate", 30,
        ["Route each step to a node: tool, human-approval, or end",
         "Send risky actions through a human-approval node",
         "Run a sequence through the graph and read the node path"],
        "LangGraph -- agents as state graphs"),
      setup(8),
      md('''## Concept
When one implicit loop isn't enough, **LangGraph** models the agent as a **state graph**: **nodes**
are steps, **edges** are transitions you control (deck slides 12&ndash;13). A key win is a **human
approval** node: a **risky** action (send email, delete, pay) is routed to a human before it runs,
while safe actions go straight to the tool node.'''),
      shimcell([],
        '''RISKY = {"send_email", "delete", "pay"}
print("actions that need human approval:", RISKY)'''),
      md('''## Your Turn
Implement `route` (which node an action goes to) and `run_graph` (walk a sequence through it).'''),
      code(render([
        'RISKY = {"send_email", "delete", "pay"}',
        "",
        "def route(action):",
        {"s": '    if action == ___:      # TODO: nothing left to do -> the end node',
         "a": '    if action == "done":'},
        '        return "end"',
        {"s": '    if action in ___:      # TODO: a risky action -> the human-approval node',
         "a": '    if action in RISKY:'},
        '        return "human"',
        '    return "tool"          # any safe tool call',
        "",
        "def run_graph(actions, max_steps=10):",
        "    path = []",
        "    for action in actions[:max_steps]:",
        {"s": '        node = ___   # TODO: decide the node for this action',
         "a": '        node = route(action)'},
        "        path.append(node)",
        '        if node == "end":',
        "            break",
        "    return path",
        "",
        "try:",
        "    print('search      ->', route('search'))",
        "    print('send_email  ->', route('send_email'))",
        "    print('done        ->', route('done'))",
        "    print('path:', run_graph(['search', 'send_email', 'done']))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("a safe action routes to the tool node", lambda: route("search") == "tool")
expect_true("a risky action routes to human approval", lambda: route("send_email") == "human")
expect_true("'done' routes to the end node", lambda: route("done") == "end")
expect_true("the graph walks the expected node path", lambda: run_graph(["search", "pay", "done"]) == ["tool", "human", "end"])
expect_true("the graph stops at the end node", lambda: run_graph(["search", "done", "search"]) == ["tool", "end"])'''),
      footer(8, "LangChain gets an agent running; LangGraph puts its flow under control -- explicit nodes, branching, and a first-class human-approval pause. Start simple; graduate when you need it."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-multi-tool", "Intermediate",
     "Multi-Tool Orchestration (day in the life)", 30,
     "Chain a search tool and a calculator through the AgentExecutor to answer a compound question.",
     ["Tool chaining", "Orchestration", "AgentExecutor"])
def _l9(sol):
    return [
      header(9, "Multi-Tool Orchestration (day in the life)", "Intermediate", 30,
        ["Give the agent TWO tools: a search and a calculator",
         "Let the executor chain them: search a fact, then compute on it",
         "Confirm both tools ran, in order, to the right answer"],
        "Connecting to real tools & APIs"),
      setup(9),
      md('''## Concept
Agents earn their keep on **multi-step** tasks that **orchestrate several tools** (deck slide 16):
*"population of France, divided by 2?"* needs a **search** (a live fact) **then** a **calculator**.
The executor chains them &mdash; each observation feeds the next step &mdash; and returns one answer.'''),
      shimcell([SAFE_CALC, LC_TOOL, LC_MODEL, LC_PROMPT, LC_EXEC],
        '''@tool
def web_search(query):
    """Search the web for a current fact."""
    facts = {"population of france": "68000000", "june average tokyo": "22"}
    return facts.get(query.lower().strip(), "no result")
@tool
def calculator(expression):
    """Do exact arithmetic on an expression."""
    return safe_calc(expression)
print("two tools ready:", web_search.name, "&", calculator.name)'''),
      md('''## Your Turn
Complete `make_executor` so the agent has **both** tools; the scripted model searches then computes.'''),
      code(render([
        "SCRIPT = [",
        '    "Thought: find the population.\\nAction: web_search\\nAction Input: population of france",',
        '    "Thought: divide it by 2.\\nAction: calculator\\nAction Input: 68000000/2",',
        '    "Thought: done.\\nFinal Answer: 34000000",',
        "]",
        "",
        "def make_executor(max_iterations=6):",
        "    model  = FakeChatModel(SCRIPT)",
        '    prompt = PromptTemplate.from_template("Q: {input}\\n{scratchpad}")',
        {"s": '    tools  = ___   # TODO: both tools, so the agent can search AND compute',
         "a": '    tools  = [web_search, calculator]'},
        "    agent  = create_react_agent(model, tools, prompt)",
        "    return AgentExecutor(agent, max_iterations=max_iterations)",
        "",
        "try:",
        '    result = make_executor().invoke({"input": "population of France divided by 2?"})',
        "    print('output:', result['output'])",
        "    print('tools used:', [s[0] for s in result['intermediate_steps']])",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the agent reaches the right final answer", lambda: make_executor().invoke({"input": "x"})["output"] == "34000000")
expect_true("it took two tool steps", lambda: len(make_executor().invoke({"input": "x"})["intermediate_steps"]) == 2)
expect_true("tools ran in order: search then calculator", lambda: [s[0] for s in make_executor().invoke({"input": "x"})["intermediate_steps"]] == ["web_search", "calculator"])
expect_true("the search returned the population", lambda: make_executor().invoke({"input": "x"})["intermediate_steps"][0][2] == "68000000")
expect_true("the calculator halved it", lambda: make_executor().invoke({"input": "x"})["intermediate_steps"][1][2] == 34000000.0)'''),
      footer(9, "Chaining search + compute in one run is exactly where agents beat a single call. Same executor, two tools -- the 'day in the life' trace, for real."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-external-apis", "Advanced",
     "Connect to External APIs (Search + Wolfram)", 40,
     "Wrap a web-search tool and a Wolfram-style compute tool, chain them, and (optionally) call the REAL APIs.",
     ["External APIs", "Search tool", "Compute tool"])
def _l10(sol):
    return [
      header(10, "Connect to External APIs (Search + Wolfram)", "Advanced", 40,
        ["Wrap a Google-Search-style tool over a live fact source",
         "Wrap a Wolfram-Alpha-style exact-compute tool",
         "Chain them in the executor; optionally call the REAL APIs"],
        "Connecting to real tools & APIs"),
      setup(10),
      md('''## Concept
Real agents reach the world through **tool integrations** (deck slide 16): **Google Search** for live
facts beyond the training cutoff, **Wolfram Alpha** for exact computation. The pattern is always: get
a key &rarr; wrap the service as a `@tool` &rarr; add it to the tools list. The **graded** cells use a
deterministic local stand-in; the **optional** cell calls the real APIs if you have keys.'''),
      shimcell([SAFE_CALC, LC_TOOL, LC_MODEL, LC_PROMPT, LC_EXEC],
        '''print("shim ready -- now wrap two external-service tools below")'''),
      md('''## Your Turn
Wrap a **google_search** tool (over a small live-fact index) and a **wolfram** compute tool, then let
the executor chain them.'''),
      code(render([
        "@tool",
        "def google_search(query):",
        {"s": '    ___   # TODO: docstring -- search the web for a live fact (the model reads this)',
         "a": '    """Search the web for a current fact or figure. Use for anything not in the model own memory."""'},
        '    index = {"gold price today usd per oz": "2400", "eiffel tower height m": "330"}',
        {"s": '    return ___   # TODO: look query up in index (lowercased/stripped), else "no result"',
         "a": '    return index.get(query.lower().strip(), "no result")'},
        "",
        "@tool",
        "def wolfram(expression):",
        '    """Compute an exact math expression (a Wolfram-Alpha-style compute tool)."""',
        '    return safe_calc(expression)',
        "",
        "SCRIPT = [",
        '    "Thought: I need the live price.\\nAction: google_search\\nAction Input: gold price today usd per oz",',
        '    "Thought: double it.\\nAction: wolfram\\nAction Input: 2400*2",',
        '    "Thought: done.\\nFinal Answer: 4800",',
        "]",
        "",
        "def make_executor(max_iterations=6):",
        "    model = FakeChatModel(SCRIPT)",
        '    prompt = PromptTemplate.from_template("Q: {input}\\n{scratchpad}")',
        {"s": '    agent = create_react_agent(model, ___, prompt)   # TODO: both external tools',
         "a": '    agent = create_react_agent(model, [google_search, wolfram], prompt)'},
        "    return AgentExecutor(agent, max_iterations=max_iterations)",
        "",
        "try:",
        "    print('search known  :', google_search.invoke('gold price today usd per oz'))",
        "    print('search unknown:', google_search.invoke('who won the 3pm race'))",
        '    result = make_executor().invoke({"input": "double the current gold price"})',
        "    print('output:', result['output'], '| tools:', [s[0] for s in result['intermediate_steps']])",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("search returns a known live fact", lambda: google_search.invoke("gold price today usd per oz") == "2400")
expect_true("search returns 'no result' for the unknown", lambda: google_search.invoke("who won the 3pm race") == "no result")
expect_true("the compute tool does exact math", lambda: wolfram.invoke("2400*2") == 4800)
expect_true("the executor chains search then compute", lambda: [s[0] for s in make_executor().invoke({"input": "x"})["intermediate_steps"]] == ["google_search", "wolfram"])
expect_true("it reaches the right final answer", lambda: make_executor().invoke({"input": "x"})["output"] == "4800")'''),
      *optional_real(
        "Swap the two stand-in tools for the REAL Google Serper and Wolfram Alpha wrappers.",
        '''import os
try:
    from langchain_community.utilities import GoogleSerperAPIWrapper
    if os.getenv("SERPER_API_KEY"):
        print("Google (Serper):", GoogleSerperAPIWrapper().run("current gold price per ounce"))
    else:
        print("Set SERPER_API_KEY (serper.dev) to run a REAL Google search here -- skipping.")
except Exception as e:
    print("Install langchain-community for the real search wrapper -- skipping:", type(e).__name__)
try:
    from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper
    if os.getenv("WOLFRAM_ALPHA_APPID"):
        print("Wolfram Alpha:", WolframAlphaAPIWrapper().run("2400 * 2"))
    else:
        print("Set WOLFRAM_ALPHA_APPID (developer.wolframalpha.com) for real compute -- skipping.")
except Exception as e:
    print("Install langchain-community + wolframalpha for the real wrapper -- skipping:", type(e).__name__)
print("The graded tools above already ran offline against a local stand-in.")'''),
      footer(10, "Get a key -> wrap the service as a @tool -> add it to the list. That is how an agent reaches live facts and real computation -- the client's Day-3 external-API lab, for real."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-guardrails-observability", "Advanced",
     "Guardrails & Observability", 35,
     "Add a tool allow-list, input validation, and a tracing callback that records every step.",
     ["Allow-list", "Validation", "Tracing"])
def _l11(sol):
    return [
      header(11, "Guardrails & Observability", "Advanced", 35,
        ["Allow-list the tools the agent may call",
         "Validate tool input before it runs",
         "Record every step with a tracing callback (LangSmith/Langfuse-style)"],
        "Observability & debugging"),
      setup(11),
      md('''## Concept
Autonomy needs **guardrails** and **observability** (deck slides 15, 17): a **tool allow-list**,
**input validation**, a **max_iterations** cap, and a **tracing callback** that logs every
(action, input, observation) so you can debug and audit. Real LangChain exposes callbacks;
**LangSmith / Langfuse** capture full traces. Here you build the offline versions.'''),
      shimcell([SAFE_CALC, LC_TOOL],
        '''@tool
def calculator(expression):
    """Do exact arithmetic on an expression."""
    return safe_calc(expression)
@tool
def lookup(key):
    """Look up a known fact by key."""
    return {"capital of france": "Paris"}.get(key.lower().strip(), "unknown")
REGISTRY = {t.name: t for t in [calculator, lookup]}
ALLOWED = {"calculator", "lookup"}
print("registry:", list(REGISTRY), "| allow-list:", ALLOWED)'''),
      md('''## Your Turn
Complete the allow-list, the input validator, and the tracing callback, then run a guarded loop.'''),
      code(render([
        "class TracingCallback:",
        "    def __init__(self):",
        "        self.events = []",
        "    def on_step(self, action, arg, observation):",
        {"s": '        self.events.append(___)   # TODO: record (action, arg, observation)',
         "a": '        self.events.append((action, arg, observation))'},
        "",
        "def is_allowed(action):",
        {"s": '    return ___   # TODO: True only if action is in the allow-list',
         "a": '    return action in ALLOWED'},
        "",
        "def validate(expr):",
        '    ok_chars = set("0123456789+-*/(). ")',
        {"s": '    return all(c in ok_chars for c in expr) and ___   # TODO: require at least one digit',
         "a": '    return all(c in ok_chars for c in expr) and any(c.isdigit() for c in expr)'},
        "",
        "def guarded_run(steps, cb, max_iterations=5):",
        "    # steps: list of (action, arg). Enforce the allow-list + step cap; trace each executed step.",
        "    for i, (action, arg) in enumerate(steps):",
        "        if i >= max_iterations:",
        "            return {'stopped': 'max_iterations', 'trace': cb.events}",
        "        if not is_allowed(action):",
        "            return {'stopped': 'blocked_tool', 'trace': cb.events}",
        "        obs = REGISTRY[action].invoke(arg)",
        "        cb.on_step(action, arg, obs)",
        "    return {'stopped': 'done', 'trace': cb.events}",
        "",
        "try:",
        "    cb = TracingCallback()",
        "    good = guarded_run([('calculator', '2+2'), ('lookup', 'capital of france')], cb)",
        "    print('good run:', good['stopped'], '| trace:', good['trace'])",
        "    blocked = guarded_run([('delete_database', 'all')], TracingCallback())",
        "    print('blocked :', blocked['stopped'])",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("allow-list permits a known tool", lambda: is_allowed("calculator") is True)
expect_true("allow-list blocks an unknown tool", lambda: is_allowed("delete_database") is False)
expect_true("validation accepts a real expression", lambda: validate("2 + 2*3") is True)
expect_true("validation rejects a dangerous input", lambda: validate("__import__('os')") is False)
expect_true("the callback records every executed step", lambda: len(guarded_run([("calculator", "2+2"), ("lookup", "capital of france")], TracingCallback())["trace"]) == 2)
expect_true("a disallowed tool is blocked, not run", lambda: guarded_run([("delete_database", "all")], TracingCallback())["stopped"] == "blocked_tool")'''),
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
print("The guarded run above already traced every step offline.")'''),
      footer(11, "Allow-list + validation + max_iterations + tracing turn an autonomous agent from a liability into something you can trust and debug. Day 5 goes deeper on responsible agents."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-langchain-agent", "Advanced",
     "Capstone: A Guardrailed LangChain Agent", 45,
     "Assemble tools + a scripted model + guardrails into an executor and run it over a suite of tasks.",
     ["End-to-end agent", "Task suite", "Guardrails"])
def _l12(sol):
    return [
      header(12, "Capstone: A Guardrailed LangChain Agent", "Advanced", 45,
        ["Assemble the module: tools + agent + executor + a max_iterations guardrail",
         "Run the agent over a SUITE of different tasks",
         "Score tasks solved / total; optionally run a REAL LangChain agent"],
        "Choosing a framework"),
      setup(12),
      md('''## Concept
Capstone: a **guardrailed LangChain-shaped agent** that ties the module together &mdash; `@tool`
tools, `create_react_agent`, an `AgentExecutor` with a **`max_iterations`** guardrail, and only
**allow-listed** tools registered &mdash; run over a **suite** (a compound task, a lookup, an
arithmetic task). The score is **solved / total**. The optional cell swaps in a **real** LangChain
agent (Ollama/Groq) &mdash; the bridge to Day 4.'''),
      shimcell([SAFE_CALC, LC_TOOL, LC_MODEL, LC_PROMPT, LC_EXEC],
        '''@tool
def lookup(key):
    """Look up a known fact by key."""
    facts = {"population of metropolis": "120000", "capital of france": "Paris"}
    return facts.get(key.lower().strip(), "unknown")
@tool
def calculator(expression):
    """Do exact arithmetic on an expression."""
    return safe_calc(expression)
print("allow-listed tools:", lookup.name, "&", calculator.name)'''),
      md('''## Your Turn
Complete `make_executor` (register only the allowed tools; set the guardrail) and `evaluate` (score
the suite). Each task has a scripted plan so the run is deterministic.'''),
      code(render([
        "SCRIPTS = {",
        '    "twice the population of metropolis": [',
        '        "Thought: look it up.\\nAction: lookup\\nAction Input: population of metropolis",',
        '        "Thought: double it.\\nAction: calculator\\nAction Input: 120000*2",',
        '        "Thought: done.\\nFinal Answer: 240000"],',
        '    "capital of france": [',
        '        "Thought: look it up.\\nAction: lookup\\nAction Input: capital of france",',
        '        "Thought: done.\\nFinal Answer: Paris"],',
        '    "compute 15*3": [',
        '        "Thought: compute.\\nAction: calculator\\nAction Input: 15*3",',
        '        "Thought: done.\\nFinal Answer: 45"],',
        "}",
        "",
        "def make_executor(goal, max_iterations=6):",
        "    model  = FakeChatModel(SCRIPTS[goal])",
        '    prompt = PromptTemplate.from_template("Q: {input}\\n{scratchpad}")',
        {"s": '    tools  = ___   # TODO: only the ALLOWED tools (lookup, calculator)',
         "a": '    tools  = [lookup, calculator]'},
        "    agent  = create_react_agent(model, tools, prompt)",
        {"s": '    return AgentExecutor(agent, max_iterations=___)   # TODO: the guardrail (cap the steps)',
         "a": '    return AgentExecutor(agent, max_iterations=max_iterations)'},
        "",
        "def solve(goal):",
        '    return make_executor(goal).invoke({"input": goal})["output"]',
        "",
        "SUITE = [",
        '    {"goal": "twice the population of metropolis", "answer": "240000"},',
        '    {"goal": "capital of france", "answer": "Paris"},',
        '    {"goal": "compute 15*3", "answer": "45"},',
        "]",
        "",
        "def evaluate():",
        {"s": '    solved = ___   # TODO: count suite tasks the agent solves correctly',
         "a": '    solved = sum(1 for t in SUITE if solve(t["goal"]) == t["answer"])'},
        "    return solved, len(SUITE)",
        "",
        "try:",
        "    for t in SUITE:",
        "        print(t['goal'], '->', solve(t['goal']))",
        "    print('solved:', evaluate())",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("solves the two-step population task", lambda: solve("twice the population of metropolis") == "240000")
expect_true("solves the capital lookup task", lambda: solve("capital of france") == "Paris")
expect_true("solves the arithmetic task", lambda: solve("compute 15*3") == "45")
expect_true("solves the whole suite (3/3)", lambda: evaluate() == (3, 3))
expect_true("only allow-listed tools are registered", lambda: set(make_executor("capital of france").tools) == {"lookup", "calculator"})
expect_true("the max_iterations guardrail is honored", lambda: make_executor("capital of france", max_iterations=1).invoke({"input": "capital of france"})["output"] is None)'''),
      *optional_real(
        "Swap the scripted model for a REAL LangChain agent (Ollama llama3.2:1b, or Groq) -- the bridge to Day 4.",
        '''try:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.2:1b")
    print(llm.invoke("In one sentence, what can an AI agent do that a plain chatbot cannot?").content)
    print("That was a REAL local LLM. Bind it to @tool functions with create_react_agent + AgentExecutor")
    print("(exactly the shapes above) for a production agent.")
except Exception as e:
    print("No local LLM available -- skipping (pip install langchain langchain-ollama + `ollama run llama3.2:1b`,")
    print("or langchain-groq with GROQ_API_KEY):", type(e).__name__)
    print("The guardrailed, offline agent above already solved the whole suite.")
    print("Next: Day 4 -- task automation & multi-agent collaboration.")'''),
      footer(12, "You assembled a guardrailed LangChain-shaped agent that solves a suite with tools, an executor and a step cap. Swap the scripted model for a real LLM and it ships -- next, Day 4 puts agents to work."),
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
        banner = md(f'''> ## SOLUTION / ANSWER KEY &mdash; Lab 6.{nn}
> This is the **completed** notebook (all `___` blanks filled). For the student version, open
> [`../{info['slug']}.ipynb`](../{info['slug']}.ipynb). Trainer use &mdash; or self-check after you've tried it yourself.''')
        with open(os.path.join(SOL_DIR, fname), "w") as f:
            json.dump(notebook([banner] + info["build"](True)), f, indent=1, ensure_ascii=False)

print(f"Wrote {len(NB)} notebooks to {OUT_DIR}" + (f" and solutions to {SOL_DIR}" if SOL_DIR else ""))

with open(os.path.join(_HERE, "_meta.json"), "w") as f:
    json.dump({str(nn): {k: NB[nn][k] for k in ("slug","level","title","mins","summary","concepts")}
               for nn in NB}, f, indent=1)
