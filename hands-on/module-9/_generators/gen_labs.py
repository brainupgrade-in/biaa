# -*- coding: utf-8 -*-
"""Generator for Day 5 Module 9 hands-on labs (12 notebooks) -- NEAR-REAL design.
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

Design: this is the "Agents in Finance, Healthcare & Cybersecurity" module -- the labs build the
FINANCIAL-REPORT INSIGHT AGENT (the client's Lab 5.1) piece by piece, exactly as the deck teaches:
ground -> reason -> structure+cite -> guardrail -> human. The labs are NEAR-REAL, not stubs: the
insight agent is a REAL `create_agent` driven by a REAL hosted model (`ChatGroq("openai/gpt-oss-20b")`,
key in the repo .env as GROQ_API_KEY), over REAL read-only `@tool`s, and the student reads the REAL
message trace where the agent grounds & cites a figure. There is NO auto-grader -- each lab ends with
"Build it -> Run it -> read the output/trace -> Your turn (open task)".

Kept real & deterministic (NOT LLM stand-ins): the grounding/citation logic, the AST-safe calculator
(wrapped in try/except -- financial math, never bare eval), anomaly flags, the no-advice guardrail, the
withheld-tool guardrail (`place_trade` is defined but never bound), grounding validation, the audit
trail, and privacy minimize/redact. Those stay real. Removed vs the old design: the mock/recorded
determinism and the expect/expect_true/Score auto-grader.

INFORMATIONAL ONLY: the agent grounds & cites every figure, gives NO investment advice, and has NO
trade tool -- a human analyst decides.

Student robustness (no grader): the cells that EXERCISE the blanks are wrapped by guard()/runguard()
so an unfilled `___` prints a friendly note instead of crashing, and the live Groq cells self-skip
cleanly when GROQ_API_KEY is unset -- so a student notebook runs top-to-bottom either way."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day5-module9-agents-in-industry.html"
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
            '    print("No GROQ_API_KEY -- add it to .env (free at console.groq.com), then re-run this cell.")\n'
            'else:\n'
            '    try:\n' + _indent(exercise, 8) +
            '\n    except Exception as e:\n        print("(Rate-limited on the free tier? wait a few seconds. Or fill the ___ blanks, then re-run.)", type(e).__name__)')

def setup(nn):
    return code(f'''# Setup -- run me first
import os, pathlib
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True), override=True)   # GROQ_API_KEY (the Day-5 provider)

WORK = "/tmp/biaa-lab-09-{nn:02d}"
os.makedirs(WORK, exist_ok=True)

def groq_ready():
    """True if a GROQ_API_KEY is set. Day-5 labs call a REAL hosted model (Groq)."""
    return bool(os.environ.get("GROQ_API_KEY"))

from langchain_groq import ChatGroq
# Day-5 provider: a REAL hosted model. openai/gpt-oss-20b is a reliable tool-caller via create_agent.
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
    print("GROQ_API_KEY set | model: openai/gpt-oss-20b | WORK:", WORK)
else:
    print("GROQ_API_KEY NOT set -- add it to .env (free at console.groq.com).")
    print("(The 'Run it for real' cells will print this note instead of crashing.)  WORK:", WORK)''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 9.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 5 &middot; Module 9 &mdash; Agents in Finance, Healthcare &amp; Cybersecurity**

### What you'll do
{g}

> **How this lab works (near-real):** read the **Concept**, fill the real `___` blanks in **Build it** (the real grounding / citation / compute logic, or the real `create_agent` wiring), then **Run it** and read the output &mdash; and, for the agent labs, the real **message trace**. Finish with an open **Your turn**. There is **no auto-grader**; the goal is a working, grounded insight agent you can read.

> **Framework note:** these labs use the **real** LangChain 1.x (`langchain`, `langchain-core`, `langchain-groq`). The insight agent is a **real** `create_agent` driven by a **real hosted model** (`ChatGroq("openai/gpt-oss-20b")`, key in `.env` as `GROQ_API_KEY`). You are building the **financial-report insight agent** &mdash; the client's Lab 5.1. It is **informational only**: it grounds &amp; **cites** every figure, gives **no advice**, and has **no trade tool** (`place_trade` is defined but never bound &mdash; a human analyst decides). A `@tool` must **catch its own errors and return a string** &mdash; a tool that raises can abort the whole run. If `GROQ_API_KEY` is unset, the run cells print how to set it instead of crashing.

**Reference:** [Module 9 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 9 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 9 labs](./index.html) &nbsp;&middot;&nbsp; [Module 9 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def concept(text):   return md("## Concept\n" + text)
def buildmd(text):   return md("## Build it\n" + text)
def observemd(text): return md("## Run it &amp; observe\n" + text)
def runmd(text):     return md("## Run it for real &amp; read the trace\n" + text + "\n\n_This calls the real `openai/gpt-oss-20b` via Groq. If `GROQ_API_KEY` is unset the cell prints how to set it instead of crashing. On the free tier, if you hit a rate limit wait a few seconds and re-run._")
def noticemd(text):  return md("## What to notice\n" + text)
def yourturn(text):  return md("## Your turn (open task &mdash; no grader)\n" + text)

def sol_answer(sol, code_text):
    """Solution-only worked reference for the open 'Your turn' task above (empty in the student notebook)."""
    if not sol:
        return []
    return [code("# --- Reference answer (ONE good way to do the 'Your turn' task -- compare with your own) ---\n" + code_text)]

def realcell(parts, demo):
    """A code cell = real-library imports/fixtures + a runnable demo."""
    return code("\n\n".join(parts) + "\n\n" + demo)

# AST-based safe arithmetic -- never bare eval() on free text (this is financial math). Tools wrap it in try/except.
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

TOOL_IMPORT = "from langchain_core.tools import tool"

# The financial report fixture -- every figure carries its SOURCE (for grounding & citation).
REPORT_FIXTURE = '''# A small financial report -- each figure carries its SOURCE, so every claim can be cited.
REPORT = {
    "revenue":    {"value": 120.0, "unit": "M", "source": "p4, income stmt"},
    "net_income": {"value": 9.0,   "unit": "M", "source": "p4, income stmt"},
    "total_debt": {"value": 40.0,  "unit": "M", "source": "p7, balance sheet"},
}
PRIOR = {"revenue": 107.1, "net_income": 9.7, "total_debt": 25.0}   # prior period, for YoY'''

NB = {}
def lab(nn, slug, level, title, mins, summary, concepts):
    def deco(fn):
        NB[nn] = dict(slug=slug, level=level, title=title, mins=mins,
                      summary=summary, concepts=concepts, build=fn)
        return fn
    return deco

# ============================================================ LAB 01
@lab(1, "lab-01-ground-a-figure", "Beginner",
     "Ground a Figure (Extract + Cite)", 20,
     "Extract a figure AND its source from a report -- the grounding discipline: never reason from memory.",
     ["Grounding", "Citation", "Source of truth"])
def _l1(sol):
    DEFS = [
      REPORT_FIXTURE, "",
      "def extract_figure(name, report):",
      '    # return the figure dict {value, source} from the report, or None if it is not there',
      {"s": '    return ___   # TODO: look up name in report (None if missing)',
       "a": '    return report.get(name)'},
      "",
      "def is_grounded(fig):",
      '    # grounded = the figure exists AND carries a non-empty source citation',
      {"s": '    return fig is not None and ___   # TODO: it has a truthy "source"',
       "a": '    return fig is not None and bool(fig.get("source"))'},
    ]
    EX = '''rev = extract_figure("revenue", REPORT)
print("revenue :", rev)
print("grounded:", is_grounded(rev))
print("missing :", extract_figure("ebitda", REPORT))
print("no-source grounded?", is_grounded({"value": 5.0}))'''
    return [
      header(1, "Ground a Figure (Extract + Cite)", "Beginner", 20,
        ["Extract a reported figure together with its source",
         "Check a figure is grounded -- it carries a citation",
         "See why a figure with no source is unusable here"],
        "The domain-agent pattern"),
      setup(1),
      concept('''In a high-stakes domain the model's memory isn't just unreliable &mdash; it's **dangerous** (deck
slides 4&ndash;5, 14). Every figure must be **grounded**: pulled from the actual document, carrying its
**source** so a human can verify it. A number without a citation is a liability dressed up as an answer.
Here you build the core move &mdash; extract a figure **and** its source &mdash; the discipline the real
insight agent (Lab 11) enforces with a read-only `extract_figure` tool.'''),
      code('''# Memory vs the document -- why this matters.
# Ask a model for revenue FROM MEMORY and it may answer a plausible-but-wrong number, with no source.
MEMORY_GUESS = 118.0            # what a model might "recall" -- plausible, and WRONG
GROUNDED = {"value": 120.0, "source": "p4, income stmt"}
print("from memory (ungrounded):", MEMORY_GUESS, "M   <- no source, do NOT trust")
print("grounded (from filing)  :", GROUNDED["value"], "M  [", GROUNDED["source"], "]")
print("gap:", round(GROUNDED["value"] - MEMORY_GUESS, 1), "M of pure hallucination risk")'''),
      buildmd('''Complete `extract_figure` (return the figure with its source) and `is_grounded` (it must carry a
citation), then run the cell to watch a grounded vs an ungrounded figure.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- A grounded figure carries **`source`** &mdash; the page cite a human can check. A bare `{"value": ...}` is **not** grounded.
- A missing figure returns **`None`** rather than a guess &mdash; the agent must say "not in the filing", never invent.
- This is exactly what the real `extract_figure` tool does in Lab 11: pull the value **with** its source.'''),
      yourturn('''Add a new figure to `REPORT` (say `"opex"` with a source), extract it, and confirm `is_grounded` is
True; then add one **without** a source and confirm it's False. **What good looks like:** every figure the
agent will state carries a page cite, and anything uncited is caught before it ships.'''),
      *sol_answer(sol, r'''REPORT["opex"]    = {"value": 30.0, "unit": "M", "source": "p5, income stmt"}
REPORT["mystery"] = {"value": 7.0, "unit": "M"}   # deliberately NO source
print("opex grounded?   ", is_grounded(extract_figure("opex", REPORT)))     # True  -- carries a page cite
print("mystery grounded?", is_grounded(extract_figure("mystery", REPORT)))  # False -- uncited, caught before it ships'''),
      footer(1, "Ground every figure: extract it WITH its source. A number without a citation can't be verified -- and in finance, health or cyber, an unverifiable claim doesn't ship."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-cite-every-claim", "Beginner",
     "Cite Every Claim", 20,
     "Turn a grounded figure into a claim that carries its citation, and detect which claims in a summary are uncited.",
     ["Citations", "Structured claim", "Auditability"])
def _l2(sol):
    DEFS = [
      REPORT_FIXTURE, "",
      "def make_claim(statement, fig):",
      '    # a claim ties a statement to its grounded value AND carries its exact source string',
      {"s": '    return {"statement": statement, "value": fig["value"], "source": ___}   # TODO: the citation',
       "a": '    return {"statement": statement, "value": fig["value"], "source": fig["source"]}'},
      "",
      "def uncited_claims(claims):",
      '    # return the STATEMENT of each claim in the summary that is missing a source citation',
      {"s": '    return [___ for c in claims if not c.get("source")]   # TODO: the statement of each uncited claim',
       "a": '    return [c["statement"] for c in claims if not c.get("source")]'},
    ]
    EX = '''c = make_claim("revenue", REPORT["revenue"])
print("claim:", c)
summary = [make_claim("revenue", REPORT["revenue"]),
           make_claim("net_income", REPORT["net_income"]),
           {"statement": "guess", "value": 5.0, "source": ""}]   # a slipped-in uncited claim
print("uncited in the mix:", uncited_claims(summary))
print("fully-cited pair  :", uncited_claims(summary[:2]))'''
    return [
      header(2, "Cite Every Claim", "Beginner", 20,
        ["Build a claim that carries its statement, value AND the exact source string",
         "Assemble a multi-claim summary and detect which claims are uncited",
         "See why one uncited claim in a mix breaks auditability"],
        "Auditability: structure & the trail"),
      setup(2),
      concept('''Lab 1 checked a *single* figure was grounded. A real summary makes **many** claims at once, and the
danger is the **mix**: five cited numbers and one silently uncited one. Auditability means every conclusion
is **traceable** (deck slide 15), so each **claim** carries the exact **source string** it came from
&mdash; the citation a later validation step (Lab 7) checks for *correctness*. Here you build the claim
record and a detector that names **which** claims in a summary are uncited.'''),
      realcell([REPORT_FIXTURE],
        '''print("a claim carries the SOURCE STRING through, e.g.:")
print({"statement": "revenue", "value": 120.0, "source": "p4, income stmt"})
print("a summary is a LIST of these -- and we must find any that are uncited.")'''),
      buildmd('''Complete `make_claim` (carry the source string through) and `uncited_claims` (name every claim in a
summary that is missing a citation &mdash; the mix detector), then run the cell.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- A claim carries its **exact source string** &mdash; not "cited: yes", but the page the number came from.
- The mix detector names the **one** uncited claim among several cited ones &mdash; the failure that's easy to miss.
- Lab 7 will check these citations for *correctness* (right page); here we just guarantee each claim *has* one.'''),
      yourturn('''Build a three-claim summary where the middle claim has `source=None`, and confirm `uncited_claims`
returns just that one. **What good looks like:** the detector pinpoints exactly the uncited claim(s), so a
single slipped-in figure can never ride along uncited into an analyst's summary.'''),
      *sol_answer(sol, r'''summary = [
    make_claim("revenue", REPORT["revenue"]),
    {"statement": "net_income", "value": 9.0, "source": None},   # middle claim: uncited
    make_claim("total_debt", REPORT["total_debt"]),
]
print("uncited:", uncited_claims(summary))   # -> just ['net_income'], the one slipped-in claim'''),
      footer(2, "A summary is a mix of claims, and one silently uncited number breaks the chain. Carrying the exact source string through -- and naming which claims lack it -- is what a validator (Lab 7) checks and what makes the agent auditable."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-compute-metrics", "Beginner",
     "Compute Derived Metrics", 25,
     "Compute YoY growth and margin from grounded figures using a safe calculator -- exact financial math, never bare eval.",
     ["Derived metrics", "Safe compute", "YoY & margin"])
def _l3(sol):
    DEFS = [
      SAFE_CALC, "", REPORT_FIXTURE, "",
      "def yoy_growth(current, prior):",
      '    # percent change year over year, rounded to 1 dp',
      {"s": '    return round(___, 1)   # TODO: (current - prior) / prior * 100',
       "a": '    return round((current - prior) / prior * 100, 1)'},
      "",
      "def margin_pct(net_income, revenue):",
      '    # net margin as a percentage, rounded to 1 dp',
      {"s": '    return round(___, 1)   # TODO: net_income / revenue * 100',
       "a": '    return round(net_income / revenue * 100, 1)'},
    ]
    EX = '''rev_now = REPORT["revenue"]["value"]; rev_prior = PRIOR["revenue"]
ni_now  = REPORT["net_income"]["value"]
print("revenue YoY  :", yoy_growth(rev_now, rev_prior), "%")
print("net margin   :", margin_pct(ni_now, rev_now), "%")
print("prior margin :", margin_pct(PRIOR["net_income"], PRIOR["revenue"]), "%")
print("safe_calc still exact:", safe_calc("(120-107.1)/107.1*100"))'''
    return [
      header(3, "Compute Derived Metrics", "Beginner", 25,
        ["Compute year-over-year growth from grounded figures",
         "Compute a margin as a percentage",
         "Use a safe calculator -- never bare eval on financial input"],
        "The financial-report insight agent, end to end"),
      setup(3),
      concept('''The insight agent computes the **derived metrics** an analyst cares about (deck slides 7&ndash;8):
**year-over-year growth**, **margins**, notable movements &mdash; all from the **grounded** figures, never
invented. Financial math must be exact and safe, so compute goes through a small **AST-based safe
calculator**, never bare `eval` on model output. This is the same `safe_calc` the agent's `compute` tool
wraps in Lab 11 (catching errors, returning a string).'''),
      realcell([SAFE_CALC, REPORT_FIXTURE],
        '''print("safe compute:", safe_calc("(120-107.1)/107.1*100"), "(revenue YoY %)")
try:
    safe_calc("__import__('os')")           # not arithmetic -> raises, so a tool must catch it
except Exception as e:
    print("safe_calc refuses non-arithmetic:", type(e).__name__)'''),
      buildmd('''Complete `yoy_growth` (percent change) and `margin_pct` (net income over revenue), then run the cell to
compute this quarter's metrics from the grounded figures.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- Every metric is computed **from the grounded figures** &mdash; nothing is recalled or invented.
- `safe_calc` **refuses** anything that isn't arithmetic, which is why the agent's `compute` tool wraps it in try/except and returns a string.
- The margin fell from ~9.1% to 7.5% even as revenue grew &mdash; exactly the movement Lab 4 flags for a human.'''),
      yourturn('''Compute a **debt-to-revenue** ratio (or another metric you care about) from the grounded figures via
`safe_calc`, and print it with the pages it was derived from. **What good looks like:** the number is exact,
computed from cited inputs, and you can trace it back to the filing.'''),
      *sol_answer(sol, r'''debt = REPORT["total_debt"]; rev = REPORT["revenue"]
ratio = round(safe_calc(str(debt["value"]) + "/" + str(rev["value"]) + "*100"), 1)   # exact, via safe_calc -- never bare eval
print("debt-to-revenue:", ratio, "%   [ derived from", debt["source"], "&", rev["source"], "]")'''),
      footer(3, "Derived metrics come from the grounded figures, computed exactly through a safe calculator. The margin fell from 9.1% to 7.5% even as revenue grew -- exactly the kind of movement the agent must surface next."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-flag-anomalies", "Beginner",
     "Flag Anomalies", 20,
     "Flag notable movements -- a falling margin, a debt spike -- so an analyst's attention goes to what matters.",
     ["Anomaly flags", "Thresholds", "Surface, don't decide"])
def _l4(sol):
    DEFS = [
      "def analyze_flags(margin_now, margin_prior, debt_growth_pct):",
      "    flags = []",
      {"s": '    if ___:   # TODO: the margin declined vs the prior period',
       "a": '    if margin_now < margin_prior:'},
      '        flags.append("margin_down")',
      {"s": '    if ___:   # TODO: debt grew by more than 50%',
       "a": '    if debt_growth_pct > 50:'},
      '        flags.append("debt_spike")',
      "    return flags",
    ]
    EX = '''print("margin 7.5 vs 9.1, debt +60% ->", analyze_flags(7.5, 9.1, 60))
print("margin 9.5 vs 9.1, debt +5%  ->", analyze_flags(9.5, 9.1, 5))'''
    return [
      header(4, "Flag Anomalies", "Beginner", 20,
        ["Flag a margin that declined versus the prior period",
         "Flag a debt level that spiked beyond a threshold",
         "Surface what an analyst should look at -- not a decision"],
        "The financial-report insight agent, end to end"),
      setup(4),
      concept('''Part of the agent's value is directing a human's attention: **flag** the notable movements &mdash; a
**margin that fell**, **debt that spiked** &mdash; so the analyst spends judgement where it matters (deck
slide 7). A flag is a **signal to look**, never a decision. Thresholds keep it deterministic and
auditable.'''),
      realcell([REPORT_FIXTURE],
        '''print("this quarter debt:", REPORT["total_debt"]["value"], "M  |  prior:", PRIOR["total_debt"], "M")'''),
      buildmd('''Complete `analyze_flags`: flag a declining margin and a debt spike (growth over 50%), then run the
cell.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- A flag says **"look here"**, it never says "sell" &mdash; surfacing is not deciding.
- Thresholds are explicit and deterministic, so every flag is **auditable**: you can say exactly why it fired.
- Both conditions can fire at once (margin down **and** debt spike) &mdash; the analyst sees the full picture.'''),
      yourturn('''Add a third flag &mdash; e.g. `revenue_down` when YoY growth is negative, or `high_leverage` when
debt-to-revenue crosses a threshold you pick. **What good looks like:** the new flag fires on the right
inputs and stays a signal for a human, not a recommendation.'''),
      *sol_answer(sol, r'''def analyze_flags_v2(margin_now, margin_prior, debt_growth_pct, revenue_yoy):
    flags = analyze_flags(margin_now, margin_prior, debt_growth_pct)   # reuse Lab 4's two flags
    if revenue_yoy < 0:                        # a THIRD signal for a human -- still not a recommendation
        flags.append("revenue_down")
    return flags
print("margin 7.5<9.1, debt +60%, rev -4% ->", analyze_flags_v2(7.5, 9.1, 60, -4.0))
print("all healthy                        ->", analyze_flags_v2(9.5, 9.1, 5, 12.0))'''),
      footer(4, "Flags point the analyst at what matters -- a margin that fell as revenue grew, debt that spiked. They surface, they don't decide; the human judges what the flag means."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-no-advice-guardrail", "Beginner",
     "The No-Advice Guardrail", 20,
     "Detect and block forbidden advice language -- the insight agent informs, it never recommends buying or selling.",
     ["Guardrail", "No advice", "Informational only"])
def _l5(sol):
    DEFS = [
      'ADVICE_TERMS = ("buy", "sell", "you should", "recommend", "strong buy", "invest in")',
      "",
      "def contains_advice(text):",
      "    t = text.lower()",
      {"s": '    return ___   # TODO: True if ANY advice term appears in the text',
       "a": '    return any(term in t for term in ADVICE_TERMS)'},
      "",
      "def enforce_no_advice(summary):",
      '    # a valid insight is informational; reject it if it crosses into advice',
      {"s": '    return {"ok": ___, "summary": summary}   # TODO: ok = it does NOT contain advice',
       "a": '    return {"ok": not contains_advice(summary), "summary": summary}'},
    ]
    EX = '''clean  = "Revenue +12% YoY [p4]; net margin down to 7.5% [p4] -- FLAG."
advice = "Revenue is up -- you should buy this stock now."
print("clean  ->", enforce_no_advice(clean))
print("advice ->", enforce_no_advice(advice))'''
    return [
      header(5, "The No-Advice Guardrail", "Beginner", 20,
        ["Detect buy/sell/recommend language in a summary",
         "Reject any output that crosses into advice",
         "Keep the agent informational -- analysis, not a recommendation"],
        "The insight agent, in code"),
      setup(5),
      concept('''The insight agent has a hard boundary (deck slides 6, 9): it **informs** &mdash; it does **not** give
personalized investment advice. Providing buy/sell recommendations is a regulated activity, out of scope,
and dangerous to hand to an LLM. So a guardrail **detects advice language** and rejects it: the output stays
**analysis**, and a human analyst draws any conclusion. In Lab 10 you'll run this same check over a **real
model's** output.'''),
      code('''# Words that turn analysis into (forbidden) advice.
ADVICE_TERMS = ("buy", "sell", "you should", "recommend", "strong buy", "invest in")
print("advice terms to block:", ADVICE_TERMS)'''),
      buildmd('''Complete `contains_advice` and `enforce_no_advice` (reject a summary that gives advice), then run the
cell.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- A clean, cited summary passes; the moment it says "you should buy", it's **rejected** &mdash; informational only.
- This is a deterministic guardrail you own; it runs *after* the model, on whatever text the model produced.
- Withholding the trade tool (Lab 6) stops the agent *acting*; this stops it *advising*. Both are needed.'''),
      yourturn('''The keyword list is a blunt instrument &mdash; try a phrasing that slips past it (e.g. *"a compelling
entry point"*) and decide whether you'd add it. **What good looks like:** you understand the guardrail's
limits and can tighten it, while accepting that the *real* safety net is the withheld tool, not the word
list.'''),
      *sol_answer(sol, r'''sneaky = "Margin fell to 7.5% [p4]; still, a compelling entry point here."
print("slips past the keyword list?", not contains_advice(sneaky))   # True -- the blunt list misses it
# Tighten it by adding the phrasing -- but the REAL safety net stays the withheld trade tool (Lab 6).
EXTRA_TERMS = ADVICE_TERMS + ("entry point", "compelling")
def contains_advice_v2(text):
    t = text.lower()
    return any(term in t for term in EXTRA_TERMS)
print("caught after tightening? ", contains_advice_v2(sneaky))       # True'''),
      footer(5, "The agent informs, never advises. Detecting and blocking advice language keeps it on the safe, valuable side of the line -- analysis for a human, not a recommendation. Next: the stronger guardrail."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-withhold-the-tool", "Beginner",
     "Withhold the Dangerous Tool", 25,
     "The strongest guardrail: give the agent read/compute tools but NO trade or advice tool -- it cannot act.",
     ["Withhold the tool", "Read-only", "Cannot act"])
def _l6(sol):
    DEFS = [
      'FORBIDDEN = {"place_trade", "give_advice", "execute_order", "wire_funds"}',
      'ALL_TOOLS = ["extract_figure", "compute", "place_trade", "give_advice"]   # a MIXED, untrusted toolbox',
      "",
      "def agent_tools():",
      '    # read-only: keep every tool from ALL_TOOLS that is NOT a forbidden capability',
      {"s": '    return ___   # TODO: filter ALL_TOOLS, dropping anything that is in FORBIDDEN',
       "a": '    return [t for t in ALL_TOOLS if t not in FORBIDDEN]'},
      "",
      "def can_act(tools):",
      '    # True if the toolset contains any consequential (forbidden) tool',
      {"s": '    return ___   # TODO: any tool that is in FORBIDDEN',
       "a": '    return any(t in FORBIDDEN for t in tools)'},
    ]
    EX = '''print("tools    :", agent_tools())
print("can act? :", can_act(agent_tools()))
print("if given a trade tool:", can_act(agent_tools() + ["place_trade"]))'''
    return [
      header(6, "Withhold the Dangerous Tool", "Beginner", 25,
        ["Give the agent only read-only tools (extract, compute)",
         "Confirm it holds no place_trade or give_advice tool",
         "See why withholding the tool beats any prompt instruction"],
        "Assistive on judgement, autonomous on legwork"),
      setup(6),
      concept('''The strongest guardrail is the simplest (deck slides 9, 17): don't **give** the agent the dangerous
tool. The insight agent gets `extract_figure` and `compute` &mdash; **read-only** &mdash; and there is
**no** `place_trade`, no `give_advice`. Just as the email agent couldn't send, this agent literally
**cannot** trade or advise. Withholding a capability is far stronger than instructing against it &mdash; and
in Lab 11 you'll see this exact list drive a **real** `create_agent` where `place_trade` is defined but
never bound.'''),
      code('''FORBIDDEN = {"place_trade", "give_advice", "execute_order", "wire_funds"}
ALL_TOOLS = ["extract_figure", "compute", "place_trade", "give_advice"]   # a MIXED, untrusted toolbox
print("all available tools :", ALL_TOOLS)
print("tools an insight agent must NEVER hold:", FORBIDDEN)'''),
      buildmd('''Complete `agent_tools` &mdash; **filter** the mixed `ALL_TOOLS` toolbox down to the read-only ones &mdash;
and `can_act` (does the toolset contain a forbidden tool?), then run the cell.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- The bound toolset is exactly `["extract_figure", "compute"]` &mdash; **read-only**, so `can_act` is False.
- *Add* a trade tool and `can_act` flips True &mdash; which is why you never add it. The guardrail is the missing capability.
- A prompt ("please don't trade") can be jailbroken; a tool that isn't bound cannot be called at all.'''),
      yourturn('''Imagine a stakeholder asks to "let the agent auto-rebalance". Show what `can_act` returns if you add
`execute_order`, and write one sentence on why you'd refuse. **What good looks like:** you can demonstrate,
in code, that adding the capability is what makes the agent able to act &mdash; so the safe design is to
leave it out.'''),
      *sol_answer(sol, r'''requested = agent_tools() + ["execute_order"]   # what "let it auto-rebalance" would require
print("tools if we grant it:", requested)
print("can act now?         :", can_act(requested))            # True -- it could now place orders
print("execute_order forbidden?:", "execute_order" in FORBIDDEN)
# Refuse: adding execute_order is exactly what makes the agent able to act, so the safe design leaves it
# out -- the agent analyses, a human executes any rebalance.'''),
      footer(6, "In a high-stakes domain your strongest safety control is the tool you DON'T provide. Read-only tools mean the agent can analyse all day and still cannot trade or advise -- the guardrail is the missing capability."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-validate-grounding", "Intermediate",
     "Validate Grounding", 30,
     "Before shipping a summary, validate that every claim is grounded and cites the RIGHT source.",
     ["Validation", "Grounding check", "Right source"])
def _l7(sol):
    DEFS = [
      REPORT_FIXTURE, "",
      "def validate_summary(claims, report):",
      "    problems = []",
      "    for c in claims:",
      "        fig = report.get(c['metric'])",
      "        if fig is None:",
      '            problems.append("ungrounded: " + c["metric"])   # cites a figure not in the report',
      {"s": '        elif ___:   # TODO: the claim cites a source that does not match the report',
       "a": '        elif c["source"] != fig["source"]:'},
      '            problems.append("wrong source: " + c["metric"])',
      {"s": '    return {"ok": ___, "problems": problems}   # TODO: ok = no problems',
       "a": '    return {"ok": len(problems) == 0, "problems": problems}'},
    ]
    EX = '''good = [{"metric": "revenue", "source": "p4, income stmt"}]
ungrounded = [{"metric": "ebitda", "source": "p9"}]
wrong = [{"metric": "revenue", "source": "p1, cover"}]
print("good      ->", validate_summary(good, REPORT))
print("ungrounded->", validate_summary(ungrounded, REPORT))
print("wrong src ->", validate_summary(wrong, REPORT))'''
    return [
      header(7, "Validate Grounding", "Intermediate", 30,
        ["Check every claim maps to a real figure in the report",
         "Check each claim cites the correct source",
         "Refuse to ship a summary with an ungrounded claim"],
        "Grounding: RAG & citations"),
      setup(7),
      concept('''Never ship an ungrounded claim (deck slides 4, 8, 14). Before the summary goes to an analyst, the agent
**validates** it: every claim must map to a **real figure** in the report, and it must cite the **correct
source**. A claim that cites the wrong page, or a figure that isn't in the report, is a grounding failure
&mdash; don't ship it. This is the gate that turns "cited" (Lab 2) into "**correctly** cited".'''),
      realcell([REPORT_FIXTURE],
        '''print("a claim must match REPORT[metric] on the source string, e.g. revenue -> 'p4, income stmt'")'''),
      buildmd('''Complete `validate_summary`: collect an ungrounded claim and a wrong-source claim, and return `ok` only
when there are no problems. Then run the cell.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- A claim about a figure **not in the report** is `ungrounded`; a claim citing the **wrong page** is `wrong source`.
- `ok` is True only when the `problems` list is empty &mdash; one bad claim blocks the whole summary.
- This is the validation Lab 12's capstone pipeline runs before it flags a report `needs_review`.'''),
      yourturn('''Feed `validate_summary` a mixed list with one good claim, one ungrounded, and one wrong-source, and read
the collected problems. **What good looks like:** every problem is named individually, and `ok` is False, so
nothing ungrounded or mis-cited can slip through to an analyst.'''),
      *sol_answer(sol, r'''mixed = [
    {"metric": "revenue",    "source": "p4, income stmt"},   # good     -- matches the report
    {"metric": "ebitda",     "source": "p9"},                # ungrounded -- not in the report
    {"metric": "net_income", "source": "p1, cover"},         # wrong source -- real figure, wrong page
]
result = validate_summary(mixed, REPORT)
print("ok:", result["ok"])          # False -- one bad claim blocks the whole summary
for p in result["problems"]:
    print("problem:", p)'''),
      footer(7, "Validation is the gate before an analyst sees the summary: every claim must map to a real figure and cite the right source. An ungrounded or mis-cited claim doesn't ship -- that's the high-stakes bar."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-audit-trail", "Intermediate",
     "The Audit Trail", 30,
     "Log the whole run -- trigger, figures pulled, reasoning, output -- into a replayable, fully-sourced trail.",
     ["Audit trail", "Replayable", "Fully sourced"])
def _l8(sol):
    DEFS = [
      "class AuditTrail:",
      "    def __init__(self):",
      "        self.entries = []",
      "    def record(self, step, detail, source=None):",
      {"s": '        ___   # TODO: append {"step": step, "detail": detail, "source": source}',
       "a": '        self.entries.append({"step": step, "detail": detail, "source": source})'},
      "    def steps(self):",
      "        return [e['step'] for e in self.entries]",
      "    def fully_sourced(self):",
      '        # every FIGURE step must carry a source (analysis/decision steps need not)',
      {"s": '        return all(___ for e in self.entries if e["step"] == "figure")   # TODO: e has a source',
       "a": '        return all(e["source"] for e in self.entries if e["step"] == "figure")'},
    ]
    EX = '''t = AuditTrail()
t.record("trigger", "analyze Q3 report")
t.record("figure", "revenue=120.0M", "p4, income stmt")
t.record("figure", "net_income=9.0M", "p4, income stmt")
t.record("output", "summary + needs_review")
print("steps        :", t.steps())
print("fully sourced:", t.fully_sourced())'''
    return [
      header(8, "The Audit Trail", "Intermediate", 30,
        ["Record each step of the run with its detail and source",
         "Read back the ordered trail for replay",
         "Check every figure step carries a source"],
        "Auditability: structure & the trail"),
      setup(8),
      concept('''In a regulated domain you must be able to **prove** how the agent reached its conclusion (deck slides 15,
19). The **audit trail** logs the whole run &mdash; the trigger, every figure pulled and its source, the
reasoning, the output, the human decision &mdash; so the run is **replayable** and every figure is
**traceable**. It's also how you debug and improve the agent. (In Lab 11 the real agent's **message trace**
is exactly this, produced for free by `create_agent`.)'''),
      code('''# One entry per step: what happened, and (for a figure) where it came from.
print("an entry:", {"step": "figure", "detail": "revenue=120.0M", "source": "p4, income stmt"})'''),
      buildmd('''Complete `AuditTrail`: record entries, read back the steps, and check every figure is sourced. Then run
the cell.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- The trail preserves **order**, so the run is replayable step by step &mdash; what a regulator asks for.
- `fully_sourced` checks only **figure** steps carry a source (a "trigger" or "output" step needn't).
- The real agent gives you this automatically: its list of `AIMessage`/`ToolMessage` **is** the trail (Lab 11).'''),
      yourturn('''Add a step to the trail with **no** source for a figure and confirm `fully_sourced` turns False; then add
a "human_decision" step and read the full ordered trail. **What good looks like:** any unsourced figure is
caught, and the trail reads as a replayable record of the whole run.'''),
      *sol_answer(sol, r'''t = AuditTrail()
t.record("trigger", "analyze Q3 report")
t.record("figure", "revenue=120.0M", "p4, income stmt")
t.record("figure", "ebitda=15.0M", None)              # unsourced figure -- must be caught
print("fully sourced?", t.fully_sourced())            # False
t.record("human_decision", "analyst approved summary for filing")
for e in t.entries:                                    # the full ordered, replayable trail
    print(e["step"], "|", e["detail"], "|", e["source"])'''),
      footer(8, "The audit trail makes the whole run replayable and every figure traceable -- what a regulator needs and what lets you debug the agent. Structured claims make each answer checkable; the trail makes the run accountable."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-privacy-redaction", "Intermediate",
     "Privacy: Minimize & Redact", 30,
     "Minimize what you send the model and redact sensitive identifiers -- data handling as a first-class concern.",
     ["Privacy", "Minimize", "Redaction"])
def _l9(sol):
    DEFS = [
      "def redact_account(text):",
      '    out, run = [], ""',
      '    for ch in text + " ":            # trailing space flushes the final run',
      "        if ch.isdigit():",
      "            run += ch",
      "        else:",
      {"s": '            if ___:            # TODO: run is a long number (6+ digits)',
       "a": '            if len(run) >= 6:'},
      '                out.append("[REDACTED]")',
      "            else:",
      "                out.append(run)",
      '            run = ""',
      "            out.append(ch)",
      '    return "".join(out).rstrip()',
      "",
      "def minimize(record, needed_fields):",
      '    # send the model ONLY the fields the task needs -- not the whole record',
      {"s": '    return ___   # TODO: build a dict of just the needed_fields that exist in record',
       "a": '    return {k: record[k] for k in needed_fields if k in record}'},
    ]
    EX = '''print(redact_account("acct 1234567890 for FY2026"))
rec = {"name": "ACME", "revenue": 120.0, "account": "1234567890", "ssn": "999-99-9999"}
print(minimize(rec, ["name", "revenue"]))'''
    return [
      header(9, "Privacy: Minimize & Redact", "Intermediate", 30,
        ["Redact long identifiers (account/card numbers) from text",
         "Send the model only the fields the task needs",
         "Treat data handling as a first-class design constraint"],
        "Privacy, compliance & data handling"),
      setup(9),
      concept('''High-stakes agents run on the most sensitive data there is (deck slide 16). Two disciplines: **minimize**
&mdash; send the model only the fields the task needs, not the whole record &mdash; and **redact** &mdash;
mask identifiers (account numbers, card numbers) before they leave your systems. Less exposed data is less
risk. It's why Day 1 started on **local models**; here you also see why Day-5 hosted calls (Groq) must be
fed **minimized, redacted** input.'''),
      code('''# We mask any run of 6+ consecutive digits (account/card numbers), keeping short numbers like a year.
print("redact 'acct 1234567890 for FY2026' -> mask the long number, keep 2026")'''),
      buildmd('''Complete `redact_account` (mask long digit runs) and `minimize` (keep only needed fields), then run the
cell.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      noticemd('''- A 10-digit account number becomes **`[REDACTED]`**; a 4-digit year survives &mdash; the threshold is the rule.
- `minimize` sends **only** `["name", "revenue"]`; the account number and SSN never leave your systems.
- Before any text goes to a hosted model, run it through both &mdash; the model should never see what it doesn't need.'''),
      yourturn('''Extend `redact_account` (or write a second redactor) to also mask an email address, then minimize a record
down to the two fields a summary needs. **What good looks like:** the text you'd send a hosted model carries
no raw identifiers, and only the necessary fields leave your boundary.'''),
      *sol_answer(sol, r'''import re
def redact_pii(text):
    text = redact_account(text)                          # Lab 9: mask 6+ digit runs (account/card numbers)
    return re.sub(r"[\w.]+@[\w.]+\.\w+", "[EMAIL]", text) # ALSO mask email addresses
print(redact_pii("acct 1234567890, contact cfo@acme.com for FY2026"))
rec = {"name": "ACME", "revenue": 120.0, "account": "1234567890", "email": "cfo@acme.com"}
print(minimize(rec, ["name", "revenue"]))                # only the two fields a summary needs leave the boundary'''),
      footer(9, "Minimize what you send and redact identifiers before they leave your systems. Data handling is a first-class design constraint -- decide where the data can go before you build, which is why this course runs on local models where it can."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-assistive-not-autonomous", "Advanced",
     "Assistive, Not Autonomous", 40,
     "Make the agent recommend-for-review but never decide -- then run a REAL Groq model and push its output through the assistive gate.",
     ["Assistive", "needs_review", "Automation bias"])
def _l10(sol):
    DEFS = [
      "def make_insight(summary, claims):",
      '    # analysis + a needs_review flag -- the agent never decides',
      {"s": '    return {"summary": summary, "status": ___, "claims": claims}   # TODO: the review flag',
       "a": '    return {"summary": summary, "status": "needs_review", "claims": claims}'},
      "",
      "def reviewable(insight):",
      '    # a review is only genuine if EVERY claim is cited (defends against automation bias)',
      {"s": '    return all(___ for c in insight["claims"])   # TODO: each claim has a source',
       "a": '    return all(c.get("source") for c in insight["claims"])'},
      "",
      "def owns_decision(insight):",
      '    # the agent only "owns" a decision it already executed; an assistive (needs_review) insight',
      '    # is owned by a human -- so branch on the status field to return the owner',
      {"s": '    return "agent" if ___ else "human"   # TODO: the status shows the agent already acted (executed)',
       "a": '    return "agent" if insight["status"] == "executed" else "human"'},
    ]
    EX = '''claims = [{"metric": "revenue", "source": "p4"}, {"metric": "margin", "source": "p4"}]
ins = make_insight("Revenue +12% YoY [p4]; margin down [p4].", claims)
print("status    :", ins["status"])
print("reviewable:", reviewable(ins))
print("owns (assistive):", owns_decision(ins))
print("owns (if executed):", owns_decision({"status": "executed"}))
uncited = make_insight("...", [{"metric": "guess", "source": ""}])
print("uncited reviewable?", reviewable(uncited))'''
    RUN = '''# Ask the REAL model for a one-line, cited, NO-advice insight -- then push its output through YOUR gate.
prompt = ("In ONE line, state revenue and net income with their page cites, and give NO advice: "
          "revenue 120.0M (p4, income stmt), net income 9.0M (p4, income stmt).")
text = llm.invoke(prompt).content
print("REAL model insight:", text)
ins = make_insight(text, [{"metric": "revenue", "source": "p4, income stmt"},
                          {"metric": "net_income", "source": "p4, income stmt"}])
print("status                  :", ins["status"], "(never a decision)")
print("owner of the decision   :", owns_decision(ins))
advice_terms = ("buy", "sell", "recommend", "you should", "invest in")
print("no-advice guardrail holds:", not any(t in text.lower() for t in advice_terms))'''
    return [
      header(10, "Assistive, Not Autonomous", "Advanced", 40,
        ["Return analysis flagged for review -- never a decision",
         "Require every claim to be cited so review is genuine",
         "Run a REAL model and gate its output as needs_review"],
        "Assistive on judgement, autonomous on legwork"),
      setup(10),
      concept('''The golden rule of Day 5 (deck slides 11, 17): agents are **assistive, not autonomous**. The insight
agent does the grounded legwork and returns analysis flagged **`needs_review`** &mdash; it never decides.
And to defend against **automation bias** (humans rubber-stamping a confident machine), the review is only
real if the agent **shows its work**: every claim **cited**. The **human** owns any consequential decision.
Here you build the gate, then push a **real model's** output through it.'''),
      code('''# The agent's output is analysis + a needs_review flag -- never "executed" or a recommendation.
print("assistive output shape:", {"summary": "...", "status": "needs_review", "claims": ["..."]})'''),
      buildmd('''Complete `make_insight` (flag for review), `reviewable` (require citations), and `owns_decision`, then
run the cell.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Now ask the **real** Groq model for a cited, no-advice insight and push its output through your assistive gate &mdash; the model does the drafting, your code keeps it `needs_review` and advice-free."),
      code(runguard(RUN)),
      noticemd('''- The real model's text is wrapped **`needs_review`** &mdash; the agent never marks anything `executed`, so a **human** owns the decision.
- `reviewable` is only True when every claim is cited &mdash; an uncited insight makes review a rubber-stamp, and it's caught.
- The no-advice guardrail (Lab 5) runs on the **real** output here &mdash; a live model, gated by your deterministic rules.'''),
      yourturn('''Change the prompt to tempt the model into advice (e.g. add *"...and say whether to buy"*) and re-run.
**What good looks like:** even if the model slips, your `no-advice guardrail holds` check flips False so you
*catch* it &mdash; and the output is still `needs_review`, owned by a human. The safety is in your gate, not
the model's goodwill.'''),
      *sol_answer(sol, r'''if groq_ready():
    tempt = ("In ONE line state revenue 120.0M (p4) and net income 9.0M (p4) with cites, "
             "and say whether to buy.")            # deliberately tempts the model into advice
    text = llm.invoke(tempt).content
    ins  = make_insight(text, [{"metric": "revenue", "source": "p4"}])
    advice_terms = ("buy", "sell", "recommend", "you should", "invest in")
    print("model said:", text)
    print("no-advice guardrail holds:", not any(t in text.lower() for t in advice_terms))  # flips False if it slipped
    print("status:", ins["status"], "| owner:", owns_decision(ins))   # still needs_review, a human owns it
else:
    print("(add GROQ_API_KEY to .env to run the real model)")'''),
      footer(10, "Assistive, not autonomous: the agent flags analysis for review and never decides, and citations make the review genuine rather than a rubber-stamp. You just gated a real model's output. The human owns every consequential decision."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-assemble-insight-agent", "Advanced",
     "Assemble the Insight Agent", 35,
     "Bind read-only extract & compute tools (NO trade tool) into a REAL Groq create_agent, run it, and read the trace where it grounds & cites a figure.",
     ["create_agent", "Read-only tools", "Real trace"])
def _l11(sol):
    DEMO = '''from langchain_core.tools import tool

@tool
def extract_figure(name: str) -> dict:
    """Pull a reported figure and its source from the filing. Use this to ground any number before stating it."""
    return REPORT.get(name, {})

@tool
def compute(expression: str) -> str:
    """Do exact arithmetic on a financial expression such as '(120-107.1)/107.1*100'. Use for any calculation."""
    try:
        return str(safe_calc(expression))          # success path
    except Exception:
        return "error: not a numeric expression"    # a tool must NEVER raise -- return a string

@tool
def place_trade(ticker: str, shares: int) -> str:
    """Place a trade. (Defined to show the capability -- but DELIBERATELY WITHHELD from the agent.)"""
    return "TRADED"

print("read-only tools:", extract_figure.name, "&", compute.name, "| withheld:", place_trade.name)'''
    DEFS = [
      "from langchain.agents import create_agent",
      "",
      "def readonly_tools():",
      {"s": '    return ___   # TODO: read-only -- [extract_figure, compute], NEVER place_trade',
       "a": '    return [extract_figure, compute]'},
      "",
      "def make_insight_agent():",
      {"s": '    return create_agent(llm, ___)   # TODO: bind the read-only tools to the real Groq model',
       "a": '    return create_agent(llm, readonly_tools())'},
      "",
      "def wrap_needs_review(insight, tools_used):",
      '    # analysis only: wrap the finding so a human analyst reviews it -- never a decision',
      {"s": '    return {"insight": insight, "status": ___, "tools_used": tools_used}   # TODO: needs_review',
       "a": '    return {"insight": insight, "status": "needs_review", "tools_used": tools_used}'},
    ]
    EX = '''print("bound tools :", [t.name for t in readonly_tools()])
print("can it trade?:", "place_trade" in [t.name for t in readonly_tools()])
print("place_trade still exists as a capability, just unbound:", place_trade.name)
print("wrapped shape:", wrap_needs_review("Revenue 120.0M [p4].", ["extract_figure"])["status"])'''
    RUN = '''agent = make_insight_agent()
print("agent type:", type(agent).__name__)          # a runnable CompiledStateGraph
result = agent.invoke({"messages": [{"role": "user",
         "content": "Use extract_figure to get revenue, then state it with its source. Give NO advice."}]},
         config={"recursion_limit": 8})
print_trace(result)
print("---")
used = [tc["name"] for m in result["messages"] for tc in (getattr(m, "tool_calls", None) or [])]
out = wrap_needs_review(result["messages"][-1].content, used)
print("tools used:", out["tools_used"])
print("status    :", out["status"], "(no trade tool bound, so the agent cannot act)")
print("insight   :", out["insight"])'''
    return [
      header(11, "Assemble the Insight Agent", "Advanced", 35,
        ["Bind read-only @tools into a real Groq agent with create_agent",
         "Withhold any trade/advice tool so it cannot act",
         "Run it and read the trace where it grounds & cites a figure"],
        "The financial-report insight agent, end to end"),
      setup(11),
      concept('''Now assemble the insight agent (deck slides 7&ndash;9): `@tool` **read-only** tools (`extract_figure`,
`compute`) bound with **`create_agent`** into a runnable **`CompiledStateGraph`**, driven by the **real**
Groq model. The agent grounds a figure and states it with its source. The design choice: the tools list is
**read-only** &mdash; `place_trade` is **defined but not bound** &mdash; and the output is wrapped
**`needs_review`** for a human analyst. The guardrail is what's **missing** from the tools list.'''),
      realcell([SAFE_CALC, TOOL_IMPORT, REPORT_FIXTURE], DEMO),
      buildmd('''Build the agent with **read-only** tools (no `place_trade`), bound to the real `llm`, and wrap whatever
it finds as **`needs_review`**. Run the cell to confirm the wiring &mdash; then run it for real below.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Assemble the real agent, invoke it on a grounding task, and read the **real trace**: the model calls `extract_figure`, reads the observation, and states revenue **with its page cite** &mdash; no trade tool anywhere."),
      code(runguard(RUN)),
      noticemd('''- `type(agent).__name__` is **`CompiledStateGraph`** &mdash; a real runnable graph, driven by the real Groq model.
- The trace shows **`TOOL CALL: extract_figure`** &rarr; an **`OBS:`** with the sourced figure &rarr; a final answer that **cites the page** &mdash; grounding, for real.
- **`place_trade` is never in `readonly_tools()`**, so however the model is prompted it *cannot* trade. The output is `needs_review` for a human.'''),
      yourturn('''Ask the agent a question that needs **both** tools &mdash; e.g. *"extract revenue and net income, then use
compute for the net margin, and cite both pages"* &mdash; and re-run. **What good looks like:** the trace
chains `extract_figure` &rarr; `compute`, the answer cites the pages, and there is still no way for it to
trade or advise.'''),
      *sol_answer(sol, r'''if groq_ready():
    agent = make_insight_agent()                     # read-only tools; place_trade is never bound
    result = agent.invoke({"messages": [{"role": "user",
             "content": ("Use extract_figure for revenue and net_income, then use compute for the net "
                         "margin (net_income/revenue*100). Cite both pages. Give NO advice.")}]},
             config={"recursion_limit": 10})
    print_trace(result)                              # trace chains extract_figure -> compute, cites the pages
    used = [tc["name"] for m in result["messages"] for tc in (getattr(m, "tool_calls", None) or [])]
    print("tools used:", used, "| status:", wrap_needs_review(result["messages"][-1].content, used)["status"])
else:
    print("(add GROQ_API_KEY to .env to run the real agent)")'''),
      footer(11, "The guardrail is what's MISSING from the tools list -- place_trade is never bound, so the real agent grounds, computes and cites but cannot trade or advise. Next: run the whole pipeline over a suite."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-insight-agent", "Advanced",
     "Capstone: The Financial-Report Insight Agent", 45,
     "Run the full insight agent: an offline redact->ground->cite->validate pipeline over a mixed suite, then a REAL Groq agent grounding & citing a report.",
     ["End-to-end agent", "Report suite", "Cited & assistive"])
def _l12(sol):
    HELPERS = '''# The pieces you built this module, provided so you can assemble the whole agent.
import re
def margin_pct(ni, rev):
    return round(ni / rev * 100, 1)
def redact(text):
    # Lab 9: mask any run of 6+ digits (account/card numbers) before it leaves your systems
    return re.sub(r"\\d{6,}", "[REDACTED]", text)
def build_summary(report):
    rev, ni = report["revenue"], report["net_income"]
    m = margin_pct(ni["value"], rev["value"])
    note = report.get("note", "")               # free-text note -- may hold an account number or advice
    return ("Revenue " + str(rev["value"]) + "M [" + rev["source"] + "]; "
            "net margin " + str(m) + "% [" + ni["source"] + "]. " + note).strip()
def claims_of(report):
    return [{"metric": "revenue", "source": report["revenue"]["source"]},
            {"metric": "net_income", "source": report["net_income"]["source"]}]
ADVICE_TERMS = ("buy", "sell", "recommend", "you should", "invest in")
print("helpers ready: redact, build_summary, claims_of, margin_pct")'''
    DEFS = [
      "def process(report):",
      "    raw     = build_summary(report)",
      {"s": '    summary = ___   # TODO: redact account/card numbers from raw before it leaves your systems',
       "a": '    summary = redact(raw)'},
      "    claims  = claims_of(report)",
      {"s": '    cited   = ___   # TODO: True if every claim has a source',
       "a": '    cited   = all(c["source"] for c in claims)'},
      "    advice  = any(t in summary.lower() for t in ADVICE_TERMS)",
      '    # ship for review only if fully cited AND advice-free; else reject',
      {"s": '    status  = "needs_review" if (___) else "rejected"   # TODO: cited and not advice',
       "a": '    status  = "needs_review" if (cited and not advice) else "rejected"'},
      '    return {"summary": summary, "cited": cited, "advice": advice, "status": status}',
      "",
      "SUITE = [",
      '    {"revenue": {"value": 120.0, "source": "p4"}, "net_income": {"value": 9.0,  "source": "p4"}, "note": "Acct 1234567890 on file."},',
      '    {"revenue": {"value": 80.0,  "source": "p3"}, "net_income": {"value": 12.0, "source": "p3"}, "note": "You should buy more."},',
      '    {"revenue": {"value": 60.0,  "source": ""},   "net_income": {"value": 5.0,  "source": "p2"}, "note": "Solid quarter."},',
      '    {"revenue": {"value": 200.0, "source": "p5"}, "net_income": {"value": 20.0, "source": "p5"}, "note": "Debt down YoY."},',
      "]",
      "",
      "def evaluate():",
      '    # score the suite: count only the reports that ship (cited AND flagged needs_review)',
      {"s": '    ok = ___   # TODO: count reports where cited and status == "needs_review"',
       "a": '    ok = sum(1 for r in SUITE if process(r)["cited"] and process(r)["status"] == "needs_review")'},
      "    return ok, len(SUITE)",
    ]
    EX = '''for r in SUITE:
    out = process(r)
    print(out["status"], "| cited:", out["cited"], "| advice:", out["advice"], "->", out["summary"][:56])
print("shipped/total:", evaluate())'''
    RUN = '''# The REAL insight agent over two reports -- read the trace where it grounds & cites each figure.
from langchain_core.tools import tool
from langchain.agents import create_agent

REPORTS = {
    "acme": {"revenue": {"value": 120.0, "source": "p4, income stmt"}, "net_income": {"value": 9.0, "source": "p4"}},
    "globex": {"revenue": {"value": 80.0, "source": "p3, income stmt"}, "net_income": {"value": 12.0, "source": "p3"}},
}
@tool
def extract_figure(company: str, name: str) -> dict:
    """Pull a reported figure and its source for a company from the filings."""
    return REPORTS.get(company, {}).get(name, {})
@tool
def place_trade(ticker: str, shares: int) -> str:
    """Place a trade. (Defined, but DELIBERATELY WITHHELD -- the agent never gets it.)"""
    return "TRADED"

agent = create_agent(llm, [extract_figure])          # read-only: place_trade is NOT bound
for company in ("acme", "globex"):
    result = agent.invoke({"messages": [{"role": "user",
             "content": f"Use extract_figure for {company}'s revenue, then state it WITH its source. Give NO advice."}]},
             config={"recursion_limit": 8})
    print("==", company, "==")
    print_trace(result)
    print()
print("Every figure was grounded via extract_figure and cited from the trace; no trade tool was ever bound.")'''
    return [
      header(12, "Capstone: The Financial-Report Insight Agent", "Advanced", 45,
        ["Chain redact -> ground -> cite -> validate into one analyzer",
         "Reject any output with advice or an uncited claim",
         "Then run a REAL Groq agent that grounds & cites across a suite"],
        "The financial-report insight agent, end to end"),
      setup(12),
      concept('''Capstone: the **financial-report insight agent** (the client's Lab 5.1), end to end. First an **offline**
pipeline for each report &mdash; **redact** sensitive identifiers (Lab 9), **ground** the figures, build a
**cited** summary, check it is fully cited and contains **no advice**, and flag it **`needs_review`** &mdash;
run over a **mixed suite** (clean / advice / uncited) so only the good ones ship (a **partial** score is the
correct outcome). Then the **real** Groq agent runs over two reports and you read the **trace** where it
grounds &amp; cites each figure &mdash; never a decision, never a trade.'''),
      realcell([REPORT_FIXTURE], HELPERS),
      buildmd('''Complete `process` (redact &rarr; cited + no-advice &rarr; status) and `evaluate` (score the mixed suite),
then run the cell to see which reports ship and which are rejected.'''),
      code(render(DEFS, sol) + "\n\n" + guard(EX)),
      runmd("Now run the **real** insight agent over two reports. Read each trace: the model calls `extract_figure`, and states the figure **with its page cite** &mdash; grounded, cited, and with no trade tool anywhere."),
      code(runguard(RUN)),
      noticemd('''- The offline pipeline ships **only** the clean, cited, advice-free reports &mdash; a **partial** score (2 of 4) is exactly right; the advice and uncited reports are rejected.
- Account numbers are **redacted** before any summary ships, and the real agent's trace shows every figure **grounded via a tool** and **cited**.
- Across both runs, `place_trade` is never bound &mdash; the agent grounds, cites and computes but **cannot** trade or advise. A human decides.'''),
      yourturn('''Add a fifth report to `SUITE` that *looks* clean but cites a page that isn't in the filing, and extend
`process` (or reuse Lab 7's `validate_summary`) to reject it. Then ask the real agent for a metric that
needs a `compute` step and read the chained trace. **What good looks like:** mis-cited reports are rejected,
the real agent chains tools and cites its figures, and nothing ever trades.'''),
      *sol_answer(sol, r'''# Part 1 (offline): a report that LOOKS clean but cites a page not in the filing -> reject it.
bad = {"revenue": {"value": 90.0, "source": "p99, does-not-exist"},
       "net_income": {"value": 8.0, "source": "p3"}, "note": "Steady quarter."}
REAL_PAGES = {"p3", "p4", "p5"}                         # pages that actually exist in this filing
def process_v2(report):
    out = process(report)
    grounded = all(c["source"].split(",")[0] in REAL_PAGES for c in claims_of(report))  # cited page must be real
    if not grounded:
        out["status"] = "rejected"                     # mis-cited -> does not ship
    return out
print("mis-cited report ->", process_v2(bad)["status"])   # rejected

# Part 2 (real agent): ask for a metric that needs a compute step, and read the chained trace.
if groq_ready():
    from langchain_core.tools import tool
    from langchain.agents import create_agent
    @tool
    def net_margin(net_income: float, revenue: float) -> str:
        """Compute net margin percent = net_income / revenue * 100. Use for the margin metric."""
        try:
            return str(margin_pct(net_income, revenue))   # HELPERS' safe rounded math -- never bare eval
        except Exception:
            return "error: bad inputs"
    agent2 = create_agent(llm, [extract_figure, net_margin])   # read-only; place_trade never bound
    r = agent2.invoke({"messages": [{"role": "user",
        "content": ("Use extract_figure for acme's revenue and net_income, then use net_margin to compute "
                    "the margin. Cite both pages. Give NO advice.")}]},
        config={"recursion_limit": 10})
    print_trace(r)
else:
    print("(add GROQ_API_KEY to .env to run the real agent)")'''),
      footer(12, "You built the financial-report insight agent end to end -- it grounds and cites every figure, gives no advice, has no trade tool, and flags for a human. That's a genuinely useful high-stakes agent. Next: Module 10 -- doing it responsibly."),
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
        banner = md(f'''> ## SOLUTION / ANSWER KEY &mdash; Lab 9.{nn}
> This is the **completed** notebook (all `___` blanks filled). For the student version, open
> [`../{info['slug']}.ipynb`](../{info['slug']}.ipynb). Trainer use &mdash; or self-check after you've tried it yourself.''')
        with open(os.path.join(SOL_DIR, fname), "w") as f:
            json.dump(notebook([banner] + info["build"](True)), f, indent=1, ensure_ascii=False)

print(f"Wrote {len(NB)} notebooks to {OUT_DIR}" + (f" and solutions to {SOL_DIR}" if SOL_DIR else ""))

with open(os.path.join(_HERE, "_meta.json"), "w") as f:
    json.dump({str(nn): {k: NB[nn][k] for k in ("slug","level","title","mins","summary","concepts")}
               for nn in NB}, f, indent=1)
