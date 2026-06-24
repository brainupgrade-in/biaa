# -*- coding: utf-8 -*-
"""Generator for Day 2 Module 4 hands-on labs (12 notebooks).
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

Design: every GRADED cell is offline (NumPy / scikit-learn) so the labs run and
verify with no network and no heavy installs. "Fine-tuning" is taught as transfer
learning -- a FROZEN feature extractor (TF-IDF) + a TRAINABLE head -- which runs
anywhere. Each Advanced lab also includes an OPTIONAL, guarded Hugging Face cell
(real bert-tiny / sentiment pipeline, not graded) that degrades gracefully if
`transformers` is absent and never needs a paid API key. Real BERT fine-tuning is
the managed-sandbox target; the offline path is what guarantees the labs verify."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day2-module4-pretrained-models-and-fine-tuning.html"
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
WORK = "/tmp/biaa-lab-04-{nn:02d}"
os.makedirs(WORK, exist_ok=True)
print("Working dir:", WORK){extra}''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 4.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 2 &middot; Module 4 &mdash; Pre-trained Models & Fine-tuning**

### What you'll do
{g}

> **How this lab works (experiential flow):** read the **Concept**, run the **Demo** to see it work, then complete **Your Turn** by replacing every `___` placeholder. Run the **grader** cell at the end &mdash; it prints `[PASS]` / `[FAIL]` / `[TODO]` and a final `Score`. Aim for a full score.

**Reference:** [Module 4 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 4 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 4 labs](./index.html) &nbsp;&middot;&nbsp; [Module 4 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def optional_hf(intro, body):
    """An OPTIONAL, non-graded Hugging Face cell that degrades gracefully."""
    return [md(f'''## Optional &mdash; the real thing with Hugging Face (not graded)
{intro} Safe to skip &mdash; it needs `pip install transformers torch` and a one-time model
download. If `transformers` is not installed (or offline), the cell prints a note and moves on.
**Real BERT fine-tuning is the managed-sandbox target; the graded steps above run offline so the
lab always works.**'''),
            code(body)]

# A small sentiment dataset reused by the ML labs. Strong sentiment words RECUR
# across examples (love/great/wonderful/... vs hate/terrible/awful/...) so a model
# trained on one split generalises to the held-out split -- essential on tiny data.
SENT_DATA = '''# A tiny labelled sentiment dataset (1 = positive, 0 = negative)
SENT = [
    ("i love this it is great", 1),
    ("a great and wonderful film", 1),
    ("truly wonderful i love it", 1),
    ("excellent and brilliant work", 1),
    ("the best most brilliant story", 1),
    ("i love how great it is", 1),
    ("wonderful excellent and great fun", 1),
    ("a brilliant and great success", 1),
    ("great fun i really love it", 1),
    ("the best film wonderful and brilliant", 1),
    ("excellent great and lovely work", 1),
    ("i love this brilliant great film", 1),
    ("wonderful great and the best", 1),
    ("so good i love it great", 1),
    ("i hate this it is terrible", 0),
    ("a terrible and awful film", 0),
    ("truly awful i hate it", 0),
    ("boring and terrible work", 0),
    ("the worst most boring story", 0),
    ("i hate how bad it is", 0),
    ("awful boring and dull mess", 0),
    ("a terrible and bad failure", 0),
    ("boring mess i really hate it", 0),
    ("the worst film awful and boring", 0),
    ("terrible bad and dull work", 0),
    ("i hate this awful boring film", 0),
    ("awful terrible and the worst", 0),
    ("so bad i hate it terrible", 0),
]
texts  = [t for t, y in SENT]
labels = [y for t, y in SENT]'''

NB = {}
def lab(nn, slug, level, title, mins, summary, concepts):
    def deco(fn):
        NB[nn] = dict(slug=slug, level=level, title=title, mins=mins,
                      summary=summary, concepts=concepts, build=fn)
        return fn
    return deco

# ============================================================ LAB 01
@lab(1, "lab-01-using-a-pretrained-model", "Beginner",
     "Using a Pre-trained Model: Sentiment Out of the Box", 20,
     "Use a ready-made sentiment model to label text without any training -- the power of pre-training.",
     ["Pre-trained models", "Inference", "Sentiment"])
def _l1(sol):
    return [
      header(1, "Using a Pre-trained Model: Sentiment Out of the Box", "Beginner", 20,
        ["Understand what 'pre-trained' buys you: useful predictions with zero training",
         "Use a ready-made sentiment scorer to label new text",
         "Measure how accurate an out-of-the-box model is"],
        "Hugging Face hub & pipelines"),
      setup(1),
      md('''## Concept
A **pre-trained model** already learned from huge data, so it works **out of the box** &mdash;
you just run **inference**. Real systems use a pretrained transformer; here we use a tiny
lexicon "model" (someone already built the word knowledge) to feel the idea. The real Hugging
Face pipeline is in the optional cell at the end.'''),
      code('''# DEMO -- a ready-made (pre-built) sentiment lexicon
POS = {"loved","fantastic","masterpiece","brilliant","wonderful","moving","great",
       "recommend","best","delightful","funny","heartwarming","superb","beautiful",
       "excellent","enjoyed","charming","uplifting","amazing","gripping","joy","touching",
       "entertaining"}
NEG = {"terrible","waste","hated","boring","long","awful","dull","worst","painfully",
       "bad","disappointing","forgettable","tedious","lifeless","mess","bored","weak",
       "dreadful","letdown","badly","slow","clumsy","regret","rubbish"}
print("positive words known:", len(POS), "| negative words known:", len(NEG))'''),
      md('''## Your Turn
Use the lexicon to **predict** a label for any text, then score it on a few examples.'''),
      code(render([
        "SAMPLES = [",
        '    ("a brilliant and moving masterpiece", 1),',
        '    ("a boring dreadful waste of time", 0),',
        '    ("i loved it, truly excellent", 1),',
        '    ("awful and disappointing", 0),',
        "]",
        "",
        "def predict(text):",
        '    toks = text.lower().split()',
        {"s": '    pos = ___   # TODO: count tokens that are in POS',
         "a": '    pos = sum(1 for t in toks if t in POS)'},
        {"s": '    neg = ___   # TODO: count tokens that are in NEG',
         "a": '    neg = sum(1 for t in toks if t in NEG)'},
        {"s": '    return ___   # TODO: 1 if pos >= neg else 0',
         "a": '    return 1 if pos >= neg else 0'},
        "",
        "def accuracy():",
        "    return sum(1 for t, y in SAMPLES if predict(t) == y) / len(SAMPLES)",
        "",
        "try: print('accuracy:', accuracy())",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("predicts a clearly positive text as 1", lambda: predict("a brilliant wonderful film") == 1)
expect_true("predicts a clearly negative text as 0", lambda: predict("a dull boring mess") == 0)
expect_true("accuracy on the samples == 1.0", lambda: accuracy() == 1.0)'''),
      *optional_hf(
        "Run a REAL pretrained sentiment model from the Hugging Face hub on the same texts.",
        '''try:
    from transformers import pipeline
    clf = pipeline("sentiment-analysis")   # downloads a small pretrained model once
    for t in ["a brilliant and moving masterpiece", "a boring dreadful waste of time"]:
        print(t, "->", clf(t)[0])
except Exception as e:
    print("transformers not available -- skipping the real model.", type(e).__name__)
    print("The graded lexicon model above already shows the idea: pre-trained = works out of the box.")'''),
      footer(1, "A pre-trained model delivers value with **zero training** &mdash; you just run inference. Next we make this an explicit, reusable **pipeline**."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-confidence-scores", "Beginner",
     "Reading a Model's Confidence (softmax)", 20,
     "Turn raw model scores into probabilities with softmax and read off the predicted label and its confidence.",
     ["Softmax", "Probabilities", "Confidence"])
def _l2(sol):
    return [
      header(2, "Reading a Model's Confidence (softmax)", "Beginner", 20,
        ["Convert raw scores (logits) into probabilities with softmax",
         "Read the predicted label and its confidence",
         "See why a model can be confident -- or unsure"],
        "GPT generation / BERT sentiment"),
      setup(2),
      md('''## Concept
A classifier outputs raw scores (**logits**), one per class. **Softmax** turns them into
probabilities that sum to 1. The **argmax** is the prediction; the **max probability** is the
**confidence**. This is exactly what a Hugging Face sentiment pipeline returns.'''),
      code('''# DEMO -- two raw scores [negative, positive]
import numpy as np
logits = np.array([0.3, 2.1])
print("logits:", logits)'''),
      md('''## Your Turn
Implement **softmax**, then return the predicted label and confidence.'''),
      code(render([
        "import numpy as np",
        "",
        "def softmax(x):",
        "    x = np.asarray(x, dtype=float)",
        {"s": '    e = ___   # TODO: np.exp(x - x.max())  (subtract max for stability)',
         "a": '    e = np.exp(x - x.max())'},
        {"s": '    return ___   # TODO: e divided by its sum',
         "a": '    return e / e.sum()'},
        "",
        "def predict(logits):",
        "    p = softmax(logits)",
        {"s": '    label = ___   # TODO: index of the largest probability (np.argmax)',
         "a": '    label = int(np.argmax(p))'},
        {"s": '    conf = ___    # TODO: the largest probability (p.max())',
         "a": '    conf = float(p.max())'},
        "    return label, conf",
        "",
        "try: print('predict([0.3, 2.1]) ->', predict([0.3, 2.1]))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''import numpy as np
expect_true("softmax sums to 1", lambda: abs(float(np.sum(softmax([1.0, 2.0, 3.0]))) - 1.0) < 1e-9)
expect_true("softmax is monotonic (bigger logit -> bigger prob)", lambda: softmax([0.3, 2.1])[1] > softmax([0.3, 2.1])[0])
expect_true("predicts class 1 for [0.3, 2.1]", lambda: predict([0.3, 2.1])[0] == 1)
expect_true("confidence is in (0.5, 1.0] for a clear case", lambda: 0.5 < predict([0.3, 2.1])[1] <= 1.0)'''),
      footer(2, "Softmax turns scores into **calibrated-looking probabilities**. The confidence tells you *how sure* the model is &mdash; vital when a human reviews its output."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-prompt-finetune-or-rag", "Beginner",
     "Prompt, Fine-tune, or RAG? Choosing the Approach", 15,
     "Match real scenarios to the right strategy -- prompting, fine-tuning, or retrieval (RAG).",
     ["Prompting", "Fine-tuning", "RAG"])
def _l3(sol):
    return [
      header(3, "Prompt, Fine-tune, or RAG? Choosing the Approach", "Beginner", 15,
        ["Tell prompting, fine-tuning and RAG apart",
         "Pick the right approach for a given need",
         "Build the judgement you'll use on every real project"],
        "Prompt vs fine-tune vs RAG"),
      setup(3),
      md('''## Concept
Three ways to adapt a pre-trained model to your need:
- **Prompt** &mdash; just ask, no training. Fast, flexible, good default.
- **Fine-tune** &mdash; train further on your labelled data. Best for a fixed, specialised task/style.
- **RAG** (retrieval) &mdash; fetch your documents at query time. Best when answers must come from *your* up-to-date knowledge.'''),
      code('''# DEMO
print("Prompt    -> 'Summarise this email.'           (no training)")
print("Fine-tune -> a sentiment model tuned on YOUR labelled reviews")
print("RAG       -> 'Answer from our latest policy PDFs.'  (retrieve then answer)")'''),
      md('''## Your Turn
Label each scenario `"prompt"`, `"fine-tune"`, or `"rag"`.'''),
      code(render([
        "answers = {",
        {"s": '    "Quickly draft a one-off marketing tagline":                 "___",',
         "a": '    "Quickly draft a one-off marketing tagline":                 "prompt",'},
        {"s": '    "Classify 50k support tickets into your 8 fixed categories": "___",',
         "a": '    "Classify 50k support tickets into your 8 fixed categories": "fine-tune",'},
        {"s": '    "Answer staff questions from our internal policy documents":  "___",',
         "a": '    "Answer staff questions from our internal policy documents":  "rag",'},
        {"s": '    "Always reply in our brand voice for a specialised task":     "___",',
         "a": '    "Always reply in our brand voice for a specialised task":     "fine-tune",'},
        {"s": '    "Ground answers in our constantly changing product catalogue": "___",',
         "a": '    "Ground answers in our constantly changing product catalogue": "rag",'},
        {"s": '    "Try an idea once with no setup":                            "___",',
         "a": '    "Try an idea once with no setup":                            "prompt",'},
        "}",
        "from collections import Counter",
        "print(Counter(answers.values()))",
      ], sol)),
      grader('''KEY = {
  "Quickly draft a one-off marketing tagline": "prompt",
  "Classify 50k support tickets into your 8 fixed categories": "fine-tune",
  "Answer staff questions from our internal policy documents": "rag",
  "Always reply in our brand voice for a specialised task": "fine-tune",
  "Ground answers in our constantly changing product catalogue": "rag",
  "Try an idea once with no setup": "prompt",
}
for k, want in KEY.items():
    expect(k[:34], answers.get(k), want)'''),
      footer(3, "Default to **prompting**; **fine-tune** for a fixed specialised task (this module's focus); reach for **RAG** when answers must come from your own changing data (Day 3)."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-tokenization-for-a-model", "Beginner",
     "Model Inputs: IDs, Padding & Attention Masks", 25,
     "Turn text into the padded input_ids and attention_mask a transformer actually consumes.",
     ["input_ids", "Padding", "Attention mask"])
def _l4(sol):
    return [
      header(4, "Model Inputs: IDs, Padding & Attention Masks", "Beginner", 25,
        ["Encode text into integer token IDs against a vocabulary",
         "Pad a batch to equal length",
         "Build the attention mask that tells the model which tokens are real"],
        "Hugging Face pipelines"),
      setup(4),
      md('''## Concept
A transformer takes a batch of equal-length integer sequences. So we **encode** tokens to IDs,
**pad** short sequences to the batch's max length with a `[PAD]` id (0), and supply an
**attention mask** (1 for real tokens, 0 for padding) so the model ignores the padding.'''),
      code('''# DEMO -- a toy vocabulary ([PAD]=0, [UNK]=1)
VOCAB = {"[PAD]":0, "[UNK]":1, "i":2, "loved":3, "it":4, "great":5, "film":6}
def encode_tokens(toks): return [VOCAB.get(t, 1) for t in toks]
print(encode_tokens(["i","loved","it"]))
print(encode_tokens(["great","film","wow"]))   # 'wow' -> [UNK]=1'''),
      md('''## Your Turn
Encode a batch to IDs, pad to the longest, and build the attention mask.'''),
      code(render([
        'VOCAB = {"[PAD]":0, "[UNK]":1, "i":2, "loved":3, "it":4, "great":5, "film":6, "the":7, "best":8}',
        "PAD = 0",
        "batch = [['i','loved','it'], ['the','best','film','great'], ['great']]",
        "",
        "def encode(toks):",
        {"s": '    return ___   # TODO: map each token to its id (use VOCAB, default [UNK]=1)',
         "a": '    return [VOCAB.get(t, 1) for t in toks]'},
        "",
        "def pad_batch(batch):",
        "    ids = [encode(toks) for toks in batch]",
        "    max_len = max(len(x) for x in ids)",
        "    input_ids, attention_mask = [], []",
        "    for seq in ids:",
        {"s": '        mask = ___   # TODO: a list of 1s, one per real token in seq',
         "a": '        mask = [1] * len(seq)'},
        {"s": '        pad_n = ___  # TODO: how many PADs to add (max_len - len(seq))',
         "a": '        pad_n = max_len - len(seq)'},
        "        input_ids.append(seq + [PAD] * pad_n)",
        "        attention_mask.append(mask + [0] * pad_n)",
        "    return input_ids, attention_mask",
        "",
        "try:",
        "    ii, am = pad_batch(batch)",
        "    for a, b in zip(ii, am): print(a, am and b)",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''def _run(): return pad_batch(batch)
expect_true("all rows padded to the same length", lambda: len(set(len(r) for r in _run()[0])) == 1)
expect_true("attention mask matches input length", lambda: all(len(a)==len(m) for a,m in zip(*_run())))
expect_true("mask has a 1 per real token", lambda: _run()[1][0] == [1,1,1,0])
expect_true("padding id is 0 where mask is 0", lambda: all(tok==0 for r,m in zip(*_run()) for tok,bit in zip(r,m) if bit==0))'''),
      footer(4, "`input_ids` + `attention_mask` is the real contract with a transformer. The Hugging Face tokenizer does exactly this for you &mdash; now you know what it returns and why."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-dataset-prep", "Beginner",
     "Preparing a Dataset for Fine-tuning", 20,
     "Turn raw labelled examples into the clean texts and integer labels a training run needs.",
     ["Dataset prep", "Label encoding", "Class balance"])
def _l5(sol):
    return [
      header(5, "Preparing a Dataset for Fine-tuning", "Beginner", 20,
        ["Separate raw examples into texts and labels",
         "Normalise text and encode string labels to integers",
         "Check class balance before training"],
        "Dataset prep for fine-tuning"),
      setup(5),
      md('''## Concept
Before fine-tuning you need clean **texts** and integer **labels**. Real datasets have string
labels (e.g. "pos"/"neg") that must be **encoded** to integers, and you should check the
**class balance** so the model does not just learn to predict the majority.'''),
      code('''# DEMO -- raw rows with STRING labels
RAW = [("Loved it!", "pos"), ("So boring.", "neg"), ("Brilliant film", "pos"),
       ("A dull mess", "neg"), ("Wonderful!", "pos"), ("Terrible.", "neg")]
print(RAW[0])'''),
      md('''## Your Turn
Build cleaned `texts`, a `label2id` map, and integer `y`, then report class balance.'''),
      code(render([
        'RAW = [("Loved it!", "pos"), ("So boring.", "neg"), ("Brilliant film", "pos"),',
        '       ("A dull mess", "neg"), ("Wonderful!", "pos"), ("Terrible.", "neg"),',
        '       ("Great stuff", "pos"), ("I hated it", "neg")]',
        "",
        "def clean(s):",
        {"s": '    return ___   # TODO: lowercase and strip surrounding whitespace',
         "a": '    return s.lower().strip()'},
        "",
        "label2id = {\"neg\": 0, \"pos\": 1}",
        {"s": 'texts = ___   # TODO: cleaned text for each row',
         "a": 'texts = [clean(t) for t, lbl in RAW]'},
        {"s": 'y = ___       # TODO: integer label for each row via label2id',
         "a": 'y = [label2id[lbl] for t, lbl in RAW]'},
        "",
        "from collections import Counter",
        "def balance(): return dict(Counter(y))",
        "try: print('texts:', len(texts), '| labels:', y, '| balance:', balance())",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("texts cleaned (lowercase)", lambda: texts[0] == "loved it!")
expect_true("one integer label per row", lambda: len(y) == len(RAW) and set(y) <= {0,1})
expect_true("labels encoded correctly", lambda: y[:4] == [1,0,1,0])
expect_true("class balance computed", lambda: balance().get(0,0) > 0 and balance().get(1,0) > 0)'''),
      footer(5, "Clean text + integer labels + a balance check is the unglamorous 80% of any fine-tune. Garbage in, garbage out &mdash; prep earns the accuracy."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-train-val-split", "Beginner",
     "Train / Validation Split: Judge on Unseen Data", 20,
     "Hold out a validation set so you measure real generalisation, not memorisation.",
     ["Train/val split", "Stratification", "Held-out evaluation"])
def _l6(sol):
    return [
      header(6, "Train / Validation Split: Judge on Unseen Data", "Beginner", 20,
        ["Split a dataset into train and validation sets",
         "Stratify so both classes appear in each split",
         "Understand why you never evaluate on training data"],
        "Dataset prep for fine-tuning"),
      setup(6),
      md('''## Concept
You must judge a model on data it **never trained on**, or you only measure memorisation.
We hold out a **validation set**, and **stratify** so the class proportions are preserved in
both splits (vital for small or imbalanced data).'''),
      code('''# DEMO
''' + SENT_DATA + '''
print("total examples:", len(texts), "| positives:", sum(labels))'''),
      md('''## Your Turn
Make a stratified train/validation split and sanity-check it.'''),
      code(render([
        SENT_DATA,
        "from sklearn.model_selection import train_test_split",
        "",
        "def split():",
        {"s": '    test_frac = ___   # TODO: a fraction like 0.25',
         "a": '    test_frac = 0.25'},
        "    return train_test_split(texts, labels, test_size=test_frac,",
        {"s": '                            random_state=0, stratify=___)   # TODO: stratify on labels',
         "a": '                            random_state=0, stratify=labels)'},
        "",
        "try:",
        "    Xtr, Xval, ytr, yval = split()",
        "    print('train:', len(Xtr), '| val:', len(Xval), '| val positives:', sum(yval))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''def _s(): return split()
expect_true("split returns 4 parts", lambda: len(_s()) == 4)
expect_true("validation set is non-empty and smaller than train", lambda: 0 < len(_s()[1]) < len(_s()[0]))
expect_true("no overlap between train and val texts", lambda: set(_s()[0]).isdisjoint(set(_s()[1])))
expect_true("both classes present in validation (stratified)", lambda: set(_s()[3]) == {0,1})'''),
      footer(6, "The validation set is sacred: it is your honest estimate of real-world accuracy. Stratify on small data so a class is not accidentally missing."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-feature-extraction-head", "Intermediate",
     "Transfer Learning: Frozen Features + a Trainable Head", 30,
     "Freeze a feature extractor (TF-IDF) and train only a small classifier head -- the essence of fine-tuning.",
     ["Transfer learning", "Feature extraction", "Classifier head"])
def _l7(sol):
    return [
      header(7, "Transfer Learning: Frozen Features + a Trainable Head", "Intermediate", 30,
        ["Use a frozen feature extractor to turn text into vectors",
         "Train only a small classifier head on top",
         "See why this is fast, data-efficient transfer learning"],
        "Transfer learning"),
      setup(7),
      md('''## Concept
**Fine-tuning** in its cheapest form: keep a powerful **frozen feature extractor** and train
only a small **head**. Here TF-IDF is the frozen extractor and `LogisticRegression` is the head.
(In the sandbox you swap TF-IDF for a frozen BERT &mdash; the *shape* is identical; see the
optional cell.)'''),
      code('''# DEMO
''' + SENT_DATA + '''
from sklearn.model_selection import train_test_split
Xtr_text, Xval_text, ytr, yval = train_test_split(texts, labels, test_size=0.25,
                                                   random_state=0, stratify=labels)
print("train:", len(Xtr_text), "| val:", len(Xval_text))'''),
      md('''## Your Turn
Fit the frozen extractor on the training text, transform both splits, train the head, score it.'''),
      code(render([
        "from sklearn.feature_extraction.text import TfidfVectorizer",
        "from sklearn.linear_model import LogisticRegression",
        "from sklearn.metrics import accuracy_score",
        "",
        "def run():",
        "    vec = TfidfVectorizer()",
        {"s": '    Xtr = ___   # TODO: vec.fit_transform on the TRAIN text',
         "a": '    Xtr = vec.fit_transform(Xtr_text)'},
        {"s": '    Xval = ___  # TODO: vec.transform on the VAL text (transform only!)',
         "a": '    Xval = vec.transform(Xval_text)'},
        "    head = LogisticRegression(max_iter=1000)",
        {"s": '    ___   # TODO: fit the head on (Xtr, ytr)',
         "a": '    head.fit(Xtr, ytr)'},
        "    return accuracy_score(yval, head.predict(Xval))",
        "",
        "try: print('val accuracy:', round(run(), 3))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("pipeline returns an accuracy", lambda: isinstance(run(), float))
expect_true("val accuracy >= 0.8 (transfer learning works)", lambda: run() >= 0.8)'''),
      *optional_hf(
        "Swap TF-IDF for a REAL frozen transformer as the feature extractor, then train the same head.",
        '''try:
    from transformers import pipeline
    import numpy as np
    fe = pipeline("feature-extraction", model="prajjwal1/bert-tiny")
    def embed(t):
        v = np.array(fe(t)[0])      # (tokens, dim)
        return v.mean(axis=0)       # mean-pool to one vector
    print("bert-tiny embedding dim:", embed("a great film").shape)
    print("Same recipe: frozen transformer features -> a small trainable head.")
except Exception as e:
    print("transformers not available -- the TF-IDF version above already taught the pattern.", type(e).__name__)'''),
      footer(7, "Frozen extractor + trainable head = transfer learning. It needs little data and trains in seconds &mdash; the workhorse before you ever unfreeze the big model."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-evaluation-metrics", "Intermediate",
     "Beyond Accuracy: Precision, Recall & Confusion", 30,
     "Compute precision, recall and a confusion matrix -- the metrics that reveal what accuracy hides.",
     ["Precision/recall", "Confusion matrix", "Evaluation"])
def _l8(sol):
    return [
      header(8, "Beyond Accuracy: Precision, Recall & Confusion", "Intermediate", 30,
        ["Build a confusion matrix from predictions",
         "Compute precision and recall for the positive class",
         "See why accuracy alone can mislead"],
        "Evaluation"),
      setup(8),
      md('''## Concept
Accuracy hides *how* a model is wrong. The **confusion matrix** counts TP/FP/FN/TN.
**Precision** = TP / (TP+FP) ("when it says positive, is it right?").
**Recall** = TP / (TP+FN) ("of the real positives, how many did it catch?").'''),
      code('''# DEMO -- true vs predicted labels
y_true = [1,1,1,0,0,0,1,0]
y_pred = [1,0,1,0,1,0,1,0]
print("true:", y_true)
print("pred:", y_pred)'''),
      md('''## Your Turn
Compute TP/FP/FN, then precision and recall for the positive class (label 1).'''),
      code(render([
        "y_true = [1,1,1,0,0,0,1,0]",
        "y_pred = [1,0,1,0,1,0,1,0]",
        "",
        "def counts():",
        {"s": '    TP = ___   # TODO: predicted 1 AND true 1',
         "a": '    TP = sum(1 for t,p in zip(y_true,y_pred) if t==1 and p==1)'},
        {"s": '    FP = ___   # TODO: predicted 1 BUT true 0',
         "a": '    FP = sum(1 for t,p in zip(y_true,y_pred) if t==0 and p==1)'},
        {"s": '    FN = ___   # TODO: predicted 0 BUT true 1',
         "a": '    FN = sum(1 for t,p in zip(y_true,y_pred) if t==1 and p==0)'},
        "    return TP, FP, FN",
        "",
        "def precision():",
        "    TP, FP, FN = counts()",
        {"s": '    return ___   # TODO: TP / (TP + FP)',
         "a": '    return TP / (TP + FP)'},
        "def recall():",
        "    TP, FP, FN = counts()",
        {"s": '    return ___   # TODO: TP / (TP + FN)',
         "a": '    return TP / (TP + FN)'},
        "",
        "try: print('counts(TP,FP,FN):', counts(), '| precision:', round(precision(),3), '| recall:', round(recall(),3))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect("TP,FP,FN counts", counts(), (3, 1, 1))
expect_true("precision == 0.75", lambda: abs(precision() - 0.75) < 1e-9)
expect_true("recall == 0.75", lambda: abs(recall() - 0.75) < 1e-9)
from sklearn.metrics import precision_score
expect_true("matches sklearn precision", lambda: abs(precision() - precision_score(y_true, y_pred)) < 1e-9)'''),
      footer(8, "On imbalanced or high-stakes tasks, precision and recall matter more than accuracy. Always look at the confusion matrix before trusting a score."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-frozen-vs-finetune", "Intermediate",
     "Data Efficiency: How Much Training Data Do You Need?", 30,
     "Train the head on growing slices of data and watch accuracy climb -- the case for transfer learning.",
     ["Data efficiency", "Learning curve", "Transfer learning"])
def _l9(sol):
    return [
      header(9, "Data Efficiency: How Much Training Data Do You Need?", "Intermediate", 30,
        ["Train the same head on growing fractions of data",
         "Plot a learning curve of validation accuracy vs train size",
         "See why transfer learning shines with little data"],
        "Transfer learning"),
      setup(9),
      md('''## Concept
A big reason to use pre-trained models: they need **little task data**. We train the head on
growing slices of the training set and watch validation accuracy rise &mdash; a **learning
curve**. With frozen good features, even a few dozen examples go a long way.'''),
      code('''# DEMO
''' + SENT_DATA + '''
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
Xtr_t, Xval_t, ytr, yval = train_test_split(texts, labels, test_size=0.3, random_state=0, stratify=labels)
vec = TfidfVectorizer().fit(Xtr_t)
Xtr, Xval = vec.transform(Xtr_t), vec.transform(Xval_t)
print("train pool:", Xtr.shape[0], "| val:", Xval.shape[0])'''),
      md('''## Your Turn
For each fraction, train on the first k examples and record validation accuracy.'''),
      code(render([
        "from sklearn.linear_model import LogisticRegression",
        "from sklearn.metrics import accuracy_score",
        "import numpy as np",
        "",
        "def curve():",
        "    n = Xtr.shape[0]",
        "    accs = []",
        "    for frac in [0.25, 0.5, 1.0]:",
        "        k = max(2, int(n * frac))",
        "        head = LogisticRegression(max_iter=1000)",
        {"s": '        head.fit(Xtr[:k], ytr[:k])   # train on the first k examples',
         "a": '        head.fit(Xtr[:k], ytr[:k])'},
        {"s": '        acc = ___   # TODO: accuracy_score(yval, head.predict(Xval))',
         "a": '        acc = accuracy_score(yval, head.predict(Xval))'},
        "        accs.append(acc)",
        "    return accs",
        "",
        "try:",
        "    accs = curve()",
        "    print('val accuracy at 25%/50%/100%:', [round(a,3) for a in accs])",
        "    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt",
        "    plt.plot([0.25,0.5,1.0], accs, 'o-'); plt.xlabel('train fraction'); plt.ylabel('val accuracy')",
        "    plt.title('Learning curve'); plt.savefig(WORK + '/learning_curve.png', dpi=90)",
        "    print('saved', WORK + '/learning_curve.png')",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("curve returns 3 accuracies", lambda: len(curve()) == 3)
expect_true("all accuracies are valid probabilities", lambda: all(0.0 <= a <= 1.0 for a in curve()))
expect_true("full data is at least as good as the smallest slice", lambda: curve()[-1] >= curve()[0] - 1e-9)'''),
      footer(9, "Transfer learning is **data-efficient**: good frozen features mean a small head learns from few labels. That is why fine-tuning beats training from scratch."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-finetune-sentiment", "Advanced",
     "Fine-tune a Sentiment Classifier (before vs after)", 40,
     "Fine-tune a task head on a pre-trained representation and prove it beats the untrained baseline.",
     ["Fine-tuning", "Baseline vs trained", "Prediction"])
def _l10(sol):
    return [
      header(10, "Fine-tune a Sentiment Classifier (before vs after)", "Advanced", 40,
        ["Establish an untrained baseline accuracy",
         "Fine-tune (train) the classifier head and beat the baseline",
         "Predict sentiment on brand-new sentences"],
        "Fine-tuning end-to-end"),
      setup(10),
      md('''## Concept
This is the client's **fine-tune for sentiment**, in its portable form: a pre-trained feature
extractor (frozen) + a head we **train** on labelled reviews. We measure accuracy **before**
(an untrained majority baseline) vs **after** training, then predict on new text. The optional
cell does the *same task* by fine-tuning a real **bert-tiny** &mdash; the sandbox target.'''),
      code('''# DEMO
''' + SENT_DATA + '''
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
Xtr_t, Xval_t, ytr, yval = train_test_split(texts, labels, test_size=0.3, random_state=0, stratify=labels)
vec = TfidfVectorizer().fit(Xtr_t)
Xtr, Xval = vec.transform(Xtr_t), vec.transform(Xval_t)
print("ready: train", Xtr.shape[0], "val", Xval.shape[0])'''),
      md('''## Your Turn
Compute the baseline, train the head, compare, and predict on new sentences.'''),
      code(render([
        "from sklearn.linear_model import LogisticRegression",
        "from sklearn.metrics import accuracy_score",
        "from collections import Counter",
        "",
        "def baseline_acc():",
        "    # always predict the majority class of the training labels",
        "    majority = Counter(ytr).most_common(1)[0][0]",
        {"s": '    return ___   # TODO: accuracy of always predicting `majority` on yval',
         "a": '    return accuracy_score(yval, [majority] * len(yval))'},
        "",
        "head = LogisticRegression(max_iter=1000)",
        "def trained_acc():",
        {"s": '    ___   # TODO: fit head on (Xtr, ytr)',
         "a": '    head.fit(Xtr, ytr)'},
        "    return accuracy_score(yval, head.predict(Xval))",
        "",
        "def predict_new(sentences):",
        "    head.fit(Xtr, ytr)",
        {"s": '    return list(head.predict(___))   # TODO: vectorise sentences with vec.transform',
         "a": '    return list(head.predict(vec.transform(sentences)))'},
        "",
        "try:",
        "    print('baseline:', round(baseline_acc(),3), '| trained:', round(trained_acc(),3))",
        "    print('predict:', predict_new(['a wonderful brilliant film', 'a boring awful mess']))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("baseline computed (<= 0.7 on balanced data)", lambda: baseline_acc() <= 0.7)
expect_true("trained accuracy >= 0.8", lambda: trained_acc() >= 0.8)
expect_true("training beats the baseline", lambda: trained_acc() > baseline_acc())
expect_true("predicts new positive/negative correctly", lambda: predict_new(['a wonderful brilliant film','a boring awful mess']) == [1,0])'''),
      *optional_hf(
        "Fine-tune a REAL bert-tiny on the same sentences (a few CPU steps) and predict.",
        '''try:
    import torch, numpy as np
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    name = "prajjwal1/bert-tiny"
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSequenceClassification.from_pretrained(name, num_labels=2)
    opt = torch.optim.AdamW(model.parameters(), lr=5e-4)
    enc = tok(Xtr_t, padding=True, truncation=True, return_tensors="pt")
    yt = torch.tensor(ytr)
    model.train()
    for step in range(30):                      # a few steps on tiny data
        opt.zero_grad()
        out = model(**enc, labels=yt)
        out.loss.backward(); opt.step()
    model.eval()
    with torch.no_grad():
        venc = tok(Xval_t, padding=True, truncation=True, return_tensors="pt")
        pred = model(**venc).logits.argmax(-1).numpy()
    print("real bert-tiny val accuracy:", float((pred == np.array(yval)).mean()))
except Exception as e:
    print("transformers/torch not available -- the graded head above already fine-tuned a model.", type(e).__name__)'''),
      footer(10, "You fine-tuned a classifier: an untrained baseline, then a head trained on your labels that beats it and predicts new text. Real BERT fine-tuning (optional cell) is the same loop, scaled."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-improve-and-evaluate", "Advanced",
     "Improve & Evaluate Your Fine-tuned Model", 40,
     "Tune the model's regularisation and evaluate it honestly with a confusion matrix.",
     ["Regularisation (C)", "Hyperparameters", "Confusion matrix"])
def _l11(sol):
    return [
      header(11, "Improve & Evaluate Your Fine-tuned Model", "Advanced", 40,
        ["Tune the head's regularisation strength C",
         "Beat a weak, over-regularised baseline",
         "Evaluate with a confusion matrix you can read"],
        "Cost / latency / data tradeoffs"),
      setup(11),
      md('''## Concept
A first model is rarely the best. The head's **regularisation** strength `C` matters: too small
and the model **underfits** (it barely learns); a larger `C` lets it fit the signal. We start
from a weak, over-regularised baseline, **tune `C`**, and **evaluate** with a confusion matrix to
see exactly which class it confuses. (Bigger isn't always better &mdash; on tiny data simpler
often wins; tuning is empirical.)'''),
      code('''# DEMO
''' + SENT_DATA + '''
from sklearn.model_selection import train_test_split
Xtr_t, Xval_t, ytr, yval = train_test_split(texts, labels, test_size=0.3, random_state=0, stratify=labels)
print("baseline recipe = unigrams + default C")'''),
      md('''## Your Turn
Build a weak (over-regularised) baseline, then a tuned model, and the confusion matrix.'''),
      code(render([
        "from sklearn.feature_extraction.text import TfidfVectorizer",
        "from sklearn.linear_model import LogisticRegression",
        "from sklearn.metrics import accuracy_score, confusion_matrix",
        "",
        "vec = TfidfVectorizer()",
        "Xtr, Xval = vec.fit_transform(Xtr_t), vec.transform(Xval_t)",
        "",
        "def fit_C(C):",
        "    head = LogisticRegression(max_iter=1000, C=C).fit(Xtr, ytr)",
        "    pred = head.predict(Xval)",
        "    return accuracy_score(yval, pred), confusion_matrix(yval, pred)",
        "",
        "def weak_acc():",
        {"s": '    return fit_C(___)[0]   # TODO: a tiny C that under-fits, e.g. 0.05',
         "a": '    return fit_C(0.05)[0]'},
        "def tuned():",
        {"s": '    return fit_C(___)      # TODO: a well-tuned C like 4.0  -> (acc, confusion)',
         "a": '    return fit_C(4.0)'},
        "",
        "try:",
        "    acc, cm = tuned()",
        "    print('weak baseline acc:', round(weak_acc(),3), '| tuned acc:', round(acc,3))",
        "    print('confusion matrix [[TN,FP],[FN,TP]]:')",
        "    print(cm)",
        "    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt",
        "    plt.imshow(cm, cmap='Blues'); plt.title('Confusion matrix'); plt.colorbar()",
        "    plt.savefig(WORK + '/confusion.png', dpi=90); print('saved', WORK + '/confusion.png')",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("tuned model returns (acc, confusion matrix)", lambda: tuned()[1].shape == (2,2))
expect_true("tuned val accuracy >= 0.8", lambda: tuned()[0] >= 0.8)
expect_true("tuning beats the weak baseline", lambda: tuned()[0] > weak_acc())
expect_true("confusion matrix totals match the val set size", lambda: int(tuned()[1].sum()) == len(yval))'''),
      footer(11, "Iterate: tune regularisation and judge on a confusion matrix. This is the real fine-tuning loop &mdash; small honest steps measured every time, and 'bigger' is not always better."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-adapt-a-model", "Advanced",
     "Capstone: Adapt a Pre-trained Model to a New Task", 45,
     "Take a fresh labelled task end-to-end -- pick features, train a head, evaluate, and predict.",
     ["End-to-end", "Transfer learning", "Capstone"])
def _l12(sol):
    return [
      header(12, "Capstone: Adapt a Pre-trained Model to a New Task", "Advanced", 45,
        ["Apply the whole Module 4 pipeline to a NEW task (topic detection)",
         "Build features, train a head, and hold out a validation set",
         "Evaluate and predict on unseen text"],
        "Fine-tuning end-to-end"),
      setup(12),
      md('''## Concept
Capstone: the full transfer-learning workflow on a **new** task &mdash; classify a sentence as
**sports** vs **tech**. Same recipe as sentiment: frozen features + trainable head + held-out
evaluation. This is exactly how you would adapt a pre-trained model to *your* problem.'''),
      code('''# DEMO -- a new tiny task: sports (0) vs tech (1). Keywords recur across rows
# (team/goal/game/player... vs app/software/data/chip...) so the model generalises.
TASK = [
    ("the team scored a goal to win the game", 0),
    ("our team won the match with a late goal", 0),
    ("the player scored twice in the game", 0),
    ("a great goal helped the team win the match", 0),
    ("the coach and team celebrated the win", 0),
    ("the player passed the ball and scored a goal", 0),
    ("the team lost the game by one goal", 0),
    ("the new app runs on a fast chip", 1),
    ("the software update improved the app", 1),
    ("the app stores its data in the cloud", 1),
    ("a new chip makes the computer software faster", 1),
    ("the cloud server runs the data software", 1),
    ("the app uses data and a fast chip", 1),
    ("the computer software had a data bug", 1),
]
print("examples:", len(TASK))'''),
      md('''## Your Turn
Split, fit a frozen extractor + head, evaluate, and predict on new sentences.'''),
      code(render([
        "from sklearn.model_selection import train_test_split",
        "from sklearn.feature_extraction.text import TfidfVectorizer",
        "from sklearn.linear_model import LogisticRegression",
        "from sklearn.metrics import accuracy_score",
        "",
        "X = [t for t, y in TASK]; Y = [y for t, y in TASK]",
        "Xtr_t, Xval_t, ytr, yval = train_test_split(X, Y, test_size=0.3, random_state=0, stratify=Y)",
        "vec = TfidfVectorizer()",
        "head = LogisticRegression(max_iter=1000)",
        "",
        "def fit_and_eval():",
        {"s": '    Xtr = ___   # TODO: vec.fit_transform on the train text',
         "a": '    Xtr = vec.fit_transform(Xtr_t)'},
        {"s": '    head.fit(Xtr, ytr)   # train the head',
         "a": '    head.fit(Xtr, ytr)'},
        {"s": '    return accuracy_score(yval, head.predict(___))   # TODO: vectorise val text',
         "a": '    return accuracy_score(yval, head.predict(vec.transform(Xval_t)))'},
        "",
        "def classify(sentence):",
        "    return int(head.predict(vec.transform([sentence]))[0])",
        "",
        "try:",
        "    print('val accuracy:', round(fit_and_eval(), 3))",
        "    print('\"the goalkeeper made a great save\" ->', classify('the player scored a goal for the team'))",
        "    print('\"the gpu accelerates the neural network\" ->', classify('the app stores data on the cloud server'))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("end-to-end pipeline returns an accuracy", lambda: isinstance(fit_and_eval(), float))
expect_true("val accuracy >= 0.8 on the new task", lambda: fit_and_eval() >= 0.8)
expect_true("classifies a sports sentence as 0", lambda: (fit_and_eval(), classify('the player scored a goal for the team'))[1] == 0)
expect_true("classifies a tech sentence as 1", lambda: (fit_and_eval(), classify('the app stores data on the cloud server'))[1] == 1)'''),
      *optional_hf(
        "Adapt a REAL pretrained model to this task with zero-shot classification (no training).",
        '''try:
    from transformers import pipeline
    zs = pipeline("zero-shot-classification")
    out = zs("the gpu accelerates the neural network", candidate_labels=["sports", "tech"])
    print(out["labels"][0], "(", round(out["scores"][0], 3), ")")
    print("Pre-trained models can even classify with NO task training -- zero-shot.")
except Exception as e:
    print("transformers not available -- your trained head above already solves the task.", type(e).__name__)'''),
      footer(12, "You adapted the pre-trained pipeline to a brand-new task end-to-end. That is Module 4 in one move: stand on a pre-trained model, add a small head, evaluate honestly, ship. Next: Day 3 &mdash; agents."),
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
        banner = md(f'''> ## SOLUTION / ANSWER KEY &mdash; Lab 4.{nn}
> This is the **completed** notebook (all `___` blanks filled). For the student version, open
> [`../{info['slug']}.ipynb`](../{info['slug']}.ipynb). Trainer use &mdash; or self-check after you've tried it yourself.''')
        with open(os.path.join(SOL_DIR, fname), "w") as f:
            json.dump(notebook([banner] + info["build"](True)), f, indent=1, ensure_ascii=False)

print(f"Wrote {len(NB)} notebooks to {OUT_DIR}" + (f" and solutions to {SOL_DIR}" if SOL_DIR else ""))

with open(os.path.join(_HERE, "_meta.json"), "w") as f:
    json.dump({str(nn): {k: NB[nn][k] for k in ("slug","level","title","mins","summary","concepts")}
               for nn in NB}, f, indent=1)
