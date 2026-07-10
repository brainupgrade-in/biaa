# -*- coding: utf-8 -*-
# Run gen_labs.py first (it writes _meta.json beside this script), then this.
import json, os
_HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(_HERE)  # the module-9 dir (parent of _generators)
meta = json.load(open(os.path.join(_HERE, "_meta.json")))
order = sorted(meta, key=lambda k: int(k))
total_min = sum(meta[k]["mins"] for k in order)
by = {"Beginner": [], "Intermediate": [], "Advanced": []}
for k in order: by[meta[k]["level"]].append(k)

LEVELBADGE = {"Beginner": ("beg", "Beginner"), "Intermediate": ("int", "Intermediate"), "Advanced": ("adv", "Advanced")}

def card(k):
    m = meta[k]
    lv = LEVELBADGE[m["level"]][0]
    concepts = "".join(f'<span class="chip">{c}</span>' for c in m["concepts"])
    return f'''      <div class="lab {lv}">
        <div class="lab-top">
          <span class="num">Lab 9.{k}</span>
          <span class="time">&#9201; {m["mins"]} min</span>
        </div>
        <h4>{m["title"]}</h4>
        <p>{m["summary"]}</p>
        <div class="chips">{concepts}</div>
        <div class="links">
          <a class="open" href="{m["slug"]}.ipynb">&#9654; Open lab</a>
          <a class="sol" href="solutions/{m["slug"]}.ipynb">Solution</a>
        </div>
      </div>'''

def section(level):
    ks = by[level]
    mins = sum(meta[k]["mins"] for k in ks)
    lv = LEVELBADGE[level][0]
    cards = "\n".join(card(k) for k in ks)
    return f'''    <section>
      <h2><span class="dot {lv}"></span>{level} <span class="scount">{len(ks)} labs &middot; ~{mins} min</span></h2>
      <div class="grid">
{cards}
      </div>
    </section>'''

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Day 5 &middot; Module 9 &mdash; Hands-on Labs</title>
  <style>
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background:#f5f6fb; color:#1e1f33; font-size:14px; line-height:1.45; }}
    a {{ color:#4f46e5; }}
    header {{ background:linear-gradient(135deg,#1e1b4b 0%,#312e81 100%); color:#fff; padding:24px 20px; text-align:center; border-bottom:3px solid #06b6d4; }}
    header h1 {{ margin:0; font-size:1.6em; }}
    header .tagline {{ margin-top:6px; color:#a5b4fc; font-weight:600; }}
    header .meta {{ margin-top:10px; color:#cbd0e8; font-size:.9em; }}
    header .meta span {{ margin:0 7px; }}
    header .meta .k {{ color:#67e8f9; font-weight:600; }}
    .home {{ position:absolute; top:14px; right:18px; font-size:.78rem; background:rgba(255,255,255,.92); border:1px solid #d8dcf0; color:#312e81; padding:5px 12px; border-radius:14px; text-decoration:none; font-weight:600; }}
    .container {{ max-width:1080px; margin:16px auto; background:#fff; padding:18px 26px 28px; box-shadow:0 0 10px rgba(0,0,0,.08); }}
    .callout {{ background:#eef2ff; border:1px solid #a5b4fc; border-left:4px solid #4f46e5; border-radius:6px; padding:12px 16px; font-size:.92em; margin:14px 0; }}
    .callout.warn {{ background:#fffbeb; border-color:#f59e0b; border-left-color:#f59e0b; }}
    .callout code {{ background:#e0e7ff; padding:1px 5px; border-radius:4px; font-size:.92em; }}
    h2 {{ display:flex; align-items:center; gap:10px; font-size:1.2em; color:#312e81; border-bottom:2px solid #06b6d4; padding-bottom:6px; margin:22px 0 14px; }}
    h2 .scount {{ font-size:.6em; color:#5b5f7a; font-weight:500; margin-left:auto; }}
    .dot {{ width:12px; height:12px; border-radius:50%; display:inline-block; }}
    .dot.beg {{ background:#059669; }} .dot.int {{ background:#f59e0b; }} .dot.adv {{ background:#dc2626; }}
    .grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }}
    @media(max-width:860px) {{ .grid {{ grid-template-columns:1fr; }} }}
    .lab {{ border:1px solid #e2e5f3; border-top:4px solid #4f46e5; border-radius:8px; padding:12px 14px; display:flex; flex-direction:column; background:#fcfcff; }}
    .lab.beg {{ border-top-color:#059669; }} .lab.int {{ border-top-color:#f59e0b; }} .lab.adv {{ border-top-color:#dc2626; }}
    .lab-top {{ display:flex; justify-content:space-between; align-items:center; }}
    .lab .num {{ font-weight:700; color:#312e81; font-size:.82em; letter-spacing:.02em; }}
    .lab .time {{ font-size:.74em; color:#5b5f7a; }}
    .lab h4 {{ margin:6px 0 4px; font-size:1em; color:#1e1b4b; line-height:1.25; }}
    .lab p {{ margin:0 0 8px; font-size:.86em; color:#3a3c57; flex:1; }}
    .chips {{ margin-bottom:10px; }}
    .chip {{ display:inline-block; background:#eef2ff; color:#4338ca; border:1px solid #c7d2fe; border-radius:10px; font-size:.68em; padding:1px 8px; margin:0 4px 4px 0; }}
    .links {{ display:flex; gap:8px; }}
    .links a {{ text-decoration:none; font-size:.8em; font-weight:600; padding:5px 10px; border-radius:6px; }}
    .links .open {{ background:#4f46e5; color:#fff; flex:1; text-align:center; }}
    .links .open:hover {{ background:#4338ca; }}
    .links .sol {{ background:#fff; color:#5b5f7a; border:1px solid #d8dcf0; }}
    .links .sol:hover {{ border-color:#a5b4fc; color:#4f46e5; }}
    footer {{ background:#1e1b4b; color:#fff; text-align:center; padding:16px; font-size:.85em; margin-top:8px; }}
    footer a {{ color:#a5b4fc; text-decoration:none; }}
  </style>
</head>
<body>
  <header>
    <a class="home" href="../../course-outline-building-intelligent-ai-agents.html">&#8962; Course outline</a>
    <h1>Day 5 &middot; Module 9 &mdash; Hands-on Labs</h1>
    <div class="tagline">Agents in Finance, Healthcare &amp; Cybersecurity &mdash; build the financial-report insight agent</div>
    <div class="meta">
      <span class="k">{len(order)} labs</span> |
      <span>{len(by["Beginner"])} Beginner &middot; {len(by["Intermediate"])} Intermediate &middot; {len(by["Advanced"])} Advanced</span> |
      <span class="k">~{total_min//60}h {total_min%60}m total</span> |
      <span>Experiential: concept &rarr; demo &rarr; practice</span>
    </div>
  </header>

  <div class="container">
    <div class="callout">
      <strong>How these labs work.</strong> Each notebook follows the same rhythm &mdash; read the
      <strong>Concept</strong>, run the <strong>Demo</strong>, then complete <strong>Your Turn</strong> by
      replacing every <code>___</code> placeholder. Run the <strong>grader</strong> cell at the bottom: it
      prints <code>[PASS]</code> / <code>[FAIL]</code> / <code>[TODO]</code> and a final <code>Score</code>.
      Each lab writes to its own <code>/tmp/biaa-lab-09-NN/</code> working dir. Stuck? Every lab has a full
      answer key under <a href="solutions/"><code>solutions/</code></a> &mdash; try first, then check.
    </div>
    <div class="callout warn">
      <strong>Setup.</strong> These labs use the <strong>real LangChain</strong> (<code>langchain</code>,
      <code>langchain-core</code>, <code>langchain-ollama</code> &mdash; all in the course
      <code>biaa-venv</code>). You build the <strong>financial-report insight agent</strong>
      (the client&rsquo;s Lab 5.1) piece by piece: ground &amp; cite every figure, compute derived metrics,
      flag anomalies, the <strong>no-advice guardrail</strong>, <strong>withholding the trade tool</strong>,
      grounding validation, the audit trail, privacy/redaction, and assistive-not-autonomous. The
      agent-assembly labs bind real <code>@tool</code> functions with <code>create_agent</code>. The
      <strong>graded</strong> cells assert only on the deterministic parts you build (grounding/citation
      logic, tool wiring, the read-only guardrail) and <strong>never call an LLM</strong>, so they verify
      offline with <strong>no API keys and no network</strong>. Financial math uses a small
      <strong>AST-based safe evaluator</strong> (never bare <code>eval</code>). Cells marked
      <em>Optional &mdash; run it for real</em> call a live local model (<code>ollama run llama3.2:1b</code>,
      or <code>ChatGroq</code> with a <code>GROQ_API_KEY</code>) and self-skip if none is reachable.
    </div>
    <div class="callout" style="border-left-color:#dc2626;background:#fef2f2;border-color:#fca5a5">
      &#128737;&#65039; <strong>Responsible-AI note.</strong> The insight agent is <strong>informational
      only</strong>. It grounds &amp; <strong>cites</strong> every figure, gives <strong>no investment
      advice</strong>, and has <strong>no trade tool</strong> &mdash; a human analyst reviews and decides.
      That guardrail (assistive, not autonomous) is the point of the module, not a limitation.
    </div>

{section("Beginner")}

{section("Intermediate")}

{section("Advanced")}

    <div class="callout" style="margin-top:22px">
      &#128218; <strong>Reference material:</strong>
      <a href="../../presentation/day5-module9-agents-in-industry.html">Module 9 slides &mdash; Agents in Finance, Healthcare &amp; Cybersecurity</a>
      &middot; <a href="../../course-outline-building-intelligent-ai-agents.html">Full course outline</a>
      &middot; <a href="../module-8/index.html">Module 8 labs</a>.
      These labs build the insight agent offline &amp; deterministically; the <em>optional</em> cells run the
      genuine library. Next &mdash; <strong>Module 10</strong>: ethics &amp; responsible AI &mdash; bias,
      transparency, safety, accountability &amp; debugging.
    </div>
  </div>

  <footer>
    &copy; 2026 Gheware DevOps &amp; Agentic AI |
    <a href="https://devops.gheware.com">devops.gheware.com</a> |
    Trainer: Rajesh Gheware |
    Building Intelligent AI Agents &middot; Day 5 Module 9 Labs v1.0
  </footer>
</body>
</html>'''

open(os.path.join(D, "index.html"), "w").write(html)
print("wrote index.html  | total labs:", len(order), "| total minutes:", total_min)
