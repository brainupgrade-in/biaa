# -*- coding: utf-8 -*-
"""Generator for Day 2 Module 3 hands-on labs (12 notebooks).
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR.

Design: every GRADED cell is offline (NumPy / scikit-learn) so the labs run and
verify with no network and no heavy installs. The "use a real transformer" steps
are OPTIONAL, guarded Hugging Face cells (not graded) that degrade gracefully if
`transformers` is absent -- and they never require a paid API key."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day2-module3-why-transformers.html"
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
WORK = "/tmp/biaa-lab-03-{nn:02d}"
os.makedirs(WORK, exist_ok=True)
print("Working dir:", WORK){extra}''')

def header(nn, title, level, mins, goals, concept_slide):
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 3.{nn} &mdash; {title}

**Level:** {level} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 2 &middot; Module 3 &mdash; Why Transformers?**

### What you'll do
{g}

> **How this lab works (experiential flow):** read the **Concept**, run the **Demo** to see it work, then complete **Your Turn** by replacing every `___` placeholder. Run the **grader** cell at the end &mdash; it prints `[PASS]` / `[FAIL]` / `[TODO]` and a final `Score`. Aim for a full score.

**Reference:** [Module 3 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 3 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 3 labs](./index.html) &nbsp;&middot;&nbsp; [Module 3 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

def optional_hf(intro, body):
    """An OPTIONAL, non-graded Hugging Face cell that degrades gracefully."""
    return [md(f'''## Optional &mdash; the real thing with Hugging Face (not graded)
{intro} Safe to skip &mdash; it needs `pip install transformers torch` and a one-time model
download. If `transformers` is not installed, the cell simply prints a note and moves on.'''),
            code(body)]

NB = {}
def lab(nn, slug, level, title, mins, summary, concepts):
    def deco(fn):
        NB[nn] = dict(slug=slug, level=level, title=title, mins=mins,
                      summary=summary, concepts=concepts, build=fn)
        return fn
    return deco

# ============================================================ LAB 01
@lab(1, "lab-01-tokenization", "Beginner",
     "Tokenization: Turning Text into Tokens", 20,
     "Split raw text into tokens, build a vocabulary, and encode tokens to integer IDs -- step one for every transformer.",
     ["Tokenization", "Vocabulary", "Encoding to IDs"])
def _l1(sol):
    return [
      header(1, "Tokenization: Turning Text into Tokens", "Beginner", 20,
        ["Split text into tokens with a simple rule",
         "Build a vocabulary mapping tokens to integer IDs",
         "Encode a sentence into the IDs a model consumes"],
        "Tokens & embeddings"),
      setup(1),
      md('''## Concept
A transformer never sees text &mdash; it sees **token IDs**. First we **tokenize** (split text into
pieces), then map each unique token to an integer via a **vocabulary**, then **encode**. Real models
use *subword* tokenizers (Lab 3.6); here we start with words.'''),
      code('''# DEMO -- the simplest tokenizer: lowercase + split on whitespace
text = "The cat sat on the mat"
print(text.lower().split())'''),
      md('''## Your Turn
Implement a slightly smarter tokenizer (splits off punctuation), a **vocabulary** builder, and an **encoder**.'''),
      code(render([
        "import re",
        "def tokenize(text):",
        {"s": '    return ___   # TODO: lowercase, split on non-alphanumeric, drop empties',
         "a": '    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if t]'},
        "",
        "def build_vocab(tokens):",
        {"s": '    return ___   # TODO: {token: id} over the SORTED unique tokens (use enumerate)',
         "a": '    return {tok: i for i, tok in enumerate(sorted(set(tokens)))}'},
        "",
        "def encode(tokens, vocab):",
        {"s": '    return ___   # TODO: list of vocab[t] for each token',
         "a": '    return [vocab[t] for t in tokens]'},
        "",
        "try:",
        '    toks = tokenize("The cat, the CAT! sat.")',
        "    vocab = build_vocab(toks)",
        '    print("tokens:", toks); print("vocab:", vocab); print("ids:", encode(toks, vocab))',
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("tokenize lowercases & strips punctuation", lambda: tokenize("The cat, CAT!") == ["the", "cat", "cat"])
expect_true("build_vocab maps sorted unique tokens", lambda: build_vocab(["b", "a", "a"]) == {"a": 0, "b": 1})
expect_true("encode maps tokens to their ids", lambda: encode(["a", "b"], {"a": 0, "b": 1}) == [0, 1])'''),
      *optional_hf("See how a real transformer tokenizer (BERT's WordPiece) splits the same text into subwords.",
'''try:
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("prajjwal1/bert-tiny")
    print(tok.tokenize("Tokenization is unbelievably powerful!"))
except Exception as e:
    print("Optional real-model demo skipped (the graded cells above already covered this).")
    print("  reason:", type(e).__name__, "--", e)'''),
      footer(1, "Every model pipeline starts here: text -> tokens -> IDs. Next we give those tokens *meaning* as vectors."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-embeddings-cosine", "Beginner",
     "Word Embeddings & Cosine Similarity", 20,
     "Represent words as vectors and measure how similar two words are with cosine similarity.",
     ["Embeddings", "Cosine similarity", "Semantic distance"])
def _l2(sol):
    return [
      header(2, "Word Embeddings & Cosine Similarity", "Beginner", 20,
        ["Represent words as vectors (embeddings)",
         "Implement cosine similarity in NumPy",
         "Find the most similar word to a query"],
        "Tokens & embeddings"),
      setup(2),
      md('''## Concept
After tokenizing, each token becomes a vector &mdash; an **embedding** &mdash; chosen so that words
with similar meaning point in similar directions. **Cosine similarity** measures the angle between
two vectors: `1.0` = identical direction, `0` = unrelated.'''),
      code('''# DEMO -- toy 3-D embeddings; royalty vs fruit
import numpy as np
EMB = {"king":  np.array([0.9, 0.8, 0.1]), "queen": np.array([0.8, 0.9, 0.1]),
       "apple": np.array([0.1, 0.2, 0.9]), "orange":np.array([0.2, 0.1, 0.85])}
print("king dot queen:", float(np.dot(EMB["king"], EMB["queen"])))'''),
      md('''## Your Turn
Implement `cosine` and use it to find each word's nearest neighbour.'''),
      code(render([
        "import numpy as np",
        'EMB = {"king":  np.array([0.9, 0.8, 0.1]), "queen": np.array([0.8, 0.9, 0.1]),',
        '       "apple": np.array([0.1, 0.2, 0.9]), "orange":np.array([0.2, 0.1, 0.85])}',
        "",
        "def cosine(a, b):",
        {"s": '    return ___   # TODO: (a . b) / (||a|| * ||b||)   use np.dot, np.linalg.norm',
         "a": '    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))'},
        "",
        "def most_similar(word):",
        "    best, best_sim = None, -2.0",
        "    for other in EMB:",
        "        if other == word: continue",
        {"s": '        s = ___   # TODO: cosine between word and other',
         "a": '        s = cosine(EMB[word], EMB[other])'},
        "        if s > best_sim: best_sim, best = s, other",
        "    return best",
        "",
        "try: print('nearest to king:', most_similar('king'))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''import numpy as np
expect_true("cosine of a vector with itself is 1.0", lambda: abs(cosine(EMB["king"], EMB["king"]) - 1.0) < 1e-9)
expect_true("king is closer to queen than to apple", lambda: cosine(EMB["king"], EMB["queen"]) > cosine(EMB["king"], EMB["apple"]))
expect_true("most_similar('king') == 'queen'", lambda: most_similar("king") == "queen")'''),
      footer(2, "Embeddings turn meaning into geometry, and cosine similarity measures it. This is the engine behind search, RAG and recommendations."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-attention-by-hand", "Beginner",
     "Self-Attention by Hand", 25,
     "Implement scaled dot-product attention in NumPy -- the single idea at the heart of every transformer.",
     ["Query/Key/Value", "Softmax", "Scaled dot-product attention"])
def _l3(sol):
    return [
      header(3, "Self-Attention by Hand", "Beginner", 25,
        ["Implement a numerically-stable softmax",
         "Compute scaled dot-product attention: softmax(Q.Kt / sqrt(d)) . V",
         "See a query 'attend' to the matching key"],
        "Self-attention (Q/K/V)"),
      setup(3),
      md('''## Concept
**Attention** lets each token look at every other token and pull in what's relevant. For queries
**Q**, keys **K** and values **V**:
`attention(Q, K, V) = softmax( Q . Kt / sqrt(d) ) . V`.
The `softmax` turns similarity scores into weights that sum to 1; the scaling by `sqrt(d)` keeps them stable.'''),
      code('''# DEMO -- the shapes
import numpy as np
Q = np.array([[1.0, 0.0]]); K = np.array([[1.0, 0.0], [0.0, 1.0]]); V = np.array([[10.0, 0.0], [0.0, 10.0]])
print("Q", Q.shape, "K", K.shape, "V", V.shape)'''),
      md('''## Your Turn
Implement `softmax` and `attention`.'''),
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
        "",
        "Q = np.array([[10.0, 0.0], [0.0, 10.0]]); K = np.array([[1.0, 0.0], [0.0, 1.0]]); V = np.array([[1.0, 0.0], [0.0, 1.0]])",
        "try: print('attention output:\\n', np.round(attention(Q, K, V), 3))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''import numpy as np
expect_true("softmax of [1,1] is [0.5,0.5]", lambda: np.allclose(softmax(np.array([1.0, 1.0])), [0.5, 0.5]))
expect_true("softmax rows sum to 1", lambda: abs(float(softmax(np.array([2.0, 1.0, 0.0])).sum()) - 1.0) < 1e-9)
Q = np.array([[10.0,0.0],[0.0,10.0]]); K = np.array([[1.0,0.0],[0.0,1.0]]); V = np.array([[1.0,0.0],[0.0,1.0]])
expect_true("output has shape (queries, value_dim)", lambda: attention(Q, K, V).shape == (2, 2))
expect_true("a strong query attends to its matching value", lambda: np.allclose(attention(Q, K, V), np.eye(2), atol=1e-2))'''),
      footer(3, "That is the whole mechanism. A transformer stacks many of these attention steps -- and that is what 'Attention Is All You Need' meant."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-positional-encoding", "Beginner",
     "Positional Encoding", 25,
     "Give a transformer a sense of word order with sinusoidal positional encodings.",
     ["Word order", "Sinusoidal encoding", "Position vectors"])
def _l4(sol):
    return [
      header(4, "Positional Encoding", "Beginner", 25,
        ["Understand why attention alone is order-blind",
         "Implement sinusoidal positional encodings",
         "Confirm each position gets a distinct vector"],
        "Positional encoding"),
      setup(4),
      md('''## Concept
Attention treats a sentence as a **set** &mdash; it has no built-in sense of order. So we **add** a
**positional encoding** to each token's embedding. The classic recipe uses sines and cosines of
different frequencies:
`PE(pos, 2i) = sin(pos / 10000^(2i/d))`, `PE(pos, 2i+1) = cos(pos / 10000^(2i/d))`.

> The plot needs `matplotlib`.'''),
      code('''# DEMO -- positions and dimensions
import numpy as np
seq_len, d_model = 5, 8
print("we will build a", (seq_len, d_model), "matrix: one row per position")'''),
      md('''## Your Turn
Fill in the **angle** and the **sin/cos** assignments.'''),
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
        "",
        "try:",
        "    PE = positional_encoding(5, 8)",
        "    print('shape:', PE.shape); print('position 0:', np.round(PE[0], 2))",
        "    import matplotlib.pyplot as plt",
        "    plt.imshow(PE, cmap='RdBu', aspect='auto'); plt.xlabel('dimension'); plt.ylabel('position')",
        "    plt.title('Positional encoding'); plt.colorbar(); plt.tight_layout()",
        "    plt.savefig(WORK + '/positional_encoding.png', dpi=90); plt.show()",
        "except Exception as e: print('Fill the blanks (plot needs matplotlib).', type(e).__name__)",
      ], sol)),
      grader('''import numpy as np
expect_true("shape is (seq_len, d_model)", lambda: positional_encoding(5, 8).shape == (5, 8))
expect_true("all values are within [-1, 1]", lambda: np.all(np.abs(positional_encoding(5, 8)) <= 1.0 + 1e-9))
expect_true("position 0 starts sin=0, cos=1", lambda: abs(positional_encoding(5, 8)[0, 0]) < 1e-9 and abs(positional_encoding(5, 8)[0, 1] - 1.0) < 1e-9)
expect_true("different positions get different vectors", lambda: not np.allclose(positional_encoding(5, 8)[1], positional_encoding(5, 8)[2]))'''),
      footer(4, "Embedding + positional encoding is what actually enters a transformer block. Now the model knows both *what* and *where*."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-fill-mask", "Beginner",
     "What a Pretrained Model Knows: Fill-in-the-Blank", 25,
     "Predict a masked word from its context with a tiny language model -- the idea BERT is pretrained on.",
     ["Masked language modelling", "Context prediction", "Bigram model"])
def _l5(sol):
    return [
      header(5, "What a Pretrained Model Knows: Fill-in-the-Blank", "Beginner", 25,
        ["Understand masked language modelling (predicting a hidden word)",
         "Build a tiny next-word model from a corpus",
         "Predict the most likely word to fill a blank"],
        "Encoder vs decoder (BERT vs GPT)"),
      setup(5),
      md('''## Concept
BERT is **pretrained** by hiding words and predicting them from context (**masked language
modelling**). We build the tiniest version: count which word follows which, then fill a `[MASK]`
with the most likely next word.'''),
      code('''# DEMO -- our toy corpus
CORPUS = "the cat sat on the mat the cat sat on the rug the cat ran fast".split()
print("tokens:", len(CORPUS))'''),
      md('''## Your Turn
Build the bigram counts and a `fill_mask` that returns the most likely word after a given word.'''),
      code(render([
        "from collections import defaultdict, Counter",
        'CORPUS = "the cat sat on the mat the cat sat on the rug the cat ran fast".split()',
        "",
        "def build_bigrams(tokens):",
        "    b = defaultdict(Counter)",
        "    for prev, nxt in zip(tokens, tokens[1:]):",
        {"s": '        ___   # TODO: count nxt as following prev:  b[prev][nxt] += 1',
         "a": '        b[prev][nxt] += 1'},
        "    return b",
        "",
        "def fill_mask(prev_word, bigrams):",
        {"s": '    return ___   # TODO: the most common word after prev_word (Counter.most_common)',
         "a": '    return bigrams[prev_word].most_common(1)[0][0]'},
        "",
        "try:",
        "    bg = build_bigrams(CORPUS)",
        "    print('the [MASK] ->', fill_mask('the', bg))",
        "    print('sat [MASK] ->', fill_mask('sat', bg))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("'the' is most often followed by 'cat'", lambda: fill_mask("the", build_bigrams(CORPUS)) == "cat")
expect_true("'sat' is most often followed by 'on'", lambda: fill_mask("sat", build_bigrams(CORPUS)) == "on")
expect_true("'on' is most often followed by 'the'", lambda: fill_mask("on", build_bigrams(CORPUS)) == "the")'''),
      *optional_hf("Watch a real pretrained BERT fill the same kind of blank from its vast training.",
'''try:
    from transformers import pipeline
    fm = pipeline("fill-mask", model="prajjwal1/bert-tiny")
    for r in fm("the cat sat on the [MASK].")[:3]:
        print(round(r["score"], 3), r["token_str"])
except Exception as e:
    print("Optional real-model demo skipped (the graded cells above already covered this).")
    print("  reason:", type(e).__name__, "--", e)'''),
      footer(5, "Scale this idea to billions of words and a transformer, and you get a model with real language knowledge -- which we *use* on Day 2's pretrained labs (Module 4)."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-subword-tokenizer", "Beginner",
     "Why Subwords? A Greedy Subword Tokenizer", 25,
     "Build a greedy subword tokenizer and see how it handles words a word-level vocabulary would miss.",
     ["Subword tokenization", "Out-of-vocabulary", "Greedy matching"])
def _l6(sol):
    return [
      header(6, "Why Subwords? A Greedy Subword Tokenizer", "Beginner", 25,
        ["See the out-of-vocabulary problem with word tokenizers",
         "Implement greedy longest-match subword tokenization",
         "Tokenize an unseen word from known pieces"],
        "Tokens & embeddings"),
      setup(6),
      md('''## Concept
Word tokenizers choke on unseen words (every typo or rare word is 'unknown'). Real transformers use
**subword** tokenizers: a fixed vocabulary of word-pieces, assembled greedily, with single characters
as the always-available fallback. So `"tokenization"` becomes `["token", "iz", "ation"]` &mdash; no
'unknown' needed.'''),
      code('''# DEMO -- a tiny subword vocabulary
SUBWORDS = {"un", "happy", "ly", "token", "iz", "ation", "ing", "play", "ful"}
print("known pieces:", sorted(SUBWORDS))'''),
      md('''## Your Turn
Complete the greedy matcher: at each position take the **longest** piece that is in the vocab
(or a single character).'''),
      code(render([
        'SUBWORDS = {"un", "happy", "ly", "token", "iz", "ation", "ing", "play", "ful"}',
        "",
        "def subword_tokenize(word):",
        "    pieces, i = [], 0",
        "    while i < len(word):",
        "        matched = None",
        "        for L in range(len(word) - i, 0, -1):   # longest first",
        "            cand = word[i:i + L]",
        {"s": '            if ___ or L == 1:   # TODO: accept cand if it is a known subword',
         "a": '            if cand in SUBWORDS or L == 1:'},
        "                matched = cand; break",
        "        pieces.append(matched)",
        {"s": '        i += ___   # TODO: advance by the length of the matched piece',
         "a": '        i += len(matched)'},
        "    return pieces",
        "",
        "try:",
        "    for w in ['unhappy', 'tokenization', 'xyz']:",
        "        print(w, '->', subword_tokenize(w))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("'unhappy' -> ['un','happy']", lambda: subword_tokenize("unhappy") == ["un", "happy"])
expect_true("'tokenization' -> ['token','iz','ation']", lambda: subword_tokenize("tokenization") == ["token", "iz", "ation"])
expect_true("unknown letters fall back to single chars", lambda: subword_tokenize("xy") == ["x", "y"])'''),
      footer(6, "Subwords give a finite vocabulary that can still spell *any* word -- which is why every modern transformer uses them. That ends the Beginner set."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-semantic-search", "Intermediate",
     "Semantic Search with Embeddings", 35,
     "Turn a small corpus into vectors and rank documents by similarity to a query -- the core of search and RAG.",
     ["TF-IDF embeddings", "Cosine ranking", "Top-k retrieval"])
def _l7(sol):
    return [
      header(7, "Semantic Search with Embeddings", "Intermediate", 35,
        ["Vectorise a corpus of documents",
         "Rank documents by cosine similarity to a query",
         "Return the top-k most relevant documents"],
        "Tokens & embeddings"),
      setup(7),
      md('''## Concept
**Retrieval** powers search and RAG (Day 3): embed every document, embed the query, and return the
closest documents by cosine similarity. We use TF-IDF vectors as a lightweight, offline stand-in for
transformer embeddings &mdash; the *mechanics* are identical.

> Needs `scikit-learn`.'''),
      code('''# DEMO -- a tiny document collection
DOCS = ["the cat is a small pet animal", "dogs are loyal pets that bark",
        "python is a programming language", "neural networks learn from data",
        "transformers use attention for language", "kittens are baby cats"]
from sklearn.feature_extraction.text import TfidfVectorizer
vec = TfidfVectorizer().fit(DOCS)
print("vocabulary size:", len(vec.vocabulary_))'''),
      md('''## Your Turn
Embed the query, score all documents, and return the **top-k** indices.'''),
      code(render([
        "from sklearn.feature_extraction.text import TfidfVectorizer",
        "from sklearn.metrics.pairwise import cosine_similarity",
        "import numpy as np",
        'DOCS = ["the cat is a small pet animal", "dogs are loyal pets that bark",',
        '        "python is a programming language", "neural networks learn from data",',
        '        "transformers use attention for language", "kittens are baby cats"]',
        "vec = TfidfVectorizer().fit(DOCS)",
        "doc_vecs = vec.transform(DOCS)",
        "",
        "def search(query, k=2):",
        {"s": '    qv = ___   # TODO: transform [query] into a vector',
         "a": '    qv = vec.transform([query])'},
        {"s": '    sims = ___   # TODO: cosine_similarity(qv, doc_vecs)[0]',
         "a": '    sims = cosine_similarity(qv, doc_vecs)[0]'},
        {"s": '    return list(___)   # TODO: indices of the top-k scores (highest first)',
         "a": '    return list(np.argsort(sims)[::-1][:k])'},
        "",
        "try:",
        "    hits = search('a cute kitten pet', k=2)",
        "    for idx in hits: print(idx, '->', DOCS[idx])",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("search returns k indices", lambda: len(search("a cute kitten pet", k=2)) == 2)
expect_true("a pet query retrieves a cat/kitten doc first", lambda: search("a cute kitten pet", k=1)[0] in (0, 5))
expect_true("a coding query retrieves the python doc", lambda: 2 in search("software programming code", k=2))'''),
      footer(7, "Swap TF-IDF for transformer embeddings and you have modern semantic search -- and the retrieval half of RAG, which returns on Day 3."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-self-attention-sequence", "Intermediate",
     "Self-Attention Over a Sequence", 40,
     "Project a sequence into Q/K/V and run self-attention over every position, checking the shapes at each step.",
     ["Q/K/V projections", "Attention matrix", "Shape discipline"])
def _l8(sol):
    return [
      header(8, "Self-Attention Over a Sequence", "Intermediate", 40,
        ["Project token embeddings into queries, keys and values",
         "Run self-attention over a whole sequence at once",
         "Confirm the attention matrix is row-normalised"],
        "The transformer block"),
      setup(8),
      md('''## Concept
In a real block, each token embedding **X** is projected by learned matrices into **Q = X.Wq**,
**K = X.Wk**, **V = X.Wv**, then attention runs over the sequence. The **attention matrix** A is
`seq x seq`: row *i* says how much token *i* attends to each token. Each row sums to 1.'''),
      code('''# DEMO -- a 3-token sequence, 4-d embeddings
import numpy as np
rng = np.random.default_rng(0)
X = rng.normal(size=(3, 4))
print("sequence X shape:", X.shape)'''),
      md('''## Your Turn
Build the projections and the attention matrix.'''),
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
        "",
        "rng = np.random.default_rng(0)",
        "X = rng.normal(size=(3, 4))",
        "Wq = rng.normal(size=(4, 4)); Wk = rng.normal(size=(4, 4)); Wv = rng.normal(size=(4, 4))",
        "try:",
        "    out, A = self_attention(X, Wq, Wk, Wv)",
        "    print('output shape:', out.shape, '| attention matrix shape:', A.shape)",
        "    print('row sums:', np.round(A.sum(axis=1), 3))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''import numpy as np
rng = np.random.default_rng(0)
X = rng.normal(size=(3, 4)); Wq = rng.normal(size=(4, 4)); Wk = rng.normal(size=(4, 4)); Wv = rng.normal(size=(4, 4))
expect_true("output has shape (seq_len, value_dim)", lambda: self_attention(X, Wq, Wk, Wv)[0].shape == (3, 4))
expect_true("attention matrix is seq x seq", lambda: self_attention(X, Wq, Wk, Wv)[1].shape == (3, 3))
expect_true("every attention row sums to 1", lambda: np.allclose(self_attention(X, Wq, Wk, Wv)[1].sum(axis=1), 1.0))'''),
      footer(8, "You just ran one head of self-attention over a sequence. Stack a few heads and a feed-forward layer and you have a transformer block."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-attention-heatmap", "Intermediate",
     "Visualising an Attention Matrix", 35,
     "Compute and plot the attention weights for a short sentence to see which words attend to which.",
     ["Attention weights", "Heatmap", "Interpretability"])
def _l9(sol):
    return [
      header(9, "Visualising an Attention Matrix", "Intermediate", 35,
        ["Compute self-attention weights for a toy sentence",
         "Plot the attention matrix as a heatmap",
         "Read which tokens attend most strongly to which"],
        "Self-attention (Q/K/V)"),
      setup(9),
      md('''## Concept
Attention is **interpretable**: the `seq x seq` weight matrix shows, for each word, where it looked.
We compute simple self-similarity attention (`X . Xt`) for a tiny sentence and plot it.

> The heatmap needs `matplotlib`.'''),
      code('''# DEMO -- a 4-word sentence with hand-made embeddings
import numpy as np
WORDS = ["the", "cat", "sat", "down"]
X = np.array([[1,0.1,0.1],[0.1,1,0.3],[0.1,0.3,1],[0.2,0.1,0.95]], dtype=float)
X = X / np.linalg.norm(X, axis=1, keepdims=True)   # unit embeddings
print("words:", WORDS, "| embedding matrix:", X.shape)'''),
      md('''## Your Turn
Compute the attention-weight matrix (row-normalised self-similarity).'''),
      code(render([
        "import numpy as np",
        "def softmax(x, axis=-1):",
        "    x = x - x.max(axis=axis, keepdims=True); e = np.exp(x)",
        "    return e / e.sum(axis=axis, keepdims=True)",
        "",
        'WORDS = ["the", "cat", "sat", "down"]',
        "X = np.array([[1,0.1,0.1],[0.1,1,0.3],[0.1,0.3,1],[0.2,0.1,0.95]], dtype=float)",
        "X = X / np.linalg.norm(X, axis=1, keepdims=True)   # unit embeddings",
        "",
        "def attention_weights(X):",
        "    d = X.shape[-1]",
        {"s": '    return ___   # TODO: softmax(X @ X^T / sqrt(d), axis=-1)',
         "a": '    return softmax(X @ X.T / np.sqrt(d), axis=-1)'},
        "",
        "try:",
        "    A = attention_weights(X)",
        "    print(np.round(A, 2))",
        "    import matplotlib.pyplot as plt",
        "    plt.imshow(A, cmap='viridis'); plt.xticks(range(4), WORDS); plt.yticks(range(4), WORDS)",
        "    plt.title('attention weights'); plt.colorbar(); plt.tight_layout()",
        "    plt.savefig(WORK + '/attention_heatmap.png', dpi=90); plt.show()",
        "except Exception as e: print('Fill the blank (plot needs matplotlib).', type(e).__name__)",
      ], sol)),
      grader('''import numpy as np
expect_true("attention matrix is 4x4", lambda: attention_weights(X).shape == (4, 4))
expect_true("rows are valid distributions (sum to 1)", lambda: np.allclose(attention_weights(X).sum(axis=1), 1.0))
expect_true("each token attends most to itself here", lambda: np.all(attention_weights(X).argmax(axis=1) == np.arange(4)))'''),
      footer(9, "Attention maps are how researchers peek inside transformers. The same plot on a real model reveals grammar and coreference being learned."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-text-generation", "Advanced",
     "Text Generation: Greedy vs Sampling", 40,
     "Generate text by predicting the next token -- with greedy decoding and temperature sampling -- the way GPT works.",
     ["Next-token prediction", "Greedy decoding", "Temperature sampling"])
def _l10(sol):
    return [
      header(10, "Text Generation: Greedy vs Sampling", "Advanced", 40,
        ["Build a tiny next-word model and generate from it",
         "Implement greedy decoding (always the top token)",
         "Implement temperature-controlled softmax sampling"],
        "Encoder vs decoder (BERT vs GPT)"),
      setup(10),
      md('''## Concept
GPT-style models **generate** by repeatedly predicting the **next token** and feeding it back in. Two
decoding strategies: **greedy** (always take the most likely token) and **sampling** with a
**temperature** (lower = safer/sharper, higher = more random/creative). We build a tiny word-level
model so the mechanics are crystal clear. The client's GPT-API generation is the same loop at scale &mdash;
the optional cell at the end shows the real thing.'''),
      code('''# DEMO -- build a tiny next-word model from a corpus
from collections import defaultdict, Counter
CORPUS = "the cat sat on the mat the cat sat on the rug the cat ran fast".split()
MODEL = defaultdict(Counter)
for a, b in zip(CORPUS, CORPUS[1:]): MODEL[a][b] += 1
print("after 'the':", dict(MODEL["the"]))'''),
      md('''## Your Turn
Implement temperature **softmax**, **greedy** next-token, and the **generate** loop.'''),
      code(render([
        "import numpy as np",
        "from collections import defaultdict, Counter",
        'CORPUS = "the cat sat on the mat the cat sat on the rug the cat ran fast".split()',
        "MODEL = defaultdict(Counter)",
        "for a, b in zip(CORPUS, CORPUS[1:]): MODEL[a][b] += 1",
        "",
        "def softmax_temp(logits, temp=1.0):",
        "    z = np.array(logits, dtype=float) / temp",
        {"s": '    e = ___   # TODO: exp of (z - z.max()) for stability',
         "a": '    e = np.exp(z - z.max())'},
        "    return e / e.sum()",
        "",
        "def greedy_next(word):",
        {"s": '    return ___   # TODO: the most common next word after `word` (Counter.most_common)',
         "a": '    return MODEL[word].most_common(1)[0][0]'},
        "",
        "def generate(start, steps=4):",
        "    out = [start]",
        "    for _ in range(steps):",
        {"s": '        out.append(___)   # TODO: greedy next word after the last token',
         "a": '        out.append(greedy_next(out[-1]))'},
        "    return out",
        "",
        "try:",
        "    print('greedy:', ' '.join(generate('the', 4)))",
        "    print('temp 0.5 vs 2.0 max prob:', round(softmax_temp([2,1,0],0.5).max(),3), round(softmax_temp([2,1,0],2.0).max(),3))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''import numpy as np
expect_true("softmax_temp sums to 1", lambda: abs(float(softmax_temp([2.0,1.0,0.0]).sum()) - 1.0) < 1e-9)
expect_true("lower temperature is sharper (higher max prob)", lambda: softmax_temp([2,1,0], 0.5).max() > softmax_temp([2,1,0], 2.0).max())
expect_true("greedy_next('the') == 'cat'", lambda: greedy_next("the") == "cat")
expect_true("generate('the', 4) starts the cat sat on", lambda: generate("the", 4)[:4] == ["the", "cat", "sat", "on"])'''),
      *optional_hf("Generate text with a real (tiny) GPT-style model. To instead use the OpenAI/Groq API, set your key in the marked spot &mdash; never commit keys.",
'''try:
    from transformers import pipeline, set_seed
    set_seed(0)
    gen = pipeline("text-generation", model="sshleifer/tiny-gpt2")
    print(gen("The future of AI is", max_new_tokens=15)[0]["generated_text"])
except Exception as e:
    print("Optional real-model demo skipped (the graded cells above already covered this).")
    print("  reason:", type(e).__name__, "--", e)

# --- OPTIONAL: real GPT API (needs your own key; not graded) ---
# import os; from openai import OpenAI
# client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))   # set OPENAI_API_KEY yourself
# print(client.chat.completions.create(model="gpt-4o-mini",
#       messages=[{"role":"user","content":"Write one sentence about transformers."}]).choices[0].message.content)'''),
      footer(10, "Greedy + temperature are the decoding knobs behind every chat model. You now understand what 'temperature' on the GPT API actually does."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-feature-extraction-head", "Advanced",
     "Feature Extraction + a Classifier Head", 40,
     "Use a model as a feature extractor, then train a small classifier head on top -- the essence of transfer learning.",
     ["Feature extraction", "Classifier head", "Transfer learning"])
def _l11(sol):
    return [
      header(11, "Feature Extraction + a Classifier Head", "Advanced", 40,
        ["Turn text into feature vectors (embeddings)",
         "Train a lightweight classifier head on those features",
         "Predict sentiment on unseen sentences"],
        "The model landscape"),
      setup(11),
      md('''## Concept
A powerful pattern: let a model turn text into **features**, then train a small **head** on top for
your task &mdash; **transfer learning** (the heart of Module 4). We use TF-IDF as an offline stand-in
for transformer embeddings, then fit a logistic-regression head for sentiment.

> Needs `scikit-learn`.'''),
      code('''# DEMO -- a tiny labelled sentiment set (1 = positive, 0 = negative)
TRAIN = [("i love this movie", 1), ("what a great film", 1), ("wonderful and amazing", 1),
         ("brilliant acting throughout", 1), ("i hate this movie", 0), ("what an awful film", 0),
         ("terrible and boring", 0), ("bad acting throughout", 0)]
print("examples:", len(TRAIN))'''),
      md('''## Your Turn
Fit the classifier **head** on the features, and implement **predict** for new text.'''),
      code(render([
        "from sklearn.feature_extraction.text import TfidfVectorizer",
        "from sklearn.linear_model import LogisticRegression",
        'TRAIN = [("i love this movie", 1), ("what a great film", 1), ("wonderful and amazing", 1),',
        '         ("brilliant acting throughout", 1), ("i hate this movie", 0), ("what an awful film", 0),',
        '         ("terrible and boring", 0), ("bad acting throughout", 0)]',
        "texts = [t for t, _ in TRAIN]; labels = [y for _, y in TRAIN]",
        "vec = TfidfVectorizer().fit(texts)            # the 'feature extractor'",
        "X = vec.transform(texts)",
        "",
        "def train_head():",
        {"s": '    return ___   # TODO: LogisticRegression().fit(X, labels)',
         "a": '    return LogisticRegression().fit(X, labels)'},
        "",
        "clf = train_head()",
        "def predict(text):",
        {"s": '    return int(___)   # TODO: clf.predict(vec.transform([text]))[0]',
         "a": '    return int(clf.predict(vec.transform([text]))[0])'},
        "",
        "try:",
        "    for s in ['i love it', 'absolutely terrible']: print(predict(s), '<-', s)",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("head fits and exposes predict", lambda: hasattr(train_head(), "predict"))
expect_true("positive sentence -> 1", lambda: predict("i love this great film") == 1)
expect_true("negative sentence -> 0", lambda: predict("an awful and terrible movie") == 0)'''),
      *optional_hf("Use a real transformer as the feature extractor (embeddings) instead of TF-IDF.",
'''try:
    from transformers import pipeline
    fx = pipeline("feature-extraction", model="prajjwal1/bert-tiny")
    vecs = fx("transformers turn text into vectors")
    import numpy as np
    print("embedding shape (tokens x dims):", np.array(vecs[0]).shape)
except Exception as e:
    print("Optional real-model demo skipped (the graded cells above already covered this).")
    print("  reason:", type(e).__name__, "--", e)'''),
      footer(11, "Features from a big model + a tiny trained head = transfer learning. Module 4 does exactly this, fine-tuning a real BERT for sentiment."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-capstone-mini-transformer", "Advanced",
     "Capstone: A Mini Transformer Pipeline", 45,
     "Assemble the whole Module-3 toolkit -- tokenize, embed, add positions, self-attend, pool -- into one pipeline.",
     ["End-to-end pipeline", "Self-attention", "Sequence pooling"])
def _l12(sol):
    return [
      header(12, "Capstone: A Mini Transformer Pipeline", "Advanced", 45,
        ["Chain tokenize -> embed -> positional-encode -> self-attend -> pool",
         "Produce a single vector that represents a whole sentence",
         "Confirm different sentences get different representations"],
        "The transformer block"),
      setup(12),
      md('''## Concept &mdash; the module's payoff
Everything you built now snaps together into a **mini transformer encoder**: tokenize a sentence,
look up **embeddings**, add **positional encodings**, run **self-attention**, and **mean-pool** the
result into one sentence vector &mdash; the representation a classifier or search index would use.'''),
      code('''# DEMO -- the shared pieces (given)
import numpy as np
def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True); e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)
def positional_encoding(seq_len, d):
    pos = np.arange(seq_len)[:, None]; i = np.arange(d)[None, :]
    ang = pos / np.power(10000, (2 * (i // 2)) / d)
    pe = np.zeros((seq_len, d)); pe[:, 0::2] = np.sin(ang[:, 0::2]); pe[:, 1::2] = np.cos(ang[:, 1::2])
    return pe
rng = np.random.default_rng(0)
VOCAB = {w: i for i, w in enumerate("the cat sat on mat dog ran fast".split())}
TABLE = rng.normal(size=(len(VOCAB), 4))   # an embedding per vocab word, d=4
print("vocab:", VOCAB)'''),
      md('''## Your Turn
Complete the four pipeline steps.'''),
      code(render([
        "import numpy as np",
        "def embed(tokens):",
        {"s": '    return np.array([___ for t in tokens])   # TODO: look up TABLE[VOCAB[t]]',
         "a": '    return np.array([TABLE[VOCAB[t]] for t in tokens])'},
        "",
        "def encode_sentence(sentence):",
        "    tokens = sentence.split()",
        "    X = embed(tokens)",
        "    d = X.shape[-1]",
        {"s": '    X = X + ___   # TODO: add positional_encoding(len(tokens), d)',
         "a": '    X = X + positional_encoding(len(tokens), d)'},
        {"s": '    A = ___   # TODO: softmax(X @ X^T / sqrt(d), axis=-1)',
         "a": '    A = softmax(X @ X.T / np.sqrt(d), axis=-1)'},
        "    context = A @ X",
        {"s": '    return ___   # TODO: mean-pool the context over the tokens (axis=0)',
         "a": '    return context.mean(axis=0)'},
        "",
        "try:",
        "    v = encode_sentence('the cat ran')",
        "    print('sentence vector (dim', len(v), '):', np.round(v, 3))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''import numpy as np
expect_true("embed returns one row per token", lambda: embed(["the", "cat"]).shape == (2, 4))
expect_true("encode_sentence returns a single d-dim vector", lambda: encode_sentence("the cat ran").shape == (4,))
expect_true("the pipeline is deterministic", lambda: np.allclose(encode_sentence("the cat ran"), encode_sentence("the cat ran")))
expect_true("different sentences -> different vectors", lambda: not np.allclose(encode_sentence("the cat ran"), encode_sentence("the dog sat")))'''),
      *optional_hf("Compare your hand-built sentence vector to a real transformer's sentence embedding.",
'''try:
    from transformers import pipeline
    import numpy as np
    fx = pipeline("feature-extraction", model="prajjwal1/bert-tiny")
    emb = np.array(fx("the cat ran")[0]).mean(axis=0)
    print("real transformer sentence vector dim:", emb.shape)
except Exception as e:
    print("Optional real-model demo skipped (the graded cells above already covered this).")
    print("  reason:", type(e).__name__, "--", e)'''),
      footer(12, "You built a working transformer encoder from parts you wrote yourself. Day 2 Module 4 takes the real, pretrained versions and fine-tunes them. That completes Module 3."),
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
