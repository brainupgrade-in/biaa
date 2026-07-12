# -*- coding: utf-8 -*-
"""Generator for Day 1 Module 1 hands-on labs (12 notebooks + index.html).
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR (for verification)."""
import json, os, sys

# Defaults: write student notebooks into the module-1 dir (parent of _generators),
# solutions into module-1/solutions. Override by passing OUT_DIR [SOL_DIR] as args.
_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day1-module1-understanding-ai-and-its-evolution.html"
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
        if isinstance(ln, dict):
            out.append(ln["a"] if sol else ln["s"])
        else:
            out.append(ln)
    return "\n".join(out)

# Standard grader preamble (inlined in each grader cell)
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
WORK = os.path.join(os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp", "biaa-lab-01-{nn:02d}")
os.makedirs(WORK, exist_ok=True)
print("Working dir:", WORK){extra}''')

def header(nn, title, level, mins, goals, concept_slide):
    badge = {"Beginner": "🟢 Beginner", "Intermediate": "🟡 Intermediate", "Advanced": "🔴 Advanced"}[level]
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 1.{nn} &mdash; {title}

**Level:** {badge} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 1 &middot; Module 1 &mdash; Understanding AI &amp; its Evolution**

### What you'll do
{g}

> **How this lab works (experiential flow):** read the **Concept**, run the **Demo** to see it work, then complete **Your Turn** by replacing every `___` placeholder. Run the **grader** cell at the end &mdash; it prints `[PASS]` / `[FAIL]` / `[TODO]` and a final `Score`. Aim for a full score.

**Reference:** [Module 1 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 1 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 1 labs](./index.html) &nbsp;&middot;&nbsp; [Module 1 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

NB = {}  # name -> (level, title, mins, summary, concepts, build_fn)

def lab(nn, slug, level, title, mins, summary, concepts):
    def deco(fn):
        NB[nn] = dict(slug=slug, level=level, title=title, mins=mins,
                      summary=summary, concepts=concepts, build=fn)
        return fn
    return deco

# ============================================================ LAB 01
@lab(1, "lab-01-rules-vs-learning", "Beginner",
     "Rules vs. Learning: your first AI", 20,
     "Hand-write a rule-based spam filter, feel where rules break, and see why modern AI learns from data instead.",
     ["Rule-based AI", "Why we shifted to learning from data"])
def _l1(sol):
    cells = [
      header(1, "Rules vs. Learning: your first AI", "Beginner", 20,
        ["See how 'classic' AI worked: humans writing explicit if-then rules",
         "Build a keyword spam filter and measure its accuracy",
         "Feel the brittleness that pushed the field toward machine learning"],
        "The shift, in code"),
      setup(1),
      md('''## Concept
The earliest AI was **symbolic** &mdash; humans wrote the rules by hand. It works until the
world gets messy. Below, a tiny spam filter built from keyword rules. Watch where it slips.'''),
      code('''# DEMO -- a hand-written rule
def demo_is_spam(msg):
    bad = ["winner", "lottery"]
    return 1 if any(w in msg.lower() for w in bad) else 0

for m in ["You are a LOTTERY winner", "Lunch at noon?", "limited offer, act now"]:
    print(demo_is_spam(m), "<--", m)
# Note: "limited offer, act now" is spam but slips through. Rules miss cases.'''),
      md('''## Your Turn
Make the filter better by (a) choosing good **spam keywords** and (b) a sensible **threshold**
(how many keyword hits = spam). Replace each `___`.'''),
      code(render([
        "# labelled data: (message, 1=spam / 0=ham)",
        "DATA = [",
        '    ("congratulations you won a free prize claim now", 1),',
        '    ("are we still on for lunch tomorrow", 0),',
        '    ("cheap meds click this link now", 1),',
        '    ("project status update attached", 0),',
        '    ("you have won a lottery claim your reward", 1),',
        '    ("can you review the report by friday", 0),',
        "]",
        "",
        "# (a) list of lower-case spam keywords  (b) hits needed to call it spam",
        {"s": 'SPAM_WORDS = "___"   # TODO: e.g. ["free", "prize", ...]',
         "a": 'SPAM_WORDS = ["free", "prize", "claim", "now", "cheap", "click", "won", "lottery", "reward"]'},
        {"s": 'THRESHOLD  = "___"   # TODO: a whole number, e.g. 2',
         "a": 'THRESHOLD  = 2'},
        "",
        "def is_spam(msg):",
        "    text = msg.lower()",
        "    hits = sum(1 for w in SPAM_WORDS if w in text)",
        "    return 1 if hits >= THRESHOLD else 0",
        "",
        "def accuracy():",
        "    correct = sum(1 for msg, label in DATA if is_spam(msg) == label)",
        "    return correct / len(DATA)",
        "",
        "try:",
        '    print("accuracy:", accuracy())',
        "except Exception as e:",
        '    print("Fill SPAM_WORDS and THRESHOLD, then re-run. (", type(e).__name__, ")")',
      ], sol)),
      grader('''expect_true("is_spam flags an obvious spam", lambda: is_spam("free prize claim now") == 1)
expect_true("is_spam passes a clean message", lambda: is_spam("see you at lunch") == 0)
expect_true("accuracy on the dataset >= 0.8", lambda: accuracy() >= 0.8)'''),
      footer(1, "Rules are explicit but **brittle** &mdash; you can never write enough of them. Machine learning flips it: show **examples**, let the model infer the rule. That is Lab 1.6 onward."),
    ]
    return cells

# ============================================================ LAB 02
@lab(2, "lab-02-ai-family-tree", "Beginner",
     "The AI Family Tree: AI &sup; ML &sup; DL &sup; GenAI", 15,
     "Place real technologies into the nested rings of AI, ML, Deep Learning and Generative AI.",
     ["The nested rings", "Telling ML / DL / GenAI apart"])
def _l2(sol):
    cells = [
      header(2, "The AI Family Tree: AI &sup; ML &sup; DL &sup; GenAI", "Beginner", 15,
        ["Understand that AI, ML, deep learning and generative AI are nested, not separate",
         "Classify real-world technologies into the correct ring",
         "Build the habit of asking 'which ring?' when someone says 'AI'"],
        "AI contains ML contains DL contains GenAI"),
      setup(2),
      md('''## Concept
The terms nest like Russian dolls:
**AI** (any machine intelligence) &sup; **ML** (learns from data) &sup; **Deep Learning**
(neural networks) &sup; **Generative AI** (creates content). A rule-based system is AI but *not* ML.'''),
      code('''# DEMO
RINGS = {
    "AI":    "any machine that mimics intelligence (incl. hand-written rules)",
    "ML":    "learns patterns from data (no neural net required)",
    "DL":    "machine learning with deep neural networks",
    "GenAI": "deep learning that creates text / images / code",
}
for k, v in RINGS.items():
    print(f"{k:6} = {v}")'''),
      md('''## Your Turn
For each technology, fill in the **innermost** ring it belongs to: `"AI"`, `"ML"`, `"DL"` or `"GenAI"`.'''),
      code(render([
        "answers = {",
        {"s": '    "A hand-coded chess rulebook":            "___",',
         "a": '    "A hand-coded chess rulebook":            "AI",'},
        {"s": '    "A spam filter trained on labelled email": "___",',
         "a": '    "A spam filter trained on labelled email": "ML",'},
        {"s": '    "A deep neural network that reads x-rays": "___",',
         "a": '    "A deep neural network that reads x-rays": "DL",'},
        {"s": '    "ChatGPT writing an email":                "___",',
         "a": '    "ChatGPT writing an email":                "GenAI",'},
        {"s": '    "A decision tree on a spreadsheet":        "___",',
         "a": '    "A decision tree on a spreadsheet":        "ML",'},
        {"s": '    "An image-generating diffusion model":     "___",',
         "a": '    "An image-generating diffusion model":     "GenAI",'},
        "}",
        "for tech, ring in answers.items():",
        '    print(f"{ring:6} <- {tech}")',
      ], sol)),
      grader('''KEY = {
  "A hand-coded chess rulebook": "AI",
  "A spam filter trained on labelled email": "ML",
  "A deep neural network that reads x-rays": "DL",
  "ChatGPT writing an email": "GenAI",
  "A decision tree on a spreadsheet": "ML",
  "An image-generating diffusion model": "GenAI",
}
for tech, want in KEY.items():
    expect(tech[:34], answers.get(tech), want)'''),
      footer(2, "When anyone says 'AI', ask **which ring**. Agentic AI (the course goal) wraps the **GenAI** ring with tools and a goal."),
    ]
    return cells

# ============================================================ LAB 03
@lab(3, "lab-03-timeline", "Beginner",
     "A Timeline of AI (and its Winters)", 20,
     "Build the 70-year AI timeline in code, add the milestones that ended the 'AI winters', and compute the gaps.",
     ["AI history & evolution", "The two AI winters"])
def _l3(sol):
    cells = [
      header(3, "A Timeline of AI (and its Winters)", "Beginner", 20,
        ["Assemble the major milestones of AI from 1950 to today",
         "Add the deep-learning era events that ended the last 'AI winter'",
         "Compute how long the field took to reach the modern moment"],
        "A short history of AI"),
      setup(3),
      md('''## Concept
AI is ~70 years old and moved in waves &mdash; booms followed by **"AI winters"** when hype
outran results. The modern wave began in **2012** (deep learning) and **2017** (the transformer).'''),
      code('''# DEMO
milestones = [
    (1950, "Turing asks: can machines think?"),
    (1956, "Dartmouth workshop coins the term 'Artificial Intelligence'"),
    (1997, "Deep Blue beats world chess champion Kasparov"),
]
for year, ev in sorted(milestones):
    print(year, "-", ev)'''),
      md('''## Your Turn
Add the **three** milestones that define the modern era, then compute two numbers.'''),
      code(render([
        "my_milestones = [",
        "    (1950, \"Turing test\"),",
        "    (1956, \"term 'AI' coined\"),",
        "    (1997, \"Deep Blue\"),",
        {"s": '    # TODO: add (2012, "..."), (2017, "..."), (2022, "...")',
         "a": '    (2012, "AlexNet: deep learning breaks out"),'},
        {"s": '    ("___", "___"),',
         "a": '    (2017, "Transformer: Attention Is All You Need"),'},
        {"s": '    ("___", "___"),',
         "a": '    (2022, "ChatGPT brings AI mainstream"),'},
        {"s": '    ("___", "___"),',
         "a": '    (2023, "the agent era begins"),'},
        "]",
        "",
        "# years from the Dartmouth workshop (1956) to ChatGPT (2022):",
        {"s": 'years_to_chatgpt = "___"   # TODO: compute 2022 - 1956',
         "a": 'years_to_chatgpt = 2022 - 1956'},
        "",
        "def has_year(y): return any(m[0] == y for m in my_milestones)",
        "try:",
        "    for y, ev in sorted(my_milestones):",
        '        print(y, "-", ev)',
        "except TypeError:",
        '    print("Replace the (\\"___\\", \\"___\\") rows with real (year, text) entries, then re-run.")',
      ], sol)),
      grader('''expect_true("2012 (deep learning) added", lambda: has_year(2012))
expect_true("2017 (transformer) added", lambda: has_year(2017))
expect_true("2022 (ChatGPT) added", lambda: has_year(2022))
expect("years 1956 -> 2022", years_to_chatgpt, 66)'''),
      footer(3, "Capability scales with **data + compute + algorithms**. Those three crossing a threshold around 2012 is what ended the last winter."),
    ]
    return cells

# ============================================================ LAB 04
@lab(4, "lab-04-narrow-general-super", "Beginner",
     "Narrow, General &amp; Super AI", 15,
     "Sort real and hypothetical systems into ANI / AGI / ASI and see that everything in production today is narrow.",
     ["Types of AI", "Where we actually are today"])
def _l4(sol):
    cells = [
      header(4, "Narrow, General &amp; Super AI", "Beginner", 15,
        ["Distinguish Narrow (ANI), General (AGI) and Super (ASI) AI",
         "Classify systems into the right tier",
         "Internalise that everything real today is narrow AI"],
        "Narrow / General / Super -- where we are"),
      setup(4),
      md('''## Concept
- **ANI (Narrow):** superb at *specific* tasks. **Everything real today.**
- **AGI (General):** human-level across *any* task. Does not exist yet.
- **ASI (Super):** beyond human ability. Speculative.'''),
      code('''# DEMO
print("ANI = a chess engine, a spam filter, ChatGPT  (all narrow!)")
print("AGI = a single AI that matches a human at ANY job (hypothetical)")
print("ASI = an AI beyond all human ability (speculative)")'''),
      md('''## Your Turn
Label each scenario `"ANI"`, `"AGI"` or `"ASI"`. (Hint: only some are real today.)'''),
      code(render([
        "answers = {",
        {"s": '    "A model that beats grandmasters at Go":              "___",',
         "a": '    "A model that beats grandmasters at Go":              "ANI",'},
        {"s": '    "An assistant that drafts emails and code":           "___",',
         "a": '    "An assistant that drafts emails and code":           "ANI",'},
        {"s": '    "One AI that can do ANY human job as well as a human": "___",',
         "a": '    "One AI that can do ANY human job as well as a human": "AGI",'},
        {"s": '    "Self-driving car perception":                        "___",',
         "a": '    "Self-driving car perception":                        "ANI",'},
        {"s": '    "A hypothetical mind smarter than all humans combined":"___",',
         "a": '    "A hypothetical mind smarter than all humans combined":"ASI",'},
        {"s": '    "A spam filter":                                      "___",',
         "a": '    "A spam filter":                                      "ANI",'},
        "}",
        "from collections import Counter",
        "print(Counter(answers.values()))",
      ], sol)),
      grader('''KEY = {
  "A model that beats grandmasters at Go": "ANI",
  "An assistant that drafts emails and code": "ANI",
  "One AI that can do ANY human job as well as a human": "AGI",
  "Self-driving car perception": "ANI",
  "A hypothetical mind smarter than all humans combined": "ASI",
  "A spam filter": "ANI",
}
for k, want in KEY.items():
    expect(k[:36], answers.get(k), want)'''),
      footer(4, "Our 'intelligent agents' this week are **narrow tools we direct and supervise** &mdash; capable, not autonomous beings. That keeps expectations and ethics grounded."),
    ]
    return cells

# ============================================================ LAB 05
@lab(5, "lab-05-how-machines-learn", "Beginner",
     "Three Ways Machines Learn", 15,
     "Match tasks to supervised, unsupervised and reinforcement learning -- the three paradigms used all week.",
     ["Supervised / unsupervised / reinforcement"])
def _l5(sol):
    cells = [
      header(5, "Three Ways Machines Learn", "Beginner", 15,
        ["Tell supervised, unsupervised and reinforcement learning apart",
         "Match real tasks to the right learning type",
         "Recognise which days of the course use each"],
        "Three ways machines learn"),
      setup(5),
      md('''## Concept
- **Supervised:** learn from *labelled* examples (input + right answer).
- **Unsupervised:** find *structure* with no labels (grouping, embeddings).
- **Reinforcement:** learn by *trial, reward & error* toward a goal.'''),
      code('''# DEMO
print("supervised    : photo -> 'cat'   (labelled)")
print("unsupervised  : group shoppers by behaviour (no labels)")
print("reinforcement : a bot learns a game from reward")'''),
      md('''## Your Turn
Label each task `"supervised"`, `"unsupervised"` or `"reinforcement"`.'''),
      code(render([
        "answers = {",
        {"s": '    "Predict house price from labelled past sales":       "___",',
         "a": '    "Predict house price from labelled past sales":       "supervised",'},
        {"s": '    "Group customers into segments with no labels":       "___",',
         "a": '    "Group customers into segments with no labels":       "unsupervised",'},
        {"s": '    "Teach a robot to walk using rewards":                "___",',
         "a": '    "Teach a robot to walk using rewards":                "reinforcement",'},
        {"s": '    "Classify email as spam/ham from labelled data":      "___",',
         "a": '    "Classify email as spam/ham from labelled data":      "supervised",'},
        {"s": '    "Discover topics in a pile of unlabelled documents":  "___",',
         "a": '    "Discover topics in a pile of unlabelled documents":  "unsupervised",'},
        {"s": '    "Train a game agent by trial and reward":             "___",',
         "a": '    "Train a game agent by trial and reward":             "reinforcement",'},
        "}",
        "for task, t in answers.items(): print(f'{t:14} <- {task}')",
      ], sol)),
      grader('''KEY = {
  "Predict house price from labelled past sales": "supervised",
  "Group customers into segments with no labels": "unsupervised",
  "Teach a robot to walk using rewards": "reinforcement",
  "Classify email as spam/ham from labelled data": "supervised",
  "Discover topics in a pile of unlabelled documents": "unsupervised",
  "Train a game agent by trial and reward": "reinforcement",
}
for k, want in KEY.items():
    expect(k[:34], answers.get(k), want)'''),
      footer(5, "This course rests mostly on **supervised learning** + huge **pre-trained** models. You'll meet all three ideas, intuition-first."),
    ]
    return cells

# ============================================================ LAB 06
@lab(6, "lab-06-data-is-the-new-code", "Beginner",
     "Data is the New Code: find a pattern by hand", 25,
     "Derive a classifier from data by choosing a threshold -- the manual version of what an ML model learns automatically.",
     ["Learning from data", "Decision threshold", "Accuracy"])
def _l6(sol):
    cells = [
      header(6, "Data is the New Code: find a pattern by hand", "Beginner", 25,
        ["See how a pattern can come from data instead of rules",
         "Choose a decision threshold that separates two classes",
         "Measure accuracy -- the score every model is judged on"],
        "The shift, in code"),
      setup(6),
      md('''## Concept
Instead of writing rules, we **look at data and find a boundary**. Here: apples are lighter,
oranges heavier. You'll pick the weight threshold that best splits them &mdash; exactly what a
model learns automatically in Lab 1.7.'''),
      code('''# DEMO -- the data (weight in grams, label)
FRUITS = [(150,"apple"),(170,"apple"),(140,"apple"),(160,"apple"),
          (200,"orange"),(210,"orange"),(190,"orange"),(220,"orange")]
apples  = [w for w,l in FRUITS if l=="apple"]
oranges = [w for w,l in FRUITS if l=="orange"]
print("apple weights :", apples,  "avg", sum(apples)/len(apples))
print("orange weights:", oranges, "avg", sum(oranges)/len(oranges))'''),
      md('''## Your Turn
Pick a **THRESHOLD** weight: at or above it = orange, below = apple. Aim for the best accuracy.'''),
      code(render([
        {"s": 'THRESHOLD = "___"   # TODO: a weight in grams between the two groups',
         "a": 'THRESHOLD = 180'},
        "",
        "def classify(weight):",
        {"s": '    return "___"   # TODO: "orange" if weight >= THRESHOLD else "apple"',
         "a": '    return "orange" if weight >= THRESHOLD else "apple"'},
        "",
        "def accuracy():",
        "    correct = sum(1 for w, label in FRUITS if classify(w) == label)",
        "    return correct / len(FRUITS)",
        "",
        "try: print('accuracy:', accuracy())",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("classifies a 150g fruit as apple", lambda: classify(150) == "apple")
expect_true("classifies a 210g fruit as orange", lambda: classify(210) == "orange")
expect_true("accuracy >= 0.85", lambda: accuracy() >= 0.85)'''),
      footer(6, "You just **learned a model from data** by hand: a threshold + an accuracy score. Next, scikit-learn finds the boundary for you across many features."),
    ]
    return cells

# ============================================================ LAB 07
@lab(7, "lab-07-first-ml-pipeline", "Intermediate",
     "Your First ML Pipeline (scikit-learn)", 25,
     "Run the full data -> split -> train -> evaluate pipeline on the classic Iris dataset with scikit-learn.",
     ["Train/test split", "Fitting a model", "Evaluating accuracy"])
def _l7(sol):
    cells = [
      header(7, "Your First ML Pipeline (scikit-learn)", "Intermediate", 25,
        ["Run the standard ML pipeline: data, split, train, evaluate",
         "Train a real classifier with scikit-learn",
         "Score it on data it has never seen"],
        "How a model is built: the ML pipeline"),
      setup(7),
      md('''## Concept
The five-step pipeline from the slides: **data &rarr; split &rarr; train &rarr; evaluate &rarr; predict**.
The golden rule: judge the model on a **held-out test set** it never trained on.

> Needs `scikit-learn` (`pip install scikit-learn`).'''),
      code('''# DEMO -- load the data
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
print("samples:", X.shape[0], "| features:", X.shape[1], "| classes:", sorted(int(c) for c in set(y)))'''),
      md('''## Your Turn
Complete the pipeline: choose a **test fraction**, **fit** the model, and **predict** on the test set.'''),
      code(render([
        "from sklearn.model_selection import train_test_split",
        "from sklearn.tree import DecisionTreeClassifier",
        "from sklearn.metrics import accuracy_score",
        "",
        "def run_pipeline():",
        "    X, y = load_iris(return_X_y=True)",
        {"s": '    test_frac = "___"   # TODO: a fraction like 0.25',
         "a": '    test_frac = 0.25'},
        "    X_tr, X_te, y_tr, y_te = train_test_split(",
        "        X, y, test_size=test_frac, random_state=0)",
        "    clf = DecisionTreeClassifier(random_state=0)",
        {"s": '    ___   # TODO: fit clf on the TRAINING data',
         "a": '    clf.fit(X_tr, y_tr)'},
        {"s": '    preds = ___   # TODO: predict on X_te',
         "a": '    preds = clf.predict(X_te)'},
        "    return accuracy_score(y_te, preds)",
        "",
        "try: print('test accuracy:', run_pipeline())",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("pipeline runs and returns a number", lambda: isinstance(run_pipeline(), float))
expect_true("test accuracy >= 0.85", lambda: run_pipeline() >= 0.85)'''),
      footer(7, "No rules written &mdash; the model **learned** the boundaries from labelled examples. This same shape powers every supervised lab this week."),
    ]
    return cells

# ============================================================ LAB 08
@lab(8, "lab-08-overfitting", "Intermediate",
     "The Train/Test Trap: seeing overfitting", 30,
     "Watch a model ace the data it trained on but stumble on new data -- the single most important pitfall in ML.",
     ["Overfitting", "Why you must evaluate on unseen data"])
def _l8(sol):
    cells = [
      header(8, "The Train/Test Trap: seeing overfitting", "Intermediate", 30,
        ["Measure accuracy on training vs unseen test data",
         "Witness overfitting: high train score, lower test score",
         "Understand why the test set is sacred"],
        "How a model is built: the ML pipeline"),
      setup(8),
      md('''## Concept
A model that **memorises** its training data scores ~100% there but fails on new data &mdash;
**overfitting**. The gap between train and test accuracy is the tell. We use a deliberately
noisy dataset and a deep tree to make it obvious.'''),
      code('''# DEMO -- a noisy dataset, split off a test set
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
X, y = make_classification(n_samples=300, n_features=10, n_informative=4,
                           flip_y=0.25, random_state=0)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.4, random_state=0)
print("train:", len(X_tr), "test:", len(X_te))'''),
      md('''## Your Turn
A deep decision tree is fitted for you. Compute its **train** and **test** accuracy and the **gap**.'''),
      code(render([
        "from sklearn.tree import DecisionTreeClassifier",
        "from sklearn.metrics import accuracy_score",
        "",
        "deep = DecisionTreeClassifier(max_depth=None, random_state=0).fit(X_tr, y_tr)",
        "",
        "def train_acc():",
        {"s": '    return ___   # TODO: accuracy on the TRAINING data',
         "a": '    return accuracy_score(y_tr, deep.predict(X_tr))'},
        "def test_acc():",
        {"s": '    return ___   # TODO: accuracy on the TEST data',
         "a": '    return accuracy_score(y_te, deep.predict(X_te))'},
        "def gap():",
        "    return train_acc() - test_acc()",
        "",
        "try: print(f'train={train_acc():.2f}  test={test_acc():.2f}  gap={gap():.2f}')",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("train accuracy computed (very high)", lambda: train_acc() >= 0.95)
expect_true("test accuracy computed (lower)", lambda: 0.0 < test_acc() < 0.95)
expect_true("overfitting visible: train > test", lambda: gap() > 0.1)'''),
      md('''## Counterfactual: is the gap the *noise*, or *overfitting*?
A sharp question: with 25% label noise, maybe the gap is just the noise &mdash; not overfitting?
Test it. Hold the **noisy data fixed** and change only the model's **capacity**. If noise alone
opened the gap, a shallow tree (same data) would show it too.'''),
      code('''# DEMO -- same noisy data, vary ONLY capacity (nothing to fill in)
for depth in (None, 2):
    m  = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(X_tr, y_tr)
    tr = accuracy_score(y_tr, m.predict(X_tr))
    te = accuracy_score(y_te, m.predict(X_te))
    tag = "deep (can memorise noise)" if depth is None else "shallow (cannot memorise)"
    print(f"max_depth={str(depth):<4}  train={tr:.2f}  test={te:.2f}  gap={tr-te:+.2f}   {tag}")
print("\\nSame noise in BOTH rows -- only model capacity changed.")
print("The GAP tracks capacity, not noise: it collapses from ~0.24 to ~0.10 the moment the")
print("tree can no longer memorise. So the train>>test gap IS overfitting.")
print("Separately, the noise caps the best achievable TEST score near ~0.75 -- that ceiling")
print("is why even the deep tree tops out around 0.76 on test, never 1.00.")'''),
      footer(8, "The model memorised the noise. Always report the **test** score &mdash; the train score flatters and lies. Module 2 covers how to fight overfitting."),
    ]
    return cells

# ============================================================ LAB 09
@lab(9, "lab-09-supervised-vs-unsupervised", "Intermediate",
     "Supervised vs Unsupervised: same data, two lenses", 30,
     "Cluster the Iris flowers with no labels (KMeans) and compare the discovered groups to the true species.",
     ["Unsupervised learning", "Clustering", "Comparing to ground truth"])
def _l9(sol):
    cells = [
      header(9, "Supervised vs Unsupervised: same data, two lenses", "Intermediate", 30,
        ["Run unsupervised clustering (KMeans) with no labels",
         "Compare discovered clusters to the real species",
         "See how structure can emerge from data alone"],
        "Three ways machines learn"),
      setup(9),
      md('''## Concept
Supervised learning needs labels; **unsupervised** finds structure without them. KMeans groups
the flowers by similarity, blind to species &mdash; then we *check* how well its groups line up
with the truth using the **Adjusted Rand Index** (1.0 = perfect, 0 = random).'''),
      code('''# DEMO
from sklearn.datasets import load_iris
X, y = load_iris(return_X_y=True)
print("We will hide y from the algorithm and see if it rediscovers 3 groups.")'''),
      md('''## Your Turn
Cluster into the right number of groups and read off the agreement score.'''),
      code(render([
        "from sklearn.cluster import KMeans",
        "from sklearn.metrics import adjusted_rand_score",
        "",
        "def cluster():",
        "    X, y = load_iris(return_X_y=True)",
        {"s": '    k = "___"   # TODO: how many species are there?',
         "a": '    k = 3'},
        "    km = KMeans(n_clusters=k, n_init=10, random_state=0)",
        {"s": '    labels = ___   # TODO: km.fit_predict(X)',
         "a": '    labels = km.fit_predict(X)'},
        "    return labels, adjusted_rand_score(y, labels)",
        "",
        "try:",
        "    labs, ari = cluster()",
        "    print('clusters found:', sorted(int(c) for c in set(labs)), '| agreement (ARI):', round(ari,3))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("found exactly 3 clusters", lambda: len(set(cluster()[0])) == 3)
expect_true("agreement with truth (ARI) >= 0.5", lambda: cluster()[1] >= 0.5)'''),
      footer(9, "KMeans-style clustering powers the **embeddings & retrieval** behind RAG and agent memory later in the course &mdash; unsupervised ideas, everywhere."),
    ]
    return cells

# ============================================================ LAB 10
@lab(10, "lab-10-perceptron-from-scratch", "Advanced",
     "Peek Inside a Neural Network: a perceptron from scratch", 40,
     "Build and train a single neuron with nothing but NumPy -- implement the sigmoid, the forward pass and the learning step.",
     ["Neurons & weights", "Forward pass", "Gradient-descent training"])
def _l10(sol):
    cells = [
      header(10, "Peek Inside a Neural Network: a perceptron from scratch", "Advanced", 40,
        ["Implement a neuron's forward pass with NumPy",
         "Implement the sigmoid activation and a gradient-descent update",
         "Train it to learn the OR logic gate from data"],
        "A peek inside a neural network"),
      setup(10),
      md('''## Concept
A neuron computes `output = sigmoid(weights . inputs + bias)`. **Training** nudges the weights
to reduce error, repeatedly (gradient descent). You'll implement the three core pieces and watch
a single neuron *learn* the OR gate. Pure NumPy &mdash; no deep-learning framework.'''),
      code('''# DEMO -- the data: the OR gate
import numpy as np
X = np.array([[0,0],[0,1],[1,0],[1,1]], dtype=float)
y = np.array([0, 1, 1, 1], dtype=float)   # OR: true if either input is 1
print("inputs:\\n", X, "\\ntargets:", y)'''),
      md('''## Your Turn
Fill in the **sigmoid**, the **forward pass**, and the **weight update**. Then train.'''),
      code(render([
        "import numpy as np",
        "",
        "def sigmoid(z):",
        {"s": '    return ___   # TODO: 1 / (1 + e^(-z))  -> use np.exp',
         "a": '    return 1.0 / (1.0 + np.exp(-z))'},
        "",
        "def train(X, y, lr=0.5, epochs=3000):",
        "    rng = np.random.default_rng(0)",
        "    w = rng.normal(size=X.shape[1]); b = 0.0",
        "    for _ in range(epochs):",
        {"s": '        z = ___          # TODO: X . w + b',
         "a": '        z = X.dot(w) + b'},
        "        p = sigmoid(z)",
        "        error = p - y",
        {"s": '        w = w - lr * ___ # TODO: gradient wrt w = X^T . error / N',
         "a": '        w = w - lr * X.T.dot(error) / len(y)'},
        "        b = b - lr * error.mean()",
        "    return w, b",
        "",
        "def predict(X, w, b):",
        "    return (sigmoid(X.dot(w) + b) >= 0.5).astype(int)",
        "",
        "try:",
        "    w, b = train(X, y)",
        "    print('predictions:', predict(X, w, b), '| target:', y.astype(int))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''import numpy as np
expect_true("sigmoid(0) == 0.5", lambda: abs(sigmoid(0.0) - 0.5) < 1e-9)
expect_true("sigmoid saturates near 1 for large z", lambda: sigmoid(10) > 0.99)
def _learned():
    w, b = train(X, y)
    return np.array_equal(predict(X, w, b), y.astype(int))
expect_true("the neuron learned the OR gate", _learned)'''),
      footer(10, "That loop &mdash; forward, measure error, nudge weights, repeat &mdash; is **all** a deep network does, just with millions of neurons. Module 2 goes deeper."),
    ]
    return cells

# ============================================================ LAB 11
@lab(11, "lab-11-digits-deep-learning", "Advanced",
     "Deep Learning for Real: recognise handwritten digits", 40,
     "Train a multi-layer neural network to read handwritten digits and visualise how it decides -- and where it errs.",
     ["Neural network classifier", "Evaluation", "Visualising decisions"])
def _l11(sol):
    cells = [
      header(11, "Deep Learning for Real: recognise handwritten digits", "Advanced", 40,
        ["Train a multi-layer neural network (MLP) on handwritten digits",
         "Reach 90%+ accuracy on unseen digits",
         "Visualise predictions -- including a mistake -- to see how AI decides"],
        "A peek inside a neural network"),
      setup(11),
      md('''## Concept
This is the experience the whole module builds toward: a **neural network that learns to see**.
We use the 8x8 `digits` dataset (loads offline, no download). You'll build the network, score it,
and *look* at its decisions &mdash; the "visualising how AI decides" goal from the slides.

> **See it first (interactive):** [Inside `hidden_layer_sizes=(64,)`](../../presentation/inside-hidden-64-neural-network.html)
> &mdash; a *real* trained `(64,)` network runs its forward pass in your browser on these very digits. Pick a
> sample or draw your own and watch the 64 hidden neurons fire, then come back and build it yourself.

> Needs `scikit-learn` and `matplotlib`.'''),
      code('''# DEMO -- load & peek at the data
from sklearn.datasets import load_digits
digits = load_digits()
X, y = digits.data, digits.target
print("images:", X.shape[0], "| each is", digits.images[0].shape, "pixels | first label:", y[0])'''),
      md('''## Your Turn
Build an MLP with a hidden layer, fit it, and measure test accuracy.'''),
      code(render([
        "from sklearn.model_selection import train_test_split",
        "from sklearn.neural_network import MLPClassifier",
        "from sklearn.metrics import accuracy_score",
        "",
        "X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=0)",
        "",
        "def build_and_train():",
        {"s": '    hidden = "___"   # TODO: a tuple of layer sizes, e.g. (64,)',
         "a": '    hidden = (64,)'},
        "    clf = MLPClassifier(hidden_layer_sizes=hidden, max_iter=500, random_state=0)",
        {"s": '    ___   # TODO: fit clf on the training data',
         "a": '    clf.fit(X_tr, y_tr)'},
        "    return clf",
        "",
        "def test_accuracy(clf):",
        {"s": '    return ___   # TODO: accuracy_score(y_te, clf.predict(X_te))',
         "a": '    return accuracy_score(y_te, clf.predict(X_te))'},
        "",
        "try:",
        "    model = build_and_train()",
        "    print('test accuracy:', round(test_accuracy(model), 3))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''def _acc():
    return test_accuracy(build_and_train())
expect_true("model trains and predicts", lambda: 0.0 < _acc() <= 1.0)
expect_true("test accuracy >= 0.90", lambda: _acc() >= 0.90)'''),
      md('''## Bonus: visualise the decisions
Run this to *see* the model read digits &mdash; including, where present, a mistake. (Not graded.)'''),
      code('''try:
    import matplotlib.pyplot as plt
    model = build_and_train()
    preds = model.predict(X_te)
    # find a few correct and (if any) one wrong
    import numpy as np
    wrong = np.where(preds != y_te)[0]
    show = list(range(6)) + ([wrong[0]] if len(wrong) else [])
    fig, axes = plt.subplots(1, len(show), figsize=(2*len(show), 2.4))
    for ax, i in zip(np.atleast_1d(axes), show):
        ax.imshow(X_te[i].reshape(8,8), cmap="gray_r")
        ok = preds[i] == y_te[i]
        ax.set_title(f"pred {preds[i]}\\n(true {y_te[i]})", color=("green" if ok else "red"), fontsize=9)
        ax.axis("off")
    plt.tight_layout(); plt.savefig(WORK + "/digit_predictions.png", dpi=90); plt.show()
    print("saved:", WORK + "/digit_predictions.png")
except Exception as e:
    print("Visualisation needs matplotlib + a trained model.", type(e).__name__)'''),
      footer(11, "You trained a real neural network to **see**, and watched it decide. The MNIST lab in Module 2 scales this up &mdash; same idea, bigger images."),
    ]
    return cells

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-model-to-agent", "Advanced",
     "Capstone: From Model to Agent (LLM + Tools + Goal + Loop)", 45,
     "Build a mini autonomous agent that plans, picks tools, acts and loops -- the pattern the entire course builds toward.",
     ["The agent loop", "Tools", "Goal-directed reasoning"])
def _l12(sol):
    cells = [
      header(12, "Capstone: From Model to Agent (LLM + Tools + Goal + Loop)", "Advanced", 45,
        ["Assemble the agent pattern: a planner + tools + a goal + a loop",
         "Implement tool dispatch and the act-observe loop",
         "Run a multi-step goal end-to-end -- no LLM key required",
         "(Optional) swap in a real local LLM via Ollama"],
        "From a model that answers to an agent that acts"),
      setup(12),
      md('''## Concept &mdash; the destination of the whole course
An **agent = brain (planner) + tools + a goal + a loop**. Today the "brain" is a tiny rule-based
planner so the lab runs anywhere; from Day 3 you swap in a real LLM (LangChain). The *shape* is
identical: read the goal &rarr; plan steps &rarr; **use a tool** &rarr; observe &rarr; loop &rarr; answer.'''),
      code('''# DEMO -- the tools available to our agent
import re

def tool_calc(expr):
    if not re.fullmatch(r"[\\d+\\-*/(). ]+", expr):
        raise ValueError("unsafe expression")
    return eval(expr, {"__builtins__": {}}, {})

def tool_wordcount(text):
    return len(text.split())

print("calc 3*14+8 =", tool_calc("3*14+8"))
print("wordcount   =", tool_wordcount("the quick brown fox"))'''),
      md('''## Your Turn
Wire up the **tool dispatcher** and the **agent loop**. A `plan` is a list of `(tool, argument)`
steps; the agent runs each step, *observes* the result, and returns the **final** observation.'''),
      code(render([
        "TOOLS = {'calc': tool_calc, 'wordcount': tool_wordcount}",
        "",
        "def run_tool(name, arg):",
        '    """Look up a tool by name and call it with arg."""',
        {"s": '    return ___   # TODO: call the right tool from TOOLS with arg',
         "a": '    return TOOLS[name](arg)'},
        "",
        "def agent_run(plan, verbose=True):",
        '    """Execute each (tool, arg) step; observe; return the LAST observation."""',
        "    observation = None",
        "    for step_no, (tool, arg) in enumerate(plan, 1):",
        {"s": '        observation = ___   # TODO: run this step with run_tool',
         "a": '        observation = run_tool(tool, arg)'},
        "        if verbose:",
        "            print(f'  step {step_no}: {tool}({arg!r}) -> {observation}')",
        "    return observation",
        "",
        "# a 2-step goal: 3*14, then add 8 to it",
        "demo_plan = [('calc', '3*14'), ('calc', '42+8')]",
        "try:",
        "    print('FINAL:', agent_run(demo_plan))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("run_tool calls calc", lambda: run_tool("calc", "2+2") == 4)
expect_true("run_tool calls wordcount", lambda: run_tool("wordcount", "a b c") == 3)
expect_true("agent runs a multi-step plan", lambda: agent_run([("calc","3*14"),("calc","42+8")], verbose=False) == 50)
expect_true("agent handles a wordcount goal", lambda: agent_run([("wordcount","the quick brown fox")], verbose=False) == 4)'''),
      md('''## Optional &mdash; use a REAL local LLM as the planner (Ollama)
If you have [Ollama](https://ollama.com) running with a small model, this turns the goal from a
hand-written plan into one an LLM proposes. Safe to skip &mdash; **not graded**.'''),
      code('''# OPTIONAL: requires `pip install langchain-community` and a running Ollama (llama3.2:1b)
try:
    from langchain_community.chat_models import ChatOllama
    llm = ChatOllama(model="llama3.2:1b", temperature=0)
    msg = llm.invoke("In one short sentence, what is an AI agent?")
    print("LLM says:", getattr(msg, "content", msg))
except Exception as e:
    print("Ollama not available -- that's fine, the lab above is complete without it.")
    print("  reason:", type(e).__name__)'''),
      footer(12, "You built the **LLM + Tools + Goal + Loop** pattern by hand. Every framework this week (LangChain, AutoGPT) is this same loop, scaled up. You're ready for Day 2."),
    ]
    return cells

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
        banner = md(f'''> ## &#9989; SOLUTION / ANSWER KEY &mdash; Lab 1.{nn}
> This is the **completed** notebook (all `___` blanks filled). For the student version, open
> [`../{info['slug']}.ipynb`](../{info['slug']}.ipynb). Trainer use &mdash; or self-check after you've tried it yourself.''')
        sol_cells = [banner] + info["build"](True)
        with open(os.path.join(SOL_DIR, fname), "w") as f:
            json.dump(notebook(sol_cells), f, indent=1, ensure_ascii=False)

print(f"Wrote {len(NB)} notebooks to {OUT_DIR}" + (f" and solutions to {SOL_DIR}" if SOL_DIR else ""))

# expose metadata for the index generator (kept beside the generators, not in the labs dir)
with open(os.path.join(_HERE, "_meta.json"), "w") as f:
    json.dump({str(nn): {k: NB[nn][k] for k in ("slug","level","title","mins","summary","concepts")}
               for nn in NB}, f, indent=1)
