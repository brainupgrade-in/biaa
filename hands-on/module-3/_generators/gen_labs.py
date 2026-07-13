# -*- coding: utf-8 -*-
"""Generator for Day 2 Module 3 hands-on labs (12 notebooks) -- NEAR-REAL design.
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

This is the "Why Transformers?" module. Participants run REAL Hugging Face Transformers
locally on CPU -- a real tokenizer, real embeddings, real fill-mask, real attention extracted
from a real model, real text generation -- plus a hosted "GPT API" path via ChatGroq. There is
NO auto-grader: every lab ends "Build it -> Run it for real -> What to notice -> Your turn".

What stays hand-computed (REAL mechanics, not stubs): scaled dot-product attention, sinusoidal
positional encoding, and cosine similarity -- these teach the maths a transformer runs. Wherever
a lab *invokes a model*, it is a REAL HF model, never a fake.

Models used (small, CPU-friendly, cached after first download):
  distilbert-base-uncased ............ tokenizer / fill-mask / subwords (labs 1, 5, 6)
  sentence-transformers/all-MiniLM-L6-v2 . sentence embeddings (labs 2, 7, 11, 12)
  prajjwal1/bert-tiny ................ real attention weights, output_attentions=True (lab 9)
  distilgpt2 ......................... text generation (lab 10) + ChatGroq hosted "GPT API"

Student robustness (no grader): cells that exercise the blanks or load a model are wrapped by
guard()/hfrun() so an unfilled `___` -- or a missing network on first download -- prints a
friendly note instead of crashing. A student notebook runs top-to-bottom; a solution notebook
runs the real thing and prints real model output."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day2-module3-why-transformers.html"
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
    """Wrap a 'run a real model' cell: friendly note if a blank is unfilled OR the first
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
os.environ.setdefault("USE_TF", "0")                 # these labs are torch-only; skip the TF backend
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")   # mute TensorFlow's C++ INFO/WARNING startup noise
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True), override=True)   # GROQ_API_KEY etc. (used by the text-gen lab)

WORK = os.path.join(os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp", "biaa-lab-03-{nn:02d}")
os.makedirs(WORK, exist_ok=True)
print("WORK:", WORK)
print("Real Hugging Face models load from the hub on first use (one-time download, then cached).")''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 3.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 2 &middot; Module 3 &mdash; Why Transformers?**

### What you'll do
{g}

> **How this lab works (near-real):** these labs run **real Hugging Face Transformers** locally on CPU. Read the **Concept**, fill the real `___` blanks in **Build it** (real tokenizer / model / decoding calls), **Run it for real** to see the **actual model output**, note **What to notice**, then finish with an open **Your turn**. There is **no auto-grader** &mdash; the goal is real model output you can read. The genuine maths (attention, positional encoding, cosine) you still compute **by hand** &mdash; that is real mechanics, not a stub.

> **Models:** small, CPU-friendly models from the HF hub &mdash; `distilbert-base-uncased` (tokenizer / fill-mask), `sentence-transformers/all-MiniLM-L6-v2` (embeddings), `prajjwal1/bert-tiny` (attention), `distilgpt2` (generation). First use downloads the weights (needs network), then they are cached. The hosted "GPT API" path uses `ChatGroq` (`GROQ_API_KEY` in `.env`).

**Reference:** [Module 3 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 3 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 3 labs](./index.html) &nbsp;&middot;&nbsp; [Module 3 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

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

# A REAL sentence-embedding function: run a real model, then mean-pool token vectors (the
# standard sentence-transformers pooling) into one unit vector. Lazy-loads + caches the model on
# first call so the *build* cell never touches the network -- only the guarded run cell does.
EMBED_DEF = '''import numpy as np
_EMB = {}
def embed(texts):
    """Real sentence embeddings from all-MiniLM-L6-v2: model forward pass -> mean-pool -> unit vector."""
    import torch
    from transformers import AutoTokenizer, AutoModel
    if not _EMB:
        name = "sentence-transformers/all-MiniLM-L6-v2"
        _EMB["tok"] = AutoTokenizer.from_pretrained(name)
        _EMB["mdl"] = AutoModel.from_pretrained(name); _EMB["mdl"].eval()
    if isinstance(texts, str): texts = [texts]
    enc = _EMB["tok"](texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad(): out = _EMB["mdl"](**enc)
    mask = enc["attention_mask"].unsqueeze(-1).float()
    pooled = (out.last_hidden_state * mask).sum(1) / mask.sum(1)     # mean over REAL tokens
    return torch.nn.functional.normalize(pooled, dim=1).numpy()      # unit vectors -> dot == cosine'''

NB = {}
def lab(nn, slug, level, title, mins, summary, concepts):
    def deco(fn):
        NB[nn] = dict(slug=slug, level=level, title=title, mins=mins,
                      summary=summary, concepts=concepts, build=fn)
        return fn
    return deco

# ============================================================ LAB 01
@lab(1, "lab-01-tokenization", "Beginner",
     "Tokenization: Text into Tokens & IDs", 20,
     "Use a REAL transformer tokenizer (distilbert) to split text into subword tokens and encode them to the integer IDs a model actually consumes.",
     ["Real tokenizer", "Subword pieces", "Token IDs"])
def _l1(sol):
    return [
      header(1, "Tokenization: Text into Tokens & IDs", "Beginner", 20,
        ["Split text into subword tokens with a real tokenizer",
         "Convert tokens into the integer IDs a model reads",
         "See the special tokens ([CLS]/[SEP]) a model adds"],
        "Tokens & embeddings"),
      setup(1),
      concept('''A transformer never sees text &mdash; it sees **token IDs**. Real models use a **subword**
tokenizer: a fixed vocabulary of word-pieces so any word (even a typo) can be spelled from known
pieces. We use **distilbert-base-uncased**'s real WordPiece tokenizer: `tokenize` splits text into
pieces, `convert_tokens_to_ids` maps pieces to integers, and calling `tok(text)` returns the exact
dict a model consumes (adding the special `[CLS]` / `[SEP]` markers).'''),
      buildmd("Fill in the three real tokenizer calls."),
      code(render([
        "def tokenize_encode(text, tok):",
        {"s": '    pieces = ___   # TODO: tok.tokenize(text) -- split into subword tokens',
         "a": '    pieces = tok.tokenize(text)'},
        {"s": '    ids = ___      # TODO: tok.convert_tokens_to_ids(pieces)',
         "a": '    ids = tok.convert_tokens_to_ids(pieces)'},
        {"s": '    full = ___     # TODO: tok(text) -- the dict the model consumes (adds [CLS]/[SEP])',
         "a": '    full = tok(text)'},
        "    return pieces, ids, full",
      ], sol)),
      runmd("Load the real tokenizer and encode a few sentences."),
      code(hfrun('''from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")   # a REAL subword tokenizer
for text in ["Transformers are unbelievably powerful!", "tokenization"]:
    pieces, ids, full = tokenize_encode(text, tok)
    print(repr(text))
    print("  tokens            :", pieces)
    print("  ids               :", ids)
    print("  input_ids (+specials):", full["input_ids"])''')),
      noticemd('''- `unbelievably` splits into **several subword pieces** &mdash; that is how a finite vocabulary spells any word.
- `##` prefixes mark a piece that **continues** the previous token (no space before it).
- `tok(text)` adds `[CLS]` (id `101`) at the front and `[SEP]` (id `102`) at the end &mdash; markers every BERT-family model expects.
- The `ids` are exactly what the model's embedding layer looks up next (Lab 3.2).'''),
      yourturn('''Feed `tokenize_encode` your own tricky inputs &mdash; a rare word, a URL, an emoji, a number like
`3.14159`. How many pieces does each become? Then load a **different** tokenizer
(`AutoTokenizer.from_pretrained("bert-base-cased")`) and compare: does casing change the split? A
"good" answer: you can predict roughly how many tokens a string will cost before you send it.'''),
      *sol_answer(sol, hfrun(r'''from transformers import AutoTokenizer
for text in ["3.14159", "https://gheware.com/agents", "naive"]:   # tricky inputs
    pieces, ids, full = tokenize_encode(text, tok)
    print(f"{text!r:32s} -> {len(pieces)} pieces: {pieces}")
cased = AutoTokenizer.from_pretrained("bert-base-cased")           # a cased tokenizer
print("uncased 'Hello World':", tok.tokenize("Hello World"))
print("cased   'Hello World':", cased.tokenize("Hello World"))    # casing IS preserved here''')),
      footer(1, "Every model pipeline starts here: text -> subword tokens -> IDs. Next we give those IDs *meaning* as real embedding vectors."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-embeddings-cosine", "Beginner",
     "Real Embeddings & Cosine Similarity", 20,
     "Turn words into REAL vectors with a sentence-embedding model, then measure similarity with cosine computed by hand -- real geometry of meaning.",
     ["Real embeddings", "Cosine by hand", "Nearest neighbour"])
def _l2(sol):
    return [
      header(2, "Real Embeddings & Cosine Similarity", "Beginner", 20,
        ["Turn words into real vectors with a sentence-embedding model",
         "Implement cosine similarity by hand in NumPy",
         "Find each word's nearest neighbour in embedding space"],
        "Tokens & embeddings"),
      setup(2),
      concept('''Each token becomes a vector &mdash; an **embedding** &mdash; learned so that words with similar
meaning point in similar directions. We get **real** embeddings from
`sentence-transformers/all-MiniLM-L6-v2` (a real model forward pass, mean-pooled to one vector per
word), then measure similarity ourselves with **cosine similarity** &mdash; the angle between two
vectors: `1.0` = same direction, `0` = unrelated. The `embed()` helper is real; the cosine maths is
yours (that is real mechanics worth knowing).'''),
      buildmd("`embed()` (given) is a real model. You implement **cosine** and the nearest-neighbour search."),
      code(render([
        EMBED_DEF,
        "",
        "def cosine(a, b):",
        {"s": '    return ___   # TODO: (a . b) / (||a|| * ||b||)   use np.dot, np.linalg.norm',
         "a": '    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))'},
        "",
        "def most_similar(word, words, E):",
        "    i = words.index(word)",
        "    best, best_sim = None, -2.0",
        "    for j, other in enumerate(words):",
        "        if j == i: continue",
        {"s": '        s = ___   # TODO: cosine between embedding E[i] and E[j]',
         "a": '        s = cosine(E[i], E[j])'},
        "        if s > best_sim: best_sim, best = s, other",
        "    return best",
      ], sol)),
      runmd("Embed real words and inspect the geometry."),
      code(hfrun('''WORDS = ["king", "queen", "man", "woman", "apple", "orange"]
E = embed(WORDS)                       # real model -> one unit vector per word
print("embedding dim:", E.shape[1])
for w in WORDS:
    print(f"  {w:8s} nearest -> {most_similar(w, WORDS, E)}")
print("cos(king,queen) =", round(cosine(E[0], E[1]), 3),
      "| cos(king,apple) =", round(cosine(E[0], E[4]), 3))''')),
      noticemd('''- The vectors are **384-dimensional** &mdash; real learned features, not toy numbers.
- `king` and `queen` sit close (**high cosine**); `king` and `apple` sit far apart (**low cosine**). Meaning became geometry.
- Because `embed()` returns **unit** vectors, the dot product already *is* the cosine &mdash; that is why fast vector search uses dot products.'''),
      yourturn('''Add your own words to `WORDS` (try `paris`, `france`, `tokyo`, `japan`) and re-run. Do
countries cluster near their capitals? Try short sentences instead of single words &mdash; `embed`
handles those too. A "good" answer: nearest-neighbour matches your intuition about meaning, and you
can explain one case where it surprises you.'''),
      *sol_answer(sol, hfrun(r'''W2 = ["paris", "france", "tokyo", "japan", "berlin", "germany"]
E2 = embed(W2)                                    # real model -> one unit vector per word
for w in W2:
    print(f"  {w:8s} nearest -> {most_similar(w, W2, E2)}")
print("cos(paris,france) =", round(cosine(E2[0], E2[1]), 3),
      "| cos(paris,japan) =", round(cosine(E2[0], E2[3]), 3))   # capitals sit near their country''')),
      footer(2, "Embeddings turn meaning into geometry, and cosine measures it. This is the engine behind search, RAG and recommendations -- and Lab 3.7 turns it into real semantic search."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-attention-by-hand", "Beginner",
     "Self-Attention by Hand", 25,
     "Implement scaled dot-product attention in NumPy -- the single idea at the heart of every transformer (real mechanics, computed by hand).",
     ["Query/Key/Value", "Softmax", "Scaled dot-product attention"])
def _l3(sol):
    return [
      header(3, "Self-Attention by Hand", "Beginner", 25,
        ["Implement a numerically-stable softmax",
         "Compute scaled dot-product attention: softmax(Q.Kt / sqrt(d)) . V",
         "See a query 'attend' to the matching key"],
        "Self-attention (Q/K/V)"),
      setup(3),
      concept('''**Attention** lets each token look at every other token and pull in what's relevant. For queries
**Q**, keys **K** and values **V**:
`attention(Q, K, V) = softmax( Q . Kt / sqrt(d) ) . V`.
The `softmax` turns similarity scores into weights that sum to 1; the scaling by `sqrt(d)` keeps them
stable. This is the exact maths a real model runs &mdash; here we compute it by hand so the mechanism
is unambiguous (Lab 3.9 pulls the same weights out of a real model).

> **See it live (interactive):** [softmax &mdash; from scores to attention weights](../../presentation/softmax-attention-weights.html) &mdash; drag the raw scores and the temperature and watch `exp` &rarr; `normalise` happen. Its defaults reproduce **cat**'s attention row from this lab (the `/sqrt(d)` scaling is the temperature).'''),
      buildmd("Implement `softmax` and `attention`."),
      code(render([
        "import numpy as np",
        "def softmax(x, axis=-1):",
        "    x = x - x.max(axis=axis, keepdims=True)   # numerical stability",
        {"s": '    e = ___   # TODO: elementwise exp of x',
         "a": '    e = np.exp(x)'},
        "    return e / e.sum(axis=axis, keepdims=True)",
        "",
        "def attention(Q, K, V):",
        "    d = Q.shape[-1]",
        {"s": '    scores = ___   # TODO: Q . K^T divided by sqrt(d)',
         "a": '    scores = Q @ K.T / np.sqrt(d)'},
        "    weights = softmax(scores, axis=-1)",
        {"s": '    return ___   # TODO: weights . V',
         "a": '    return weights @ V'},
      ], sol)),
      runmd("Run attention on a tiny example where the answer is obvious."),
      code(guard('''import numpy as np
Q = np.array([[10.0, 0.0], [0.0, 10.0]])   # two strong queries
K = np.array([[1.0, 0.0], [0.0, 1.0]])     # two orthogonal keys
V = np.array([[1.0, 0.0], [0.0, 1.0]])     # values to fetch
print("attention output:\\n", np.round(attention(Q, K, V), 3))
print("softmax([2,1,0]) =", np.round(softmax(np.array([2.0, 1.0, 0.0])), 3), "(sums to 1)")''')),
      noticemd('''- The output is (almost) the identity: query 1 pulls value 1, query 2 pulls value 2 &mdash; each **strong query attended to its matching key**.
- Softmax weights are a **probability distribution** &mdash; they sum to 1, so attention is a weighted average of the values.
- Drop the `/ sqrt(d)` scaling and, for large `d`, the softmax saturates (one weight ~1, the rest ~0) &mdash; that is the vanishing-gradient problem the scaling fixes.'''),
      runmd("Identity matrices proved the maths. Now run the **same** `attention` on a **real sentence** &mdash; four words, each given a hand-made 2-D meaning-vector (axis&nbsp;0&nbsp;=&nbsp;`animal`-ness, axis&nbsp;1&nbsp;=&nbsp;`action`-ness). Watch which words attend to which &mdash; this is slide 8's &ldquo;it&nbsp;&rarr;&nbsp;animal&rdquo;, computed."),
      code(guard('''import numpy as np
# A tiny sentence -- each word gets a hand-made 2-D "meaning" vector.
words = ["cat", "and", "dog", "ran"]
E = np.array([[1.0, 0.0],    # cat  -> animal
              [0.0, 0.0],    # and  -> neutral (no direction)
              [0.9, 0.0],    # dog  -> animal
              [0.0, 1.0]])   # ran  -> action

# Self-attention: every word is its OWN Query, Key and Value.
W = softmax(E @ E.T / np.sqrt(2), axis=-1)   # row i = how much word i attends to each word

print("attention weights  (each row sums to 1):")
print("       " + " ".join(f"{w:>5}" for w in words))
for w, row in zip(words, W):
    print(f"{w:>5} |" + " ".join(f"{p:5.2f}" for p in row))

print()
print("context-aware outputs (each word = weighted blend of the Values):")
print(np.round(attention(E, E, E), 2))''')),
      noticemd('''- Read **cat&rsquo;s row**: most of its weight lands on **cat** and **dog** &mdash; the two animal words (~0.66 combined) &mdash; and little on **and**/**ran**. Attention *pooled the related words*, exactly like slide 8&rsquo;s &ldquo;it &rarr; animal&rdquo;.
- **ran&rsquo;s row** attends mostly to **itself** &mdash; no other word points in the `action` direction.
- **and&rsquo;s row** is split ~evenly: its vector is all-zeros, so it has **no direction** to prefer anyone &mdash; a neutral word attends to everything equally.
- Nothing is hand-waved: we *chose* the vectors, so every weight is explainable. A real model **learns** vectors that do this on real sentences &mdash; Lab 3.9 pulls exactly these weights out of a live model.'''),
      *([md('''### Answer-key note &mdash; reading `attention(E, E, E)`

The weight matrix above shows **who looks at whom**. The second block &mdash; `attention(E, E, E)` &mdash; shows **what each word *becomes*** afterwards: its original vector *replaced* by a weighted blend of every word&rsquo;s Value.

```
[[0.63 0.17]    <- cat
 [0.48 0.25]    <- and
 [0.62 0.18]    <- dog
 [0.38 0.40]]   <- ran
```

**Where cat&rsquo;s `[0.63, 0.17]` comes from** &mdash; its weight row was `cat 0.34, and 0.17, dog 0.32, ran 0.17`, times the Value vectors:

```
0.34*[1.0,0] + 0.17*[0,0] + 0.32*[0.9,0] + 0.17*[0,1]
  = [0.34+0.29, 0.17]
  = [0.63, 0.17]
```

So cat started as pure &ldquo;animal&rdquo; `[1.0, 0.0]` and comes out `[0.63, 0.17]`: still mostly animal (0.63 on axis&nbsp;0, pulled from **cat** and **dog**), plus a little &ldquo;action&rdquo; (0.17) leaked in from the small weight it gave *ran*.

**Why it matters:** the weight matrix is the *diagnosis* (who is relevant to whom); this block is the *result that flows onward*. Every token leaves an attention layer carrying a mix of the tokens it attended to &mdash; and that context-aware vector is exactly what a real transformer stacks layer after layer. See **ran** &rarr; `[0.38, 0.40]`: it attended mostly to itself but still picked up some animal content, so it is no longer pure &ldquo;action&rdquo;.''')] if sol else []),
      yourturn('''Grow the sentence: add a fifth word **&ldquo;kitten&rdquo;** as another animal &mdash; a vector
near **cat**, e.g. `[0.95, 0.05]` &mdash; and rebuild the weight matrix. **Before you run it**, predict:
whose rows change, and where does **cat**&rsquo;s attention go now that there are *three* animals? Then check.
Stretch: flip **ran** toward the `animal` axis and watch the whole matrix rebalance. A "good" answer: you can
call the rough shape of each row before running &mdash; **kitten**&rsquo;s row should come out almost identical
to **cat**&rsquo;s.'''),
      *sol_answer(sol, r'''import numpy as np
# Added "kitten" -- a third animal, near "cat" -- and rebuilt the weight matrix.
words = ["cat", "and", "dog", "ran", "kitten"]
E = np.array([[1.00, 0.00],    # cat    -> animal
              [0.00, 0.00],    # and    -> neutral
              [0.90, 0.00],    # dog    -> animal
              [0.00, 1.00],    # ran    -> action
              [0.95, 0.05]])   # kitten -> animal, near cat
W = softmax(E @ E.T / np.sqrt(2), axis=-1)
print("       " + " ".join(f"{w:>6}" for w in words))
for w, row in zip(words, W):
    print(f"{w:>6} |" + " ".join(f"{p:6.2f}" for p in row))
print()
print("cat's attention now splits across THREE animals (cat, dog, kitten);")
print("kitten's row is nearly identical to cat's -- near-identical vectors attend alike.")'''),
      footer(3, "That is the whole mechanism. A transformer stacks many of these attention steps -- and that is what 'Attention Is All You Need' meant."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-positional-encoding", "Beginner",
     "Positional Encoding", 25,
     "Give a transformer a sense of word order with sinusoidal positional encodings -- the real formula, computed and plotted by hand.",
     ["Word order", "Sinusoidal encoding", "Position vectors"])
def _l4(sol):
    return [
      header(4, "Positional Encoding", "Beginner", 25,
        ["Understand why attention alone is order-blind",
         "Implement sinusoidal positional encodings",
         "Confirm each position gets a distinct vector"],
        "Positional encoding"),
      setup(4),
      concept('''Attention treats a sentence as a **set** &mdash; it has no built-in sense of order. So we **add** a
**positional encoding** to each token's embedding. The classic recipe uses sines and cosines of
different frequencies:
`PE(pos, 2i) = sin(pos / 10000^(2i/d))`, `PE(pos, 2i+1) = cos(pos / 10000^(2i/d))`.
This is the real formula from the original transformer paper.

> The plot needs `matplotlib` (already in the lab venv).'''),
      buildmd("Fill in the **angle** and the **sin/cos** assignments."),
      code(render([
        "import numpy as np",
        "def positional_encoding(seq_len, d_model):",
        "    pos = np.arange(seq_len)[:, None]",
        "    i = np.arange(d_model)[None, :]",
        {"s": '    angle = ___   # TODO: pos / (10000 ** (2*(i//2) / d_model))',
         "a": '    angle = pos / np.power(10000, (2 * (i // 2)) / d_model)'},
        "    pe = np.zeros((seq_len, d_model))",
        {"s": '    pe[:, 0::2] = ___   # TODO: sin of the even-index angles',
         "a": '    pe[:, 0::2] = np.sin(angle[:, 0::2])'},
        {"s": '    pe[:, 1::2] = ___   # TODO: cos of the odd-index angles',
         "a": '    pe[:, 1::2] = np.cos(angle[:, 1::2])'},
        "    return pe",
      ], sol)),
      runmd("Build a positional-encoding matrix and plot it."),
      code(guard('''import numpy as np
PE = positional_encoding(10, 16)
print("shape:", PE.shape)
print("position 0:", np.round(PE[0], 2))
print("position 1:", np.round(PE[1], 2))
import matplotlib.pyplot as plt
plt.imshow(PE, cmap="RdBu", aspect="auto"); plt.xlabel("dimension"); plt.ylabel("position")
plt.title("Sinusoidal positional encoding"); plt.colorbar(); plt.tight_layout()
plt.savefig(WORK + "/positional_encoding.png", dpi=90); plt.show()
print("saved:", WORK + "/positional_encoding.png")''')),
      noticemd('''- Position 0 starts `sin=0, cos=1` &mdash; every position gets a **distinct** vector.
- The plot shows **stripes**: low dimensions oscillate fast, high dimensions slow &mdash; a multi-scale "clock" the model reads as position.
- Every value is in `[-1, 1]`, so it can be **added** to token embeddings without dominating them.'''),
      yourturn('''Change `seq_len` and `d_model` and re-plot. Then compute the cosine similarity between the
encodings of positions 0&1 vs 0&9 &mdash; does "closer in the sentence" mean "more similar encoding"?
A "good" answer: you can point to the plot and explain how the model could recover *distance* between
two positions from these vectors.'''),
      *sol_answer(sol, r'''import numpy as np
PE = positional_encoding(10, 16)
def cos(a, b): return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
print("cos(pos0, pos1) =", round(cos(PE[0], PE[1]), 3), "  (adjacent -> high)")
print("cos(pos0, pos9) =", round(cos(PE[0], PE[9]), 3), "  (far apart -> lower)")
print("-> closer positions have more similar encodings, so the model can read distance")'''),
      footer(4, "Embedding + positional encoding is what actually enters a transformer block. Now the model knows both *what* and *where*."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-fill-mask", "Beginner",
     "What a Pretrained Model Knows: Fill-in-the-Blank", 25,
     "Predict a masked word from context with a REAL pretrained BERT (distilbert) -- the masked-language-modelling task BERT is trained on.",
     ["Masked language modelling", "Real BERT", "fill-mask pipeline"])
def _l5(sol):
    return [
      header(5, "What a Pretrained Model Knows: Fill-in-the-Blank", "Beginner", 25,
        ["Understand masked language modelling (predicting a hidden word)",
         "Run a real pretrained model on a fill-mask task",
         "Read the model's ranked predictions with confidences"],
        "Encoder vs decoder (BERT vs GPT)"),
      setup(5),
      concept('''BERT is **pretrained** by hiding words and predicting them from context (**masked language
modelling**). No toy this time: we load the real **distilbert-base-uncased** and ask it to fill a
`[MASK]`. The model returns a **ranked list** of candidate words, each with a confidence score &mdash;
knowledge distilled from millions of sentences.'''),
      buildmd("Fill in the real model name and complete `top_fills`."),
      code(render([
        "from transformers import pipeline",
        "def build_fillmask():",
        {"s": '    return pipeline("fill-mask", model=___)   # TODO: "distilbert-base-uncased"',
         "a": '    return pipeline("fill-mask", model="distilbert-base-uncased")'},
        "",
        "def top_fills(fm, sentence, k=5):",
        {"s": '    return [(round(r["score"], 3), r["token_str"]) for r in ___[:k]]   # TODO: fm(sentence)',
         "a": '    return [(round(r["score"], 3), r["token_str"]) for r in fm(sentence)[:k]]'},
      ], sol)),
      runmd("Load the real model and let it fill some blanks. `[MASK]` is distilbert's mask token."),
      code(hfrun('''fm = build_fillmask()
for sentence in ["The capital of France is [MASK].",
                 "A transformer processes text using [MASK].",
                 "The doctor picked up the [MASK]."]:
    print(sentence)
    for score, word in top_fills(fm, sentence):
        print("   ", score, word)
    print()''')),
      noticemd('''- The predictions are **real** &mdash; sometimes obvious, sometimes surprising (a small distilled model is not perfect). That honesty is the point.
- Each candidate has a **confidence**; the list is ranked. Low top-scores mean the model is unsure.
- The model uses **both sides** of the blank (it is an *encoder* / bidirectional) &mdash; unlike GPT, which only sees the left context (Lab 3.10).'''),
      yourturn('''Write blanks that probe what the model knows: factual (`"Water is made of hydrogen and [MASK]."`),
grammatical, or biased (`"The nurse said [MASK] would help."`). Where does it succeed, fail, or reveal
a bias? A "good" answer: you have at least one prompt that exposes a limitation and you can explain
why a small model gets it wrong.'''),
      *sol_answer(sol, hfrun(r'''for sentence in ["Water is made of hydrogen and [MASK].",   # factual
                 "The nurse said [MASK] would help."]:      # probes gendered bias
    print(sentence)
    for score, word in top_fills(fm, sentence):
        print("   ", score, word)
    print()''')),
      footer(5, "This is a real pretrained model *using* its knowledge -- which is exactly what Module 4 fine-tunes for a specific task."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-subword-tokenizer", "Beginner",
     "Why Subwords? Watch a Real Tokenizer", 25,
     "Watch a REAL subword tokenizer (distilbert WordPiece) handle words it never saw -- splitting them into known pieces so nothing is ever 'unknown'.",
     ["Subword tokenization", "Out-of-vocabulary", "## continuation"])
def _l6(sol):
    return [
      header(6, "Why Subwords? Watch a Real Tokenizer", "Beginner", 25,
        ["See how a word tokenizer fails on unseen words",
         "Watch a real WordPiece tokenizer split any word into known pieces",
         "Read the '##' continuation marks and confirm nothing is [UNK]"],
        "Tokens & embeddings"),
      setup(6),
      concept('''Word tokenizers choke on unseen words &mdash; every typo or rare word becomes `[UNK]`. Real
transformers use **subword** tokenizers: a fixed vocabulary of word-pieces, matched greedily
(longest-first), with single characters as the always-available fallback. So a made-up word can still
be spelled from known pieces. We watch the **real** distilbert WordPiece tokenizer do it &mdash; the
`##` prefix marks a piece that continues the previous one.'''),
      buildmd("Complete the one call that returns a word's subword pieces."),
      code(render([
        "def pieces(word, tok):",
        {"s": '    return ___   # TODO: tok.tokenize(word) -- the real subword split',
         "a": '    return tok.tokenize(word)'},
      ], sol)),
      runmd("Throw rare and invented words at the real tokenizer."),
      code(hfrun('''from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")
for word in ["tokenization", "unbelievable", "antidisestablishmentarianism",
             "cryptocurrency", "gyroscopically", "zzxyq"]:
    p = pieces(word, tok)
    print(f"{word:32s} -> {p}   ({len(p)} pieces)")''')),
      noticemd('''- Every word &mdash; even the invented `zzxyq` &mdash; is spelled from known pieces. **Nothing is `[UNK]`.**
- `##` marks a **continuation** piece (glued to the one before, no space).
- Rare/long words cost **more tokens**; common words are a single piece. That is why token counts (and API bills) vary by wording.'''),
      yourturn('''Tokenize words from another language, code identifiers like `getUserById`, or a long chemical
name. How does the tokenizer cope? Then load `AutoTokenizer.from_pretrained("gpt2")` (a **BPE**
tokenizer, not WordPiece) and compare its splits on the same words. A "good" answer: you can describe
one concrete difference between WordPiece and BPE output.'''),
      *sol_answer(sol, hfrun(r'''from transformers import AutoTokenizer
bpe = AutoTokenizer.from_pretrained("gpt2")    # a BPE tokenizer, not WordPiece
for w in ["getUserById", "acetylsalicylic", "cryptocurrency"]:
    print(f"{w:18s}  WordPiece -> {pieces(w, tok)}")
    print(f"{'':18s}  BPE(gpt2) -> {bpe.tokenize(w)}")   # note the leading-space marks vs ## marks
    print()''')),
      footer(6, "Subwords give a finite vocabulary that can still spell *any* word -- which is why every modern transformer uses them. That ends the Beginner set."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-semantic-search", "Intermediate",
     "Semantic Search with Real Embeddings", 35,
     "Embed a small corpus with a REAL model and rank documents by cosine similarity to a query -- the core of search and RAG, on real vectors.",
     ["Real embeddings", "Cosine ranking", "Top-k retrieval"])
def _l7(sol):
    return [
      header(7, "Semantic Search with Real Embeddings", "Intermediate", 35,
        ["Vectorise a corpus with a real sentence-embedding model",
         "Rank documents by cosine similarity to a query",
         "Return the top-k most relevant documents with scores"],
        "Tokens & embeddings"),
      setup(7),
      concept('''**Retrieval** powers search and RAG (Day 3): embed every document, embed the query, and return the
closest documents by cosine similarity. Unlike keyword search, this matches **meaning** &mdash; a query
about "a cute kitten" finds a doc about cats even with no shared words. We use **real**
all-MiniLM-L6-v2 embeddings (unit vectors, so a dot product *is* the cosine).'''),
      buildmd("`embed()` (given) is real. Complete the query embedding, scoring, and top-k selection."),
      code(render([
        EMBED_DEF,
        "",
        'DOCS = ["the cat is a small furry pet animal",',
        '        "dogs are loyal pets that bark",',
        '        "python is a popular programming language",',
        '        "neural networks learn patterns from data",',
        '        "transformers use attention to model language",',
        '        "kittens are playful baby cats"]',
        "",
        "def search(query, DOC_E, k=2):",
        {"s": '    qv = ___     # TODO: embed([query])[0]  -- the query as a unit vector',
         "a": '    qv = embed([query])[0]'},
        {"s": '    sims = ___   # TODO: DOC_E @ qv  -- cosine of each doc with the query (unit vectors)',
         "a": '    sims = DOC_E @ qv'},
        {"s": '    order = ___  # TODO: np.argsort(sims)[::-1][:k]  -- indices of the top-k, highest first',
         "a": '    order = np.argsort(sims)[::-1][:k]'},
        "    return [(round(float(sims[i]), 3), DOCS[i]) for i in order]",
      ], sol)),
      runmd("Embed the corpus once, then run real queries against it."),
      code(hfrun('''DOC_E = embed(DOCS)                     # real model -> one unit vector per document
for query in ["a cute little kitten", "writing software code", "how do transformers work"]:
    print("QUERY:", query)
    for score, doc in search(query, DOC_E, k=2):
        print(f"   {score}  {doc}")
    print()''')),
      noticemd('''- "a cute little kitten" retrieves the **cat / kitten** docs first &mdash; with **zero shared words**. That is semantic (not keyword) matching.
- Scores are real cosines: a clear top hit scores high; an off-topic query scores low across the board.
- Embed the corpus **once**, reuse for every query &mdash; exactly how a vector database / RAG index works.'''),
      yourturn('''Add your own documents and queries. Find a query where semantic search **beats** keyword search
(no shared words but the right hit) and one where it **struggles** (needs an exact term). Try `k=3`.
A "good" answer: you can explain, from the scores, why a particular doc ranked where it did.'''),
      *sol_answer(sol, hfrun(r'''# search() looks up its results in the module-global DOCS, so extend that same list:
DOCS = DOCS + ["the ocean is deep and full of fish",
               "i baked fresh bread this morning"]
DOC_E = embed(DOCS)                                # re-embed the enlarged corpus
for query in ["something to eat for dinner", "creatures of the sea"]:
    print("QUERY:", query)
    for score, doc in search(query, DOC_E, k=3):   # top-3 this time
        print(f"   {score}  {doc}")
    print()''')),
      footer(7, "Real embeddings + cosine ranking = modern semantic search, and the retrieval half of RAG (which returns on Day 3)."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-self-attention-sequence", "Intermediate",
     "Self-Attention Over a Sequence", 40,
     "Project a sequence into Q/K/V and run self-attention over every position, checking shapes at each step -- the real block maths, by hand.",
     ["Q/K/V projections", "Attention matrix", "Shape discipline"])
def _l8(sol):
    return [
      header(8, "Self-Attention Over a Sequence", "Intermediate", 40,
        ["Project token embeddings into queries, keys and values",
         "Run self-attention over a whole sequence at once",
         "Confirm the attention matrix is row-normalised"],
        "The transformer block"),
      setup(8),
      concept('''In a real block, each token embedding **X** is projected by learned matrices into **Q = X.Wq**,
**K = X.Wk**, **V = X.Wv**, then attention runs over the sequence. The **attention matrix** A is
`seq x seq`: row *i* says how much token *i* attends to each token; each row sums to 1. We build it by
hand here so the shapes are unambiguous &mdash; Lab 3.9 extracts exactly this matrix from a real model.'''),
      buildmd("Build the projections and the attention matrix."),
      code(render([
        "import numpy as np",
        "def softmax(x, axis=-1):",
        "    x = x - x.max(axis=axis, keepdims=True); e = np.exp(x)",
        "    return e / e.sum(axis=axis, keepdims=True)",
        "",
        "def self_attention(X, Wq, Wk, Wv):",
        {"s": '    Q, K, V = ___, ___, ___   # TODO: X@Wq, X@Wk, X@Wv',
         "a": '    Q, K, V = X @ Wq, X @ Wk, X @ Wv'},
        "    d = Q.shape[-1]",
        {"s": '    A = ___   # TODO: softmax(Q @ K^T / sqrt(d), axis=-1)',
         "a": '    A = softmax(Q @ K.T / np.sqrt(d), axis=-1)'},
        "    return A @ V, A",
      ], sol)),
      runmd("Run one head of self-attention over a 3-token sequence."),
      code(guard('''import numpy as np
rng = np.random.default_rng(0)
X = rng.normal(size=(3, 4))                        # 3 tokens, 4-d embeddings
Wq = rng.normal(size=(4, 4)); Wk = rng.normal(size=(4, 4)); Wv = rng.normal(size=(4, 4))
out, A = self_attention(X, Wq, Wk, Wv)
print("output shape:", out.shape, "| attention matrix shape:", A.shape)
print("attention matrix (each row sums to 1):\\n", np.round(A, 3))
print("row sums:", np.round(A.sum(axis=1), 3))''')),
      noticemd('''- The **output** is `(seq_len, value_dim)` &mdash; one new vector per token, mixed from the whole sequence.
- The **attention matrix** is `seq x seq` and every **row sums to 1** &mdash; a per-token distribution over what it looked at.
- The learned `Wq/Wk/Wv` are what training actually optimises; the attention operation itself has **no parameters**.'''),
      yourturn('''Give two tokens **identical** embeddings and watch their rows in `A`. Then add more heads:
run `self_attention` a few times with different random `Wq/Wk/Wv` and average the outputs &mdash; that
is multi-head attention in miniature. A "good" answer: you can state the shape of every intermediate
(`Q`, `K`, `A`, output) without running the cell.'''),
      *sol_answer(sol, r'''import numpy as np
rng = np.random.default_rng(1)
X = rng.normal(size=(3, 4)); X[1] = X[0]          # tokens 0 and 1 have IDENTICAL embeddings
Wq = rng.normal(size=(4, 4)); Wk = rng.normal(size=(4, 4)); Wv = rng.normal(size=(4, 4))
_, A = self_attention(X, Wq, Wk, Wv)
print("rows 0 and 1 of A are identical:\n", np.round(A[:2], 3))
# multi-head in miniature: average a few heads with different random projections
outs = [self_attention(X, rng.normal(size=(4, 4)), rng.normal(size=(4, 4)), rng.normal(size=(4, 4)))[0]
        for _ in range(4)]
print("averaged 4-head output shape:", np.mean(outs, axis=0).shape)'''),
      footer(8, "You just ran one head of self-attention over a sequence. Stack a few heads and a feed-forward layer and you have a transformer block."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-attention-heatmap", "Intermediate",
     "Real Attention from a Real Model", 35,
     "Extract the ACTUAL attention weights from a real model (bert-tiny, output_attentions=True) and plot them over the real tokens -- interpretability for real.",
     ["Real attention weights", "output_attentions", "Heatmap"])
def _l9(sol):
    return [
      header(9, "Real Attention from a Real Model", "Intermediate", 35,
        ["Run a real model and ask it for its attention weights",
         "Extract one head's attention matrix over the real tokens",
         "Plot it as a heatmap and read which tokens attend to which"],
        "Self-attention (Q/K/V)"),
      setup(9),
      concept('''Attention is **interpretable**: for each token the model records where it looked. We load the real
**prajjwal1/bert-tiny**, ask for `output_attentions=True`, run a sentence through it, and pull out one
layer/head's `seq x seq` weight matrix &mdash; the *actual* attention the model computed, over its
*actual* subword tokens. Then we plot it.

> The heatmap needs `matplotlib` (already in the lab venv).'''),
      buildmd("Turn on attention output and extract one head's matrix."),
      code(render([
        "import torch, numpy as np",
        "from transformers import AutoTokenizer, AutoModel",
        "",
        "def load_attn_model():",
        '    name = "prajjwal1/bert-tiny"',
        "    tok = AutoTokenizer.from_pretrained(name)",
        {"s": '    model = AutoModel.from_pretrained(name, attn_implementation="eager", output_attentions=___)   # TODO: True',
         "a": '    model = AutoModel.from_pretrained(name, attn_implementation="eager", output_attentions=True)'},
        "    model.eval()",
        "    return tok, model",
        "",
        "def real_attention(sentence, tok, model, layer=-1, head=0):",
        '    enc = tok(sentence, return_tensors="pt")',
        "    with torch.no_grad(): out = model(**enc)",
        "    tokens = tok.convert_ids_to_tokens(enc['input_ids'][0])",
        {"s": '    A = ___   # TODO: out.attentions[layer][0, head].numpy()  -- one head, batch item 0',
         "a": '    A = out.attentions[layer][0, head].numpy()'},
        "    return tokens, A",
      ], sol)),
      runmd("Run a real sentence and plot its real attention."),
      code(hfrun('''tok, model = load_attn_model()
tokens, A = real_attention("the cat sat on the mat", tok, model)
print("tokens:", tokens)
print("attention matrix shape:", A.shape, "| row sums:", np.round(A.sum(axis=1), 2))
import matplotlib.pyplot as plt
plt.figure(figsize=(5, 4))
plt.imshow(A, cmap="viridis")
plt.xticks(range(len(tokens)), tokens, rotation=45, ha="right"); plt.yticks(range(len(tokens)), tokens)
plt.title("real attention (bert-tiny, last layer, head 0)"); plt.colorbar(); plt.tight_layout()
plt.savefig(WORK + "/real_attention.png", dpi=90); plt.show()
print("saved:", WORK + "/real_attention.png")''')),
      noticemd('''- The tokens include `[CLS]` and `[SEP]` &mdash; the model's real inputs, not just the words you typed.
- Each **row still sums to 1** (it is a softmax) &mdash; the same maths you built by hand in Labs 3.3 and 3.8.
- Many tokens attend heavily to `[CLS]`/`[SEP]` &mdash; a real, well-documented behaviour. Different heads (`head=1,2,...`) and layers show different patterns.'''),
      yourturn('''Change the sentence and the `head` / `layer` arguments. Find a head whose pattern looks
**meaningful** (e.g. a word attending to a related word) and one that looks like a "junk" / `[SEP]`
head. A "good" answer: you can point to one cell of the heatmap and say what it means in plain English.'''),
      *sol_answer(sol, hfrun(r'''import numpy as np
tokens, A = real_attention("the quick brown fox", tok, model, layer=-1, head=1)   # try head 1
print("tokens:", tokens)
print("row sums:", np.round(A.sum(axis=1), 2))
print("each token's most-attended token (head 1):")
for i, t in enumerate(tokens):
    print(f"   {t:8s} -> {tokens[int(A[i].argmax())]}")''')),
      footer(9, "Attention maps are how researchers peek inside transformers. You just read them off a real model -- the by-hand maths from Labs 3.3/3.8 made concrete."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-text-generation", "Advanced",
     "Text Generation: Greedy vs Sampling", 40,
     "Generate text with a REAL GPT-style model (distilgpt2) -- greedy vs temperature sampling -- then the same task on a hosted 'GPT API' via ChatGroq.",
     ["Real text generation", "Greedy vs temperature", "Hosted GPT API"])
def _l10(sol):
    return [
      header(10, "Text Generation: Greedy vs Sampling", "Advanced", 40,
        ["Generate text with a real GPT-style model",
         "Compare greedy decoding vs temperature sampling",
         "Run the same task on a hosted 'GPT API' (ChatGroq)"],
        "Encoder vs decoder (BERT vs GPT)"),
      setup(10),
      concept('''GPT-style models **generate** by repeatedly predicting the **next token** and feeding it back in. Two
decoding strategies: **greedy** (always the most likely token &mdash; deterministic, can get repetitive)
and **sampling** with a **temperature** (lower = safer/sharper, higher = more random/creative). We run
the real **distilgpt2** locally, then the client's "GPT API" framing for real via **ChatGroq**
(`openai/gpt-oss-20b`). Same loop &mdash; local tiny model vs a large hosted one.'''),
      buildmd("Fill in the model and the two decoding knobs."),
      code(render([
        "from transformers import pipeline, set_seed",
        "def build_gen():",
        "    set_seed(0)",
        {"s": '    return pipeline("text-generation", model=___)   # TODO: "distilgpt2"',
         "a": '    return pipeline("text-generation", model="distilgpt2")'},
        "",
        "def greedy(gen, prompt, n=25):",
        {"s": '    out = gen(prompt, max_new_tokens=n, do_sample=___)   # TODO: False -- always the top token',
         "a": '    out = gen(prompt, max_new_tokens=n, do_sample=False)'},
        '    return out[0]["generated_text"]',
        "",
        "def sampled(gen, prompt, n=25, temp=1.0):",
        {"s": '    out = gen(prompt, max_new_tokens=n, do_sample=True, top_k=50, temperature=___)   # TODO: temp',
         "a": '    out = gen(prompt, max_new_tokens=n, do_sample=True, top_k=50, temperature=temp)'},
        '    return out[0]["generated_text"]',
      ], sol)),
      runmd("Generate locally with distilgpt2 &mdash; greedy vs low vs high temperature."),
      code(hfrun('''gen = build_gen()
prompt = "The future of artificial intelligence is"
print("GREEDY      :", greedy(gen, prompt))
print()
print("TEMP 0.7    :", sampled(gen, prompt, temp=0.7))
print()
print("TEMP 1.5    :", sampled(gen, prompt, temp=1.5))''')),
      runmd("The same task on a hosted 'GPT API' via ChatGroq. (One-line swap to OpenAI shown in a comment.)"),
      code(guard('''import os
if not os.environ.get("GROQ_API_KEY"):
    print("Set GROQ_API_KEY in .env to run the hosted model (this cell is optional).")
else:
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.7)
    reply = llm.invoke("Continue in one vivid sentence: The future of artificial intelligence is")
    print("GROQ (gpt-oss-20b):", reply.content)
# One-line swap to OpenAI instead of Groq:
#   from langchain_openai import ChatOpenAI
#   llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)   # needs OPENAI_API_KEY''')),
      noticemd('''- **Greedy** is deterministic and can loop / repeat; **temperature 0.7** is coherent-but-varied; **1.5** is wilder and less grammatical.
- distilgpt2 is tiny, so its local text is rough &mdash; that is honest. The **hosted** model (Groq) is far more fluent: **same decoding loop, far more scale**.
- `temperature` on any chat API is exactly this softmax-sharpness knob you are now setting.'''),
      yourturn('''Sweep temperature from `0.2` to `2.0` on your own prompt. Where does it stop being coherent?
Then compare distilgpt2's local output to the Groq output on the *same* prompt. A "good" answer: you
can describe, in one sentence each, what low vs high temperature does and where scale matters most.'''),
      *sol_answer(sol, hfrun(r'''prompt = "In the year 2050, everyday life will"
print("GREEDY   :", greedy(gen, prompt))
for t in [0.2, 0.7, 1.2, 2.0]:              # sweep temperature low -> high
    print(f"TEMP {t}:", sampled(gen, prompt, temp=t))
# low temp stays safe/repetitive; high temp gets creative then incoherent''')),
      footer(10, "Greedy + temperature are the decoding knobs behind every chat model -- local or hosted. You now know what 'temperature' on the GPT API actually does."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-feature-extraction-head", "Advanced",
     "Feature Extraction + a Classifier Head", 40,
     "Use a REAL model as a frozen feature extractor (MiniLM embeddings), then train a small classifier head on top -- the essence of transfer learning.",
     ["Real feature extraction", "Classifier head", "Transfer learning"])
def _l11(sol):
    return [
      header(11, "Feature Extraction + a Classifier Head", "Advanced", 40,
        ["Turn text into real feature vectors with a frozen model",
         "Train a lightweight classifier head on those features",
         "Predict sentiment on unseen sentences"],
        "The model landscape"),
      setup(11),
      concept('''A powerful pattern: let a big model turn text into **features** (embeddings), freeze it, then train a
tiny **head** on top for your task &mdash; **transfer learning** (the heart of Module 4). We use the
**real** all-MiniLM-L6-v2 as the frozen feature extractor and fit a logistic-regression head for
sentiment. A handful of examples is enough because the features already carry meaning.

> Needs `scikit-learn` (already in the lab venv).'''),
      buildmd("`embed()` (given) is the real feature extractor. Train the head and complete `predict`."),
      code(render([
        EMBED_DEF,
        "",
        "from sklearn.linear_model import LogisticRegression",
        'TRAIN = [("i love this movie", 1), ("what a great film", 1), ("wonderful and amazing", 1),',
        '         ("brilliant acting throughout", 1), ("an absolute delight to watch", 1),',
        '         ("i hate this movie", 0), ("what an awful film", 0), ("terrible and boring", 0),',
        '         ("bad acting throughout", 0), ("a complete waste of time", 0)]',
        "",
        "def train_head(X, y):",
        {"s": '    return ___   # TODO: LogisticRegression(max_iter=1000).fit(X, y)',
         "a": '    return LogisticRegression(max_iter=1000).fit(X, y)'},
        "",
        "def predict(clf, text):",
        {"s": '    return int(___)   # TODO: clf.predict(embed([text]))[0]',
         "a": '    return int(clf.predict(embed([text]))[0])'},
      ], sol)),
      runmd("Extract real features, train the head, and classify unseen sentences."),
      code(hfrun('''texts = [t for t, _ in TRAIN]; labels = [y for _, y in TRAIN]
X = embed(texts)                       # real frozen feature extractor -> (n, 384)
print("feature matrix shape:", X.shape)
clf = train_head(X, labels)            # train ONLY the small head
for s in ["i really enjoyed it", "an absolute disaster", "the plot was dull and lifeless",
          "a heartwarming and beautiful story"]:
    print(f"  pred={predict(clf, s)}  <-  {s}")''')),
      noticemd('''- The head trains on **10 examples** and still generalises &mdash; because the **frozen model's features** already encode sentiment.
- You never touched the transformer's weights: **feature extraction = frozen backbone + a trained head**. Cheap, fast, no GPU.
- Swap the head (SVM, small MLP) or the task (topic, spam) &mdash; the same embeddings power all of them.'''),
      yourturn('''Add your own labelled sentences (try a **neutral** class for 3-way). Find a test sentence the
head gets **wrong** &mdash; is it a feature limitation or too little training data? A "good" answer:
you can articulate why transfer learning needs so few examples here.'''),
      *sol_answer(sol, hfrun(r'''extra = [("it was okay nothing special", 0), ("a masterpiece i will rewatch", 1),
         ("mediocre but watchable", 0), ("stunning from start to finish", 1)]
texts = [t for t, _ in TRAIN + extra]; labels = [y for _, y in TRAIN + extra]
clf2 = train_head(embed(texts), labels)       # retrain the head on more examples
for s in ["surprisingly enjoyable", "painfully boring", "a real triumph"]:
    print(f"  pred={predict(clf2, s)}  <-  {s}")   # few examples suffice: features already carry meaning''')),
      footer(11, "Frozen features from a real model + a tiny trained head = transfer learning. Module 4 goes one step further and fine-tunes the backbone itself."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-mini-transformer", "Advanced",
     "Capstone: A Real Sentence-Encoder Pipeline", 45,
     "Assemble the Module-3 pipeline on a REAL model -- tokenize, run the model, mean-pool to a sentence vector, and use it for real semantic matching.",
     ["End-to-end pipeline", "Real model", "Sentence pooling"])
def _l12(sol):
    return [
      header(12, "Capstone: A Real Sentence-Encoder Pipeline", "Advanced", 45,
        ["Chain tokenize -> real model -> mean-pool -> sentence vector",
         "Produce one vector that represents a whole sentence",
         "Use those vectors for real semantic matching"],
        "The transformer block"),
      setup(12),
      concept('''Everything in Module 3 now snaps together on a **real** model: **tokenize** a sentence, run it
through the transformer to get **contextual token vectors** (`last_hidden_state`), **mean-pool** them
into one **sentence vector**, and use those vectors for **semantic matching**. This is exactly what a
real sentence-encoder / retrieval system does &mdash; you are building it from the parts you learned.'''),
      buildmd("Complete the pooling step and the nearest-match selection."),
      code(render([
        "import torch, numpy as np",
        "from transformers import AutoTokenizer, AutoModel",
        "_M = {}",
        "def _load():",
        "    if not _M:",
        '        name = "sentence-transformers/all-MiniLM-L6-v2"',
        "        _M['tok'] = AutoTokenizer.from_pretrained(name)",
        "        _M['mdl'] = AutoModel.from_pretrained(name); _M['mdl'].eval()",
        "    return _M['tok'], _M['mdl']",
        "",
        "def encode(sentence):",
        "    tok, mdl = _load()",
        '    enc = tok(sentence, return_tensors="pt")',
        "    with torch.no_grad(): out = mdl(**enc)",
        "    H = out.last_hidden_state[0]                 # (tokens, dim) real contextual vectors",
        {"s": '    v = ___   # TODO: mean-pool H over the token axis (dim=0) -> one sentence vector',
         "a": '    v = H.mean(dim=0)'},
        "    v = v / v.norm()                             # unit vector",
        "    return v.numpy()",
        "",
        "def best_match(query, corpus):",
        "    qv = encode(query)",
        "    sims = [float(np.dot(qv, encode(s))) for s in corpus]",
        {"s": '    i = ___   # TODO: int(np.argmax(sims)) -- the most similar sentence',
         "a": '    i = int(np.argmax(sims))'},
        "    return corpus[i], round(sims[i], 3)",
      ], sol)),
      runmd("Run the full real pipeline and match queries to a small corpus."),
      code(hfrun('''# see the tokenize step for one sentence, then use the whole pipeline
tok, _ = _load()
print("tokens for 'a small furry pet':", tok.tokenize("a small furry pet"))

CORPUS = ["cats and kittens are small furry pets",
          "the stock market fell sharply today",
          "transformers use attention to understand language",
          "he cooked a delicious italian pasta dinner"]
for query in ["a cute little kitten", "how do neural networks read text", "what should i eat tonight"]:
    match, score = best_match(query, CORPUS)
    print(f"\\nQUERY: {query}\\n  best -> {match}  (cos={score})")''')),
      noticemd('''- One real pipeline: **tokenize -> model -> mean-pool -> unit vector**, every stage from Module 3 in order.
- Each query lands on the **right** corpus sentence by meaning &mdash; with no shared keywords.
- `last_hidden_state` holds **contextual** token vectors (a word's vector depends on its neighbours); mean-pooling collapses them to a fixed-size sentence vector a classifier or index can use.'''),
      yourturn('''Extend the corpus, add paraphrase queries, or swap the model for `distilbert-base-uncased`
inside `_load()` &mdash; do the matches change? Then try **max-pooling** or **CLS-token** pooling
(`H[0]`) instead of mean and compare. A "good" answer: you can name each stage of your pipeline and
say what would break if you removed it.'''),
      *sol_answer(sol, hfrun(r'''CORPUS2 = CORPUS + ["the puppy chased a ball across the park",
                    "she solved the equation on the whiteboard"]
for query in ["a tiny meowing feline", "teaching a computer to read", "outdoor play with a pet"]:
    match, score = best_match(query, CORPUS2)      # paraphrase queries, extended corpus
    print(f"QUERY: {query}\n  best -> {match}  (cos={score})")''')),
      footer(12, "You built a real sentence encoder from the parts you learned -- tokenize, embed, attend, pool. Module 4 takes real pretrained models and fine-tunes them for specific tasks. That completes Module 3."),
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
        banner = md(f'''> ## SOLUTION / ANSWER KEY &mdash; Lab 3.{nn}
> This is the **completed** notebook (all `___` blanks filled). For the student version, open
> [`../{info['slug']}.ipynb`](../{info['slug']}.ipynb). Trainer use &mdash; or self-check after you've tried it yourself.''')
        with open(os.path.join(SOL_DIR, fname), "w") as f:
            json.dump(notebook([banner] + info["build"](True)), f, indent=1, ensure_ascii=False)

print(f"Wrote {len(NB)} notebooks to {OUT_DIR}" + (f" and solutions to {SOL_DIR}" if SOL_DIR else ""))

with open(os.path.join(_HERE, "_meta.json"), "w") as f:
    json.dump({str(nn): {k: NB[nn][k] for k in ("slug","level","title","mins","summary","concepts")}
               for nn in NB}, f, indent=1)
