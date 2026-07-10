# -*- coding: utf-8 -*-
# Generator for the Module-6 BONUS lab (uncounted): AutoGPT-style autonomy vs LangGraph control.
# This is NOT part of the 12 counted labs -- gen_labs.py/regenerate.sh do not touch it, and it is
# not listed in _meta.json / index.html. Re-run this file by hand to regenerate the bonus notebook:
#     python3 _generators/gen_bonus.py
#
# Design note: both sides run on the SAME model -- Groq openai/gpt-oss-20b -- so the ONLY variable
# is STRUCTURE (an unbounded self-prompting loop vs a bounded create_agent). Groq gpt-oss-20b has
# reliable tool-calling; the local llama3.1:8b does NOT emit structured tool_calls consistently for a
# compound goal, which would make the LangGraph side look worse than the naive loop and invert the
# lesson. Near-real: real model drives both runs, no auto-grader; unfilled ___ blanks print a note.
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)                       # hands-on/module-6
REPO = os.path.abspath(os.path.join(MOD, "..", ".."))
SLUG = "lab-13-bonus-autogpt-vs-langgraph"

# This bonus is a FILLED, runnable demo (not a graded build-it lab), so there is no student/solution
# split: B always returns the working answer. (Rationale: in a Jupyter kernel `___` is bound to a
# recent cell output, not undefined -- so a blanked "self-prompting loop" silently runs on garbage
# instead of printing a clean note. A runnable demo + the "Your turn" edits is the better fit here.)
def B(student, answer, sol):
    return answer

def md(s):  return {"cell_type": "markdown", "metadata": {}, "source": s}
def code(s): return {"cell_type": "code", "metadata": {}, "outputs": [], "execution_count": None, "source": s}

def cells(sol):
    return [
    md(
"# Lab 6.13 (Bonus) &mdash; AutoGPT-style autonomy vs LangGraph control\n"
"\n"
"**Level:** Bonus / Advanced &nbsp;|&nbsp; **Est. time:** ~30 min &nbsp;|&nbsp; "
"**Day 3 &middot; Module 6 &mdash; Frameworks for Building AI Agents**\n"
"\n"
"> This bonus is the **hands-on for the two slides** *AutoGPT architecture* and "
"*AutoGPT vs LangGraph*. It is **not** one of the 12 graded labs &mdash; it is a **runnable "
"demo** (already filled in): run it top to bottom, read the two traces, then do the **Your turn** "
"edits so the lesson is felt, not just told.\n"
"\n"
"### What you'll do\n"
"- Run a **minimal AutoGPT-style self-prompting loop** &mdash; one LLM, a fixed THOUGHT/COMMAND "
"schema, tools, and a while-loop.\n"
"- Run the **same goal** through a **bounded LangGraph agent** (`create_agent` + `recursion_limit`).\n"
"- **Read the two real traces** and see the difference &mdash; not *which is smarter* "
"(same goal, same tools) but **who authors the flow and what enforces the bounds**."),

    md(
"## Concept &mdash; two ways to run the loop\n"
"\n"
"**AutoGPT** is *one LLM wrapped in a self-prompting loop*: it forces the model to emit a "
"`THOUGHT` and a single `COMMAND` each turn, runs that command as a tool, feeds the result back, "
"and repeats &mdash; **by default with no human and no fixed stop**. The structure lives in a "
"**prompt + a while-loop**.\n"
"\n"
"**LangGraph / `create_agent`** is the opposite: **you** author the flow and the bounds "
"(`recursion_limit`, which tools are bound, where a human approves).\n"
"\n"
"We give **both** the same tools and the same goal &mdash; *add up four quarterly figures, then "
"save a one-line report* &mdash; so what differs is **structure**.\n"
"\n"
"> **Heads-up on models &mdash; this pairing *is* part of the lesson.** The AutoGPT **text loop** "
"needs a model that follows a plain-text protocol: we use the local **`llama3.1:8b`**. The "
"LangGraph agent needs a **tool-calling** model: we use Groq **`gpt-oss-20b`**. Swap them and each "
"fumbles the other's job (gpt-oss-20b *refuses* the raw text protocol; llama3.1:8b fumbles "
"structured tool-calls on a compound goal). **Tool-calling models + graphs are exactly what "
"replaced text-loop AutoGPT** &mdash; the paradigm and the model co-evolved."),

    # ---- setup ----
    code(
'# Setup -- run me first\n'
'import os, socket, ast, operator, pathlib\n'
'from dotenv import load_dotenv\n'
f'load_dotenv(pathlib.Path("{REPO}/.env"))   # GROQ_API_KEY for Part B (Groq is the Day 4-5 provider)\n'
'\n'
'WORK = "/tmp/biaa-lab-06-13"\n'
'os.makedirs(WORK, exist_ok=True)\n'
'\n'
'def ollama_up(host="127.0.0.1", port=11434):\n'
'    """True if a local Ollama server is listening. If down, start:  ollama run llama3.1:8b"""\n'
'    try:\n'
'        with socket.create_connection((host, port), timeout=1):\n'
'            return True\n'
'    except OSError:\n'
'        return False\n'
'\n'
'def groq_ready():\n'
'    """True if a Groq API key is available (free at console.groq.com; put it in .env)."""\n'
'    return bool(os.getenv("GROQ_API_KEY"))\n'
'\n'
'from langchain_ollama import ChatOllama\n'
'from langchain_groq import ChatGroq\n'
'# Each paradigm on the model it was built for (see the note above):\n'
'#   Part A (AutoGPT text loop)  -> local text model. Pin 127.0.0.1 -- "localhost" can misroute.\n'
'#   Part B (LangGraph agent)    -> Groq tool-calling model.\n'
'llm_local = ChatOllama(model="llama3.1:8b", temperature=0, base_url="http://127.0.0.1:11434")\n'
'llm_groq  = ChatGroq(model="openai/gpt-oss-20b", temperature=0)\n'
'\n'
'# One AST-safe calculator, shared by both approaches (never bare eval).\n'
'_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,\n'
'        ast.Div: operator.truediv, ast.USub: operator.neg, ast.Pow: operator.pow}\n'
'def _ev(node):\n'
'    if isinstance(node, ast.Constant): return node.value\n'
'    if isinstance(node, ast.BinOp):    return _OPS[type(node.op)](_ev(node.left), _ev(node.right))\n'
'    if isinstance(node, ast.UnaryOp):  return _OPS[type(node.op)](_ev(node.operand))\n'
'    raise ValueError("unsupported expression")\n'
'def calc(expr):\n'
'    return _ev(ast.parse(expr, mode="eval").body)\n'
'\n'
'GOAL = ("Add up the 2023 quarterly revenue Q1=120, Q2=135, Q3=150, Q4=160 (in $M), "\n'
'        "then save a one-line report of the total.")\n'
'\n'
'print("Ollama up:", ollama_up(), "(Part A) | Groq key:", groq_ready(), "(Part B) | WORK:", WORK)\n'
'if not ollama_up(): print("  Part A needs Ollama:  ollama run llama3.1:8b")\n'
'if not groq_ready(): print("  Part B needs GROQ_API_KEY in .env")'),

    # ---- Part A: AutoGPT-style from scratch ----
    md(
"## Part A &mdash; the AutoGPT pattern, from scratch\n"
"\n"
"A self-prompting loop: each turn we ask the model for a `THOUGHT` and one `COMMAND`, run the "
"command, and feed the observation back. Real AutoGPT has **no step cap** &mdash; we add a small "
"`MAX_STEPS` only so the notebook ends. Driven by the local **`llama3.1:8b`**, which follows the "
"text protocol well.\n"
"\n"
"Read the two helpers &mdash; `parse_autogpt` pulls the `COMMAND` line out of the reply, "
"`run_command` dispatches it to a tool &mdash; then run the loop."),

    code(
'AUTOGPT_SYS = (\n'
'    "You are an autonomous agent. Available commands:\\n"\n'
'    "  calculator: <arithmetic expression>\\n"\n'
'    "  save_report: <one line of text>\\n"\n'
'    "  finish: <final answer>\\n"\n'
'    "Each turn reply EXACTLY as:\\nTHOUGHT: <reasoning>\\nCOMMAND: <one command from the list>"\n'
')\n'
'\n'
'def parse_autogpt(raw):\n'
'    """Pull the THOUGHT and the single COMMAND line out of the model\'s reply."""\n'
'    thought, command = "", ""\n'
'    for line in raw.splitlines():\n'
'        u = line.strip().upper()\n'
'        if u.startswith("THOUGHT:"):\n'
'            thought = line.split(":", 1)[1].strip()\n'
'        elif u.startswith("COMMAND:"):\n'
'            command = ' + B('___   # TODO: the text after "COMMAND:"  (line.split(":", 1)[1].strip())',
                             'line.split(":", 1)[1].strip()', sol) + '\n'
'    return thought, command\n'
'\n'
'def run_command(command):\n'
'    """Dispatch one COMMAND to a tool. A tool must NEVER raise -- that would abort the loop."""\n'
'    try:\n'
'        name, _, arg = command.partition(":")\n'
'        name, arg = name.strip().lower(), arg.strip()\n'
'        if name == "calculator":\n'
'            return f"{arg} = {calc(arg)}"\n'
'        if name == "save_report":\n'
'            open(os.path.join(WORK, "report.txt"), "w").write(arg)\n'
'            return f"saved to {os.path.join(WORK, \'report.txt\')}"\n'
'        return f"unknown command: {name}"\n'
'    except Exception as e:\n'
'        return f"error: {e}"\n'
'\n'
'print("helpers ready")'),

    code(
'# Run the AutoGPT-style loop for real (local llama3.1:8b).\n'
'if not ollama_up():\n'
'    print("Ollama not reachable -- start `ollama run llama3.1:8b`, then re-run this cell.")\n'
'else:\n'
'  try:\n'
'    MAX_STEPS = 8          # AutoGPT has NO cap by default; we add one so the notebook ends\n'
'    history = f"GOAL: {GOAL}\\n"\n'
'    finished = False\n'
'    for step in range(1, MAX_STEPS + 1):\n'
'        raw = llm_local.invoke(AUTOGPT_SYS + "\\n\\n" + history + "\\nYour move:").content\n'
'        thought, command = parse_autogpt(raw)\n'
'        print(f"[step {step}] THOUGHT: {thought[:80]}")\n'
'        print(f"[step {step}] COMMAND: {command[:80]}")\n'
'        if command.strip().lower().startswith("finish"):\n'
'            print("  -> model called finish. DONE.\\n"); finished = True; break\n'
'        obs = run_command(command)\n'
'        print(f"  OBS: {obs[:120]}")\n'
'        history += ' + B('___   # TODO: feed the step back -> f"\\nSTEP {step}: {command}\\nOBSERVATION: {obs}\\n"',
                          'f"\\nSTEP {step}: {command}\\nOBSERVATION: {obs}\\n"', sol) + '\n'
'    if not finished:\n'
'        print("  -> hit MAX_STEPS without a clean finish -- the classic unbounded-loop failure.")\n'
'  except Exception as e:\n'
'    print("Run error:", type(e).__name__, e)'),

    md(
"**Read your trace.** It probably reached the answer &mdash; the model is capable. But notice what "
"nothing enforced: **you** had to bolt on `MAX_STEPS` (nothing else stops it), and the model could "
"name **any** command &mdash; the loop just dispatches whatever text it emits. Run the next cell to "
"see that plainly."),

    code(
'# The loop dispatches whatever command the model NAMES. It is safe here only because we never\n'
'# implemented a dangerous command -- nothing in the loop *restricts* what may run.\n'
'print(run_command("delete: /tmp/important-file"))   # -> "unknown command: delete"\n'
'print("Safety here = your dispatch code. A real AutoGPT with a shell/file tool would run it.")'),

    # ---- Part B: LangGraph bounded ----
    md(
"## Part B &mdash; the same goal, bounded with LangGraph\n"
"\n"
"Now hand the **same goal and tools** to `create_agent` (a LangGraph agent), driven by Groq "
"**`gpt-oss-20b`** (a tool-calling model). You **bind** exactly the tools it may use and cap the "
"loop with `recursion_limit` &mdash; so misbehaviour isn't *trusted away*, it's made "
"**impossible**. Run it and read the real message trace."),

    code(
'from langchain_core.tools import tool\n'
'from langchain.agents import create_agent\n'
'\n'
'@tool\n'
'def calculator(expression: str) -> str:\n'
'    """Compute a basic arithmetic expression like \'120+135\' and return the result."""\n'
'    try:\n'
'        return f"{expression} = {calc(expression)}"\n'
'    except Exception as e:\n'
'        return f"error: {e}"\n'
'\n'
'@tool\n'
'def save_report(text: str) -> str:\n'
'    """Save a one-line report string to the working directory; returns the file path."""\n'
'    try:\n'
'        open(os.path.join(WORK, "report.txt"), "w").write(text)\n'
'        return f"saved to {os.path.join(WORK, \'report.txt\')}"\n'
'    except Exception as e:\n'
'        return f"error: {e}"\n'
'\n'
'def print_trace(result):\n'
'    """Print the REAL agent message trace: tool calls, observations, final answer."""\n'
'    for m in result["messages"]:\n'
'        for tc in (getattr(m, "tool_calls", None) or []):\n'
'            print("TOOL CALL:", tc["name"], tc["args"])\n'
'        if type(m).__name__ == "ToolMessage":\n'
'            print("OBS:", str(m.content)[:160])\n'
'        elif str(getattr(m, "content", "")).strip():\n'
'            print(type(m).__name__, ":", str(m.content)[:240])\n'
'\n'
'print("tools defined: calculator, save_report")'),

    code(
'# Build the bounded agent and run it for real (Groq gpt-oss-20b).\n'
'if not groq_ready():\n'
'    print("No GROQ_API_KEY -- set it in .env, then re-run this cell.")\n'
'else:\n'
'    try:\n'
'        agent = create_agent(llm_groq, tools=[calculator, save_report])   # bind ONLY these tools (least privilege)\n'
'        cfg = {"recursion_limit": 8}                                      # cap the loop\n'
'        result = agent.invoke({"messages": [("user", GOAL)]}, cfg)\n'
'        print_trace(result)\n'
'    except Exception as e:\n'
'        print("Run error:", type(e).__name__, e)'),

    md(
"## Compare\n"
"\n"
"Both reach **$565M** on the same goal &amp; tools. The difference isn't IQ, it's **control**:\n"
"\n"
"| | AutoGPT-style loop (Part A) | LangGraph agent (Part B) |\n"
"|---|---|---|\n"
"| Who authored the flow | the **model**, at run time | **you**, up front |\n"
"| What bounds the loop | only the `MAX_STEPS` you bolted on | `recursion_limit`, a first-class cap |\n"
"| Tools it *may* call | any it names in text (you hope your dispatch is safe) | only the tools you **bound** &mdash; others are impossible |\n"
"| When it stops | when the model *says* `finish` | when the graph reaches `END` |\n"
"| Failure at scale | drift, repeats, runaway cost | predictable &mdash; you see &amp; steer each node |\n"
"\n"
"On a toy task the unbounded loop is fine. At real scale, *trusting the model to behave* is where "
"drift, cost and runaway loops live (Module 10) &mdash; which is why your **capstone is a bounded, "
"guardrailed graph**, not an unleashed AutoGPT. *You earn autonomy with structure.*\n"
"\n"
"### Your turn\n"
"- Raise `MAX_STEPS` to 20 in Part A, and delete the `finish` line from `AUTOGPT_SYS` &mdash; now "
"nothing tells it to stop. Watch it burn every step.\n"
"- Add a `delete` branch to `run_command` and put `delete: ...` in reach &mdash; the loop will run "
"it. The LangGraph agent **can't**: there's no such tool bound (least privilege).\n"
"- Add a human-approval step to Part B's flow (see Lab 6.8, the LangGraph state machine)."),
    ]

def notebook(sol):
    cs = cells(sol)
    for i, c in enumerate(cs):
        c["id"] = f"cell{i:02d}"
    return {
        "cells": cs,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.x"},
        },
        "nbformat": 4, "nbformat_minor": 5,
    }

def write(path, sol):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(notebook(sol), f, indent=1, ensure_ascii=False)

# A single FILLED, runnable demo notebook at the module root (no student/solution split).
write(os.path.join(MOD, f"{SLUG}.ipynb"), sol=True)
# Remove any stale solution copy from an earlier iteration.
_stale = os.path.join(MOD, "solutions", f"{SLUG}.ipynb")
if os.path.exists(_stale):
    os.remove(_stale)
print("wrote", f"{SLUG}.ipynb", "(filled runnable demo; no solutions copy)")
