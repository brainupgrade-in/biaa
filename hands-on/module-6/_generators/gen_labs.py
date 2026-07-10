# -*- coding: utf-8 -*-
"""Generator for Day 3 Module 6 hands-on labs (12 notebooks).
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

Design: this is the "Frameworks for Building AI Agents" module, so the labs teach
the REAL LangChain (v1) workflow directly -- langchain_core.tools.@tool, PromptTemplate,
langchain_ollama.ChatOllama, langchain.agents.create_agent (a compiled LangGraph
agent), langgraph.StateGraph, memory, guardrails and trace-reading. There is NO shim.

Verify discipline is preserved WITHOUT faking the library: every GRADED cell asserts
only on the DETERMINISTIC scaffolding you build -- tool name/description/args, prompt
formatting, the agent's structure (a CompiledStateGraph with model+tools nodes), pure
routing/guardrail logic, and reading a fixed real message trace -- and NEVER calls an
LLM. Cells marked "Optional -- run it for real" invoke a live local model
(ChatOllama llama3.2:1b, Groq alt) and self-skip when none is reachable, so the lab
always runs top-to-bottom offline. The calculator tools use a small AST-based safe
evaluator -- never bare eval()."""
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
import os, socket
WORK = "/tmp/biaa-lab-06-{nn:02d}"
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
    return md(f'''# Lab 6.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 3 &middot; Module 6 &mdash; Frameworks for Building AI Agents**

### What you'll do
{g}

> **How this lab works (experiential flow):** read the **Concept**, run the **Demo** to see it work, then complete **Your Turn** by replacing every `___` placeholder. Run the **grader** cell at the end &mdash; it prints `[PASS]` / `[FAIL]` / `[TODO]` and a final `Score`. Aim for a full score.

> **Framework note:** these labs use the **real** LangChain (`langchain`, `langchain-core`, `langchain-ollama`, `langgraph`). The **graded** cells assert only on the deterministic parts you build &mdash; tool wiring, prompt formatting, agent structure, routing and guardrails &mdash; and never call an LLM, so the lab always verifies offline. Cells marked **Optional &mdash; run it for real** call a live local model (`ollama run llama3.2:1b`, or Groq) and self-skip if none is reachable.

**Reference:** [Module 6 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 6 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 6 labs](./index.html) &nbsp;&middot;&nbsp; [Module 6 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def live(intro, body):
    """An OPTIONAL, non-graded cell that runs REAL LangChain against a live local LLM (or self-skips)."""
    return [md(f'''## Optional &mdash; run it for real (not graded)
{intro} This calls a **real** local model via `ChatOllama("llama3.2:1b")` &mdash; start it with
`ollama run llama3.2:1b` (or swap in `ChatGroq` with a `GROQ_API_KEY`). If none is reachable the cell
prints a note and moves on. **The graded cells above never call an LLM, so the lab always verifies offline.**
*(llama3.2:1b is tiny &mdash; tool-calling can be hit-or-miss; the point is to see a real invocation.)*'''),
            code(body)]

# ---- shared building blocks -------------------------------------------------

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
     "Turn a plain function into a real LangChain tool with @tool and read its name, description and args.",
     ["@tool", "Tool schema", "tool.invoke"])
def _l1(sol):
    return [
      header(1, "Your First Tool with @tool", "Beginner", 20,
        ["Wrap a function as a tool with LangChain's @tool decorator",
         "See the name, description (from the docstring) and args the model reads",
         "Call the tool with .invoke() and get a real result"],
        "Defining a tool"),
      setup(1),
      md('''## Concept
In Module 5 you built tools by hand as dicts. A framework does it for you: LangChain's **`@tool`**
decorator (from **`langchain_core.tools`**) turns a plain function into a **`StructuredTool`** with a
**name**, a **description** (taken from the **docstring** &mdash; the text the model reads to decide
when to use it), an **args** schema, and an **`.invoke()`** method. Same idea as before &mdash; one
decorator instead of a dict.'''),
      code('''from langchain_core.tools import tool

@tool
def greet(name: str) -> str:
    """Say hello to someone by name."""
    return "Hello, " + name + "!"

print("name:", greet.name, "| description:", greet.description)
print("args:", list(greet.args))
print("greet.invoke('Ada') ->", greet.invoke("Ada"))'''),
      md('''## Your Turn
Write two real tools &mdash; a **calculator** and a **lookup** &mdash; each with a clear docstring
(the description the model reads), then call them with `.invoke()`.'''),
      code(render([
        SAFE_CALC,
        "",
        "from langchain_core.tools import tool",
        "",
        "@tool",
        "def calculator(expression: str) -> float:",
        {"s": '    """___  (TODO: replace with one line telling the model what this tool does)."""',
         "a": '    """Do exact arithmetic on an expression such as 2+2 or 120000/2."""'},
        {"s": '    return ___    # TODO: compute the expression with the safe calculator',
         "a": '    return safe_calc(expression)'},
        "",
        "@tool",
        "def lookup(key: str) -> str:",
        {"s": '    """___  (TODO: replace with one line describing this tool)."""',
         "a": '    """Look up a known fact by its key, for example capital of france."""'},
        '    facts = {"capital of france": "Paris", "population of metropolis": "120000"}',
        {"s": '    return ___    # TODO: return the fact for key (lowercased/stripped), else "unknown"',
         "a": '    return facts.get(key.lower().strip(), "unknown")'},
        "",
        "try:",
        "    print('calculator.name :', calculator.name)",
        "    print('calculator.args :', list(calculator.args))",
        "    print('calculator.invoke(\"120000/2\") =', calculator.invoke('120000/2'))",
        "    print('lookup.invoke(\"capital of france\") =', lookup.invoke('capital of france'))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("calculator is a Tool named 'calculator'", lambda: calculator.name == "calculator")
expect_true("its args schema is ['expression']", lambda: list(calculator.args) == ["expression"])
expect_true("the description comes from the docstring", lambda: "arithmetic" in calculator.description.lower())
expect_true("calculator.invoke computes 120000/2 == 60000.0", lambda: calculator.invoke("120000/2") == 60000.0)
expect_true("lookup finds a known fact", lambda: lookup.invoke("capital of france") == "Paris")
expect_true("lookup returns 'unknown' for a missing key", lambda: lookup.invoke("price of gold") == "unknown")'''),
      footer(1, "`@tool` turns a function into a real LangChain Tool the agent can call. The docstring is the description the model reads -- next we see why that description is the tool's real API."),
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
      code('''from langchain_core.tools import tool

@tool
def clock(_: str) -> str:
    """Return the current time of day."""
    return "12:00"

print("the model is shown -> ", clock.name + ": " + clock.description)'''),
      md('''## Your Turn
Write three tools with clear descriptions, render the catalog, then complete `choose_tool`.'''),
      code(render([
        "from langchain_core.tools import tool",
        "",
        "@tool",
        "def weather(city: str) -> str:",
        {"s": '    """___  (TODO: replace -- tell the model WHEN to use this tool)."""',
         "a": '    """Get the current weather for a city. Use for questions about current temperature or conditions."""'},
        '    return "sunny, 24C"',
        "",
        "@tool",
        "def calculator(expression: str) -> str:",
        {"s": '    """___  (TODO: replace -- tell the model WHEN to use this tool)."""',
         "a": '    """Do exact arithmetic on a math expression. Use for any calculation with numbers."""'},
        '    return "(computed)"',
        "",
        "@tool",
        "def translate(text: str) -> str:",
        {"s": '    """___  (TODO: replace -- tell the model WHEN to use this tool)."""',
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
        '    if any(ch.isdigit() for ch in q):   # a query with numbers',
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
expect_true("descriptions come from the docstrings", lambda: "current weather" in tool_catalog(TOOLS).lower())
expect_true("a weather query routes to weather", lambda: choose_tool("weather in paris") == "weather")
expect_true("a numeric query routes to calculator", lambda: choose_tool("what is 12*8") == "calculator")
expect_true("a translate query routes to translate", lambda: choose_tool("translate hello to french") == "translate")'''),
      footer(2, "The description is what the model reads to choose a tool -- write it for the model. Real LangChain selects from exactly this catalog; here you made it visible."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-model-and-prompt", "Beginner",
     "The Model Interface: Prompts & .invoke()", 20,
     "Build a PromptTemplate, format it, and configure a ChatOllama model -- the one interface every provider shares.",
     ["ChatModel", "PromptTemplate", ".invoke"])
def _l3(sol):
    return [
      header(3, "The Model Interface: Prompts & .invoke()", "Beginner", 20,
        ["Build a PromptTemplate with an {input} slot and format it",
         "Configure a ChatOllama model (the .invoke().content interface)",
         "See that the SAME interface works for any model (model-agnostic)"],
        "LangChain's core building blocks"),
      setup(3),
      md('''## Concept
Every LangChain chat model shares **one interface**: `model.invoke(prompt)` returns a message whose
text is in **`.content`**. That is why swapping **`ChatOllama`** for **`ChatGroq`** is a one-line
change. A **`PromptTemplate`** (from `langchain_core.prompts`) fills slots like `{input}`. Building the
prompt and configuring the model are **deterministic** &mdash; the actual call to the LLM is the one
step that needs a running model, so we do it in the optional cell.'''),
      code('''from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama

demo_prompt = PromptTemplate.from_template("Say hi to {who}.")
print("formatted:", demo_prompt.format(who="Ada"))
demo_model = ChatOllama(model="llama3.2:1b")
print("model configured:", demo_model.model, "| has .invoke:", callable(getattr(demo_model, "invoke", None)))'''),
      md('''## Your Turn
Build a prompt with an `{input}` slot, and configure the chat model. (The live call is the optional cell.)'''),
      code(render([
        "from langchain_core.prompts import PromptTemplate",
        "from langchain_ollama import ChatOllama",
        "",
        "def build_prompt(question):",
        {"s": '    template = PromptTemplate.from_template(___)   # TODO: a template with an {input} slot',
         "a": '    template = PromptTemplate.from_template("Answer concisely.\\nQuestion: {input}")'},
        {"s": '    return ___   # TODO: format the template with input=question',
         "a": '    return template.format(input=question)'},
        "",
        "def build_model():",
        {"s": '    return ___   # TODO: a ChatOllama configured for the "llama3.2:1b" model',
         "a": '    return ChatOllama(model="llama3.2:1b")'},
        "",
        "try:",
        "    print(build_prompt('what is an agent?'))",
        "    m = build_model()",
        "    print('---')",
        "    print('model:', m.model, '| same .invoke().content interface as ChatGroq')",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the prompt fills in the question", lambda: "capital of france" in build_prompt("capital of france"))
expect_true("the prompt has a Question: slot", lambda: "Question:" in build_prompt("x"))
expect_true("the model is a ChatOllama for llama3.2:1b", lambda: build_model().model == "llama3.2:1b")
expect_true("every model shares the .invoke interface", lambda: callable(getattr(build_model(), "invoke", None)))
expect_true("swapping the model is a one-line change", lambda: build_model().model == "llama3.2:1b")'''),
      *live(
        "Format a prompt, then actually call the model and read `.content`.",
        '''try:
    if ollama_up():
        model = build_model()
        reply = model.invoke(build_prompt("In one sentence, what is an AI agent?"))
        print("reply:", reply.content)
    else:
        print("No Ollama reachable -- skipping the live call. The prompt/model above are already built.")
except Exception as e:
    print("Live call skipped:", type(e).__name__, "(install langchain-ollama + run `ollama run llama3.2:1b`).")'''),
      footer(3, "One interface -- .invoke(prompt).content -- over every provider. Building the prompt and configuring the model is deterministic; only the call itself needs a running LLM."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-assemble-agent", "Beginner",
     "Assemble an Agent with create_agent", 20,
     "Bind a model + tools into a runnable agent with langchain.agents.create_agent and inspect its structure.",
     ["create_agent", "Binding tools", "CompiledStateGraph"])
def _l4(sol):
    return [
      header(4, "Assemble an Agent with create_agent", "Beginner", 20,
        ["Bind a model + a tools list into one agent with create_agent",
         "See that the agent is a runnable CompiledStateGraph",
         "Inspect its structure: the model and tools nodes it holds"],
        "Assemble an agent"),
      setup(4),
      md('''## Concept
A LangChain (v1) agent is a **model** + a **tools** list bound together by
**`create_agent(model, tools)`** (from `langchain.agents`). It returns a runnable **`CompiledStateGraph`**
&mdash; a small graph with a **`model`** node (decide) and a **`tools`** node (act) that loop until the
model answers. Building it is deterministic and needs no LLM call; **running** it is the optional cell.'''),
      code('''from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """Do exact arithmetic."""
    return "(computed)"

@tool
def lookup(key: str) -> str:
    """Look up a known fact by key."""
    return "(fact)"

print("two tools ready:", calculator.name, "&", lookup.name)'''),
      md('''## Your Turn
Assemble the agent in `build_agent`: gather the tools list and bind them to the model with `create_agent`.'''),
      code(render([
        "from langchain_ollama import ChatOllama",
        "from langchain.agents import create_agent",
        "",
        "def build_agent():",
        '    model  = ChatOllama(model="llama3.2:1b")',
        {"s": '    tools  = ___   # TODO: a list of the two tools (calculator, lookup)',
         "a": '    tools  = [calculator, lookup]'},
        {"s": '    return create_agent(model, ___)   # TODO: pass the tools list',
         "a": '    return create_agent(model, tools)'},
        "",
        "try:",
        "    agent = build_agent()",
        "    print('agent type   :', type(agent).__name__)",
        "    print('graph nodes  :', set(agent.nodes) - {'__start__'})",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("create_agent returns a runnable CompiledStateGraph", lambda: type(build_agent()).__name__ == "CompiledStateGraph")
expect_true("the agent has a model (decide) node", lambda: "model" in set(build_agent().nodes))
expect_true("the agent has a tools (act) node", lambda: "tools" in set(build_agent().nodes))
expect_true("both tools are bound to the agent", lambda: [t.name for t in [calculator, lookup]] == ["calculator", "lookup"])
expect_true("a single tool binds too", lambda: type(create_agent(ChatOllama(model="llama3.2:1b"), [calculator])).__name__ == "CompiledStateGraph")'''),
      *live(
        "Run the assembled agent on a real question and read the final answer.",
        '''try:
    if ollama_up():
        agent = build_agent()
        result = agent.invoke({"messages": [{"role": "user", "content": "What is the capital of France?"}]})
        print("final:", result["messages"][-1].content)
    else:
        print("No Ollama reachable -- skipping the live run. The agent above is already assembled.")
except Exception as e:
    print("Live run skipped:", type(e).__name__)'''),
      footer(4, "model + tools -> create_agent = a runnable CompiledStateGraph. It knows its tools and loops model<->tools until it answers; next we run it and read the trace."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-run-and-trace", "Beginner",
     "Run the Agent & Read the Trace", 25,
     "Cap the loop with recursion_limit and read an agent's message trace: which tools ran, and the final answer.",
     ["recursion_limit", "Message trace", "tool_calls"])
def _l5(sol):
    return [
      header(5, "Run the Agent & Read the Trace", "Beginner", 25,
        ["Read a real agent trace: the list of messages it returns",
         "Extract which tools were called (from each AIMessage.tool_calls)",
         "Cap the loop with recursion_limit so it can never run forever"],
        "The agent loop, made visible"),
      setup(5),
      md('''## Concept
`create_agent` runs the loop for you: the model decides, tools run, results feed back &mdash; until a
final answer, or until **`recursion_limit`** stops it. The agent returns a **list of messages** (the
trace): **`AIMessage`** with **`.tool_calls`** (what it decided to run), **`ToolMessage`** (the result),
and a final `AIMessage` with **`.content`**. Reading that trace is deterministic &mdash; here you
practise on a fixed sample, then run a live agent in the optional cell.'''),
      code('''from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# A real agent returns messages like these -- a fixed sample to practise reading:
SAMPLE = [
    HumanMessage(content="population of france divided by 2"),
    AIMessage(content="", tool_calls=[{"name": "web_search", "args": {"query": "population of france"}, "id": "a"}]),
    ToolMessage(content="68000000", tool_call_id="a"),
    AIMessage(content="", tool_calls=[{"name": "calculator", "args": {"expression": "68000000/2"}, "id": "b"}]),
    ToolMessage(content="34000000.0", tool_call_id="b"),
    AIMessage(content="The population halved is 34000000."),
]
print("messages in the trace:", len(SAMPLE))'''),
      md('''## Your Turn
Complete `tools_used` (every tool call, in order), `final_answer` (the last message with text), and
`run_config` (the loop cap the agent honors).'''),
      code(render([
        "from langchain_core.messages import AIMessage",
        "",
        "def tools_used(messages):",
        "    names = []",
        "    for m in messages:",
        {"s": '        for tc in getattr(m, "tool_calls", None) or []:   # AIMessages carry tool_calls',
         "a": '        for tc in getattr(m, "tool_calls", None) or []:   # AIMessages carry tool_calls'},
        {"s": '            names.append(___)   # TODO: the called tool name from tc',
         "a": '            names.append(tc["name"])'},
        "    return names",
        "",
        "def final_answer(messages):",
        "    for m in reversed(messages):",
        {"s": '        if isinstance(m, AIMessage) and m.content:   # the last AIMessage that has text',
         "a": '        if isinstance(m, AIMessage) and m.content:   # the last AIMessage that has text'},
        {"s": '            return ___   # TODO: the message text',
         "a": '            return m.content'},
        "    return None",
        "",
        "def run_config(max_steps):",
        {"s": '    return ___   # TODO: {"recursion_limit": max_steps} -- caps the loop',
         "a": '    return {"recursion_limit": max_steps}'},
        "",
        "try:",
        "    print('tools used  :', tools_used(SAMPLE))",
        "    print('final answer:', final_answer(SAMPLE))",
        "    print('run config  :', run_config(8))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the trace shows both tools, in order", lambda: tools_used(SAMPLE) == ["web_search", "calculator"])
expect_true("a no-tool trace yields no tool calls", lambda: tools_used([AIMessage(content="hi")]) == [])
expect_true("the final answer is the model's last text", lambda: final_answer(SAMPLE) == "The population halved is 34000000.")
expect_true("run_config caps the loop with recursion_limit", lambda: run_config(3)["recursion_limit"] == 3)
expect_true("a smaller cap is a smaller number", lambda: run_config(1)["recursion_limit"] == 1)'''),
      *live(
        "Run a real agent and read its trace with the very same functions.",
        '''try:
    if ollama_up():
        from langchain_core.tools import tool
        from langchain_ollama import ChatOllama
        from langchain.agents import create_agent
        @tool
        def double(n: int) -> int:
            """Double an integer."""
            return n * 2
        agent = create_agent(ChatOllama(model="llama3.2:1b"), [double])
        result = agent.invoke({"messages": [{"role": "user", "content": "Use the double tool on 21."}]},
                              config=run_config(8))
        print("tools used live:", tools_used(result["messages"]))
        print("final          :", final_answer(result["messages"]))
    else:
        print("No Ollama reachable -- skipping the live run. The trace-reading above already works.")
except Exception as e:
    print("Live run skipped:", type(e).__name__)'''),
      footer(5, "The agent's loop is now visible: read tool_calls to see what it did, recursion_limit is your one-line guardrail. The message trace is your #1 debugging surface."),
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
via `.invoke()`, and wrap the result as an **observation**. `create_agent` does this internally &mdash;
here you build the same safe dispatch by hand so you can debug it. Models hallucinate tool names, so
routing must fail **safely**: an unknown or failing tool returns a message, not a crash.'''),
      code('''from langchain_core.tools import tool

@tool
def weather(city: str) -> str:
    """Get the current weather for a city."""
    return "sunny, 24C"

print("a tool has .name and .invoke:", weather.name, "->", weather.invoke("tokyo"))'''),
      md('''## Your Turn
Build a registry of real tools, then implement `dispatch`: find the tool, run it via `.invoke()`, and
handle the unknown/failing cases.'''),
      code(render([
        SAFE_CALC,
        "",
        "from langchain_core.tools import tool",
        "",
        "@tool",
        "def calculator(expression: str) -> float:",
        '    """Do exact arithmetic on an expression."""',
        '    return safe_calc(expression)',
        "",
        "@tool",
        "def lookup(key: str) -> str:",
        '    """Look up a known fact by key."""',
        '    facts = {"capital of france": "Paris", "population of metropolis": "120000"}',
        '    return facts.get(key.lower().strip(), "unknown")',
        "",
        "REGISTRY = {t.name: t for t in [calculator, lookup]}",
        "",
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
expect_true("ok is True on success", lambda: dispatch(REGISTRY, "lookup", "capital of france")["ok"] is True)
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
      code('''from langchain_core.messages import HumanMessage, AIMessage

# LangChain represents a turn as a message; the running list is the history:
history = [HumanMessage(content="What is the capital of France?"), AIMessage(content="Paris.")]
print("a turn:", (history[0].type, history[0].content))'''),
      md('''## Your Turn
Implement `ConversationMemory` (store + format the history) and a prompt that injects it.'''),
      code(render([
        "from langchain_core.prompts import PromptTemplate",
        "",
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
     "LangGraph: a State Graph with Human Approval", 30,
     "Model a branching agent as a real LangGraph StateGraph with a human-approval node for risky actions.",
     ["StateGraph", "Conditional edges", "Human-in-the-loop"])
def _l8(sol):
    return [
      header(8, "LangGraph: a State Graph with Human Approval", "Intermediate", 30,
        ["Route each step to a node: tool, human-approval, or end",
         "Wire a real LangGraph StateGraph with conditional edges",
         "Run a sequence through the compiled graph and read the node path"],
        "LangGraph -- agents as state graphs"),
      setup(8),
      md('''## Concept
When one implicit loop isn't enough, **LangGraph** models the agent as a **state graph**: **nodes** are
steps, **edges** are transitions you control (deck slides 12&ndash;13). A key win is a **human approval**
node: a **risky** action (send email, delete, pay) is routed to a human before it runs, while safe
actions go straight to the tool node. Here you wire a **real** `StateGraph` with pure-Python nodes, so
its execution is fully deterministic.'''),
      code('''from langgraph.graph import StateGraph, END
from typing import TypedDict

class GState(TypedDict):
    actions: list
    path: list

print("nodes we will wire: tool, human, END |", "END sentinel:", END)'''),
      md('''## Your Turn
Complete `route` (which node an action goes to) and the conditional edges, then compile and run the graph.'''),
      code(render([
        "from langgraph.graph import StateGraph, END",
        "from typing import TypedDict",
        "",
        'RISKY = {"send_email", "delete", "pay"}',
        "",
        "class GState(TypedDict):",
        "    actions: list",
        "    path: list",
        "",
        "def route(state):",
        "    done_so_far = len(state['path'])",
        "    action = state['actions'][done_so_far] if done_so_far < len(state['actions']) else 'done'",
        {"s": '    if action == ___:      # TODO: nothing left to do -> the end node',
         "a": '    if action == "done":'},
        '        return "end"',
        {"s": '    if action in ___:      # TODO: a risky action -> the human-approval node',
         "a": '    if action in RISKY:'},
        '        return "human"',
        '    return "tool"          # any safe tool call',
        "",
        "def tool_node(state):  return {'path': state['path'] + ['tool']}",
        "def human_node(state): return {'path': state['path'] + ['human']}",
        "",
        "def build_graph():",
        "    g = StateGraph(GState)",
        "    g.add_node('tool', tool_node)",
        "    g.add_node('human', human_node)",
        "    edges = {'tool': 'tool', 'human': 'human', 'end': END}",
        {"s": '    g.set_conditional_entry_point(___, edges)   # TODO: route from the start',
         "a": "    g.set_conditional_entry_point(route, edges)"},
        "    g.add_conditional_edges('tool', route, edges)",
        "    g.add_conditional_edges('human', route, edges)",
        "    return g.compile()",
        "",
        "def run_graph(actions):",
        "    return build_graph().invoke({'actions': actions, 'path': []})['path']",
        "",
        "try:",
        "    print('search      ->', route({'actions': ['search'], 'path': []}))",
        "    print('send_email  ->', route({'actions': ['send_email'], 'path': []}))",
        "    print('path:', run_graph(['search', 'send_email', 'done']))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("a safe action routes to the tool node", lambda: route({"actions": ["search"], "path": []}) == "tool")
expect_true("a risky action routes to human approval", lambda: route({"actions": ["send_email"], "path": []}) == "human")
expect_true("nothing left routes to the end node", lambda: route({"actions": [], "path": []}) == "end")
expect_true("the compiled graph walks the expected node path", lambda: run_graph(["search", "pay", "done"]) == ["tool", "human", "end"] or run_graph(["search", "pay", "done"]) == ["tool", "human"])
expect_true("a risky step lands on the human node", lambda: "human" in run_graph(["search", "delete"]))'''),
      footer(8, "LangChain gets an agent running; LangGraph puts its flow under control -- explicit nodes, branching, and a first-class human-approval pause. Start simple; graduate when you need it."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-multi-tool", "Intermediate",
     "Multi-Tool Orchestration (day in the life)", 30,
     "Give an agent a search tool and a calculator, and read a trace that chains them to answer a compound question.",
     ["Tool chaining", "Orchestration", "Trace"])
def _l9(sol):
    return [
      header(9, "Multi-Tool Orchestration (day in the life)", "Intermediate", 30,
        ["Give the agent TWO tools: a search and a calculator",
         "Assemble them into one agent with create_agent",
         "Read a trace that chains them: search a fact, then compute on it"],
        "Connecting to real tools & APIs"),
      setup(9),
      md('''## Concept
Agents earn their keep on **multi-step** tasks that **orchestrate several tools** (deck slide 16):
*"population of France, divided by 2?"* needs a **search** (a live fact) **then** a **calculator**. You
bind both tools to one agent; the agent chains them &mdash; each observation feeds the next step. The
graded cell checks the tools are wired and reads a fixed chained trace; the optional cell runs it live.'''),
      code('''from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """Search the web for a current fact."""
    facts = {"population of france": "68000000"}
    return facts.get(query.lower().strip(), "no result")

print("a search tool:", web_search.name, "->", web_search.invoke("population of france"))'''),
      md('''## Your Turn
Give the agent **both** tools in `build_agent`, and complete `tools_used` to read a chained trace.'''),
      code(render([
        SAFE_CALC,
        "",
        "from langchain_core.tools import tool",
        "from langchain_ollama import ChatOllama",
        "from langchain.agents import create_agent",
        "from langchain_core.messages import AIMessage, ToolMessage",
        "",
        "@tool",
        "def web_search(query: str) -> str:",
        '    """Search the web for a current fact."""',
        '    facts = {"population of france": "68000000"}',
        '    return facts.get(query.lower().strip(), "no result")',
        "",
        "@tool",
        "def calculator(expression: str) -> float:",
        '    """Do exact arithmetic on an expression."""',
        '    return safe_calc(expression)',
        "",
        "def build_agent():",
        '    model = ChatOllama(model="llama3.2:1b")',
        {"s": '    tools = ___   # TODO: both tools, so the agent can search AND compute',
         "a": '    tools = [web_search, calculator]'},
        "    return create_agent(model, tools)",
        "",
        "# a fixed sample trace that chained search -> calculator:",
        "SAMPLE = [",
        '    AIMessage(content="", tool_calls=[{"name": "web_search", "args": {"query": "population of france"}, "id": "a"}]),',
        '    ToolMessage(content="68000000", tool_call_id="a"),',
        '    AIMessage(content="", tool_calls=[{"name": "calculator", "args": {"expression": "68000000/2"}, "id": "b"}]),',
        '    ToolMessage(content="34000000.0", tool_call_id="b"),',
        '    AIMessage(content="34000000"),',
        "]",
        "",
        "def tools_used(messages):",
        {"s": '    return [___ for m in messages for tc in (getattr(m, "tool_calls", None) or [])]   # TODO: tc name',
         "a": '    return [tc["name"] for m in messages for tc in (getattr(m, "tool_calls", None) or [])]'},
        "",
        "try:",
        "    agent = build_agent()",
        "    print('agent nodes:', set(agent.nodes) - {'__start__'})",
        "    print('tools chained:', tools_used(SAMPLE))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("both tools are bound to the agent", lambda: type(build_agent()).__name__ == "CompiledStateGraph" and "tools" in set(build_agent().nodes))
expect_true("the trace chained two tools", lambda: len(tools_used(SAMPLE)) == 2)
expect_true("tools ran in order: search then calculator", lambda: tools_used(SAMPLE) == ["web_search", "calculator"])
expect_true("the search tool returns the population", lambda: web_search.invoke("population of france") == "68000000")
expect_true("the calculator halves it exactly", lambda: calculator.invoke("68000000/2") == 34000000.0)'''),
      *live(
        "Run the two-tool agent live and read which tools it actually chained.",
        '''try:
    if ollama_up():
        agent = build_agent()
        result = agent.invoke({"messages": [{"role": "user",
                 "content": "Use web_search for the population of france, then use the calculator to halve it."}]},
                 config={"recursion_limit": 8})
        print("tools used live:", tools_used(result["messages"]))
        print("final          :", result["messages"][-1].content)
    else:
        print("No Ollama reachable -- skipping the live run. The wiring + trace-reading above already work.")
except Exception as e:
    print("Live run skipped:", type(e).__name__)'''),
      footer(9, "Chaining search + compute in one run is exactly where agents beat a single call. Same create_agent, two tools -- the 'day in the life' trace, for real."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-external-apis", "Advanced",
     "Connect to External APIs (Search + Wolfram)", 40,
     "Wrap a web-search tool and a Wolfram-style compute tool, bind them to an agent, and (optionally) call the REAL APIs.",
     ["External APIs", "Search tool", "Compute tool"])
def _l10(sol):
    return [
      header(10, "Connect to External APIs (Search + Wolfram)", "Advanced", 40,
        ["Wrap a Google-Search-style tool over a live fact source",
         "Wrap a Wolfram-Alpha-style exact-compute tool",
         "Bind them to an agent; optionally call the REAL APIs"],
        "Connecting to real tools & APIs"),
      setup(10),
      md('''## Concept
Real agents reach the world through **tool integrations** (deck slide 16): **Google Search** for live
facts beyond the training cutoff, **Wolfram Alpha** for exact computation. The pattern is always: get a
key &rarr; wrap the service as a `@tool` &rarr; add it to the tools list. The **graded** cell wraps
deterministic local stand-ins and binds them to a real agent; the **optional** cell calls the real APIs
if you have keys.'''),
      code('''from langchain_core.tools import tool

@tool
def google_search(query: str) -> str:
    """Search the web for a current fact or figure."""
    index = {"gold price today usd per oz": "2400"}
    return index.get(query.lower().strip(), "no result")

print("search tool ready:", google_search.invoke("gold price today usd per oz"))'''),
      md('''## Your Turn
Wrap a **google_search** tool (over a small live-fact index) and a **wolfram** compute tool, then bind
both to an agent with `create_agent`.'''),
      code(render([
        SAFE_CALC,
        "",
        "from langchain_core.tools import tool",
        "from langchain_ollama import ChatOllama",
        "from langchain.agents import create_agent",
        "",
        "@tool",
        "def google_search(query: str) -> str:",
        {"s": '    """___  (TODO: replace -- tell the model this searches for a live web fact)."""',
         "a": '    """Search the web for a current fact or figure. Use for anything not in the model own memory."""'},
        '    index = {"gold price today usd per oz": "2400", "eiffel tower height m": "330"}',
        {"s": '    return ___   # TODO: look query up in index (lowercased/stripped), else "no result"',
         "a": '    return index.get(query.lower().strip(), "no result")'},
        "",
        "@tool",
        "def wolfram(expression: str) -> float:",
        '    """Compute an exact math expression (a Wolfram-Alpha-style compute tool)."""',
        '    return safe_calc(expression)',
        "",
        "def build_agent():",
        '    model = ChatOllama(model="llama3.2:1b")',
        {"s": '    return create_agent(model, ___)   # TODO: both external tools',
         "a": '    return create_agent(model, [google_search, wolfram])'},
        "",
        "try:",
        "    print('search known  :', google_search.invoke('gold price today usd per oz'))",
        "    print('search unknown:', google_search.invoke('who won the 3pm race'))",
        "    print('wolfram        :', wolfram.invoke('2400*2'))",
        "    print('agent nodes    :', set(build_agent().nodes) - {'__start__'})",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("search returns a known live fact", lambda: google_search.invoke("gold price today usd per oz") == "2400")
expect_true("search returns 'no result' for the unknown", lambda: google_search.invoke("who won the 3pm race") == "no result")
expect_true("the compute tool does exact math", lambda: wolfram.invoke("2400*2") == 4800)
expect_true("both external tools bind to the agent", lambda: type(build_agent()).__name__ == "CompiledStateGraph" and "tools" in set(build_agent().nodes))
expect_true("the search tool carries a real (filled-in) description", lambda: "___" not in google_search.description and "search" in google_search.description.lower())'''),
      *live(
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
**input validation**, a **recursion_limit** cap, and a **tracing callback** that logs every
(action, input, observation) so you can debug and audit. Real LangChain exposes callbacks via
`BaseCallbackHandler`; **LangSmith / Langfuse** capture full traces. Here you build the offline
versions (deterministic) and see the real callback interface in the optional cell.'''),
      code('''from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """Do exact arithmetic on an expression."""
    return "(computed)"

ALLOWED = {"calculator", "lookup"}
print("allow-list:", ALLOWED, "| a tool the agent may call:", calculator.name in ALLOWED)'''),
      md('''## Your Turn
Complete the allow-list check, the input validator, and the tracing callback, then run a guarded loop.'''),
      code(render([
        SAFE_CALC,
        "",
        "from langchain_core.tools import tool",
        "",
        "@tool",
        "def calculator(expression: str) -> float:",
        '    """Do exact arithmetic on an expression."""',
        '    return safe_calc(expression)',
        "",
        "@tool",
        "def lookup(key: str) -> str:",
        '    """Look up a known fact by key."""',
        '    return {"capital of france": "Paris"}.get(key.lower().strip(), "unknown")',
        "",
        "REGISTRY = {t.name: t for t in [calculator, lookup]}",
        'ALLOWED = {"calculator", "lookup"}',
        "",
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
      *live(
        "See the REAL callback interface LangChain exposes (LangSmith / Langfuse capture full traces).",
        '''try:
    from langchain_core.callbacks import BaseCallbackHandler
    class PrintHandler(BaseCallbackHandler):
        def on_tool_end(self, output, **kw):
            print("tool ->", output)
    print("Real LangChain calls handlers like PrintHandler on every model/tool event.")
    print("Attach one with: agent.invoke(inputs, config={'callbacks': [PrintHandler()]}).")
    print("For full run traces: set LANGCHAIN_TRACING_V2=true + LANGCHAIN_API_KEY (LangSmith),")
    print("or run Langfuse (this course's stack) and attach its callback handler.")
except Exception as e:
    print("Install langchain-core to use real callbacks -- skipping:", type(e).__name__)
print("The guarded run above already traced every step offline.")'''),
      footer(11, "Allow-list + validation + recursion_limit + tracing turn an autonomous agent from a liability into something you can trust and debug. Day 5 goes deeper on responsible agents."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-langchain-agent", "Advanced",
     "Capstone: A Guardrailed LangChain Agent", 45,
     "Assemble allow-listed tools + a system prompt + a recursion cap into a real create_agent, and run it live.",
     ["End-to-end agent", "Guardrails", "create_agent"])
def _l12(sol):
    return [
      header(12, "Capstone: A Guardrailed LangChain Agent", "Advanced", 45,
        ["Assemble the module: allow-listed @tools + create_agent + a recursion cap",
         "Enforce a guardrail policy: only allow-listed tools are bound",
         "Run the real agent over a suite of tasks (optional live cell)"],
        "Choosing a framework"),
      setup(12),
      md('''## Concept
Capstone: a **guardrailed LangChain agent** that ties the module together &mdash; real `@tool` tools,
a **system prompt**, an **allow-list** so only vetted tools are bound, `create_agent`, and a
**`recursion_limit`** cap. The graded cell asserts the assembly and the guardrail policy
(deterministic); the optional cell runs the **real** agent (Ollama/Groq) over a task suite &mdash; the
bridge to Day 4.'''),
      code('''from langchain_core.tools import tool

@tool
def lookup(key: str) -> str:
    """Look up a known fact by key."""
    return {"population of metropolis": "120000", "capital of france": "Paris"}.get(key.lower().strip(), "unknown")

print("a vetted tool:", lookup.name)'''),
      md('''## Your Turn
Complete `build_agent`: keep only the **allowed** tools, add a system prompt, and set the recursion cap.
Complete `vet_tools` (the guardrail policy that drops anything not on the allow-list).'''),
      code(render([
        SAFE_CALC,
        "",
        "from langchain_core.tools import tool",
        "from langchain_ollama import ChatOllama",
        "from langchain.agents import create_agent",
        "",
        "@tool",
        "def lookup(key: str) -> str:",
        '    """Look up a known fact by key."""',
        '    facts = {"population of metropolis": "120000", "capital of france": "Paris"}',
        '    return facts.get(key.lower().strip(), "unknown")',
        "",
        "@tool",
        "def calculator(expression: str) -> float:",
        '    """Do exact arithmetic on an expression."""',
        '    return safe_calc(expression)',
        "",
        'ALLOWED = {"lookup", "calculator"}',
        "SYSTEM = \"You are a careful assistant. Use tools for facts and math; never guess.\"",
        "",
        "def vet_tools(tools):",
        '    # guardrail: keep only tools whose name is on the allow-list',
        {"s": '    return [t for t in tools if ___]   # TODO: keep allow-listed tools only',
         "a": '    return [t for t in tools if t.name in ALLOWED]'},
        "",
        "def build_agent(max_steps=8):",
        '    model = ChatOllama(model="llama3.2:1b")',
        "    tools = vet_tools([lookup, calculator])",
        {"s": '    return create_agent(model, tools, system_prompt=___)   # TODO: the system prompt',
         "a": '    return create_agent(model, tools, system_prompt=SYSTEM)'},
        "",
        "def run_config(max_steps=8):",
        {"s": '    return ___   # TODO: cap the loop with recursion_limit',
         "a": '    return {"recursion_limit": max_steps}'},
        "",
        "try:",
        "    agent = build_agent()",
        "    print('agent type :', type(agent).__name__)",
        "    print('bound tools:', [t.name for t in vet_tools([lookup, calculator])])",
        "    print('a risky tool is dropped:', [t.name for t in vet_tools([lookup])] )",
        "    print('run config :', run_config())",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the capstone agent is a runnable CompiledStateGraph", lambda: type(build_agent()).__name__ == "CompiledStateGraph")
expect_true("both allow-listed tools are bound", lambda: {t.name for t in vet_tools([lookup, calculator])} == {"lookup", "calculator"})
expect_true("the guardrail drops a non-allow-listed tool", lambda: (lambda fake: [t.name for t in vet_tools([lookup, fake])] == ["lookup"])(type("F", (), {"name": "delete_database"})()))
expect_true("the recursion cap is set", lambda: run_config(5)["recursion_limit"] == 5)
expect_true("the tools still compute correctly", lambda: calculator.invoke("120000*2") == 240000.0 and lookup.invoke("capital of france") == "Paris")'''),
      *live(
        "Run the guardrailed agent on a real task -- the bridge to Day 4. (Try more questions from the SUITE list yourself.)",
        '''SUITE = ["What is 15 times 3?", "What is the capital of France?", "What is the population of metropolis?"]
try:
    if ollama_up():
        agent = build_agent()
        q = SUITE[0]   # try the others yourself -- each is a fresh real agent run
        result = agent.invoke({"messages": [{"role": "user", "content": q}]}, config=run_config())
        print(q, "->", result["messages"][-1].content)
        print("That was a REAL guardrailed LangChain agent. Next: Day 4 -- task automation & multi-agent teams.")
    else:
        print("No Ollama reachable -- skipping the live run. The guardrailed agent above is fully assembled.")
        print("Next: Day 4 -- task automation & multi-agent collaboration.")
except Exception as e:
    print("Live run skipped:", type(e).__name__)'''),
      footer(12, "You assembled a guardrailed LangChain agent -- vetted tools, a system prompt, create_agent and a recursion cap -- and ran it for real. That is a shippable agent; next, Day 4 puts agents to work."),
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
