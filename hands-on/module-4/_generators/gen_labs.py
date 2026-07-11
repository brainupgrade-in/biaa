# -*- coding: utf-8 -*-
"""Generator for Day 2 Module 4 hands-on labs (12 notebooks) -- NEAR-REAL design.
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

This is the "Pre-trained Models & Fine-tuning" module. Participants run REAL Hugging Face
Transformers locally on CPU and -- the client's headline -- ACTUALLY FINE-TUNE a real model
for sentiment, measuring a real before -> after improvement. There is NO auto-grader: every
lab ends "Build it -> Run it for real -> What to notice -> Your turn".

What is real:
  distilbert-base-uncased-finetuned-sst-2-english . out-of-the-box sentiment + real logits (labs 1, 2, 8)
  distilbert-base-uncased ......................... real tokenizer: input_ids / mask / padding (labs 4, 5)
  prajjwal1/bert-tiny ............................. frozen feature extractor (labs 7, 9) AND the model we
                                                    really FINE-TUNE end-to-end (labs 10, 11, 12)

The fine-tune labs are the primary path (not optional): a real AutoModelForSequenceClassification,
a real tokenized batch, a real torch training loop, and a real held-out before/after accuracy. On
CPU a full fine-tune of bert-tiny on a few dozen sentences finishes in a few seconds.

What stays hand-computed (REAL mechanics, not stubs): softmax over real logits, and precision/recall
from real model predictions -- these teach the maths the metrics run on.

Student robustness (no grader): cells that exercise the blanks or load/train a model are wrapped by
guard()/hfrun() so an unfilled `___` -- or a missing network on first download -- prints a friendly
note instead of crashing. A student notebook runs top-to-bottom; a solution notebook runs the real
thing and prints real model output (including the real before -> after fine-tune numbers)."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day2-module4-pretrained-models-and-fine-tuning.html"
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
    """Wrap a cell that calls blanked code so an unfilled ___ prints a note, not a crash."""
    return ("try:\n" + _indent(exercise, 4) +
            '\nexcept Exception as e:\n    print("(Fill the ___ blanks above, then re-run.)", type(e).__name__, "--", e)')

def hfrun(exercise):
    """Wrap a 'run / train a real model' cell: friendly note if a blank is unfilled OR the first
    download has no network -- never crash Run All."""
    return ("try:\n" + _indent(exercise, 4) +
            '\nexcept Exception as e:\n'
            '    print("(If a ___ is still unfilled, fill it above. On first run the model downloads")\n'
            '    print(" from the Hugging Face hub -- that needs network; re-run once it finishes.)")\n'
            '    print("  reason:", type(e).__name__, "--", e)')

def setup(nn):
    return code(f'''# Setup -- run me first
import os, pathlib
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True), override=True)   # GROQ_API_KEY etc. (optional hosted compare)

WORK = "/tmp/biaa-lab-04-{nn:02d}"
os.makedirs(WORK, exist_ok=True)
print("WORK:", WORK)
print("Real Hugging Face models load from the hub on first use (one-time download, then cached).")''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 4.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 2 &middot; Module 4 &mdash; Pre-trained Models & Fine-tuning**

### What you'll do
{g}

> **How this lab works (near-real):** these labs use **real Hugging Face Transformers** locally on CPU &mdash; a real pretrained sentiment model, a real tokenizer, and (the headline) a **real fine-tune** you run yourself. Read the **Concept**, fill the real `___` blanks in **Build it** (real model / tokenizer / training-loop calls), **Run it for real** to see the **actual model output** (including the real **before &rarr; after** fine-tune numbers), note **What to notice**, then finish with an open **Your turn**. There is **no auto-grader** &mdash; the goal is real results you can read. The genuine maths (softmax, precision/recall) you still compute **by hand** &mdash; real mechanics, not a stub.

> **Models:** small, CPU-friendly models from the HF hub &mdash; `distilbert-base-uncased-finetuned-sst-2-english` (out-of-the-box sentiment + logits), `distilbert-base-uncased` (tokenizer), `prajjwal1/bert-tiny` (frozen features **and** the model you fine-tune). First use downloads the weights (needs network), then they are cached. An optional hosted comparison uses `ChatGroq` (`GROQ_API_KEY` in `.env`).

**Reference:** [Module 4 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 4 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 4 labs](./index.html) &nbsp;&middot;&nbsp; [Module 4 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def concept(text):  return md("## Concept\n" + text)
def buildmd(text):  return md("## Build it\n" + text)
def runmd(text):    return md("## Run it for real\n" + text)
def noticemd(text): return md("## What to notice\n" + text)
def yourturn(text): return md("## Your turn (open task &mdash; no grader)\n" + text)

def sol_answer(sol, code_text):
    """Solution-only: a worked reference for the open 'Your turn' task above.
    Returns nothing in the student notebook (the task stays open); in the SOLUTION
    it appends one runnable cell so participants have something to compare against."""
    if not sol:
        return []
    return [code("# --- Reference answer (ONE good way to do the 'Your turn' task -- compare with your own) ---\n" + code_text)]

# A tiny labelled sentiment dataset (1 = positive, 0 = negative). Strong sentiment words RECUR
# across examples so a model trained on one split generalises to the held-out split -- essential
# on tiny data and what makes a real CPU fine-tune converge in seconds.
SENT_DATA = '''# A tiny labelled sentiment dataset (1 = positive, 0 = negative)
SENT = [
    ("i love this it is great", 1), ("a great and wonderful film", 1),
    ("truly wonderful i love it", 1), ("excellent and brilliant work", 1),
    ("the best most brilliant story", 1), ("i love how great it is", 1),
    ("wonderful excellent and great fun", 1), ("a brilliant and great success", 1),
    ("great fun i really love it", 1), ("the best film wonderful and brilliant", 1),
    ("excellent great and lovely work", 1), ("i love this brilliant great film", 1),
    ("wonderful great and the best", 1), ("so good i love it great", 1),
    ("i hate this it is terrible", 0), ("a terrible and awful film", 0),
    ("truly awful i hate it", 0), ("boring and terrible work", 0),
    ("the worst most boring story", 0), ("i hate how bad it is", 0),
    ("awful boring and dull mess", 0), ("a terrible and bad failure", 0),
    ("boring mess i really hate it", 0), ("the worst film awful and boring", 0),
    ("terrible bad and dull work", 0), ("i hate this awful boring film", 0),
    ("awful terrible and the worst", 0), ("so bad i hate it terrible", 0),
]
texts  = [t for t, y in SENT]
labels = [y for t, y in SENT]'''

# A REAL frozen feature extractor: run prajjwal1/bert-tiny and mean-pool its token vectors into one
# vector per text. No training -- the backbone is frozen (torch.no_grad). Lazy-loads + caches the
# model on first call so the *build* cell never touches the network -- only the guarded run cell does.
FEATS_DEF = '''import numpy as np
_FE = {}
def extract_features(texts):
    """REAL frozen features: forward pass through prajjwal1/bert-tiny, mean-pool over real tokens."""
    import torch
    from transformers import AutoTokenizer, AutoModel
    if not _FE:
        name = "prajjwal1/bert-tiny"
        _FE["tok"] = AutoTokenizer.from_pretrained(name)
        _FE["mdl"] = AutoModel.from_pretrained(name); _FE["mdl"].eval()
    if isinstance(texts, str): texts = [texts]
    enc = _FE["tok"](texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad(): out = _FE["mdl"](**enc)          # frozen: no gradients, no weight updates
    mask = enc["attention_mask"].unsqueeze(-1).float()
    pooled = (out.last_hidden_state * mask).sum(1) / mask.sum(1)   # mean over REAL tokens only
    return pooled.numpy()'''

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
     "Run a REAL pretrained sentiment model (distilbert SST-2) out of the box on new text and measure its accuracy -- the power of pre-training, zero training required.",
     ["Real pretrained model", "Inference", "sentiment-analysis pipeline"])
def _l1(sol):
    return [
      header(1, "Using a Pre-trained Model: Sentiment Out of the Box", "Beginner", 20,
        ["Load a real pretrained sentiment model from the Hugging Face hub",
         "Label brand-new text with zero training (inference only)",
         "Measure how accurate an out-of-the-box model is"],
        "Hugging Face hub & pipelines"),
      setup(1),
      concept('''A **pre-trained model** already learned from huge data, so it works **out of the box** &mdash;
you just run **inference**. We load the real **distilbert-base-uncased-finetuned-sst-2-english**
(a distilbert that was already fine-tuned on the SST-2 movie-review sentiment task) via a Hugging
Face `pipeline` and let it label text it has never seen. No training on our side at all.'''),
      buildmd("Fill in the model name and read the pipeline's real output into a 0/1 label."),
      code(render([
        "from transformers import pipeline",
        "def build_sentiment():",
        {"s": '    return pipeline("sentiment-analysis", model=___)   # TODO: "distilbert-base-uncased-finetuned-sst-2-english"',
         "a": '    return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")'},
        "",
        "def predict(clf, text):",
        '    r = clf(text)[0]                       # e.g. {"label": "POSITIVE", "score": 0.999}',
        {"s": '    return 1 if r["label"] == ___ else 0   # TODO: "POSITIVE"',
         "a": '    return 1 if r["label"] == "POSITIVE" else 0'},
      ], sol)),
      runmd("Load the real model and label a few sentences, then score it on labelled samples."),
      code(hfrun('''clf = build_sentiment()          # downloads a real ~250MB model once, then cached
SAMPLES = [
    ("a brilliant and moving masterpiece", 1),
    ("a boring dreadful waste of time", 0),
    ("i loved it, truly excellent", 1),
    ("awful and disappointing", 0),
]
for text, _ in SAMPLES:
    print(clf(text)[0], "<-", text)
acc = sum(1 for t, y in SAMPLES if predict(clf, t) == y) / len(SAMPLES)
print("\\naccuracy on the labelled samples:", acc)''')),
      noticemd('''- The model returns a **label** (`POSITIVE` / `NEGATIVE`) **and a confidence score** &mdash; real output from a real network, not a lexicon.
- It nails these samples with **zero training on our side**: that is what "pre-trained" buys you.
- It was already **fine-tuned on SST-2** &mdash; the very thing this module teaches you to do yourself. Here you stand on someone else's fine-tune.'''),
      yourturn('''Feed it your own tricky inputs &mdash; sarcasm (`"oh great, another bug"`), negation
(`"not bad at all"`), or mixed sentiment. Where does the real model slip? Build a small labelled list
of your own and compute its accuracy. A "good" answer: you have at least one example the model gets
wrong and a hypothesis for why.'''),
      *sol_answer(sol, hfrun(r'''clf = build_sentiment()
# a small labelled set of deliberately tricky inputs
MINE = [("oh great, another bug", 0), ("not bad at all", 1),
        ("i don't hate it", 1), ("well that was just perfect", 0)]  # last two are sarcasm/litotes
for t, y in MINE:
    print(clf(t)[0], " true:", y, " <-", t)
acc = sum(1 for t, y in MINE if predict(clf, t) == y) / len(MINE)
print("accuracy on my tricky set:", acc)
print("Hypothesis: sarcasm ('oh great...') has positive words but negative intent -- the model reads surface words.")''')),
      footer(1, "A pre-trained model delivers value with **zero training** &mdash; you just run inference. Next: read the **confidence** behind that label, straight from the real logits."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-confidence-scores", "Beginner",
     "Reading a Model's Confidence (softmax over real logits)", 20,
     "Pull the RAW logits out of the real SST-2 model and turn them into a probability and confidence with softmax computed by hand -- exactly what the pipeline does internally.",
     ["Real logits", "Softmax by hand", "Confidence"])
def _l2(sol):
    return [
      header(2, "Reading a Model's Confidence (softmax over real logits)", "Beginner", 20,
        ["Run a real model to get its raw output scores (logits)",
         "Convert logits into probabilities with softmax you implement",
         "Read the predicted label and its confidence"],
        "GPT generation / BERT sentiment"),
      setup(2),
      concept('''A classifier's final layer outputs raw scores (**logits**), one per class. **Softmax** turns them
into probabilities that sum to 1; the **argmax** is the prediction and the **max probability** is the
**confidence**. The `pipeline` does this for you &mdash; here we pull the **real logits** out of
distilbert-SST-2 ourselves and run softmax by hand, so you see exactly where that confidence score
comes from.'''),
      buildmd("Implement softmax, then turn real logits into (label, confidence)."),
      code(render([
        "import numpy as np",
        "def softmax(x):",
        "    x = np.asarray(x, dtype=float)",
        {"s": '    e = ___   # TODO: np.exp(x - x.max())  (subtract max for numerical stability)',
         "a": '    e = np.exp(x - x.max())'},
        {"s": '    return ___   # TODO: e divided by its sum',
         "a": '    return e / e.sum()'},
        "",
        "def label_and_confidence(logits):",
        "    p = softmax(logits)",
        {"s": '    label = ___   # TODO: index of the largest probability (int(np.argmax(p)))',
         "a": '    label = int(np.argmax(p))'},
        {"s": '    conf = ___    # TODO: the largest probability (float(p.max()))',
         "a": '    conf = float(p.max())'},
        "    return label, conf",
      ], sol)),
      runmd("Get REAL logits from the model, then apply your softmax."),
      code(hfrun('''import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
name = "distilbert-base-uncased-finetuned-sst-2-english"
tok = AutoTokenizer.from_pretrained(name)
model = AutoModelForSequenceClassification.from_pretrained(name); model.eval()
print("class order (id -> label):", model.config.id2label)

for text in ["a brilliant and moving masterpiece", "not bad at all", "it was fine i guess"]:
    enc = tok(text, return_tensors="pt")
    with torch.no_grad():
        logits = model(**enc).logits[0].numpy()   # the REAL raw scores [neg, pos]
    label, conf = label_and_confidence(logits)
    print(f"{text!r}")
    print(f"   logits={np.round(logits,3)}  ->  label={model.config.id2label[label]}  confidence={conf:.3f}")''')),
      noticemd('''- The **logits are real** model output &mdash; two numbers, one per class. Softmax turns them into a probability you can read as confidence.
- This SST-2 model is **very confident** even on negation (`"not bad at all"` &rarr; POSITIVE, correctly) &mdash; strong fine-tuned models often are. Pushing the confidence toward 0.5 takes genuinely ambiguous or off-topic text (that is your **Your turn**).
- This confidence is *exactly* the `score` the `pipeline` returned in Lab 4.1 &mdash; you just reproduced its internals.'''),
      yourturn('''Find sentences that make the model **unsure** (confidence closer to 0.5) &mdash; negation,
mixed sentiment, or off-topic text. Confidence is vital when a human reviews the model's output: a
"good" answer names a threshold below which you would route a prediction to a human, and one real
sentence that falls under it.'''),
      *sol_answer(sol, hfrun(r'''import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
name = "distilbert-base-uncased-finetuned-sst-2-english"
tok = AutoTokenizer.from_pretrained(name); model = AutoModelForSequenceClassification.from_pretrained(name); model.eval()
THRESHOLD = 0.90   # below this, route the prediction to a human reviewer
for text in ["it was fine i guess", "not the worst thing ever", "it is a movie that exists"]:
    enc = tok(text, return_tensors="pt")
    with torch.no_grad(): logits = model(**enc).logits[0].numpy()
    label, conf = label_and_confidence(logits)
    route = "-> HUMAN" if conf < THRESHOLD else "auto-accept"
    print(f"{text!r}: {model.config.id2label[label]} conf={conf:.3f} {route}")''')),
      footer(2, "Softmax over real logits *is* the confidence score. It tells you *how sure* the model is &mdash; the number a human-in-the-loop system watches."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-prompt-finetune-or-rag", "Beginner",
     "Prompt, Fine-tune, or RAG? See Why Fine-tuning Wins Here", 15,
     "See the real difference: a model fine-tuned for sentiment nails it while a general (un-fine-tuned) model cannot -- then reason about when to prompt, fine-tune, or use RAG.",
     ["Prompting", "Fine-tuning", "RAG"])
def _l3(sol):
    return [
      header(3, "Prompt, Fine-tune, or RAG? See Why Fine-tuning Wins Here", "Beginner", 15,
        ["Tell prompting, fine-tuning and RAG apart",
         "See a fine-tuned model succeed where a general model fails",
         "Build the judgement you'll use on every real project"],
        "Prompt vs fine-tune vs RAG"),
      setup(3),
      concept('''Three ways to adapt a pre-trained model:
- **Prompt** &mdash; just ask, no training. Fast, flexible, good default.
- **Fine-tune** &mdash; train further on your labelled data. Best for a fixed, specialised task/style (this module).
- **RAG** &mdash; fetch your documents at query time. Best when answers must come from *your* up-to-date knowledge (Day 3).

To *feel* why fine-tuning matters, we compare a **fine-tuned** sentiment model against a **general**
model that was never fine-tuned for sentiment &mdash; on the same sentences.'''),
      buildmd("Pick the two real models: one fine-tuned for sentiment, one general (has a random sentiment head)."),
      code(guard(render([
        "FINETUNED = GENERAL = None   # filled in below",
        {"s": 'FINETUNED = ___   # TODO: "distilbert-base-uncased-finetuned-sst-2-english"',
         "a": 'FINETUNED = "distilbert-base-uncased-finetuned-sst-2-english"'},
        {"s": 'GENERAL   = ___   # TODO: "prajjwal1/bert-tiny"  (never fine-tuned for sentiment)',
         "a": 'GENERAL   = "prajjwal1/bert-tiny"'},
      ], sol))),
      runmd("Run both real models on the same sentences and compare."),
      code(hfrun('''import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
SENTS = ["a brilliant and moving masterpiece", "a boring dreadful waste of time", "i loved it truly excellent"]
TRUE  = [1, 0, 1]

def run_model(name):
    tok = AutoTokenizer.from_pretrained(name)
    mdl = AutoModelForSequenceClassification.from_pretrained(name, num_labels=2); mdl.eval()
    enc = tok(SENTS, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad(): pred = mdl(**enc).logits.argmax(-1).tolist()
    return pred

ft = run_model(FINETUNED)
gen = run_model(GENERAL)
print("truth            :", TRUE)
print("fine-tuned model :", ft, " correct:", sum(p==t for p,t in zip(ft, TRUE)), "/3")
print("general model    :", gen, " correct:", sum(p==t for p,t in zip(gen, TRUE)), "/3", "  <- random head, no idea")''')),
      noticemd('''- The **fine-tuned** model gets sentiment right; the **general** bert-tiny (its sentiment head is randomly initialised) is essentially guessing. **Fine-tuning is what specialised the first one.**
- If a plain prompt to a general model already solved your task, you would **prompt** and skip training. When it cannot &mdash; as here &mdash; you **fine-tune** (labs 4&ndash;12).
- When the answer must come from *your own changing documents*, neither helps: you reach for **RAG** (Day 3).'''),
      yourturn('''Map each scenario to `"prompt"`, `"fine-tune"`, or `"rag"` and justify it: (a) draft a one-off
tagline; (b) classify 50k tickets into your 8 fixed categories; (c) answer staff questions from
internal policy PDFs; (d) always reply in your brand voice. No grader &mdash; a "good" answer explains
*why*, and names which one you would try **first** and how you would know it was enough.'''),
      *sol_answer(sol, r'''DECISION = {
    "(a) draft a one-off tagline":            ("prompt",    "one-shot, no labels; flexibility beats training"),
    "(b) 50k tickets into 8 fixed categories": ("fine-tune", "fixed high-volume task WITH labels -> specialise once, cheap at inference"),
    "(c) answer from internal policy PDFs":    ("rag",       "answers must come from your own changing documents at query time"),
    "(d) always reply in brand voice":         ("fine-tune", "a persistent learned style, not per-query facts"),
}
for scenario, (choice, why) in DECISION.items():
    print(f"{choice:10s} <- {scenario}")
    print(f"           ({why})")
print("Try FIRST: prompt -- it is free to test. Escalate to fine-tune/RAG only when a plain prompt is not good enough.")'''),
      footer(3, "Default to **prompting**; **fine-tune** for a fixed specialised task (this module); reach for **RAG** when answers must come from your own changing data (Day 3)."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-tokenization-for-a-model", "Beginner",
     "Model Inputs: IDs, Padding & Attention Masks (real tokenizer)", 25,
     "Use a REAL transformer tokenizer to turn a batch of text into the padded input_ids and attention_mask a model actually consumes.",
     ["Real tokenizer", "input_ids / mask", "Padding a batch"])
def _l4(sol):
    return [
      header(4, "Model Inputs: IDs, Padding & Attention Masks (real tokenizer)", "Beginner", 25,
        ["Encode a batch of text into integer token IDs with a real tokenizer",
         "Pad the batch to equal length automatically",
         "Read the attention mask that tells the model which tokens are real"],
        "Hugging Face pipelines"),
      setup(4),
      concept('''A transformer takes a batch of equal-length integer sequences. The real tokenizer does all of it:
**encode** tokens to IDs, **pad** short sequences to the batch's max length, and build the
**attention mask** (1 for real tokens, 0 for padding) so the model ignores the padding. We call the
real **distilbert-base-uncased** tokenizer and inspect exactly what it returns.'''),
      buildmd("Fill in the real tokenizer call that pads a batch and returns tensors."),
      code(render([
        "from transformers import AutoTokenizer",
        "def encode_batch(tok, batch):",
        {"s": '    return tok(batch, padding=___, return_tensors="pt")   # TODO: True -- pad to the longest in the batch',
         "a": '    return tok(batch, padding=True, return_tensors="pt")'},
      ], sol)),
      runmd("Encode a real batch and inspect ids, mask, and the decoded padding."),
      code(hfrun('''tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")
batch = ["i loved it", "the best film great and wonderful", "great"]
enc = encode_batch(tok, batch)
print("input_ids:\\n", enc["input_ids"])
print("attention_mask:\\n", enc["attention_mask"])
print("shape:", tuple(enc["input_ids"].shape), "(batch, padded_length)")
print("row 0 decoded:", tok.convert_ids_to_tokens(enc["input_ids"][0]))''')),
      noticemd('''- Every row is padded to the **same length** &mdash; shorter sentences get `[PAD]` (id `0`) at the end.
- The **attention_mask** is `1` for real tokens and `0` for padding, so the model skips the pad positions.
- The tokenizer also adds special tokens: `[CLS]` (id `101`) at the front and `[SEP]` (id `102`) at the end &mdash; the real contract with a BERT-family model.'''),
      yourturn('''Add a very long sentence and a one-word sentence to `batch` and re-run &mdash; watch the padded
length grow. Try `tok(batch, padding="max_length", max_length=12, truncation=True, ...)` and see how
truncation clips long inputs. A "good" answer: you can predict the `input_ids` shape before you run it.'''),
      *sol_answer(sol, hfrun(r'''from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")
batch = ["great", "an absolutely wonderful moving brilliant and unforgettable masterpiece of a film"]
enc = encode_batch(tok, batch)           # padding=True -> pad to the LONGEST row
print("dynamic padding shape:", tuple(enc["input_ids"].shape), "(batch, longest+specials)")
enc2 = tok(batch, padding="max_length", max_length=12, truncation=True, return_tensors="pt")
print("fixed max_length=12 shape:", tuple(enc2["input_ids"].shape), "-- every row clipped/padded to exactly 12")''')),
      footer(4, "`input_ids` + `attention_mask` is the real input a transformer eats. The tokenizer hands you exactly this &mdash; now you know what each field means before you fine-tune on it."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-dataset-prep", "Beginner",
     "Preparing a Dataset for Fine-tuning (tokenized & ready)", 20,
     "Turn raw labelled examples into cleaned texts, integer labels, and a REAL tokenized batch with a label tensor -- the exact inputs a fine-tune loop consumes.",
     ["Dataset prep", "Label encoding", "Tokenized tensors"])
def _l5(sol):
    return [
      header(5, "Preparing a Dataset for Fine-tuning (tokenized & ready)", "Beginner", 20,
        ["Separate raw examples into texts and integer labels",
         "Tokenize the whole set into a padded tensor batch",
         "Produce the (encodings, labels) a training loop needs"],
        "Dataset prep for fine-tuning"),
      setup(5),
      concept('''Before fine-tuning you need clean **texts**, integer **labels**, and those texts **tokenized** into
tensors. Real datasets have string labels ("pos"/"neg") that you **encode** to integers, then you run
the real tokenizer over everything to get the `input_ids`/`attention_mask` batch plus a `labels`
tensor &mdash; the precise inputs the fine-tune loop in Lab 4.10 feeds to the model.'''),
      buildmd("Encode labels to integers, then tokenize the whole set into tensors."),
      code(render([
        'RAW = [("Loved it!", "pos"), ("So boring.", "neg"), ("Brilliant film", "pos"),',
        '       ("A dull mess", "neg"), ("Wonderful!", "pos"), ("Terrible.", "neg"),',
        '       ("Great stuff", "pos"), ("I hated it", "neg")]',
        'label2id = {"neg": 0, "pos": 1}',
        "",
        "import torch",
        "from transformers import AutoTokenizer",
        "def prepare(tok):",
        {"s": '    texts = ___   # TODO: [t.lower().strip() for t, lbl in RAW]',
         "a": '    texts = [t.lower().strip() for t, lbl in RAW]'},
        {"s": '    y = ___       # TODO: [label2id[lbl] for t, lbl in RAW]',
         "a": '    y = [label2id[lbl] for t, lbl in RAW]'},
        {"s": '    enc = ___     # TODO: tok(texts, padding=True, truncation=True, return_tensors="pt")',
         "a": '    enc = tok(texts, padding=True, truncation=True, return_tensors="pt")'},
        "    return enc, torch.tensor(y)",
      ], sol)),
      runmd("Run the real tokenizer and inspect the training-ready batch."),
      code(hfrun('''from collections import Counter
tok = AutoTokenizer.from_pretrained("prajjwal1/bert-tiny")
enc, y = prepare(tok)
print("input_ids shape:", tuple(enc["input_ids"].shape), "(examples, padded_length)")
print("labels         :", y.tolist())
print("class balance  :", dict(Counter(y.tolist())), " (0=neg, 1=pos)")''')),
      noticemd('''- `enc["input_ids"]` is a real `(8, L)` tensor &mdash; 8 examples padded to a common length `L`, ready for the model.
- The `labels` tensor is what the model compares its predictions against to compute the training **loss**.
- The **class balance** check matters: a lopsided set lets a model "win" by always predicting the majority. Prep is 80% of any fine-tune.'''),
      yourturn('''Add a few of your own rows (keep the balance even). Add a third class (e.g. a neutral label)
and extend `label2id` &mdash; does everything downstream still line up? A "good" answer: you can point
to the `(examples, length)` shape and say why every row must share the same length.'''),
      *sol_answer(sol, hfrun(r'''from collections import Counter
tok = AutoTokenizer.from_pretrained("prajjwal1/bert-tiny")
# add a few balanced rows of your own, then re-run the SAME prepare()
RAW.extend([("Superb work", "pos"), ("A total waste", "neg"),
            ("Loved every second", "pos"), ("Painfully dull", "neg")])
enc, y = prepare(tok)
print("new input_ids shape:", tuple(enc["input_ids"].shape), "| balance:", dict(Counter(y.tolist())))
print("A 3rd 'neutral' class needs label2id['neu']=2 AND num_labels=3 on the model head downstream (Lab 4.10).")''')),
      footer(5, "Clean text + integer labels + a tokenized tensor batch is exactly what a fine-tune loop eats. Garbage in, garbage out &mdash; prep earns the accuracy."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-train-val-split", "Beginner",
     "Train / Validation Split: Judge on Unseen Data", 20,
     "Hold out a stratified validation set so you measure real generalisation of your fine-tune, not memorisation.",
     ["Train/val split", "Stratification", "Held-out evaluation"])
def _l6(sol):
    return [
      header(6, "Train / Validation Split: Judge on Unseen Data", "Beginner", 20,
        ["Split a dataset into train and validation sets",
         "Stratify so both classes appear in each split",
         "Understand why you never evaluate on training data"],
        "Dataset prep for fine-tuning"),
      setup(6),
      concept('''You must judge a model on data it **never trained on**, or you only measure memorisation. We hold
out a **validation set** and **stratify** so the class proportions are preserved in both splits
(vital for small or imbalanced data). This is the split every fine-tune lab that follows relies on to
report an honest before/after number.'''),
      buildmd("Make a stratified train/validation split."),
      code(render([
        SENT_DATA,
        "from sklearn.model_selection import train_test_split",
        "",
        "def split():",
        {"s": '    test_frac = ___   # TODO: a fraction like 0.3',
         "a": '    test_frac = 0.3'},
        "    return train_test_split(texts, labels, test_size=test_frac,",
        {"s": '                            random_state=0, stratify=___)   # TODO: stratify on labels',
         "a": '                            random_state=0, stratify=labels)'},
      ], sol)),
      runmd("Make the split and sanity-check it."),
      code(guard('''Xtr, Xval, ytr, yval = split()
print("train:", len(Xtr), "| val:", len(Xval), "| val positives:", sum(yval))
print("both classes in val?", set(yval) == {0, 1})
print("no leakage (train/val disjoint)?", set(Xtr).isdisjoint(set(Xval)))''')),
      noticemd('''- The validation set is **held out** &mdash; the model never sees it in training, so its accuracy there estimates real-world performance.
- **Stratify** keeps both classes present in each split; on tiny data an un-stratified split can accidentally drop a whole class.
- **No leakage**: train and val texts are disjoint. Overlap would inflate your score and lie to you.'''),
      yourturn('''Change `test_frac` and re-run &mdash; what is the smallest validation set that still contains
both classes? Remove `stratify` and split a few times with different `random_state`s: how often does a
class go missing? A "good" answer: you can explain, on this 28-row set, why stratification is not
optional.'''),
      *sol_answer(sol, r'''from sklearn.model_selection import train_test_split
# smallest stratified val set that still holds both classes:
for tf in [0.1, 0.15, 0.2, 0.3]:
    _, Xv, _, yv = train_test_split(texts, labels, test_size=tf, random_state=0, stratify=labels)
    print(f"test_frac={tf}: val={len(Xv):2d}  both classes? {set(yv) == {0, 1}}")
# WITHOUT stratify, how often does a class vanish on this tiny set?
missing = sum(set(train_test_split(texts, labels, test_size=0.2, random_state=s)[3]) != {0, 1} for s in range(10))
print("un-stratified splits missing a whole class:", missing, "/ 10  -> why stratify is not optional here")'''),
      footer(6, "The validation set is sacred: it is your honest estimate of real-world accuracy, and the yardstick for every before/after fine-tune number to come."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-feature-extraction-head", "Intermediate",
     "Transfer Learning: Frozen Real Features + a Trainable Head", 30,
     "Use a REAL bert-tiny as a FROZEN feature extractor and train only a small classifier head on top -- the cheapest, fastest form of transfer learning.",
     ["Frozen backbone", "Real features", "Trainable head"])
def _l7(sol):
    return [
      header(7, "Transfer Learning: Frozen Real Features + a Trainable Head", "Intermediate", 30,
        ["Turn text into real feature vectors with a frozen transformer",
         "Train only a small classifier head on those features",
         "See why this is fast, data-efficient transfer learning"],
        "Transfer learning"),
      setup(7),
      concept('''**Transfer learning** in its cheapest form: keep a powerful **frozen** transformer as a feature
extractor and train only a small **head**. Here `extract_features()` runs the **real** bert-tiny under
`torch.no_grad()` (no weight updates) and mean-pools its token vectors; `LogisticRegression` is the
head. The full fine-tune (labs 4.10&ndash;4.12) *unfreezes* the backbone &mdash; this is the same
shape, one step cheaper.'''),
      buildmd("`extract_features()` (given) is the real frozen backbone. Transform both splits and train the head."),
      code(render([
        FEATS_DEF,
        "",
        "from sklearn.linear_model import LogisticRegression",
        "from sklearn.metrics import accuracy_score",
        "",
        "def run(Xtr_text, Xval_text, ytr, yval):",
        {"s": '    Xtr = ___    # TODO: extract_features(Xtr_text) -- frozen features for train text',
         "a": '    Xtr = extract_features(Xtr_text)'},
        {"s": '    Xval = ___   # TODO: extract_features(Xval_text) -- frozen features for val text',
         "a": '    Xval = extract_features(Xval_text)'},
        "    head = LogisticRegression(max_iter=1000)",
        {"s": '    ___   # TODO: fit the head on (Xtr, ytr)',
         "a": '    head.fit(Xtr, ytr)'},
        "    return Xtr.shape, accuracy_score(yval, head.predict(Xval))",
      ], sol)),
      runmd("Extract real features, train the head, and score on held-out data."),
      code(hfrun(SENT_DATA + '''
from sklearn.model_selection import train_test_split
Xtr_t, Xval_t, ytr, yval = train_test_split(texts, labels, test_size=0.3, random_state=0, stratify=labels)
shape, acc = run(Xtr_t, Xval_t, ytr, yval)
print("frozen feature matrix shape:", shape, "(examples, hidden_size)")
print("val accuracy (frozen features + trained head):", round(acc, 3))''')),
      noticemd('''- The features are **128-dimensional real** bert-tiny vectors &mdash; you never touched the transformer's weights (`torch.no_grad`).
- A tiny head trained on a handful of examples generalises, because the **frozen backbone already encodes meaning**.
- This is **cheap and fast**: no backprop through the big model, no GPU. It is the workhorse before you ever unfreeze and fine-tune.'''),
      yourturn('''Swap the head for an SVM (`from sklearn.svm import SVC`) or change the backbone in
`extract_features` to `distilbert-base-uncased` &mdash; does accuracy change? Add your own labelled
sentences. A "good" answer: you can explain why frozen-feature transfer learning needs so few labels.'''),
      *sol_answer(sol, hfrun(r'''from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
Xtr_t, Xval_t, ytr, yval = train_test_split(texts, labels, test_size=0.3, random_state=0, stratify=labels)
Xtr = extract_features(Xtr_t); Xval = extract_features(Xval_t)   # SAME frozen real features
svm = SVC().fit(Xtr, ytr)                                        # only the head changed
print("SVM head val accuracy:", round(accuracy_score(yval, svm.predict(Xval)), 3))
print("Few labels suffice: the frozen backbone already encodes meaning, so the head just draws a boundary.")''')),
      footer(7, "Frozen backbone + trainable head = transfer learning at its cheapest. Next we unfreeze the backbone and **fine-tune the whole model** &mdash; the client's headline."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-evaluation-metrics", "Intermediate",
     "Beyond Accuracy: Precision, Recall & Confusion on REAL predictions",  30,
     "Run the real sentiment model on a labelled set, then compute precision, recall and a confusion matrix from its actual predictions -- the metrics accuracy hides.",
     ["Precision/recall", "Confusion matrix", "Real predictions"])
def _l8(sol):
    return [
      header(8, "Beyond Accuracy: Precision, Recall & Confusion on Real Predictions", "Intermediate", 30,
        ["Get real predictions from a real model on a labelled set",
         "Build a confusion matrix and compute precision & recall by hand",
         "See why accuracy alone can mislead"],
        "Evaluation"),
      setup(8),
      concept('''Accuracy hides *how* a model is wrong. The **confusion matrix** counts TP/FP/FN/TN.
**Precision** = TP / (TP+FP) ("when it says positive, is it right?").
**Recall** = TP / (TP+FN) ("of the real positives, how many did it catch?").
We compute these from the **real** distilbert-SST-2 model's actual predictions on a labelled set that
includes a few genuinely tricky sentences.'''),
      buildmd("Implement TP/FP/FN and precision/recall (real mechanics)."),
      code(render([
        "def counts(y_true, y_pred):",
        {"s": '    TP = ___   # TODO: predicted 1 AND true 1',
         "a": '    TP = sum(1 for t,p in zip(y_true,y_pred) if t==1 and p==1)'},
        {"s": '    FP = ___   # TODO: predicted 1 BUT true 0',
         "a": '    FP = sum(1 for t,p in zip(y_true,y_pred) if t==0 and p==1)'},
        {"s": '    FN = ___   # TODO: predicted 0 BUT true 1',
         "a": '    FN = sum(1 for t,p in zip(y_true,y_pred) if t==1 and p==0)'},
        "    return TP, FP, FN",
        "",
        "def precision(y_true, y_pred):",
        "    TP, FP, FN = counts(y_true, y_pred)",
        {"s": '    return ___   # TODO: TP / (TP + FP) if (TP+FP) else 0.0',
         "a": '    return TP / (TP + FP) if (TP + FP) else 0.0'},
        "def recall(y_true, y_pred):",
        "    TP, FP, FN = counts(y_true, y_pred)",
        {"s": '    return ___   # TODO: TP / (TP + FN) if (TP+FN) else 0.0',
         "a": '    return TP / (TP + FN) if (TP + FN) else 0.0'},
      ], sol)),
      runmd("Get REAL predictions from the model, then measure."),
      code(hfrun('''from transformers import pipeline
from sklearn.metrics import confusion_matrix
clf = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

EVAL = [("a brilliant moving masterpiece", 1), ("a boring dreadful waste", 0),
        ("i loved every minute", 1), ("terrible and awful", 0),
        ("not bad at all", 1), ("hardly a masterpiece", 0),
        ("it was fine i guess", 1), ("a complete letdown", 0)]
y_true = [y for _, y in EVAL]
y_pred = [1 if clf(t)[0]["label"] == "POSITIVE" else 0 for t, _ in EVAL]

print("y_true:", y_true)
print("y_pred:", y_pred, " (REAL model predictions)")
print("precision:", round(precision(y_true, y_pred), 3), "| recall:", round(recall(y_true, y_pred), 3))
print("confusion matrix [[TN,FP],[FN,TP]]:")
print(confusion_matrix(y_true, y_pred))''')),
      noticemd('''- The predictions are **real** model output on deliberately tricky text (negation, hedging). This strong SST-2 model actually handles them all here, so precision and recall come out perfect &mdash; a weaker model (e.g. your fine-tuned bert-tiny) would show real FP/FN. The **framework** is the lesson, whatever the numbers.
- **Precision vs recall** tell you *which kind* of mistake it makes: false positives hurt precision, missed positives hurt recall.
- The **confusion matrix** shows the full breakdown at a glance &mdash; always read it before trusting a single accuracy number.'''),
      yourturn('''Add your own hard cases (sarcasm, mixed sentiment) to `EVAL` and re-run. Can you drive
precision and recall apart (make one high, the other low)? On a high-stakes task, which matters more &mdash;
catching every positive (recall) or being right when you flag one (precision)? A "good" answer names a
real task for each.'''),
      *sol_answer(sol, hfrun(r'''from transformers import pipeline
clf = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
# hard cases (sarcasm / negation) that tend to create FP and FN
HARD = [("i just love waiting forever for bugs", 0), ("not terrible actually", 1),
        ("a masterpiece of pure tedium", 0), ("could honestly be worse", 1)]
yt = [y for _, y in HARD]
yp = [1 if clf(t)[0]["label"] == "POSITIVE" else 0 for t, _ in HARD]
print("y_true:", yt, "\ny_pred:", yp)
print("precision:", round(precision(yt, yp), 3), "| recall:", round(recall(yt, yp), 3))
print("Precision matters most when a false alarm is costly (e.g. auto-blocking accounts);")
print("recall matters most when a MISS is costly (e.g. flagging fraud or safety issues).")''')),
      footer(8, "On imbalanced or high-stakes tasks, precision and recall matter more than accuracy. Always read the confusion matrix of **real** predictions before you trust a score."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-frozen-vs-finetune", "Intermediate",
     "Data Efficiency: How Much Training Data Do You Need?", 30,
     "Train the head on growing slices of REAL frozen features and watch validation accuracy climb -- the data-efficiency case for transfer learning.",
     ["Data efficiency", "Learning curve", "Real features"])
def _l9(sol):
    return [
      header(9, "Data Efficiency: How Much Training Data Do You Need?", "Intermediate", 30,
        ["Train the same head on growing fractions of data",
         "Plot a learning curve of validation accuracy vs train size",
         "See why transfer learning shines with little data"],
        "Transfer learning"),
      setup(9),
      concept('''A big reason to use pre-trained models: they need **little task data**. We extract **real** frozen
bert-tiny features once, then train the head on growing slices of the training set and watch
validation accuracy rise &mdash; a **learning curve**. With good frozen features, even a few dozen
examples go a long way.'''),
      buildmd("For each fraction, train on the first k examples and record validation accuracy."),
      code(render([
        "from sklearn.linear_model import LogisticRegression",
        "from sklearn.metrics import accuracy_score",
        "",
        "def curve(Xtr, ytr, Xval, yval):",
        "    n = Xtr.shape[0]",
        "    accs = []",
        "    for frac in [0.25, 0.5, 1.0]:",
        "        k = max(2, int(n * frac))",
        "        head = LogisticRegression(max_iter=1000)",
        {"s": '        head.fit(Xtr[:k], ytr[:k])   # TODO (given): train on the first k examples',
         "a": '        head.fit(Xtr[:k], ytr[:k])'},
        {"s": '        acc = ___   # TODO: accuracy_score(yval, head.predict(Xval))',
         "a": '        acc = accuracy_score(yval, head.predict(Xval))'},
        "        accs.append(acc)",
        "    return accs",
      ], sol)),
      runmd("Extract real features once, then sweep training-set size and plot the curve."),
      code(hfrun(FEATS_DEF + '\n' + SENT_DATA + '''
from sklearn.model_selection import train_test_split
Xtr_t, Xval_t, ytr, yval = train_test_split(texts, labels, test_size=0.3, random_state=0, stratify=labels)
Xtr = extract_features(Xtr_t); Xval = extract_features(Xval_t)   # REAL frozen features
accs = curve(Xtr, ytr, Xval, yval)
print("val accuracy at 25% / 50% / 100% of train data:", [round(a, 3) for a in accs])
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.plot([0.25, 0.5, 1.0], accs, "o-"); plt.xlabel("train fraction"); plt.ylabel("val accuracy")
plt.title("Learning curve (frozen real features)"); plt.tight_layout()
plt.savefig(WORK + "/learning_curve.png", dpi=90)
print("saved:", WORK + "/learning_curve.png")''')),
      noticemd('''- Accuracy generally **climbs with more data**, then plateaus &mdash; the classic learning curve.
- Even the **smallest slice** already does well, because the **frozen features carry meaning**: that is the data-efficiency of transfer learning.
- Curves on tiny data are noisy &mdash; the shape (rise then plateau), not the exact wiggle, is the lesson.'''),
      yourturn('''Add more fractions (e.g. `0.1, 0.75`) or more data to `SENT`. Where does the curve
**plateau** &mdash; the point where extra labels stop helping? That plateau is where you would **stop
labelling**. A "good" answer: you can estimate, from the curve, how many labels this task really needs.'''),
      *sol_answer(sol, hfrun(r'''from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
# reuse the frozen features Xtr/Xval extracted above; sweep MORE fractions to find the plateau
n = Xtr.shape[0]
for frac in [0.1, 0.25, 0.5, 0.75, 1.0]:
    k = max(2, int(n * frac))
    head = LogisticRegression(max_iter=1000).fit(Xtr[:k], ytr[:k])
    print(f"frac={frac:>4}: k={k:2d} train examples -> val acc={round(accuracy_score(yval, head.predict(Xval)), 3)}")
print("The curve flattens where extra labels stop moving val accuracy -- that plateau is where you stop labelling.")''')),
      footer(9, "Transfer learning is **data-efficient**: good frozen features mean a small head learns from few labels. Next we stop freezing and fine-tune the whole model."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-finetune-sentiment", "Advanced",
     "Fine-tune a REAL Sentiment Model (before vs after)", 40,
     "Actually FINE-TUNE prajjwal1/bert-tiny on labelled sentiment with a real torch training loop, and prove it beats its untrained self on held-out data (before vs after).",
     ["Real fine-tuning", "Training loop", "Before vs after"])
def _l10(sol):
    return [
      header(10, "Fine-tune a Real Sentiment Model (before vs after)", "Advanced", 40,
        ["Load a real model with a fresh (untrained) classification head",
         "Fine-tune it with a real torch training loop on labelled data",
         "Measure held-out accuracy BEFORE vs AFTER and predict new text"],
        "Fine-tuning end-to-end"),
      setup(10),
      concept('''This is the client's **fine-tune for sentiment**, for real. We load **prajjwal1/bert-tiny** with a
fresh 2-class head (randomly initialised &mdash; so it starts at chance), then run a real **training
loop**: forward pass &rarr; loss &rarr; `backward()` &rarr; optimizer `step()`, updating **the whole
model**. We measure held-out accuracy **before** (random head) vs **after** training. On CPU this
finishes in a few seconds because bert-tiny is small and the words recur.'''),
      buildmd("Fill in the model's label count and the two lines that actually train it."),
      code(render([
        "import torch, numpy as np",
        "from transformers import AutoTokenizer, AutoModelForSequenceClassification",
        "",
        "def load_model():",
        '    name = "prajjwal1/bert-tiny"',
        "    tok = AutoTokenizer.from_pretrained(name)",
        {"s": '    model = AutoModelForSequenceClassification.from_pretrained(name, num_labels=___)   # TODO: 2 (pos/neg)',
         "a": '    model = AutoModelForSequenceClassification.from_pretrained(name, num_labels=2)'},
        "    return tok, model",
        "",
        "def evaluate(model, tok, texts, y):",
        "    model.eval()",
        "    with torch.no_grad():",
        '        enc = tok(texts, padding=True, truncation=True, return_tensors="pt")',
        {"s": '        pred = model(**enc).logits.argmax(___).numpy()   # TODO: -1  (argmax over classes)',
         "a": '        pred = model(**enc).logits.argmax(-1).numpy()'},
        "    return float((pred == np.array(y)).mean())",
        "",
        "def fine_tune(model, tok, texts, y, steps=40, lr=5e-3):",
        '    enc = tok(texts, padding=True, truncation=True, return_tensors="pt")',
        "    yt = torch.tensor(y)",
        "    opt = torch.optim.AdamW(model.parameters(), lr=lr)",
        "    model.train()",
        "    for step in range(steps):",
        "        opt.zero_grad()",
        "        out = model(**enc, labels=yt)   # HF models compute the loss when given labels",
        {"s": '        ___   # TODO: out.loss.backward()   -- backprop the gradients',
         "a": '        out.loss.backward()'},
        {"s": '        ___   # TODO: opt.step()            -- update every weight',
         "a": '        opt.step()'},
        "    return float(out.loss)",
      ], sol)),
      runmd("Split, measure BEFORE, fine-tune for real, measure AFTER, then predict new text."),
      code(hfrun(SENT_DATA + '''
from sklearn.model_selection import train_test_split
Xtr, Xval, ytr, yval = train_test_split(texts, labels, test_size=0.3, random_state=0, stratify=labels)

torch.manual_seed(0)
tok, model = load_model()
before = evaluate(model, tok, Xval, yval)
final_loss = fine_tune(model, tok, Xtr, ytr)
after = evaluate(model, tok, Xval, yval)
print(f"BEFORE fine-tuning (random head):  val acc = {before:.3f}")
print(f"AFTER  fine-tuning (final loss {final_loss:.3f}): val acc = {after:.3f}")
print(f"improvement: {after - before:+.3f}")

for s in ["a wonderful brilliant film", "a boring awful mess", "i really loved every minute"]:
    enc = tok([s], return_tensors="pt")
    with torch.no_grad(): p = int(model(**enc).logits.argmax(-1))
    print(f"  pred={p} ({'pos' if p==1 else 'neg'})  <-  {s}")''')),
      noticemd('''- **BEFORE** the head is random, so val accuracy sits around chance (~0.5). **AFTER** a few seconds of real training it jumps &mdash; a genuine before &rarr; after you produced.
- Unlike Lab 4.7 (frozen backbone), here `backward()` + `step()` update **every weight in the model** &mdash; that is full fine-tuning.
- The loss **falls** across steps; the held-out jump proves the model **generalised**, not just memorised the training rows.'''),
      yourturn('''Change `steps` and `lr` in `fine_tune` &mdash; can you make it converge faster, or break it
(too-high `lr` diverges)? Add your own labelled sentences and re-run. A "good" answer: you can state
what `loss.backward()` and `opt.step()` each do, and show one setting that trains and one that doesn't.'''),
      *sol_answer(sol, hfrun(r'''from sklearn.model_selection import train_test_split
Xtr, Xval, ytr, yval = train_test_split(texts, labels, test_size=0.3, random_state=0, stratify=labels)
# same steps, two learning rates: a moderate one trains, a too-high one diverges
for lr in [5e-3, 5e-1]:
    torch.manual_seed(0)
    tok, model = load_model()
    fine_tune(model, tok, Xtr, ytr, steps=40, lr=lr)
    print(f"lr={lr}: val acc = {evaluate(model, tok, Xval, yval):.3f}")
print("backward() computes the gradients; step() applies them to every weight.")
print("Moderate lr converges; too-high lr overshoots the minimum and accuracy falls back toward chance.")''')),
      footer(10, "You fine-tuned a **real** model end-to-end: random head &rarr; a trained model that beats its old self on unseen data. That is the client's headline, done for real."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-improve-and-evaluate", "Advanced",
     "Improve & Evaluate Your Fine-tuned Model", 40,
     "Train the fine-tune longer, then evaluate it honestly with a confusion matrix built from real predictions -- the real iterate-and-measure loop.",
     ["Training budget", "Confusion matrix", "Iterate & evaluate"])
def _l11(sol):
    return [
      header(11, "Improve & Evaluate Your Fine-tuned Model", "Advanced", 40,
        ["Compare a barely-trained model to a properly-trained one",
         "Give the fine-tune enough training steps to converge",
         "Evaluate with a confusion matrix built from real predictions"],
        "Cost / latency / data tradeoffs"),
      setup(11),
      concept('''A first fine-tune is rarely your best. The **training budget** (how many steps) matters: too few and
the model **underfits** (barely better than chance); enough and it converges. We fine-tune the **real**
bert-tiny with a small budget vs a larger one, then **evaluate** with a confusion matrix of its actual
predictions to see exactly which class it confuses. (More steps help until they overfit &mdash; tuning
is empirical.)'''),
      buildmd("Fill in a too-small budget and a sufficient one, then predict for the confusion matrix."),
      code(render([
        "import torch, numpy as np",
        "from transformers import AutoTokenizer, AutoModelForSequenceClassification",
        "",
        "def train_eval(Xtr, ytr, Xval, yval, steps, lr=5e-3):",
        '    tok = AutoTokenizer.from_pretrained("prajjwal1/bert-tiny")',
        "    torch.manual_seed(0)",
        '    model = AutoModelForSequenceClassification.from_pretrained("prajjwal1/bert-tiny", num_labels=2)',
        '    enc = tok(Xtr, padding=True, truncation=True, return_tensors="pt"); yt = torch.tensor(ytr)',
        "    opt = torch.optim.AdamW(model.parameters(), lr=lr); model.train()",
        "    for _ in range(steps):",
        "        opt.zero_grad(); out = model(**enc, labels=yt); out.loss.backward(); opt.step()",
        "    model.eval()",
        '    venc = tok(Xval, padding=True, truncation=True, return_tensors="pt")',
        "    with torch.no_grad(): pred = model(**venc).logits.argmax(-1).numpy()",
        "    return float((pred == np.array(yval)).mean()), pred",
        "",
        "def weak(Xtr, ytr, Xval, yval):",
        {"s": '    return train_eval(Xtr, ytr, Xval, yval, steps=___)[0]   # TODO: a tiny budget like 2 (underfits)',
         "a": '    return train_eval(Xtr, ytr, Xval, yval, steps=2)[0]'},
        "def strong(Xtr, ytr, Xval, yval):",
        {"s": '    return train_eval(Xtr, ytr, Xval, yval, steps=___)      # TODO: a sufficient budget like 40 -> (acc, preds)',
         "a": '    return train_eval(Xtr, ytr, Xval, yval, steps=40)'},
      ], sol)),
      runmd("Fine-tune with each budget and read the confusion matrix of real predictions."),
      code(hfrun(SENT_DATA + '''
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
Xtr, Xval, ytr, yval = train_test_split(texts, labels, test_size=0.3, random_state=0, stratify=labels)

weak_acc = weak(Xtr, ytr, Xval, yval)
strong_acc, preds = strong(Xtr, ytr, Xval, yval)
print("under-trained (2 steps) val acc:", round(weak_acc, 3))
print("well-trained  (40 steps) val acc:", round(strong_acc, 3))
cm = confusion_matrix(yval, preds)
print("confusion matrix [[TN,FP],[FN,TP]] for the well-trained model:")
print(cm)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.imshow(cm, cmap="Blues"); plt.title("Confusion matrix (fine-tuned bert-tiny)"); plt.colorbar()
plt.xlabel("predicted"); plt.ylabel("true"); plt.tight_layout()
plt.savefig(WORK + "/confusion.png", dpi=90)
print("saved:", WORK + "/confusion.png")''')),
      noticemd('''- **2 steps** barely moves off chance &mdash; the model **underfits**. A **sufficient budget** converges to high accuracy. Same model, same data: only the training budget changed.
- The **confusion matrix** shows exactly which class the well-trained model confuses (if any) &mdash; far more informative than a lone accuracy number.
- Real iteration is this loop: change one knob (steps, lr), re-measure on held-out data, read the confusion matrix. Small honest steps.'''),
      yourturn('''Sweep `steps` (2, 5, 10, 20, 40) and plot accuracy &mdash; where does it plateau? Push `lr`
too high (e.g. `1e-1`) and watch it destabilise. A "good" answer: you can name the training budget
where accuracy stops improving, and describe one sign of over- vs under-training.'''),
      *sol_answer(sol, hfrun(r'''from sklearn.model_selection import train_test_split
Xtr, Xval, ytr, yval = train_test_split(texts, labels, test_size=0.3, random_state=0, stratify=labels)
# sweep the training budget and watch accuracy climb then plateau
for steps in [2, 5, 10, 20, 40]:
    acc, _ = train_eval(Xtr, ytr, Xval, yval, steps=steps)
    print(f"steps={steps:2d}: val acc = {round(acc, 3)}")
hi, _ = train_eval(Xtr, ytr, Xval, yval, steps=40, lr=1e-1)   # lr too high -> destabilises
print("lr=1e-1 (too high) val acc:", round(hi, 3), "-- underfitting sign: acc stuck near chance; overfitting sign: train perfect but val drops.")''')),
      footer(11, "Iterate: change the training budget, re-measure on held-out data, read the confusion matrix. That is the real fine-tuning loop &mdash; and 'more steps' is not always better."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-adapt-a-model", "Advanced",
     "Capstone: Fine-tune a Real Model to a NEW Task", 45,
     "Take a brand-new task (sports vs tech) end-to-end -- tokenize, split, really fine-tune bert-tiny, and prove a before -> after improvement on held-out text.",
     ["End-to-end fine-tune", "New task", "Capstone"])
def _l12(sol):
    return [
      header(12, "Capstone: Fine-tune a Real Model to a New Task", "Advanced", 45,
        ["Apply the whole Module 4 pipeline to a NEW task (topic: sports vs tech)",
         "Tokenize, split, and really fine-tune a real model end-to-end",
         "Prove a before -> after improvement and predict on unseen text"],
        "Fine-tuning end-to-end"),
      setup(12),
      concept('''Capstone: the full fine-tuning workflow on a **new** task &mdash; classify a sentence as **sports (0)**
vs **tech (1)**. Same recipe as sentiment, different labels: load a real model with a fresh head,
tokenize, split, run a real training loop, and measure held-out accuracy **before vs after**. This is
exactly how you adapt a pre-trained model to *your* problem.'''),
      buildmd("Complete the fine-tune loop and the evaluation for the new task."),
      code(render([
        "import torch, numpy as np",
        "from transformers import AutoTokenizer, AutoModelForSequenceClassification",
        "",
        "def load():",
        '    tok = AutoTokenizer.from_pretrained("prajjwal1/bert-tiny")',
        "    torch.manual_seed(0)",
        '    model = AutoModelForSequenceClassification.from_pretrained("prajjwal1/bert-tiny", num_labels=2)',
        "    return tok, model",
        "",
        "def evaluate(model, tok, texts, y):",
        "    model.eval()",
        '    enc = tok(texts, padding=True, truncation=True, return_tensors="pt")',
        "    with torch.no_grad():",
        {"s": '        pred = model(**enc).logits.argmax(___).numpy()   # TODO: -1',
         "a": '        pred = model(**enc).logits.argmax(-1).numpy()'},
        "    return float((pred == np.array(y)).mean()), pred",
        "",
        "def fine_tune(model, tok, texts, y, steps=50, lr=5e-3):",
        '    enc = tok(texts, padding=True, truncation=True, return_tensors="pt"); yt = torch.tensor(y)',
        "    opt = torch.optim.AdamW(model.parameters(), lr=lr); model.train()",
        "    for _ in range(steps):",
        "        opt.zero_grad(); out = model(**enc, labels=yt)",
        {"s": '        ___; ___   # TODO: out.loss.backward(); opt.step()',
         "a": '        out.loss.backward(); opt.step()'},
        "    return float(out.loss)",
      ], sol)),
      runmd("Run the whole pipeline on the new sports-vs-tech task."),
      code(hfrun('''# A new tiny task: sports (0) vs tech (1). Keywords recur so the model generalises.
TASK = [
    ("the team scored a goal to win the game", 0), ("our team won the match with a late goal", 0),
    ("the player scored twice in the game", 0), ("a great goal helped the team win the match", 0),
    ("the coach and team celebrated the win", 0), ("the player passed the ball and scored a goal", 0),
    ("the team lost the game by one goal", 0), ("the striker scored the winning goal", 0),
    ("the new app runs on a fast chip", 1), ("the software update improved the app", 1),
    ("the app stores its data in the cloud", 1), ("a new chip makes the computer software faster", 1),
    ("the cloud server runs the data software", 1), ("the app uses data and a fast chip", 1),
    ("the computer software had a data bug", 1), ("the developer shipped the new software app", 1),
]
X = [t for t, y in TASK]; Y = [y for t, y in TASK]
from sklearn.model_selection import train_test_split
Xtr, Xval, ytr, yval = train_test_split(X, Y, test_size=0.3, random_state=0, stratify=Y)

tok, model = load()
before, _ = evaluate(model, tok, Xval, yval)
loss = fine_tune(model, tok, Xtr, ytr)
after, _ = evaluate(model, tok, Xval, yval)
print(f"NEW TASK sports-vs-tech | BEFORE val acc = {before:.3f}  ->  AFTER (loss {loss:.3f}) = {after:.3f}  ({after-before:+.3f})")

for s in ["the striker scored a header for the team", "the gpu accelerates the software app"]:
    enc = tok([s], return_tensors="pt")
    with torch.no_grad(): p = int(model(**enc).logits.argmax(-1))
    print(f"  pred={p} ({'tech' if p==1 else 'sports'})  <-  {s}")''')),
      noticemd('''- Same loop as sentiment, **new labels** &mdash; that is the whole point: fine-tuning adapts a pre-trained model to *any* small task you have labels for.
- The **before &rarr; after** jump on held-out data proves the model learned the new task, not the training rows.
- You changed nothing but the data and labels &mdash; the pretrained backbone did the heavy lifting.'''),
      yourturn('''Invent your **own** two-class task (spam vs ham, question vs statement, urgent vs not) with a
dozen labelled sentences and run the exact same pipeline. Does it converge? A "good" answer: you can
name every stage &mdash; tokenize, split, fine-tune, evaluate &mdash; and say what would break if you
skipped the held-out split.'''),
      *sol_answer(sol, hfrun(r'''# YOUR OWN new two-class task: spam (1) vs ham (0). Keywords recur so it generalises.
from sklearn.model_selection import train_test_split
MINE = [
    ("win a free prize now click here", 1), ("claim your free cash prize today", 1),
    ("free money click this link right now", 1), ("you won a free gift claim it now", 1),
    ("congrats free voucher click now to win", 1), ("free free free click to win cash", 1),
    ("lunch meeting moved to noon today", 0), ("can you review the report today", 0),
    ("the meeting notes are attached here", 0), ("please send me the project report", 0),
    ("see you at the team meeting today", 0), ("the report review is due tomorrow", 0),
]
X = [t for t, y in MINE]; Y = [y for t, y in MINE]
Xtr, Xval, ytr, yval = train_test_split(X, Y, test_size=0.3, random_state=0, stratify=Y)
tok, model = load()                    # tokenize + fresh head
before, _ = evaluate(model, tok, Xval, yval)
fine_tune(model, tok, Xtr, ytr)        # real training loop
after, _ = evaluate(model, tok, Xval, yval)
print(f"spam-vs-ham | before={before:.3f} -> after={after:.3f}  ({after-before:+.3f})")
print("Stages: tokenize -> split -> fine-tune -> evaluate. Skip the held-out split and you'd measure memorisation, not learning.")''')),
      footer(12, "You adapted a **real** pre-trained model to a brand-new task end-to-end. That is Module 4 in one move: stand on a pretrained model, fine-tune a small head-and-body, measure honestly, ship. Next: Day 3 &mdash; agents."),
    ]

# ============================================================ WRITE
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
