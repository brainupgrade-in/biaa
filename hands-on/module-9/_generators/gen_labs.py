# -*- coding: utf-8 -*-
"""Generator for Day 5 Module 9 hands-on labs (12 notebooks).
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

Design: this is the "Agents in Finance, Healthcare & Cybersecurity" module -- the labs build the
FINANCIAL-REPORT INSIGHT AGENT (the client's Lab 5.1) piece by piece, exactly as the deck teaches:
the domain-agent pattern (ground -> reason -> structure+cite -> guardrail -> human), grounding every
figure with a citation, computing derived metrics, flagging anomalies, the no-advice guardrail,
withholding the dangerous tool, validating grounding, the audit trail, privacy/redaction, assistive-
not-autonomous, and the assembled agent. To keep the course's verify discipline (every GRADED cell
runs offline & deterministically -- no live LLM, no keys, no network), the graded cells are pure
Python stdlib; the two agent-assembly labs (11-12) reuse the SAME compact LangChain-shaped shim as
Modules 6-8 (names & shapes mirror real LangChain), driven by a deterministic scripted "FakeChatModel".
Each Advanced lab (10-12) adds ONE optional, non-graded, guarded cell that runs the SAME shapes
against the REAL library and degrades gracefully. Financial math uses a small AST-based safe
evaluator -- never bare eval()."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day5-module9-agents-in-industry.html"
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
WORK = "/tmp/biaa-lab-09-{nn:02d}"
os.makedirs(WORK, exist_ok=True)
print("Working dir:", WORK){extra}''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 9.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 5 &middot; Module 9 &mdash; Agents in Finance, Healthcare &amp; Cybersecurity**

### What you'll do
{g}

> **How this lab works (experiential flow):** read the **Concept**, run the **Demo** to see it work, then complete **Your Turn** by replacing every `___` placeholder. Run the **grader** cell at the end &mdash; it prints `[PASS]` / `[FAIL]` / `[TODO]` and a final `Score`. Aim for a full score.

> **Framework note:** the graded steps are **offline &amp; deterministic** (pure Python stdlib); the agent-assembly labs reuse the **LangChain-shaped shim** from Modules 6&ndash;8. Advanced labs end with an **optional** cell that runs the **real** library. You are building the **financial-report insight agent** &mdash; the client's Lab 5.1. It grounds &amp; cites every figure, gives **no advice**, and has **no trade tool** &mdash; a human analyst decides.

**Reference:** [Module 9 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 9 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 9 labs](./index.html) &nbsp;&middot;&nbsp; [Module 9 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def optional_real(intro, body):
    """An OPTIONAL, non-graded cell that runs the SAME shapes against the REAL LangChain."""
    return [md(f'''## Optional &mdash; run this against the REAL LangChain (not graded)
{intro} Safe to skip &mdash; it needs `pip install langchain langchain-ollama` (then
`ollama run llama3.2:1b`) or `langchain-groq` with a `GROQ_API_KEY`. If a package, model or key is
missing the cell prints a friendly note and moves on.
**The graded steps above are offline &amp; deterministic, so the lab always verifies without a model.**'''),
            code(body)]

# ---- shared building blocks (pure stdlib) -------------------------------------------------

# AST-based safe arithmetic -- never bare eval() on free text (this is financial math).
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

# A tiny LangChain-SHAPED shim (same as Modules 6-8). Names & shapes mirror real LangChain.
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
    def __init__(self, agent, tools=None, verbose=False, max_iterations=8):
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

# The financial report fixture -- every figure carries its SOURCE (for grounding & citation).
REPORT_FIXTURE = '''# A small financial report -- each figure carries its SOURCE, so every claim can be cited.
REPORT = {
    "revenue":    {"value": 120.0, "unit": "M", "source": "p4, income stmt"},
    "net_income": {"value": 9.0,   "unit": "M", "source": "p4, income stmt"},
    "total_debt": {"value": 40.0,  "unit": "M", "source": "p7, balance sheet"},
}
PRIOR = {"revenue": 107.1, "net_income": 9.7, "total_debt": 25.0}   # prior period, for YoY'''

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
@lab(1, "lab-01-ground-a-figure", "Beginner",
     "Ground a Figure (Extract + Cite)", 20,
     "Extract a figure AND its source from a report -- the grounding discipline: never reason from memory.",
     ["Grounding", "Citation", "Source of truth"])
def _l1(sol):
    return [
      header(1, "Ground a Figure (Extract + Cite)", "Beginner", 20,
        ["Extract a reported figure together with its source",
         "Check a figure is grounded -- it carries a citation",
         "See why a figure with no source is unusable here"],
        "The domain-agent pattern"),
      setup(1),
      md('''## Concept
In a high-stakes domain the model's memory isn't just unreliable &mdash; it's **dangerous** (deck
slides 4&ndash;5, 14). Every figure must be **grounded**: pulled from the actual document, carrying its
**source** so a human can verify it. A number without a citation is a liability dressed up as an
answer. Here you build the core move &mdash; extract a figure **and** its source.'''),
      shimcell([REPORT_FIXTURE],
        '''print("figures on file:", list(REPORT))
print("revenue entry:", REPORT["revenue"])'''),
      md('''## Your Turn
Complete `extract_figure` (return the figure with its source) and `is_grounded` (it must carry a
citation).'''),
      code(render([
        "def extract_figure(name, report):",
        '    # return the figure dict {value, source} from the report, or None if it is not there',
        {"s": '    return ___   # TODO: look up name in report (None if missing)',
         "a": '    return report.get(name)'},
        "",
        "def is_grounded(fig):",
        '    # grounded = the figure exists AND carries a non-empty source citation',
        {"s": '    return fig is not None and ___   # TODO: it has a truthy "source"',
         "a": '    return fig is not None and bool(fig.get("source"))'},
        "",
        "try:",
        "    rev = extract_figure('revenue', REPORT)",
        "    print('revenue :', rev)",
        "    print('grounded:', is_grounded(rev))",
        "    print('missing :', extract_figure('ebitda', REPORT))",
        "    print('no-source grounded?', is_grounded({'value': 5.0}))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("extract_figure pulls the reported value", lambda: extract_figure("revenue", REPORT)["value"] == 120.0)
expect_true("the figure carries its source", lambda: "source" in extract_figure("revenue", REPORT))
expect_true("a missing figure returns None", lambda: extract_figure("ebitda", REPORT) is None)
expect_true("a real, sourced figure is grounded", lambda: is_grounded(extract_figure("net_income", REPORT)) is True)
expect_true("a figure with no source is NOT grounded", lambda: is_grounded({"value": 5.0}) is False)'''),
      footer(1, "Ground every figure: extract it WITH its source. A number without a citation can't be verified -- and in finance, health or cyber, an unverifiable claim doesn't ship."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-cite-every-claim", "Beginner",
     "Cite Every Claim", 20,
     "Turn a grounded figure into a claim that carries its citation, and check a whole summary is fully cited.",
     ["Citations", "Structured claim", "Auditability"])
def _l2(sol):
    return [
      header(2, "Cite Every Claim", "Beginner", 20,
        ["Build a claim that ties a statement to its value AND source",
         "Check that every claim in a summary is cited",
         "See why one uncited claim breaks auditability"],
        "Auditability: structure & the trail"),
      setup(2),
      md('''## Concept
Auditability means every conclusion is **traceable** (deck slide 15): a regulator or analyst must be
able to see **why** the agent said what it did. So each **claim** is a structured record carrying its
**citation** &mdash; the source it came from. A summary is only auditable if **every** claim is cited;
one uncited number breaks the chain.'''),
      shimcell([REPORT_FIXTURE],
        '''print("we will turn figures into cited claims, e.g.:")
print({"statement": "revenue", "value": 120.0, "source": "p4, income stmt"})'''),
      md('''## Your Turn
Complete `make_claim` (carry the citation) and `all_cited` (every claim must have a source).'''),
      code(render([
        "def make_claim(statement, fig):",
        '    # a claim ties a statement to its grounded value AND its source citation',
        {"s": '    return {"statement": statement, "value": fig["value"], "source": ___}   # TODO: the citation',
         "a": '    return {"statement": statement, "value": fig["value"], "source": fig["source"]}'},
        "",
        "def all_cited(claims):",
        '    # a summary is auditable only if EVERY claim carries a source',
        {"s": '    return ___   # TODO: True if every claim has a truthy "source"',
         "a": '    return all(c.get("source") for c in claims)'},
        "",
        "try:",
        "    c = make_claim('revenue', REPORT['revenue'])",
        "    print('claim:', c)",
        "    good = [make_claim('revenue', REPORT['revenue']), make_claim('net_income', REPORT['net_income'])]",
        "    bad  = good + [{'statement': 'guess', 'value': 5.0, 'source': ''}]",
        "    print('all cited (good)?', all_cited(good))",
        "    print('all cited (bad)? ', all_cited(bad))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("a claim carries its value", lambda: make_claim("revenue", REPORT["revenue"])["value"] == 120.0)
expect_true("a claim carries its source citation", lambda: make_claim("revenue", REPORT["revenue"])["source"] == "p4, income stmt")
expect_true("a claim is machine-readable (a dict)", lambda: isinstance(make_claim("revenue", REPORT["revenue"]), dict))
expect_true("a fully-cited summary passes", lambda: all_cited([make_claim("revenue", REPORT["revenue"]), make_claim("net_income", REPORT["net_income"])]) is True)
expect_true("one uncited claim fails the whole summary", lambda: all_cited([make_claim("revenue", REPORT["revenue"]), {"statement": "guess", "value": 5.0, "source": ""}]) is False)'''),
      footer(2, "Every claim carries its citation, so a human can verify any number in seconds and an auditor can trace it. One uncited claim breaks the chain -- structured, cited output is what makes the agent auditable."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-compute-metrics", "Beginner",
     "Compute Derived Metrics", 25,
     "Compute YoY growth and margin from grounded figures using a safe calculator -- exact financial math.",
     ["Derived metrics", "Safe compute", "YoY & margin"])
def _l3(sol):
    return [
      header(3, "Compute Derived Metrics", "Beginner", 25,
        ["Compute year-over-year growth from grounded figures",
         "Compute a margin as a percentage",
         "Use a safe calculator -- never bare eval on financial input"],
        "The financial-report insight agent, end to end"),
      setup(3),
      md('''## Concept
The insight agent computes the **derived metrics** an analyst cares about (deck slides 7&ndash;8):
**year-over-year growth**, **margins**, notable movements &mdash; all from the **grounded** figures,
never invented. Financial math must be exact and safe, so compute goes through a small **AST-based
safe calculator**, never bare `eval` on model output.'''),
      shimcell([SAFE_CALC, REPORT_FIXTURE],
        '''print("safe compute:", safe_calc("(120-107.1)/107.1*100"), "(revenue YoY %)")'''),
      md('''## Your Turn
Complete `yoy_growth` (percent change) and `margin_pct` (net income over revenue).'''),
      code(render([
        "def yoy_growth(current, prior):",
        '    # percent change year over year, rounded to 1 dp',
        {"s": '    return round(___, 1)   # TODO: (current - prior) / prior * 100',
         "a": '    return round((current - prior) / prior * 100, 1)'},
        "",
        "def margin_pct(net_income, revenue):",
        '    # net margin as a percentage, rounded to 1 dp',
        {"s": '    return round(___, 1)   # TODO: net_income / revenue * 100',
         "a": '    return round(net_income / revenue * 100, 1)'},
        "",
        "try:",
        "    rev_now = REPORT['revenue']['value']; rev_prior = PRIOR['revenue']",
        "    ni_now  = REPORT['net_income']['value']",
        "    print('revenue YoY  :', yoy_growth(rev_now, rev_prior), '%')",
        "    print('net margin   :', margin_pct(ni_now, rev_now), '%')",
        "    print('prior margin :', margin_pct(PRIOR['net_income'], PRIOR['revenue']), '%')",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("revenue YoY is +12.0%", lambda: yoy_growth(120.0, 107.1) == 12.0)
expect_true("a decline gives a negative growth", lambda: yoy_growth(90.0, 100.0) == -10.0)
expect_true("net margin is 7.5%", lambda: margin_pct(9.0, 120.0) == 7.5)
expect_true("the prior margin is ~9.1%", lambda: margin_pct(9.7, 107.1) == 9.1)
expect_true("metrics are grounded in the passed figures (deterministic)", lambda: yoy_growth(120.0, 107.1) == yoy_growth(REPORT["revenue"]["value"], PRIOR["revenue"]))'''),
      footer(3, "Derived metrics come from the grounded figures, computed exactly through a safe calculator. The margin fell from 9.1% to 7.5% even as revenue grew -- exactly the kind of movement the agent must surface next."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-flag-anomalies", "Beginner",
     "Flag Anomalies", 20,
     "Flag notable movements -- a falling margin, a debt spike -- so an analyst's attention goes to what matters.",
     ["Anomaly flags", "Thresholds", "Surface, don't decide"])
def _l4(sol):
    return [
      header(4, "Flag Anomalies", "Beginner", 20,
        ["Flag a margin that declined versus the prior period",
         "Flag a debt level that spiked beyond a threshold",
         "Surface what an analyst should look at -- not a decision"],
        "The financial-report insight agent, end to end"),
      setup(4),
      md('''## Concept
Part of the agent's value is directing a human's attention: **flag** the notable movements &mdash; a
**margin that fell**, **debt that spiked** &mdash; so the analyst spends judgement where it matters
(deck slide 7). A flag is a **signal to look**, never a decision. Thresholds keep it deterministic and
auditable.'''),
      shimcell([REPORT_FIXTURE],
        '''print("this quarter debt:", REPORT["total_debt"]["value"], "M  |  prior:", PRIOR["total_debt"], "M")'''),
      md('''## Your Turn
Complete `analyze_flags`: flag a declining margin and a debt spike (growth over 50%).'''),
      code(render([
        "def analyze_flags(margin_now, margin_prior, debt_growth_pct):",
        "    flags = []",
        {"s": '    if ___:   # TODO: the margin declined vs the prior period',
         "a": '    if margin_now < margin_prior:'},
        '        flags.append("margin_down")',
        {"s": '    if ___:   # TODO: debt grew by more than 50%',
         "a": '    if debt_growth_pct > 50:'},
        '        flags.append("debt_spike")',
        "    return flags",
        "",
        "try:",
        "    print('margin 7.5 vs 9.1, debt +60% ->', analyze_flags(7.5, 9.1, 60))",
        "    print('margin 9.5 vs 9.1, debt +5%  ->', analyze_flags(9.5, 9.1, 5))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("a falling margin is flagged", lambda: "margin_down" in analyze_flags(7.5, 9.1, 10))
expect_true("a stable/rising margin is not flagged", lambda: "margin_down" not in analyze_flags(9.5, 9.1, 10))
expect_true("a debt spike (>50%) is flagged", lambda: "debt_spike" in analyze_flags(9.0, 9.0, 60))
expect_true("modest debt growth is not flagged", lambda: "debt_spike" not in analyze_flags(9.0, 9.0, 20))
expect_true("both conditions raise both flags", lambda: set(analyze_flags(7.5, 9.1, 60)) == {"margin_down", "debt_spike"})'''),
      footer(4, "Flags point the analyst at what matters -- a margin that fell as revenue grew, debt that spiked. They surface, they don't decide; the human judges what the flag means."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-no-advice-guardrail", "Beginner",
     "The No-Advice Guardrail", 20,
     "Detect and block forbidden advice language -- the insight agent informs, it never recommends buying or selling.",
     ["Guardrail", "No advice", "Informational only"])
def _l5(sol):
    return [
      header(5, "The No-Advice Guardrail", "Beginner", 20,
        ["Detect buy/sell/recommend language in a summary",
         "Reject any output that crosses into advice",
         "Keep the agent informational -- analysis, not a recommendation"],
        "The insight agent, in code"),
      setup(5),
      md('''## Concept
The insight agent has a hard boundary (deck slides 6, 9): it **informs** &mdash; it does **not** give
personalized investment advice. Providing buy/sell recommendations is a regulated activity, out of
scope, and dangerous to hand to an LLM. So a guardrail **detects advice language** and rejects it: the
output stays **analysis**, and a human analyst draws any conclusion.'''),
      code('''# Words that turn analysis into (forbidden) advice.
ADVICE_TERMS = ("buy", "sell", "you should", "recommend", "strong buy", "invest in")
print("advice terms to block:", ADVICE_TERMS)'''),
      md('''## Your Turn
Complete `contains_advice` and `enforce_no_advice` (reject a summary that gives advice).'''),
      code(render([
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
        "",
        "try:",
        '    clean  = "Revenue +12% YoY [p4]; net margin down to 7.5% [p4] -- FLAG."',
        '    advice = "Revenue is up -- you should buy this stock now."',
        "    print('clean  ->', enforce_no_advice(clean))",
        "    print('advice ->', enforce_no_advice(advice))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("advice language is detected", lambda: contains_advice("you should buy this stock") is True)
expect_true("an informational summary has no advice", lambda: contains_advice("Revenue +12% YoY [p4]; margin down.") is False)
expect_true("a 'recommend' summary is caught", lambda: contains_advice("We recommend increasing the position.") is True)
expect_true("enforce_no_advice rejects advice", lambda: enforce_no_advice("you should sell now")["ok"] is False)
expect_true("enforce_no_advice passes a clean summary", lambda: enforce_no_advice("Revenue +12% YoY [p4].")["ok"] is True)'''),
      footer(5, "The agent informs, never advises. Detecting and blocking advice language keeps it on the safe, valuable side of the line -- analysis for a human, not a recommendation. Next: the stronger guardrail."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-withhold-the-tool", "Beginner",
     "Withhold the Dangerous Tool", 25,
     "The strongest guardrail: give the agent read/compute tools but NO trade or advice tool -- it cannot act.",
     ["Withhold the tool", "Read-only", "Cannot act"])
def _l6(sol):
    return [
      header(6, "Withhold the Dangerous Tool", "Beginner", 25,
        ["Give the agent only read-only tools (extract, compute)",
         "Confirm it holds no place_trade or give_advice tool",
         "See why withholding the tool beats any prompt instruction"],
        "Assistive on judgement, autonomous on legwork"),
      setup(6),
      md('''## Concept
The strongest guardrail is the simplest (deck slides 9, 17): don't **give** the agent the dangerous
tool. The insight agent gets `extract_figure` and `compute` &mdash; **read-only** &mdash; and there is
**no** `place_trade`, no `give_advice`. Just as the email agent couldn't send, this agent literally
**cannot** trade or advise. Withholding a capability is far stronger than instructing against it.'''),
      code('''FORBIDDEN = {"place_trade", "give_advice", "execute_order", "wire_funds"}
print("tools an insight agent must NEVER hold:", FORBIDDEN)'''),
      md('''## Your Turn
Complete `agent_tools` (read-only) and `can_act` (does the toolset contain a forbidden tool?).'''),
      code(render([
        'FORBIDDEN = {"place_trade", "give_advice", "execute_order", "wire_funds"}',
        "",
        "def agent_tools():",
        '    # read-only: the insight agent may extract and compute, but NOT trade or advise',
        {"s": '    return ___   # TODO: ["extract_figure", "compute"]',
         "a": '    return ["extract_figure", "compute"]'},
        "",
        "def can_act(tools):",
        '    # True if the toolset contains any consequential (forbidden) tool',
        {"s": '    return ___   # TODO: any tool that is in FORBIDDEN',
         "a": '    return any(t in FORBIDDEN for t in tools)'},
        "",
        "try:",
        "    print('tools    :', agent_tools())",
        "    print('can act? :', can_act(agent_tools()))",
        "    print('if given a trade tool:', can_act(agent_tools() + ['place_trade']))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the toolset has extract_figure & compute", lambda: set(agent_tools()) == {"extract_figure", "compute"})
expect_true("the toolset holds NO place_trade", lambda: "place_trade" not in agent_tools())
expect_true("the read-only agent cannot act", lambda: can_act(agent_tools()) is False)
expect_true("adding a trade tool would let it act", lambda: can_act(agent_tools() + ["place_trade"]) is True)
expect_true("giving advice is also forbidden", lambda: can_act(["give_advice"]) is True)'''),
      footer(6, "In a high-stakes domain your strongest safety control is the tool you DON'T provide. Read-only tools mean the agent can analyse all day and still cannot trade or advise -- the guardrail is the missing capability."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-validate-grounding", "Intermediate",
     "Validate Grounding", 30,
     "Before shipping a summary, validate that every claim is grounded and cites the RIGHT source.",
     ["Validation", "Grounding check", "Right source"])
def _l7(sol):
    return [
      header(7, "Validate Grounding", "Intermediate", 30,
        ["Check every claim maps to a real figure in the report",
         "Check each claim cites the correct source",
         "Refuse to ship a summary with an ungrounded claim"],
        "Grounding: RAG & citations"),
      setup(7),
      md('''## Concept
Never ship an ungrounded claim (deck slides 4, 8, 14). Before the summary goes to an analyst, the agent
**validates** it: every claim must map to a **real figure** in the report, and it must cite the
**correct source**. A claim that cites the wrong page, or a figure that isn't in the report, is a
grounding failure &mdash; don't ship it.'''),
      shimcell([REPORT_FIXTURE],
        '''print("a claim must match REPORT[metric] on BOTH value-source and source string")'''),
      md('''## Your Turn
Complete `validate_summary`: collect an ungrounded claim and a wrong-source claim.'''),
      code(render([
        "def validate_summary(claims, report):",
        "    problems = []",
        "    for c in claims:",
        "        fig = report.get(c['metric'])",
        "        if fig is None:",
        {"s": '            problems.append("ungrounded: " + c["metric"])   # TODO: keep this line',
         "a": '            problems.append("ungrounded: " + c["metric"])'},
        {"s": '        elif ___:   # TODO: the claim cites a source that does not match the report',
         "a": '        elif c["source"] != fig["source"]:'},
        '            problems.append("wrong source: " + c["metric"])',
        {"s": '    return {"ok": ___, "problems": problems}   # TODO: ok = no problems',
         "a": '    return {"ok": len(problems) == 0, "problems": problems}'},
        "",
        "try:",
        "    good = [{'metric': 'revenue', 'source': 'p4, income stmt'}]",
        "    ungrounded = [{'metric': 'ebitda', 'source': 'p9'}]",
        "    wrong = [{'metric': 'revenue', 'source': 'p1, cover'}]",
        "    print('good      ->', validate_summary(good, REPORT))",
        "    print('ungrounded->', validate_summary(ungrounded, REPORT))",
        "    print('wrong src ->', validate_summary(wrong, REPORT))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("a correctly-grounded summary passes", lambda: validate_summary([{"metric": "revenue", "source": "p4, income stmt"}], REPORT)["ok"] is True)
expect_true("a claim about a missing figure is caught", lambda: any("ungrounded" in p for p in validate_summary([{"metric": "ebitda", "source": "p9"}], REPORT)["problems"]))
expect_true("a wrong-source citation is caught", lambda: any("wrong source" in p for p in validate_summary([{"metric": "revenue", "source": "p1, cover"}], REPORT)["problems"]))
expect_true("ok is False when any problem exists", lambda: validate_summary([{"metric": "ebitda", "source": "p9"}], REPORT)["ok"] is False)
expect_true("multiple problems are all collected", lambda: len(validate_summary([{"metric": "ebitda", "source": "p9"}, {"metric": "revenue", "source": "wrong"}], REPORT)["problems"]) == 2)'''),
      footer(7, "Validation is the gate before an analyst sees the summary: every claim must map to a real figure and cite the right source. An ungrounded or mis-cited claim doesn't ship -- that's the high-stakes bar."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-audit-trail", "Intermediate",
     "The Audit Trail", 30,
     "Log the whole run -- trigger, figures pulled, reasoning, output -- into a replayable, fully-sourced trail.",
     ["Audit trail", "Replayable", "Fully sourced"])
def _l8(sol):
    return [
      header(8, "The Audit Trail", "Intermediate", 30,
        ["Record each step of the run with its detail and source",
         "Read back the ordered trail for replay",
         "Check every figure step carries a source"],
        "Auditability: structure & the trail"),
      setup(8),
      md('''## Concept
In a regulated domain you must be able to **prove** how the agent reached its conclusion (deck slides
15, 19). The **audit trail** logs the whole run &mdash; the trigger, every figure pulled and its
source, the reasoning, the output, the human decision &mdash; so the run is **replayable** and every
figure is **traceable**. It's also how you debug and improve the agent.'''),
      code('''# One entry per step: what happened, and (for a figure) where it came from.
print("an entry:", {"step": "figure", "detail": "revenue=120.0M", "source": "p4, income stmt"})'''),
      md('''## Your Turn
Complete `AuditTrail`: record entries, read back the steps, and check every figure is sourced.'''),
      code(render([
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
        "",
        "try:",
        "    t = AuditTrail()",
        "    t.record('trigger', 'analyze Q3 report')",
        "    t.record('figure', 'revenue=120.0M', 'p4, income stmt')",
        "    t.record('figure', 'net_income=9.0M', 'p4, income stmt')",
        "    t.record('output', 'summary + needs_review')",
        "    print('steps        :', t.steps())",
        "    print('fully sourced:', t.fully_sourced())",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("record appends an entry", lambda: (lambda t: (t.record("trigger", "x"), len(t.entries))[1])(AuditTrail()) == 1)
expect_true("steps are read back in order", lambda: (lambda t: [t.record(s, "d") for s in ("trigger", "figure", "output")] and t.steps())(AuditTrail()) == ["trigger", "figure", "output"])
expect_true("a run whose figures are all sourced passes", lambda: (lambda t: (t.record("figure", "rev", "p4"), t.fully_sourced())[1])(AuditTrail()) is True)
expect_true("a figure with no source fails the check", lambda: (lambda t: (t.record("figure", "rev", None), t.fully_sourced())[1])(AuditTrail()) is False)
expect_true("the trail is replayable (entries preserved)", lambda: (lambda t: [t.record("figure", "rev", "p4"), t.record("output", "sum")] and len(t.entries))(AuditTrail()) == 2)'''),
      footer(8, "The audit trail makes the whole run replayable and every figure traceable -- what a regulator needs and what lets you debug the agent. Structured claims make each answer checkable; the trail makes the run accountable."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-privacy-redaction", "Intermediate",
     "Privacy: Minimize & Redact", 30,
     "Minimize what you send the model and redact sensitive identifiers -- data handling as a first-class concern.",
     ["Privacy", "Minimize", "Redaction"])
def _l9(sol):
    return [
      header(9, "Privacy: Minimize & Redact", "Intermediate", 30,
        ["Redact long identifiers (account/card numbers) from text",
         "Send the model only the fields the task needs",
         "Treat data handling as a first-class design constraint"],
        "Privacy, compliance & data handling"),
      setup(9),
      md('''## Concept
High-stakes agents run on the most sensitive data there is (deck slide 16). Two disciplines: **minimize**
&mdash; send the model only the fields the task needs, not the whole record &mdash; and **redact** &mdash;
mask identifiers (account numbers, card numbers) before they leave your systems. Less exposed data is
less risk. It's why Day 1 started on **local models**.'''),
      code('''# We mask any run of 6+ consecutive digits (account/card numbers), keeping short numbers like a year.
print("redact 'acct 1234567890 for FY2026' -> mask the long number, keep 2026")'''),
      md('''## Your Turn
Complete `redact_account` (mask long digit runs) and `minimize` (keep only needed fields).'''),
      code(render([
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
        '    # send the model ONLY the fields the task needs',
        {"s": '    return {k: record[k] for k in needed_fields if k in record}   # TODO',
         "a": '    return {k: record[k] for k in needed_fields if k in record}'},
        "",
        "try:",
        "    print(redact_account('acct 1234567890 for FY2026'))",
        "    rec = {'name': 'ACME', 'revenue': 120.0, 'account': '1234567890', 'ssn': '999-99-9999'}",
        "    print(minimize(rec, ['name', 'revenue']))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("a 10-digit account number is masked", lambda: "[REDACTED]" in redact_account("acct 1234567890 here"))
expect_true("a short number (a year) is kept", lambda: "2026" in redact_account("for FY2026"))
expect_true("the redacted text has no long digit run", lambda: not any(len(w) >= 6 and w.isdigit() for w in redact_account("acct 1234567890").split()))
expect_true("minimize keeps only the needed fields", lambda: minimize({"name": "ACME", "revenue": 120.0, "account": "1234567890"}, ["name", "revenue"]) == {"name": "ACME", "revenue": 120.0})
expect_true("minimize drops the sensitive fields", lambda: "account" not in minimize({"name": "ACME", "account": "1234567890", "ssn": "999-99-9999"}, ["name"]))'''),
      footer(9, "Minimize what you send and redact identifiers before they leave your systems. Data handling is a first-class design constraint -- decide where the data can go before you build, which is why this course runs on local models."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-assistive-not-autonomous", "Advanced",
     "Assistive, Not Autonomous", 40,
     "Make the agent recommend but never decide -- flag for review, require citations, and keep the human in charge.",
     ["Assistive", "needs_review", "Automation bias"])
def _l10(sol):
    return [
      header(10, "Assistive, Not Autonomous", "Advanced", 40,
        ["Return analysis flagged for review -- never a decision",
         "Require every claim to be cited so review is genuine",
         "Keep a human as the owner of any consequential decision"],
        "Assistive on judgement, autonomous on legwork"),
      setup(10),
      md('''## Concept
The golden rule of Day 5 (deck slides 11, 17): agents are **assistive, not autonomous**. The insight
agent does the grounded legwork and returns analysis flagged **`needs_review`** &mdash; it never
decides. And to defend against **automation bias** (humans rubber-stamping a confident machine), the
review is only real if the agent **shows its work**: every claim **cited**. The **human** owns any
consequential decision.'''),
      code('''# The agent's output is analysis + a needs_review flag -- never "executed" or a recommendation.
print("assistive output shape:", {"summary": "...", "status": "needs_review", "claims": ["..."]})'''),
      md('''## Your Turn
Complete `make_insight` (flag for review), `reviewable` (require citations), and `owns_decision`.'''),
      code(render([
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
        '    # who owns any consequential decision -- never the agent',
        {"s": '    return ___   # TODO: "human"',
         "a": '    return "human"'},
        "",
        "try:",
        "    claims = [{'metric': 'revenue', 'source': 'p4'}, {'metric': 'margin', 'source': 'p4'}]",
        "    ins = make_insight('Revenue +12% YoY [p4]; margin down [p4].', claims)",
        "    print('status    :', ins['status'])",
        "    print('reviewable:', reviewable(ins))",
        "    print('decides   :', owns_decision(ins))",
        "    uncited = make_insight('...', [{'metric': 'guess', 'source': ''}])",
        "    print('uncited reviewable?', reviewable(uncited))",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the output is flagged needs_review", lambda: make_insight("s", [])["status"] == "needs_review")
expect_true("the agent never marks a decision as executed", lambda: make_insight("s", [])["status"] != "executed")
expect_true("a fully-cited insight is genuinely reviewable", lambda: reviewable(make_insight("s", [{"metric": "revenue", "source": "p4"}])) is True)
expect_true("an uncited claim makes review a rubber-stamp (not reviewable)", lambda: reviewable(make_insight("s", [{"metric": "guess", "source": ""}])) is False)
expect_true("a human owns the decision", lambda: owns_decision(make_insight("s", [])) == "human")''')
      ,
      *optional_real(
        "See how the real LangChain exposes structured, citable output (the shape a human reviews).",
        '''try:
    from langchain_core.output_parsers import JsonOutputParser
    print("Real LangChain: bind a schema (e.g. Pydantic) so the model MUST return {summary, claims[], each cited}.")
    print("JsonOutputParser / with_structured_output enforce the shape a human reviews -- citations included.")
    print("Attach a Langfuse/LangSmith callback and the whole assistive run is logged for audit.")
except Exception as e:
    print("Install langchain-core to explore structured output -- skipping:", type(e).__name__)
print("The assistive, needs_review, fully-cited output above already runs offline.")'''),
      footer(10, "Assistive, not autonomous: the agent flags analysis for review and never decides, and citations make the review genuine rather than a rubber-stamp. The human owns every consequential decision."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-assemble-insight-agent", "Advanced",
     "Assemble the Insight Agent", 35,
     "Wire read-only extract & compute tools (NO trade tool) into an executor that grounds, cites, and flags for review.",
     ["create_react_agent", "Read-only tools", "needs_review"])
def _l11(sol):
    return [
      header(11, "Assemble the Insight Agent", "Advanced", 35,
        ["Assemble read-only tools + model + prompt into an executor",
         "Withhold any trade/advice tool so it cannot act",
         "Return a grounded, cited insight flagged needs_review"],
        "The financial-report insight agent, end to end"),
      setup(11),
      md('''## Concept
Now assemble the insight agent from Modules 6&ndash;8 pieces (deck slides 7&ndash;9): `@tool`
**read-only** tools (`extract_figure`, `compute`), `create_react_agent`, an `AgentExecutor`. The
scripted model grounds a figure, computes a metric, and drafts a **cited** Final Answer. The design
choice: the tools list is **read-only** &mdash; no `place_trade`, no `give_advice` &mdash; and the
output is flagged **`needs_review`** for a human analyst.'''),
      shimcell([SAFE_CALC, LC_TOOL, LC_MODEL, LC_PROMPT, LC_EXEC, REPORT_FIXTURE],
        '''@tool
def extract_figure(name):
    """Pull a reported figure and its source from the filing."""
    return REPORT.get(name, {})
@tool
def compute(expression):
    """Do exact arithmetic on a financial expression."""
    return safe_calc(expression)
print("read-only tools ready:", extract_figure.name, "&", compute.name)'''),
      md('''## Your Turn
Complete `make_insight_agent` (read-only tools + step cap) and `analyze_report` (flag needs_review).'''),
      code(render([
        "SCRIPT = [",
        '    "Thought: get revenue, grounded.\\nAction: extract_figure\\nAction Input: revenue",',
        '    "Thought: compute YoY vs 107.1.\\nAction: compute\\nAction Input: (120-107.1)/107.1*100",',
        '    "Thought: draft a cited insight.\\nFinal Answer: Revenue 120.0M [p4, income stmt], +12.0% YoY.",',
        "]",
        "",
        "def make_insight_agent(max_iterations=8):",
        "    model  = FakeChatModel(SCRIPT)",
        '    prompt = PromptTemplate.from_template("Report: {input}\\n{scratchpad}")',
        {"s": '    tools  = ___   # TODO: read-only -- [extract_figure, compute], NO trade/advice tool',
         "a": '    tools  = [extract_figure, compute]'},
        "    agent  = create_react_agent(model, tools, prompt)",
        {"s": '    return AgentExecutor(agent, max_iterations=___)   # TODO: the step cap',
         "a": '    return AgentExecutor(agent, max_iterations=max_iterations)'},
        "",
        "def analyze_report(report_name):",
        '    result = make_insight_agent().invoke({"input": report_name})',
        '    # analysis only: flag for a human analyst, never a decision',
        {"s": '    return {"insight": result["output"], "status": ___,   # TODO: needs_review',
         "a": '    return {"insight": result["output"], "status": "needs_review",'},
        '            "tools_used": [s[0] for s in result["intermediate_steps"]]}',
        "",
        "try:",
        "    out = analyze_report('ACME Q3')",
        "    print('tools used:', out['tools_used'])",
        "    print('status    :', out['status'])",
        "    print('insight   :', out['insight'])",
        "    print('has trade tool?', 'place_trade' in [t.name for t in make_insight_agent().tools.values()])",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the agent grounds via extract_figure first", lambda: analyze_report("x")["tools_used"][0] == "extract_figure")
expect_true("it then computes a metric", lambda: "compute" in analyze_report("x")["tools_used"])
expect_true("the insight cites its source", lambda: "p4" in analyze_report("x")["insight"])
expect_true("the output is needs_review, never a decision", lambda: analyze_report("x")["status"] == "needs_review")
expect_true("the agent holds NO trade tool", lambda: "place_trade" not in [t.name for t in make_insight_agent().tools.values()])'''),
      *optional_real(
        "Swap the scripted model for a REAL LangChain agent (Ollama llama3.2:1b, or Groq) -- read-only, grounded.",
        '''try:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.2:1b")
    out = llm.invoke("Summarize in one line, cite the page: revenue 120M on p4, up 12% YoY. Give NO advice.").content
    print("REAL insight draft:", out)
    print("In production: bind extract_figure/compute (read-only) with create_react_agent + AgentExecutor,")
    print("and simply DON'T include a trade or advice tool -- the agent can analyse but cannot act.")
except Exception as e:
    print("No local LLM available -- skipping (pip install langchain langchain-ollama + `ollama run llama3.2:1b`,")
    print("or langchain-groq with GROQ_API_KEY):", type(e).__name__)
    print("The offline agent above already produced a grounded, cited, needs_review insight.")'''),
      footer(11, "Same executor as Module 6, pointed at a filing -- and the guardrail is what's MISSING from the tools list. The agent grounds, computes and cites; it cannot trade or advise. Next: run it over a suite."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-insight-agent", "Advanced",
     "Capstone: The Financial-Report Insight Agent", 45,
     "Run the full insight agent over a suite of reports: ground, compute, cite, validate, flag -- no advice, no trade.",
     ["End-to-end agent", "Report suite", "Cited & assistive"])
def _l12(sol):
    return [
      header(12, "Capstone: The Financial-Report Insight Agent", "Advanced", 45,
        ["Chain ground -> compute -> cite -> validate into one analyzer",
         "Reject any output with advice or an uncited claim",
         "Run it over a SUITE of reports and score it"],
        "The financial-report insight agent, end to end"),
      setup(12),
      md('''## Concept
Capstone: the **financial-report insight agent** (the client's Lab 5.1), end to end. For each report
it **grounds** the figures, **computes** the metrics, builds a **cited** summary, **validates** that
every claim is cited and contains **no advice**, and returns it flagged **`needs_review`** for an
analyst &mdash; never a decision, never a trade. You run it over a **suite** of reports and score the
outcomes. The helpers below are the ones you built through the module.'''),
      shimcell([REPORT_FIXTURE],
        '''# The pieces you built this module, provided so you can assemble the whole agent.
def margin_pct(ni, rev):
    return round(ni / rev * 100, 1)
def build_summary(report):
    rev, ni = report["revenue"], report["net_income"]
    m = margin_pct(ni["value"], rev["value"])
    return ("Revenue " + str(rev["value"]) + "M [" + rev["source"] + "]; "
            "net margin " + str(m) + "% [" + ni["source"] + "].")
def claims_of(report):
    return [{"metric": "revenue", "source": report["revenue"]["source"]},
            {"metric": "net_income", "source": report["net_income"]["source"]}]
ADVICE_TERMS = ("buy", "sell", "recommend", "you should", "invest in")
print("helpers ready: build_summary, claims_of, margin_pct")'''),
      md('''## Your Turn
Assemble `process` (summary + cited + no-advice -> status) and `evaluate` (score the suite).'''),
      code(render([
        "def process(report):",
        "    summary = build_summary(report)",
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
        '    {"revenue": {"value": 120.0, "source": "p4"}, "net_income": {"value": 9.0, "source": "p4"}},',
        '    {"revenue": {"value": 80.0,  "source": "p3"}, "net_income": {"value": 12.0, "source": "p3"}},',
        "]",
        "",
        "def evaluate():",
        '    # a report is handled well if it is cited, advice-free, and flagged needs_review',
        {"s": '    ok = ___   # TODO: count reports where cited and status == "needs_review"',
         "a": '    ok = sum(1 for r in SUITE if process(r)["cited"] and process(r)["status"] == "needs_review")'},
        "    return ok, len(SUITE)",
        "",
        "try:",
        "    for r in SUITE:",
        "        out = process(r)",
        "        print(out['status'], '| cited:', out['cited'], '->', out['summary'][:52])",
        "    print('score:', evaluate())",
        "except Exception as e:",
        "    print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("every figure in the summary is cited", lambda: process(SUITE[0])["cited"] is True)
expect_true("the summary contains no advice language", lambda: process(SUITE[0])["advice"] is False)
expect_true("the output is needs_review, never a decision or trade", lambda: process(SUITE[0])["status"] == "needs_review")
expect_true("a report becomes a cited summary", lambda: "p4" in process(SUITE[0])["summary"])
expect_true("an uncited/advice output would be rejected", lambda: process({"revenue": {"value": 1.0, "source": ""}, "net_income": {"value": 1.0, "source": "p1"}})["status"] == "rejected")
expect_true("the agent handles the whole suite well", lambda: evaluate() == (2, 2))'''),
      *optional_real(
        "Swap the scripted pieces for a REAL LangChain insight agent (Ollama / Groq) -- the bridge to Module 10.",
        '''try:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.2:1b")
    out = llm.invoke("One-line, cite pages, NO advice: revenue 120M (p4), net income 9M (p4).").content
    print("REAL cited insight:\\n", out)
    print("\\nProduction shape: ground (tools/RAG) -> compute -> cite -> validate (grounded, no advice) ->")
    print("needs_review -> a human analyst decides. No trade tool, ever.")
    print("Next: Module 10 -- ethics & responsible AI: bias, transparency, safety and accountability.")
except Exception as e:
    print("No local LLM available -- skipping (pip install langchain langchain-ollama + `ollama run llama3.2:1b`,")
    print("or langchain-groq with GROQ_API_KEY):", type(e).__name__)
    print("The offline insight agent above already ran the suite -- grounded, cited, advice-free, needs_review.")
    print("Next: Module 10 -- ethics & responsible AI.")'''),
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
