# -*- coding: utf-8 -*-
"""Generator for Day 3 Module 6 hands-on labs (12 notebooks) -- NEAR-REAL design.
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

Design: this is the "Frameworks for Building AI Agents" module. Participants HAVE a local
Ollama (llama3.1:8b) and real API keys (SERPER_API_KEY, WOLFRAM_ALPHA_APPID, GROQ/OPENAI in
the repo .env). So the labs are NEAR-REAL, not stubs: a REAL LLM drives a REAL
`create_agent` over REAL `@tool`s (and real external APIs in lab 10), and the student reads the
REAL message trace. There is NO auto-grader -- each lab ends with "Run it for real -> Read the
trace -> Your turn (open task)".

Kept real & deterministic (NOT LLM stand-ins): the AST-safe calculator (wrapped in try/except),
routing/dispatch, guardrails/allow-list/validation, conversation-memory formatting, and a real
LangGraph StateGraph. Tools ALWAYS catch their own exceptions and RETURN an error string -- a
tool that raises aborts the whole agent run (the lesson taught in lab 11).

Student robustness (no grader): the cells that EXERCISE the blanks are wrapped by guard()/
runguard() so an unfilled `___` prints a friendly "fill the blanks" note instead of crashing --
so a student notebook runs top-to-bottom, and a solution notebook runs the real thing."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day3-module6-frameworks-for-building-ai-agents.html"
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
load_dotenv(find_dotenv(usecwd=True))   # SERPER_API_KEY, WOLFRAM_ALPHA_APPID, GROQ/OPENAI keys

WORK = "/tmp/biaa-lab-06-{nn:02d}"
os.makedirs(WORK, exist_ok=True)

def ollama_up(host="127.0.0.1", port=11434):
    """True if a local Ollama server is listening. If it's down, start it with:  ollama run llama3.1:8b"""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False

from langchain_ollama import ChatOllama
# Day-3 provider: a REAL local model. Pin the host -- plain 'localhost' can give 'No route to host'.
llm = ChatOllama(model="llama3.1:8b", temperature=0, base_url="http://127.0.0.1:11434")

def print_trace(result):
    """Print a REAL agent message trace: tool calls the model made, tool observations, final answer."""
    for m in result["messages"]:
        for tc in (getattr(m, "tool_calls", None) or []):
            print("TOOL CALL:", tc["name"], tc["args"])
        if type(m).__name__ == "ToolMessage":
            print("OBS:", str(m.content)[:200])
        elif str(getattr(m, "content", "")).strip():
            print(type(m).__name__, ":", str(m.content)[:300])

if ollama_up():
    print("Ollama reachable at 127.0.0.1:11434 | model:", llm.model, "| WORK:", WORK)
else:
    print("Ollama NOT reachable -- start it with:  ollama run llama3.1:8b")
    print("(The 'Run it for real' cells will print this note instead of crashing.)  WORK:", WORK)''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 6.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 3 &middot; Module 6 &mdash; Frameworks for Building AI Agents**

### What you'll do
{g}

> **How this lab works (near-real):** you have a local Ollama running `llama3.1:8b`. Read the **Concept**, fill the real `___` blanks in **Build it** (real tool bodies, real prompts, the real `create_agent` call), then **Run it for real** &mdash; a real LLM drives a real agent over real tools &mdash; and **read the trace** to see exactly what it did. Finish with an open **Your turn**. There is **no auto-grader**; the goal is a working agent and a trace you can read.

> **Framework note:** these labs use the **real** LangChain (`langchain`, `langchain-core`, `langchain-ollama`, `langgraph`) and a **real local model** (`ollama run llama3.1:8b`, pinned to `http://127.0.0.1:11434`). If Ollama is down, the run cells print how to start it instead of crashing. A `@tool` must **catch its own errors and return a string** &mdash; a tool that *raises* aborts the whole agent run (you'll see exactly this in Lab 11).

**Reference:** [Module 6 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 6 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 6 labs](./index.html) &nbsp;&middot;&nbsp; [Module 6 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def concept(text):   return md("## Concept\n" + text)
def buildmd(text):   return md("## Build it\n" + text)
def runmd(text):     return md("## Run it for real &amp; read the trace\n" + text + "\n\n_This calls the real `llama3.1:8b` via Ollama. If Ollama is down the cell prints how to start it instead of crashing._")
def noticemd(text):  return md("## What to notice\n" + text)
def yourturn(text):  return md("## Your turn (open task &mdash; no grader)\n" + text)

# AST-based safe arithmetic -- never bare eval() on free text. Tools wrap this in try/except.
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
     "Turn plain functions into real LangChain @tools, then watch a real llama3.1:8b agent call YOUR tools.",
     ["@tool", "Tool schema", "Real agent run"])
def _l1(sol):
    DEFS = [
      SAFE_CALC, "",
      "from langchain_core.tools import tool",
      "",
      "@tool",
      "def calculator(expression: str) -> str:",
      {"s": '    """___  (TODO: one line telling the model WHEN to use this -- it is the tool\'s API)."""',
       "a": '    """Do exact arithmetic on a numeric expression such as 2+2 or 120000/2. Use for any calculation."""'},
      "    try:",
      "        return str(safe_calc(expression))          # success path",
      "    except Exception:",
      '        return "error: not a numeric expression"    # a tool must NEVER raise -- return a string',
      "",
      "@tool",
      "def lookup(key: str) -> str:",
      '    """Look up a known fact by its key, for example \'capital of france\'."""',
      '    facts = {"capital of france": "Paris", "population of metropolis": "120000"}',
      {"s": '    return ___    # TODO: return the fact for key (lowercased/stripped), else "unknown"',
       "a": '    return facts.get(key.lower().strip(), "unknown")'},
    ]
    EX = '''print("calculator.name :", calculator.name)
print("calculator.args :", list(calculator.args))
print("calculator.invoke('120000/2') =", calculator.invoke("120000/2"))
print("calculator.invoke('oops')     =", calculator.invoke("oops"))   # returns a string, no crash
print("lookup.invoke('capital of france') =", lookup.invoke("capital of france"))'''
    RUN = '''from langchain.agents import create_agent
agent = create_agent(llm, tools=[calculator, lookup])
result = agent.invoke({"messages": [("user",
         "What is the capital of France, and what is 120000 divided by 2?")]},
         config={"recursion_limit": 8})
print_trace(result)'''
    return [
      header(1, "Your First Tool with @tool", "Beginner", 20,
        ["Wrap a function as a tool with LangChain's @tool decorator",
         "See the name, description (from the docstring) and args the model reads",
         "Bind your tools to a real agent and watch the model call them"],
        "Defining a tool"),
      setup(1),
      concept('''In Module 5 you built tools by hand as dicts. A framework does it for you: LangChain's **`@tool`**
decorator (from **`langchain_core.tools`**) turns a plain function into a **`StructuredTool`** with a
**name**, a **description** (taken from the **docstring** &mdash; the text the model reads to decide when
to use it), an **args** schema, and an **`.invoke()`** method. Notice the calculator **catches its own
error and returns a string** &mdash; never let a tool raise.'''),
      code('''from langchain_core.tools import tool

@tool
def greet(name: str) -> str:
    """Say hello to someone by name."""
    return "Hello, " + name + "!"

print("name:", greet.name, "| description:", greet.description)
print("args:", list(greet.args))
print("greet.invoke('Ada') ->", greet.invoke("Ada"))'''),
      buildmd('''Write two **real** tools &mdash; a **calculator** (safe arithmetic, wrapped so it never raises) and a
**lookup** &mdash; then call them with `.invoke()`.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Bind both of YOUR tools to a real agent and ask a question that needs each one. Read the trace: the model calls your functions."),
      code(runguard(RUN)),
      noticemd('''- The trace shows **`TOOL CALL: lookup {...}`** and **`TOOL CALL: calculator {...}`** &mdash; the model chose to call *your* Python functions.
- Each **`OBS:`** line is what your tool returned; the model reads it and continues.
- A small model can still make a wrong call now and then &mdash; that's real agent behaviour, and it's why we read traces.'''),
      yourturn('''Add a **third** tool of your own &mdash; e.g. a `word_count(text)` tool with a clear docstring &mdash; put it
in the `tools=[...]` list, and re-run the agent with a question that needs it.
**What good looks like:** the trace shows your new tool being called with sensible args, and the final
answer uses its result. If the model ignores your tool, sharpen the docstring (that's the tool's real API).'''),
      footer(1, "`@tool` turns a function into a real Tool the agent can call, and the docstring is the API the model reads. You just watched llama3.1:8b call your own Python -- next we make descriptions drive which tool it picks."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-tool-descriptions", "Beginner",
     "The Docstring Is the Tool's API", 20,
     "Prove the docstring drives tool choice: give a real agent well- vs poorly-described tools and watch what it picks.",
     ["Descriptions", "Tool selection", "Real trace"])
def _l2(sol):
    DEFS = [
      "from langchain_core.tools import tool",
      "",
      "@tool",
      "def weather(city: str) -> str:",
      {"s": '    """___  (TODO: tell the model WHEN to use this -- e.g. current temperature/conditions for a city)."""',
       "a": '    """Get the current weather for a city. Use for questions about current temperature or conditions."""'},
      '    return city.title() + ": sunny, 24C"',
      "",
      "@tool",
      "def dictionary(word: str) -> str:",
      {"s": '    """___  (TODO: tell the model WHEN to use this -- e.g. the meaning of an English word)."""',
       "a": '    """Define an English word. Use when the user asks what a word means."""'},
      '    return word + ": (a definition)"',
      "",
      "@tool",
      "def translate(text: str) -> str:",
      {"s": '    """___  (TODO: tell the model WHEN to use this -- e.g. translate text into French)."""',
       "a": '    """Translate the given English text into French. Use for translation requests."""'},
      '    return "(translated) " + text',
      "",
      "TOOLS = [weather, dictionary, translate]",
    ]
    EX = '''print("catalog the model is shown:")
for t in TOOLS:
    print(" -", t.name + ":", t.description)'''
    RUN = '''from langchain.agents import create_agent
agent = create_agent(llm, tools=TOOLS)
result = agent.invoke({"messages": [("user", "What's the weather like in Tokyo right now?")]},
                      config={"recursion_limit": 6})
print_trace(result)'''
    return [
      header(2, "The Docstring Is the Tool's API", "Beginner", 20,
        ["Write descriptions that tell the model WHEN to use each tool",
         "Bind the tools to a real agent and ask a targeted question",
         "Read the trace to see the description decide which tool fires"],
        "Defining a tool"),
      setup(2),
      concept('''The model never sees your code &mdash; only each tool's **name**, **description** and **args**. So the
**docstring is the tool's real API**: a vague one makes the agent pick the wrong tool (or none). Here you
write good descriptions, bind the tools to a real agent, and **watch the trace** confirm the model routed
by your words.'''),
      code('''from langchain_core.tools import tool

@tool
def clock(_: str) -> str:
    """Return the current time of day."""
    return "12:00"

print("the model is shown -> ", clock.name + ": " + clock.description)'''),
      buildmd('''Write three tools with **clear descriptions** (that's the part graded by reality &mdash; a good agent
run). The bodies are simple; the **docstring** is what matters.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Bind the three tools to a real agent and ask a weather question. The description &mdash; not any keyword you coded &mdash; is what makes the model pick `weather`."),
      code(runguard(RUN)),
      noticemd('''- The trace should show **`TOOL CALL: weather {'city': 'Tokyo'}`** &mdash; chosen from your description, not your code.
- The model matched the *question* to the *docstring*. That is the entire selection mechanism.'''),
      yourturn('''Change `weather`'s docstring to something vague like `"""Does stuff with a place."""` and re-run the agent
on the same question. **What good looks like:** with a vague description the model often stops calling
`weather` (or calls the wrong tool). Restore a clear description and it comes back. You've just proven the
docstring is the API &mdash; write it for the model.'''),
      footer(2, "The description is what the model reads to choose a tool -- write it for the model. You watched a real agent route by your words, and watched a vague docstring break it."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-model-and-prompt", "Beginner",
     "The Model Interface: Prompts & .invoke()", 20,
     "Build a real PromptTemplate, call ChatOllama with .invoke(), and read .content -- the interface every provider shares.",
     ["ChatModel", "PromptTemplate", "Real .invoke"])
def _l3(sol):
    DEFS = [
      "from langchain_core.prompts import PromptTemplate",
      "",
      "def build_template():",
      {"s": '    return PromptTemplate.from_template(___)   # TODO: a template with an {input} slot',
       "a": '    return PromptTemplate.from_template("Answer in one concise sentence.\\nQuestion: {input}")'},
      "",
      "def build_prompt(question):",
      {"s": '    return ___   # TODO: format build_template() with input=question',
       "a": '    return build_template().format(input=question)'},
      "",
      "def ask(question):",
      '    """Call the real model and return its text."""',
      {"s": '    reply = llm.invoke(___)   # TODO: pass the formatted prompt for this question',
       "a": '    reply = llm.invoke(build_prompt(question))'},
      {"s": '    return ___               # TODO: the model\'s text is in .content',
       "a": '    return reply.content'},
    ]
    EX = '''print("input variables:", build_template().input_variables)
print("prompt sent:", build_prompt("what is an AI agent?"))'''
    RUN = '''print("Q: In one sentence, what is an AI agent?")
print("A:", ask("In one sentence, what is an AI agent?"))'''
    return [
      header(3, "The Model Interface: Prompts & .invoke()", "Beginner", 20,
        ["Build a PromptTemplate with an {input} slot and format it",
         "Call the real ChatOllama model with .invoke() and read .content",
         "See that the SAME interface would work for ChatGroq (model-agnostic)"],
        "LangChain's core building blocks"),
      setup(3),
      concept('''Every LangChain chat model shares **one interface**: `model.invoke(prompt)` returns a message whose
text is in **`.content`**. That is why swapping **`ChatOllama`** for **`ChatGroq`** is a one-line change.
A **`PromptTemplate`** (from `langchain_core.prompts`) fills slots like `{input}`. Here you build the
prompt and call the **real** model.'''),
      code('''from langchain_core.prompts import PromptTemplate

demo_prompt = PromptTemplate.from_template("Say hi to {who}.")
print("formatted:", demo_prompt.format(who="Ada"))
print("the setup cell already built `llm` =", llm.model)'''),
      buildmd('''Build a **template** with an `{input}` slot, a `build_prompt` that fills it, and `ask` that calls the
**real** `llm` and returns `.content`.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Call the real model through your `ask()` and read the answer it returns."),
      code(runguard(RUN)),
      noticemd('''- The reply came back through **`.invoke(prompt).content`** &mdash; the one interface.
- Swap `llm` for `ChatGroq(model="llama-3.3-70b-versatile")` (with a `GROQ_API_KEY`) and `ask()` is unchanged. That's what "model-agnostic" buys you.'''),
      yourturn('''Change the template &mdash; make it answer as bullet points, or in French, or as a five-year-old &mdash; and
re-run `ask()`. Then (optional) build a second model `groq = ChatGroq(model="llama-3.3-70b-versatile")`
and call `groq.invoke(build_prompt(...)).content`. **What good looks like:** the answer's *style* changes
with the template, and the *same* `.invoke().content` call works across models.'''),
      footer(3, "One interface -- .invoke(prompt).content -- over every provider. The PromptTemplate shapes the request; swapping the model is one line."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-assemble-agent", "Beginner",
     "Assemble an Agent with create_agent", 20,
     "Bind the real model + tools into a runnable agent with create_agent, run it, and read the final answer.",
     ["create_agent", "Binding tools", "Real run"])
def _l4(sol):
    DEFS = [
      "from langchain.agents import create_agent",
      "",
      "def build_agent():",
      {"s": '    tools = ___   # TODO: a list holding the lookup tool (add more later)',
       "a": '    tools = [lookup]'},
      {"s": '    return create_agent(llm, ___)   # TODO: pass the tools list',
       "a": '    return create_agent(llm, tools)'},
    ]
    EX = '''agent = build_agent()
print("agent type  :", type(agent).__name__)
print("graph nodes :", set(agent.nodes) - {"__start__"})'''
    RUN = '''result = agent.invoke({"messages": [("user", "What is the capital of Japan?")]},
                      config={"recursion_limit": 6})
print_trace(result)
print("---")
print("final answer:", result["messages"][-1].content)'''
    return [
      header(4, "Assemble an Agent with create_agent", "Beginner", 20,
        ["Bind the model + a tools list into one agent with create_agent",
         "See that the agent is a runnable CompiledStateGraph with model+tools nodes",
         "Invoke it on a real question and read the answer"],
        "Assemble an agent"),
      setup(4),
      concept('''A LangChain (v1) agent is a **model** + a **tools** list bound together by
**`create_agent(model, tools)`** (from `langchain.agents`). It returns a runnable **`CompiledStateGraph`**
&mdash; a small graph with a **`model`** node (decide) and a **`tools`** node (act) that loop until the
model answers. You assemble it here, then run it for real.'''),
      code('''from langchain_core.tools import tool

@tool
def lookup(key: str) -> str:
    """Look up a known fact by key, e.g. 'capital of france'."""
    return {"capital of france": "Paris", "capital of japan": "Tokyo"}.get(key.lower().strip(), "unknown")

print("one tool ready:", lookup.name)'''),
      buildmd('''Assemble the agent in `build_agent`: gather the tools list and bind them to the real `llm` with
`create_agent`.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Invoke the assembled agent on a real question and read the final answer (and the tool call it made to get there)."),
      code(runguard(RUN)),
      noticemd('''- `type(agent).__name__` is **`CompiledStateGraph`** &mdash; a real runnable graph, not a wrapper.
- Its nodes are **`model`** and **`tools`**: the loop is decide -> act -> decide until an answer.
- The final message's `.content` is the answer; everything before it is how the agent got there.'''),
      yourturn('''Add a second tool (a calculator, or a second fact source) to `build_agent`'s list and re-run with a
question that needs both. **What good looks like:** the trace shows two different `TOOL CALL`s and the
final answer combines them &mdash; a real multi-tool agent, assembled in three lines.'''),
      footer(4, "model + tools -> create_agent = a runnable CompiledStateGraph that loops decide<->act until it answers. Next: read the full trace and cap the loop."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-run-and-trace", "Beginner",
     "Run the Agent & Read the Trace", 25,
     "Run a real agent, extract which tools fired and the final answer from the REAL message trace, and cap the loop.",
     ["recursion_limit", "Message trace", "tool_calls"])
def _l5(sol):
    DEFS = [
      "from langchain_core.messages import AIMessage",
      "from langchain.agents import create_agent",
      "",
      "def run_config(max_steps):",
      {"s": '    return ___   # TODO: {"recursion_limit": max_steps} -- caps the loop',
       "a": '    return {"recursion_limit": max_steps}'},
      "",
      "def tools_used(messages):",
      "    names = []",
      "    for m in messages:",
      '        for tc in (getattr(m, "tool_calls", None) or []):   # AIMessages carry tool_calls',
      {"s": '            names.append(___)   # TODO: the called tool name from tc',
       "a": '            names.append(tc["name"])'},
      "    return names",
      "",
      "def final_answer(messages):",
      "    for m in reversed(messages):",
      "        if isinstance(m, AIMessage) and m.content:   # the last AIMessage that has text",
      {"s": '            return ___   # TODO: the message text',
       "a": '            return m.content'},
      "    return None",
      "",
      "agent = create_agent(llm, tools=[web_search, calculator])",
    ]
    EX = 'print("run config:", run_config(8))'
    RUN = '''result = agent.invoke(
    {"messages": [("user", "Use web_search for the population of France, then halve it with the calculator.")]},
    config=run_config(8))
print("full trace:")
print_trace(result)
print("---")
print("tools used  :", tools_used(result["messages"]))
print("final answer:", final_answer(result["messages"]))'''
    return [
      header(5, "Run the Agent & Read the Trace", "Beginner", 25,
        ["Run a real agent and capture the list of messages it returns",
         "Extract which tools were called (from each AIMessage.tool_calls)",
         "Cap the loop with recursion_limit so it can never run forever"],
        "The agent loop, made visible"),
      setup(5),
      concept('''`create_agent` runs the loop for you: the model decides, tools run, results feed back &mdash; until a
final answer, or until **`recursion_limit`** stops it. The agent returns a **list of messages** (the
trace): **`AIMessage`** with **`.tool_calls`** (what it decided to run), **`ToolMessage`** (the result),
and a final `AIMessage` with **`.content`**. Here you run a real agent and read *its* trace.'''),
      code('''from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """Search for a current fact. Use for figures the model may not know."""
    return {"population of france": "68000000"}.get(query.lower().strip(), "no result")

@tool
def calculator(expression: str) -> str:
    """Do exact arithmetic, e.g. '68000000/2'."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception:
        return "error: not a numeric expression"

print("two tools ready:", web_search.name, "&", calculator.name)'''),
      buildmd('''Complete `run_config` (the loop cap the agent honors), `tools_used` (every tool call, in order), and
`final_answer` (the last message with text). You'll apply them to a **real** trace next.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Run a real compound query, then read the trace with YOUR functions: which tools fired, and the final answer."),
      code(runguard(RUN)),
      noticemd('''- **`tools_used`** reads straight off the real trace &mdash; it's your #1 debugging surface.
- **`recursion_limit`** is a one-line guardrail: even a confused agent can't loop forever.
- If the model skipped a tool or chained them differently, that's real behaviour &mdash; the trace tells you the truth.'''),
      yourturn('''Drop the cap to `run_config(2)` and re-run. **What good looks like:** on a task that needs two tool
steps, a cap of 2 can cut the agent off before it finishes &mdash; you'll see it in the trace. Raise the cap
and it completes. That's the safety/completeness trade-off you tune per task.'''),
      footer(5, "The agent's loop is now visible: tool_calls show what it did; recursion_limit is your one-line guardrail. The message trace is the truth of what happened."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-tool-routing", "Beginner",
     "Routing an Action to a Tool (safely)", 20,
     "Build the safe dispatch create_agent does internally -- look up a tool, run it, survive unknown/failing tools -- then run the real agent.",
     ["Routing", "Safe dispatch", "Real agent"])
def _l6(sol):
    DEFS = [
      SAFE_CALC, "",
      "from langchain_core.tools import tool",
      "",
      "@tool",
      "def calculator(expression: str) -> str:",
      '    """Do exact arithmetic on an expression."""',
      "    try:",
      "        return str(safe_calc(expression))",
      "    except Exception:",
      '        return "error: not a numeric expression"',
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
    ]
    EX = '''print(dispatch(REGISTRY, "calculator", "10/2"))
print(dispatch(REGISTRY, "lookup", "capital of france"))
print(dispatch(REGISTRY, "no_such_tool", "x"))    # hallucinated name -> handled, no crash'''
    RUN = '''from langchain.agents import create_agent
agent = create_agent(llm, tools=list(REGISTRY.values()))
result = agent.invoke({"messages": [("user", "What is 10 divided by 2?")]},
                      config={"recursion_limit": 6})
print_trace(result)'''
    return [
      header(6, "Routing an Action to a Tool (safely)", "Beginner", 20,
        ["Look a tool up by name in a registry and run it with .invoke()",
         "Handle an unknown tool and a failing tool without crashing",
         "Then let the real agent do the same routing over the same tools"],
        "LangChain's core building blocks"),
      setup(6),
      concept('''Once the model picks an **action name**, the framework must **route** it to the matching tool, run it
via `.invoke()`, and wrap the result as an **observation**. `create_agent` does this internally &mdash;
here you build the same safe dispatch by hand so you can debug it. Models hallucinate tool names, so
routing must fail **safely**: an unknown or failing tool returns a message, not a crash. (This is genuine
rule-based plumbing, not an LLM stand-in.)'''),
      code('''from langchain_core.tools import tool

@tool
def weather(city: str) -> str:
    """Get the current weather for a city."""
    return "sunny, 24C"

print("a tool has .name and .invoke:", weather.name, "->", weather.invoke("tokyo"))'''),
      buildmd('''Build a registry of real tools, then implement `dispatch`: find the tool, run it via `.invoke()`, and
handle the unknown/failing cases without crashing.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Now hand the same tools to a real agent and let *it* do the routing. Compare the trace to your by-hand dispatch."),
      code(runguard(RUN)),
      noticemd('''- Your `dispatch` and the agent's internal routing do the **same job**: name -> tool -> observation.
- The agent's version never crashes on a bad tool name because tools return strings &mdash; the discipline you enforced by hand.
- Splitting *deciding* (the model) from *running* (the executor) is what makes agents debuggable.'''),
      yourturn('''Add a third tool to `REGISTRY`, rebuild the agent with `list(REGISTRY.values())`, and ask a question that
routes to it. **What good looks like:** the trace shows the agent routing to your new tool by name, and an
intentionally wrong tool name (in `dispatch`) still returns a clean "unknown tool" message.'''),
      footer(6, "Routing turns a chosen action into a real observation -- safely. You built the dispatch create_agent does for you, and saw both survive a bad tool name."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-conversation-memory", "Intermediate",
     "Memory: Conversation History", 30,
     "Give the model conversation memory so a real follow-up ('is it bigger than Osaka?') resolves against earlier turns.",
     ["Memory", "Chat history", "Follow-ups"])
def _l7(sol):
    DEFS = [
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
      '    template = PromptTemplate.from_template("Conversation so far:\\n{history}\\nUser: {input}\\nAnswer concisely.")',
      {"s": '    return template.format(history=___, input=question)   # TODO: the running history',
       "a": '    return template.format(history=memory.history(), input=question)'},
    ]
    EX = '''mem = ConversationMemory()
mem.add("user", "What is the capital of France?")
mem.add("assistant", "Paris.")
print(build_prompt(mem, "Is it bigger than Osaka?"))'''
    RUN = '''mem = ConversationMemory()
q1 = "What is the capital of France?"
a1 = llm.invoke(build_prompt(mem, q1)).content
print("Q1:", q1); print("A1:", a1)
mem.add("user", q1); mem.add("assistant", a1)

q2 = "Is it bigger than Osaka?"     # 'it' only resolves via memory
a2 = llm.invoke(build_prompt(mem, q2)).content
print("Q2:", q2); print("A2:", a2)
print("---")
print("memory carried the context?", "paris" in a2.lower() or "france" in a2.lower())'''
    return [
      header(7, "Memory: Conversation History", "Intermediate", 30,
        ["Store each turn (role, text) in a memory object",
         "Format the running history the model re-reads each turn",
         "Ask a real elliptical follow-up and watch memory resolve it"],
        "Memory -- plugged in, not hand-built"),
      setup(7),
      concept('''A framework keeps **conversation memory** so follow-ups work: ask *"capital of France?"*, then
*"is it bigger than Osaka?"* &mdash; the model needs the earlier turns to resolve *"it"*. Memory is a
component you **attach**: it stores turns and re-injects the **history** into each prompt. Here you build
it and prove it with a **real** two-turn conversation. (Long-term memory is a vector store &mdash; the
bridge to RAG.)'''),
      code('''from langchain_core.messages import HumanMessage, AIMessage

# LangChain represents a turn as a message; the running list is the history:
history = [HumanMessage(content="What is the capital of France?"), AIMessage(content="Paris.")]
print("a turn:", (history[0].type, history[0].content))'''),
      buildmd('''Implement `ConversationMemory` (store + format the history) and a prompt that injects it.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Run a real two-turn conversation. The second question says *'it'* &mdash; only memory lets the model resolve it to Paris."),
      code(runguard(RUN)),
      noticemd('''- With memory, the model answers Q2 **about Paris** even though Q2 never says "Paris" &mdash; it read the history.
- Try deleting the `mem.add(...)` line after A1: the model no longer knows what *"it"* is. That's the whole value of memory.
- In a framework this is a component you attach, not a scratchpad you re-thread by hand.'''),
      yourturn('''Extend the conversation to a third turn (e.g. *"And what language do they speak there?"*) &mdash; add each
answer to `mem` and re-run. **What good looks like:** each new answer stays on-topic across turns; remove
memory and the follow-ups fall apart.'''),
      footer(7, "Memory carries context across turns so 'is it bigger than Osaka?' just works. In a framework it's a component you attach -- and you just proved it with a real model."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-langgraph-state-machine", "Intermediate",
     "LangGraph: a State Graph with Human Approval", 30,
     "Wire a REAL LangGraph StateGraph with conditional edges and a human-approval node for risky actions, then run it.",
     ["StateGraph", "Conditional edges", "Human-in-the-loop"])
def _l8(sol):
    DEFS = [
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
    ]
    EX = '''print("search      ->", route({"actions": ["search"], "path": []}))
print("send_email  ->", route({"actions": ["send_email"], "path": []}))
print("safe then risky :", run_graph(["search", "send_email", "done"]))
print("delete is gated :", run_graph(["search", "delete"]))
print("all safe        :", run_graph(["search", "search", "done"]))'''
    return [
      header(8, "LangGraph: a State Graph with Human Approval", "Intermediate", 30,
        ["Route each step to a node: tool, human-approval, or end",
         "Wire a real LangGraph StateGraph with conditional edges",
         "Run a sequence through the compiled graph and read the node path"],
        "LangGraph -- agents as state graphs"),
      setup(8),
      concept('''When one implicit loop isn't enough, **LangGraph** models the agent as a **state graph**: **nodes** are
steps, **edges** are transitions you control (deck slides 12&ndash;13). A key win is a **human approval**
node: a **risky** action (send email, delete, pay) is routed to a human before it runs, while safe actions
go straight to the tool node. Here you wire a **real** `StateGraph` and run it &mdash; the graph really
compiles and executes (no LLM needed for this one).'''),
      code('''from langgraph.graph import StateGraph, END
from typing import TypedDict

class GState(TypedDict):
    actions: list
    path: list

print("nodes we will wire: tool, human, END |", "END sentinel:", END)'''),
      buildmd('''Complete `route` (which node an action goes to) and the conditional entry point, then compile and run the
real graph. A risky step lands on the human node before anything happens.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- The path shows **`human`** appearing exactly where a risky action was &mdash; the graph *paused* for approval.
- `set_conditional_entry_point` + `add_conditional_edges` are the real LangGraph API; this graph genuinely compiled and ran.
- LangChain gets an agent running; LangGraph puts its flow under explicit control.'''),
      yourturn('''Add a new risky action name to `RISKY` (e.g. `"wire_transfer"`) and a sequence that uses it, then re-run.
**What good looks like:** your new risky action routes to `human` while safe actions go straight to `tool`.
(Advanced: add a real `llm`-backed node that decides the next action &mdash; the graph will call it.)'''),
      footer(8, "LangChain gets an agent running; LangGraph puts its flow under control -- explicit nodes, branching, and a first-class human-approval pause. Start simple; graduate when you need it."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-multi-tool", "Intermediate",
     "Multi-Tool Orchestration (day in the life)", 30,
     "Give a real agent a search tool AND a calculator and read the trace where it chains them -- then check the chain was grounded.",
     ["Tool chaining", "Orchestration", "Grounding check"])
def _l9(sol):
    DEFS = [
      SAFE_CALC, "",
      "from langchain_core.tools import tool",
      "from langchain.agents import create_agent",
      "from langchain_core.messages import ToolMessage",
      "",
      "@tool",
      "def web_search(query: str) -> str:",
      '    """Search the web for a current fact or figure. Use for population, prices, live facts."""',
      '    facts = {"population of france": "68000000"}',
      '    return facts.get(query.lower().strip(), "no result")',
      "",
      "@tool",
      "def calculator(expression: str) -> str:",
      '    """Do exact arithmetic on an expression such as 68000000/2."""',
      "    try:",
      "        return str(safe_calc(expression))",
      "    except Exception:",
      '        return "error: not a numeric expression"',
      "",
      "def build_agent():",
      {"s": '    tools = ___   # TODO: both tools, so the agent can search AND compute',
       "a": '    tools = [web_search, calculator]'},
      "    return create_agent(llm, tools)",
      "",
      "def chained_arg(messages):",
      '    """Pull (first search observation, calculator expression) out of the real trace."""',
      '    obs = next((str(m.content) for m in messages if isinstance(m, ToolMessage)), None)',
      "    expr = None",
      "    for m in messages:",
      '        for tc in (getattr(m, "tool_calls", None) or []):',
      '            if tc["name"] == "calculator":',
      '                expr = str(tc["args"].get("expression", ""))',
      "    return obs, expr",
      "",
      "def chain_is_grounded(messages):",
      "    obs, expr = chained_arg(messages)",
      {"s": '    return bool(obs and expr and ___)   # TODO: the search observation appears inside the calculator expression',
       "a": '    return bool(obs and expr and obs in expr)'},
      "",
      "agent = build_agent()",
    ]
    EX = 'print("agent nodes:", set(agent.nodes) - {"__start__"})'
    RUN = '''result = agent.invoke(
    {"messages": [("user", "Use web_search for the population of france, then use the calculator to halve it.")]},
    config={"recursion_limit": 8})
print_trace(result)
print("---")
print("data dependency:", chained_arg(result["messages"]))
print("grounded?      :", chain_is_grounded(result["messages"]))'''
    return [
      header(9, "Multi-Tool Orchestration (day in the life)", "Intermediate", 30,
        ["Give the agent TWO tools: a search and a calculator",
         "Run a real compound query and read the chained trace",
         "Check the compute step was grounded in the search result"],
        "Connecting to real tools & APIs"),
      setup(9),
      concept('''Agents earn their keep on **multi-step** tasks that **orchestrate several tools** (deck slide 16):
*"population of France, divided by 2?"* needs a **search** (a live fact) **then** a **calculator**. You
bind both tools to one agent; the agent chains them &mdash; each observation feeds the next step. After
the run you'll **check the chain was grounded**: did the calculator actually operate on the number search
returned, or hallucinate one?'''),
      code('''from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """Search the web for a current fact or figure."""
    facts = {"population of france": "68000000"}
    return facts.get(query.lower().strip(), "no result")

print("a search tool:", web_search.name, "->", web_search.invoke("population of france"))'''),
      buildmd('''Give the agent **both** tools in `build_agent`, and complete `chain_is_grounded` &mdash; the check that the
calculator step's argument was **derived from** the search result (real validation, not an LLM stand-in).'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Run the two-tool agent on a compound question, read the chained trace, and check whether it grounded the compute step in the search result."),
      code(runguard(RUN)),
      noticemd('''- A **grounded** run shows the calculator expression containing the exact number search returned (e.g. `68000000/2`).
- If `grounded?` is False, the model computed on a number it made up &mdash; a real, common failure you can now *detect* from the trace.
- Chaining search + compute in one run is exactly where an agent beats a single model call.'''),
      yourturn('''Ask a different compound question (e.g. *"population of france, times 3"*) and re-run. **What good looks
like:** the trace chains `web_search` -> `calculator`, and `chain_is_grounded` is True because the compute
used the searched figure. If it's False, read the trace to see where the model went off the rails.'''),
      footer(9, "Chaining search + compute in one run is where agents beat a single call. Same create_agent, two tools -- plus a grounding check that catches a hallucinated chain."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-external-apis", "Advanced",
     "Connect to External APIs (Google + Wolfram)", 40,
     "Wrap the REAL Google Serper and Wolfram APIs as guarded @tools, call them live, and bind them to a real agent.",
     ["External APIs", "Serper search", "Wolfram compute"])
def _l10(sol):
    DEFS = [
      "import os, urllib.parse, urllib.request",
      "from langchain_core.tools import tool",
      "from langchain_community.utilities import GoogleSerperAPIWrapper",
      "from langchain.agents import create_agent",
      "",
      "@tool",
      "def google_search(query: str) -> str:",
      '    """Search the web for a current fact or figure. Use for anything not in the model\'s own memory."""',
      '    if not os.getenv("SERPER_API_KEY"):',
      '        return "search unavailable: set SERPER_API_KEY in .env (free at serper.dev)"',
      "    try:",
      {"s": '        return ___   # TODO: GoogleSerperAPIWrapper().run(query) -- the REAL search',
       "a": '        return GoogleSerperAPIWrapper().run(query)'},
      "    except Exception as e:",
      {"s": '        return ___   # TODO: return an error STRING (never raise) -- e.g. "search error: " + type(e).__name__',
       "a": '        return "search error: " + type(e).__name__'},
      "",
      "def _wolfram_llm(query):",
      '    """Call Wolfram\'s LLM API (the endpoint recommended for agents)."""',
      '    appid = os.getenv("WOLFRAM_ALPHA_APPID")',
      '    url = "https://www.wolframalpha.com/api/v1/llm-api?appid=" + urllib.parse.quote(appid) + "&input=" + urllib.parse.quote(query)',
      '    with urllib.request.urlopen(url, timeout=20) as r:',
      '        return r.read().decode("utf-8", "replace")',
      "",
      "@tool",
      "def wolfram(query: str) -> str:",
      '    """Compute or look up an exact quantity: math, unit conversions, science facts. Use for precise computation."""',
      '    if not os.getenv("WOLFRAM_ALPHA_APPID"):',
      '        return "compute unavailable: set WOLFRAM_ALPHA_APPID in .env (developer.wolframalpha.com)"',
      "    try:",
      '        return _wolfram_llm(query)[:400]',
      "    except Exception as e:",
      '        return "compute error: " + type(e).__name__',
      "",
      "def build_agent():",
      {"s": '    return create_agent(llm, ___)   # TODO: bind both real external tools',
       "a": '    return create_agent(llm, [google_search, wolfram])'},
    ]
    EX = '''# Direct sanity calls -- these hit the REAL APIs (guarded):
print("google_search ->", google_search.invoke("population of France")[:120])
print("wolfram       ->", wolfram.invoke("2400 * 2")[:120])'''
    RUN = '''agent = build_agent()
result = agent.invoke(
    {"messages": [("user", "Search for the height of the Eiffel Tower in metres, then use wolfram to convert it to feet.")]},
    config={"recursion_limit": 8})
print_trace(result)'''
    return [
      header(10, "Connect to External APIs (Google + Wolfram)", "Advanced", 40,
        ["Wrap the REAL Google Serper search API as a @tool",
         "Wrap the REAL Wolfram Alpha compute API as a @tool",
         "Guard every call so a missing key or API error returns a string, not a crash"],
        "Connecting to real tools & APIs"),
      setup(10),
      concept('''Real agents reach the world through **tool integrations** (deck slide 16): **Google Search** (via
[serper.dev](https://serper.dev)) for live facts beyond the training cutoff, **Wolfram Alpha** for exact
computation. The pattern is always: get a key &rarr; wrap the service as a `@tool` &rarr; add it to the
tools list. But **real APIs fail** &mdash; rate limits, timeouts, bad queries, missing keys &mdash; so a
production tool must **guard the call and return a string** instead of crashing the whole agent. Your keys
are loaded from `.env`; if one is missing the tool prints guidance and the run still completes.'''),
      code('''import os
print("SERPER_API_KEY set :", bool(os.getenv("SERPER_API_KEY")))
print("WOLFRAM_ALPHA_APPID set :", bool(os.getenv("WOLFRAM_ALPHA_APPID")))
# Note: this WOLFRAM key is a Short-Answers / LLM-API key -- we call Wolfram's LLM API endpoint,
# the one Wolfram recommends for agents (the langchain_community v2/query wrapper needs a different app type).'''),
      buildmd('''Wrap the two real APIs as guarded `@tool`s (fill the API call + the error-string fallback), then bind both
to a real agent with `create_agent`.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Bind both real tools to an agent and ask a question that needs a live search and an exact compute. The trace shows real external API calls."),
      code(runguard(RUN)),
      noticemd('''- The **direct** `google_search.invoke(...)` / `wolfram.invoke(...)` calls above returned **live** data &mdash; real network, real keys.
- Every call is **guarded**: a missing key or an API error returns a string, so the agent survives. Delete a key from `.env` and the tool prints guidance instead of crashing.
- This is the client's Day-3 "connect agents to Google Search + Wolfram Alpha" lab, for real.'''),
      yourturn('''Ask a question that needs only search, then one that needs only compute, then one that needs both, and
compare the traces. **What good looks like:** the agent calls `google_search` for live facts and `wolfram`
for exact math, and a temporarily-broken key (rename it in `.env`) yields a graceful "unavailable" string
rather than a stack trace.'''),
      footer(10, "Get a key -> wrap the service as a guarded @tool -> add it to the list. That is how an agent reaches live Google facts and exact Wolfram computation -- the client's Day-3 external-API lab, for real."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-guardrails-observability", "Advanced",
     "Guardrails & Observability", 35,
     "Learn why a tool must never raise, then attach a REAL LangChain callback to a real agent run and read every tool event.",
     ["Tools never raise", "Callbacks", "Allow-list"])
def _l11(sol):
    DEFS = [
      SAFE_CALC, "",
      "from langchain_core.tools import tool",
      "from langchain_core.callbacks import BaseCallbackHandler",
      "",
      "@tool",
      "def calculator(expression: str) -> str:",
      '    """Do exact arithmetic on an expression such as 10/2."""',
      {"s": '    ___   # TODO: try safe_calc(expression) and return str(...); on Exception return an error STRING (never raise)',
       "a": '    try:\n        return str(safe_calc(expression))\n    except Exception:\n        return "error: not a numeric expression"'},
      "",
      'ALLOWED = {"calculator", "lookup"}',
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
      "class TraceHandler(BaseCallbackHandler):",
      '    """A REAL LangChain callback: LangChain calls these methods on every tool event."""',
      "    def __init__(self):",
      "        self.events = []",
      "    def on_tool_end(self, output, **kw):",
      {"s": '        self.events.append(___)   # TODO: record ("tool_end", str(output)[:80])',
       "a": '        self.events.append(("tool_end", str(output)[:80]))'},
    ]
    EX = '''print("safe calculator(10/0):", calculator.invoke("10/0"))   # returns a string, no crash
print("is_allowed(calculator):", is_allowed("calculator"), "| is_allowed(delete_db):", is_allowed("delete_db"))
print("validate('2+2'):", validate("2+2"), "| validate('__import__'):", validate("__import__"))'''
    RUN = '''from langchain.agents import create_agent
handler = TraceHandler()
agent = create_agent(llm, tools=[calculator])
result = agent.invoke({"messages": [("user", "What is 144 divided by 12?")]},
                      config={"recursion_limit": 6, "callbacks": [handler]})
print("final:", result["messages"][-1].content)
print("callback captured tool events:")
for e in handler.events:
    print("  ", e)'''
    return [
      header(11, "Guardrails & Observability", "Advanced", 35,
        ["See why a raising tool aborts the whole agent run -- and fix it",
         "Allow-list the tools the agent may call + validate input",
         "Attach a REAL BaseCallbackHandler and read every tool event from a live run"],
        "Observability & debugging"),
      setup(11),
      concept('''Autonomy needs **guardrails** and **observability** (deck slides 15, 17). Two lessons here, both real:
**(1) A tool must never raise.** If a `@tool` throws on a bad argument, the exception can abort the entire
agent run &mdash; so tools **catch and return a string**. **(2) Observe everything.** LangChain exposes a
real **`BaseCallbackHandler`**; attach one and it fires on every tool start/end so you can trace and audit
(LangSmith / Langfuse capture full runs this way). You also keep a deterministic **allow-list** + input
**validation**.'''),
      code('''from langchain_core.tools import tool

# The WRONG way: this tool raises on bad input.
@tool
def unsafe_divide(expr: str) -> str:
    """Divide two numbers like '10/2'. (Unsafe demo -- raises on bad input!)"""
    a, b = expr.split("/")
    return str(int(a) / int(b))     # ZeroDivisionError / ValueError propagate -> can abort the agent

print("ok  :", unsafe_divide.invoke("10/2"))
try:
    print(unsafe_divide.invoke("10/0"))
except Exception as e:
    print("raised:", type(e).__name__, "-- inside an agent this can abort the whole run")'''),
      buildmd('''Write the **safe** version of the tool (catch + return a string), the allow-list check, the validator,
and a **real** callback handler that records each tool result.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Attach your REAL callback to a real agent run via `config={'callbacks': [...]}` and read the tool events it captured."),
      code(runguard(RUN)),
      noticemd('''- The safe `calculator` returned a **string** for `10/0` &mdash; inside the live run that's the difference between a recoverable step and an aborted agent.
- Your `TraceHandler` is a **real** `BaseCallbackHandler`; LangChain called `on_tool_end` for you on every tool result. That's the same hook LangSmith / Langfuse use.
- Allow-list + validation + `recursion_limit` + a callback = an agent you can trust and audit.'''),
      yourturn('''Bind the **unsafe** tool (`unsafe_divide`) to the agent instead and ask *"What is 10 divided by 0?"* &mdash;
watch how a raising tool derails the run. Then switch back to the safe `calculator`. Add an
`on_tool_start(self, serialized, input_str, **kw)` method to your handler to log inputs too. **What good
looks like:** the safe agent recovers and answers; your callback logs every tool start and end.'''),
      footer(11, "Tools that return strings (never raise) + allow-list + validation + a real callback turn an autonomous agent from a liability into something you can trust and debug. Day 5 goes deeper."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-langchain-agent", "Advanced",
     "Capstone: A Guardrailed LangChain Agent", 45,
     "Assemble allow-listed tools + a system prompt + a recursion cap into a real create_agent, and run it over a task suite.",
     ["End-to-end agent", "Guardrails", "Real suite"])
def _l12(sol):
    DEFS = [
      SAFE_CALC, "",
      "from langchain_core.tools import tool",
      "from langchain_core.callbacks import BaseCallbackHandler",
      "from langchain.agents import create_agent",
      "",
      "@tool",
      "def lookup(key: str) -> str:",
      '    """Look up a known fact by key, e.g. \'capital of france\'."""',
      '    facts = {"population of metropolis": "120000", "capital of france": "Paris"}',
      '    return facts.get(key.lower().strip(), "unknown")',
      "",
      "@tool",
      "def calculator(expression: str) -> str:",
      '    """Do exact arithmetic on an expression such as 120000/2."""',
      "    try:",
      "        return str(safe_calc(expression))",
      "    except Exception:",
      '        return "error: not a numeric expression"',
      "",
      'ALLOWED = {"lookup", "calculator"}',
      'SYSTEM = "You are a careful assistant. Use the tools for facts and math; never guess a number."',
      "",
      "class TraceHandler(BaseCallbackHandler):",
      "    def __init__(self): self.events = []",
      "    def on_tool_end(self, output, **kw): self.events.append(str(output)[:60])",
      "",
      "def vet_tools(tools):",
      {"s": '    return [t for t in tools if ___]   # TODO: keep only allow-listed tools (guardrail)',
       "a": '    return [t for t in tools if t.name in ALLOWED]'},
      "",
      "def build_agent():",
      "    tools = vet_tools([lookup, calculator])",
      {"s": '    return create_agent(llm, tools, system_prompt=___)   # TODO: pass the system prompt',
       "a": '    return create_agent(llm, tools, system_prompt=SYSTEM)'},
      "",
      "def run_config(max_steps=8, handler=None):",
      {"s": '    cfg = ___   # TODO: {"recursion_limit": max_steps} -- cap the loop',
       "a": '    cfg = {"recursion_limit": max_steps}'},
      "    if handler is not None:",
      '        cfg["callbacks"] = [handler]',
      "    return cfg",
    ]
    EX = '''agent = build_agent()
print("agent type :", type(agent).__name__)
print("bound tools:", [t.name for t in vet_tools([lookup, calculator])])
print("dropped a fake risky tool?:", "delete_db" not in [t.name for t in vet_tools([lookup, calculator])])'''
    RUN = '''SUITE = [
    "What is the capital of France?",
    "What is the population of metropolis, divided by 2?",
    "What is 15 times 3?",
]
for q in SUITE:
    handler = TraceHandler()
    result = agent.invoke({"messages": [("user", q)]}, config=run_config(8, handler))
    print("Q:", q)
    print("  final :", result["messages"][-1].content)
    print("  tools :", handler.events)
    print()
print("That was a REAL guardrailed LangChain agent over a suite. Next: Day 4 -- task automation & multi-agent teams.")'''
    return [
      header(12, "Capstone: A Guardrailed LangChain Agent", "Advanced", 45,
        ["Vet tools against an allow-list before binding them",
         "Assemble a real create_agent with a system prompt + recursion cap",
         "Run the guardrailed agent over a suite of real tasks and read the traces"],
        "Choosing a framework"),
      setup(12),
      concept('''Capstone &mdash; a real **synthesis** of the module. You compose the pieces into one guarded agent: an
**allow-list** so only vetted tools are bound, a **system prompt** that sets the agent's policy, a
**`recursion_limit`** cap so the loop can never run away, and a **tracing callback** (Lab 11) so every
step is recorded. Then you run it **for real** over a small task suite &mdash; the bridge to Day 4.'''),
      code('''from langchain_core.tools import tool

@tool
def lookup(key: str) -> str:
    """Look up a known fact by key, e.g. 'capital of france'."""
    return {"population of metropolis": "120000", "capital of france": "Paris"}.get(key.lower().strip(), "unknown")

print("a vetted tool:", lookup.name)'''),
      buildmd('''Complete `vet_tools` (the allow-list guardrail), `build_agent` (the real `create_agent` with a system
prompt), and `run_config` (the recursion cap).'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Run the guardrailed agent over a real task suite. Each item is a fresh real agent run; the callback records every tool observation."),
      code(runguard(RUN)),
      noticemd('''- The agent is a real **`CompiledStateGraph`** built from **vetted** tools only &mdash; a fake `delete_db` tool never gets bound.
- The **system prompt** shapes behaviour ("never guess a number"); the **recursion cap** bounds the loop; the **callback** records every tool result.
- Across the suite you can see which tasks needed tools and which the model answered directly &mdash; all from real traces.'''),
      yourturn('''Add your own tool (respecting the allow-list &mdash; add its name to `ALLOWED`), extend `SUITE` with a task
that needs it, and re-run. **What good looks like:** your new tool is vetted in, the agent calls it on the
right task, the recursion cap holds, and the callback logs every step. That's a shippable, guardrailed
agent &mdash; the foundation for Day 4.'''),
      footer(12, "You assembled a guardrailed LangChain agent -- vetted tools, a system prompt, create_agent and a recursion cap -- and ran it over a real suite. That is a shippable agent; next, Day 4 puts agents to work."),
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
