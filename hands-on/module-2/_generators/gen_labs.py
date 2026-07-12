# -*- coding: utf-8 -*-
"""Generator for Day 1 Module 2 hands-on labs (12 notebooks).
Emits STUDENT notebooks to OUT_DIR and SOLUTION notebooks to SOL_DIR."""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_HERE)
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else _MODULE_DIR
SOL_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT_DIR, "solutions")
os.makedirs(OUT_DIR, exist_ok=True)
if SOL_DIR: os.makedirs(SOL_DIR, exist_ok=True)

DECK = "../../presentation/day1-module2-introduction-to-deep-learning.html"
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
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"   # quiet TensorFlow logs (used in the advanced labs)
WORK = os.path.join(os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp", "biaa-lab-02-{nn:02d}")
os.makedirs(WORK, exist_ok=True)
print("Working dir:", WORK){extra}''')

def header(nn, title, level, mins, goals, concept_slide):
    badge = {"Beginner": "Beginner", "Intermediate": "Intermediate", "Advanced": "Advanced"}[level]
    g = "\n".join(f"- {x}" for x in goals)
    return md(f'''# Lab 2.{nn} &mdash; {title}

**Level:** {badge} &nbsp;|&nbsp; **Est. time:** {mins} min &nbsp;|&nbsp; **Day 1 &middot; Module 2 &mdash; Introduction to Deep Learning**

### What you'll do
{g}

> **How this lab works (experiential flow):** read the **Concept**, run the **Demo** to see it work, then complete **Your Turn** by replacing every `___` placeholder. Run the **grader** cell at the end &mdash; it prints `[PASS]` / `[FAIL]` / `[TODO]` and a final `Score`. Aim for a full score.

**Reference:** [Module 2 slides &mdash; {concept_slide}]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE}) &nbsp;&middot;&nbsp; [All Module 2 labs](./index.html)''')

def footer(nn, nxt):
    return md(f'''---
### Key takeaway
{nxt}

[&#8592; All Module 2 labs](./index.html) &nbsp;&middot;&nbsp; [Module 2 slides]({DECK}) &nbsp;&middot;&nbsp; [Course outline]({OUTLINE})

<sub>&copy; 2026 Gheware DevOps &amp; Agentic AI &middot; Building Intelligent AI Agents &middot; devops.gheware.com &middot; Trainer: Rajesh Gheware</sub>''')

# Shared Keras image-data loader (MNIST with offline digits fallback) -- inlined into advanced labs.
LOADER = '''# Data loader: real MNIST in the sandbox, sklearn digits as an offline fallback.
import numpy as np
def load_image_data(n_train=12000, n_test=2000):
    try:
        from tensorflow.keras.datasets import mnist
        (xtr, ytr), (xte, yte) = mnist.load_data()
        xtr = xtr.reshape(len(xtr), -1).astype("float32") / 255.0
        xte = xte.reshape(len(xte), -1).astype("float32") / 255.0
        name, side = "MNIST (28x28)", 28
    except Exception:
        from sklearn.datasets import load_digits
        d = load_digits(); X = (d.data / 16.0).astype("float32"); y = d.target
        xtr, ytr, xte, yte = X[:1400], y[:1400], X[1400:], y[1400:]
        name, side = "sklearn digits (8x8, offline fallback)", 8
    return (xtr[:n_train], ytr[:n_train]), (xte[:n_test], yte[:n_test]), name, side, xtr.shape[1]'''

NB = {}

def lab(nn, slug, level, title, mins, summary, concepts):
    def deco(fn):
        NB[nn] = dict(slug=slug, level=level, title=title, mins=mins,
                      summary=summary, concepts=concepts, build=fn)
        return fn
    return deco

# ============================================================ LAB 01
@lab(1, "lab-01-artificial-neuron", "Beginner",
     "The Artificial Neuron", 20,
     "Build a single artificial neuron in NumPy: a weighted sum of inputs, a bias, and an activation.",
     ["Weights & bias", "Weighted sum", "Activation"])
def _l1(sol):
    return [
      header(1, "The Artificial Neuron", "Beginner", 20,
        ["Understand a neuron = weighted sum of inputs + bias, passed through an activation",
         "Implement the weighted sum with NumPy",
         "Combine it with an activation to get the neuron's output"],
        "The artificial neuron"),
      setup(1),
      md('''## Concept
The building block of every neural network is one **neuron**:
`output = activation(w1*x1 + w2*x2 + ... + bias)`. The **weights** say how much each input
matters; the **bias** shifts the result; the **activation** adds the non-linearity.'''),
      code('''# DEMO -- a neuron with fixed weights, by hand
import numpy as np
def sigmoid(z): return 1.0 / (1.0 + np.exp(-z))
x = np.array([1.0, 0.0])          # two inputs
w = np.array([0.6, 0.9])          # one weight per input
b = -0.2
z = np.dot(w, x) + b              # weighted sum + bias
print("weighted sum z =", z, "-> activation =", round(float(sigmoid(z)), 3))'''),
      md('''## Your Turn
Implement the **weighted sum** and the full **neuron** (weighted sum -> sigmoid).'''),
      code(render([
        "import numpy as np",
        "def sigmoid(z): return 1.0 / (1.0 + np.exp(-z))",
        "",
        "def weighted_sum(x, w, b):",
        {"s": '    return ___   # TODO: w . x + b   (use np.dot)',
         "a": '    return np.dot(w, x) + b'},
        "",
        "def neuron(x, w, b):",
        {"s": '    return ___   # TODO: sigmoid of the weighted sum',
         "a": '    return sigmoid(weighted_sum(x, w, b))'},
        "",
        "x = np.array([1.0, 1.0]); w = np.array([0.5, 0.5]); b = 0.0",
        "try: print('neuron output:', round(float(neuron(x, w, b)), 3))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''import numpy as np
expect_true("weighted_sum([1,1],[0.5,0.5],0) == 1.0", lambda: abs(weighted_sum(np.array([1.0,1.0]), np.array([0.5,0.5]), 0.0) - 1.0) < 1e-9)
expect_true("weighted_sum applies the bias", lambda: abs(weighted_sum(np.array([1.0,0.0]), np.array([2.0,2.0]), -0.5) - 1.5) < 1e-9)
expect_true("neuron(0 weighted sum) == 0.5", lambda: abs(neuron(np.array([0.0,0.0]), np.array([1.0,1.0]), 0.0) - 0.5) < 1e-9)'''),
      footer(1, "Stack many of these neurons into layers and you have a **neural network**. Next we look at the activations that give them their power."),
    ]

# ============================================================ LAB 02
@lab(2, "lab-02-activation-functions", "Beginner",
     "Activation Functions", 20,
     "Implement and compare the three classic activations -- sigmoid, ReLU and tanh.",
     ["Sigmoid", "ReLU", "tanh", "Non-linearity"])
def _l2(sol):
    return [
      header(2, "Activation Functions", "Beginner", 20,
        ["Implement sigmoid, ReLU and tanh in NumPy",
         "See how each squashes or clips its input",
         "Understand why non-linear activations matter"],
        "Activation functions"),
      setup(2),
      md('''## Concept
Without a non-linear **activation**, stacking layers just gives another straight line. The classics:
- **sigmoid**: squashes to (0, 1)
- **ReLU**: `max(0, z)` -- keeps positives, zeroes negatives (the workhorse of deep nets)
- **tanh**: squashes to (-1, 1)'''),
      code('''# DEMO
import numpy as np
z = np.array([-2.0, -0.5, 0.0, 0.5, 2.0])
print("input :", z)
print("relu  :", np.maximum(0, z))'''),
      md('''## Your Turn
Implement all three. Use `np.exp`, `np.maximum`, `np.tanh`.'''),
      code(render([
        "import numpy as np",
        "def sigmoid(z):",
        {"s": '    return ___   # TODO: 1 / (1 + e^-z)',
         "a": '    return 1.0 / (1.0 + np.exp(-z))'},
        "def relu(z):",
        {"s": '    return ___   # TODO: max(0, z), elementwise',
         "a": '    return np.maximum(0, z)'},
        "def tanh(z):",
        {"s": '    return ___   # TODO: the hyperbolic tangent',
         "a": '    return np.tanh(z)'},
        "",
        "z = np.array([-2.0, 0.0, 2.0])",
        "try: print('sigmoid', sigmoid(z)); print('relu', relu(z)); print('tanh', tanh(z))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''import numpy as np
expect_true("sigmoid(0) == 0.5", lambda: abs(float(sigmoid(np.array([0.0]))[0]) - 0.5) < 1e-9)
expect_true("sigmoid saturates to ~1 for large z", lambda: float(sigmoid(np.array([10.0]))[0]) > 0.99)
expect_true("relu(-3) == 0 and relu(2) == 2", lambda: float(relu(np.array([-3.0]))[0]) == 0.0 and float(relu(np.array([2.0]))[0]) == 2.0)
expect_true("tanh(0) == 0", lambda: abs(float(tanh(np.array([0.0]))[0])) < 1e-9)'''),
      footer(2, "ReLU is the default in modern deep learning -- simple and fast. These non-linearities are what let networks model curves, not just lines."),
    ]

# ============================================================ LAB 03
@lab(3, "lab-03-loss-mse", "Beginner",
     "Loss: Measuring How Wrong", 20,
     "Implement mean squared error -- the number a network tries to shrink during training.",
     ["Loss function", "Mean squared error", "Lower = better"])
def _l3(sol):
    return [
      header(3, "Loss: Measuring How Wrong", "Beginner", 20,
        ["Understand loss as a single number for 'how wrong' the model is",
         "Implement mean squared error (MSE) in NumPy",
         "Confirm a better prediction gives a lower loss"],
        "What 'learning' means: loss"),
      setup(3),
      md('''## Concept
Training needs a score to minimise: the **loss**. **Mean Squared Error** averages the squared
gaps between predictions and truth: `MSE = mean((y_true - y_pred)^2)`. Perfect prediction -> 0;
the worse the guesses, the bigger the loss.'''),
      code('''# DEMO
import numpy as np
y_true = np.array([3.0, 5.0, 2.0])
good   = np.array([3.0, 4.5, 2.0])
print("squared errors (good):", (y_true - good) ** 2)'''),
      md('''## Your Turn
Implement `mse`, then compare a good vs a poor prediction.'''),
      code(render([
        "import numpy as np",
        "def mse(y_true, y_pred):",
        {"s": '    return ___   # TODO: mean of (y_true - y_pred) squared',
         "a": '    return np.mean((y_true - y_pred) ** 2)'},
        "",
        "y_true = np.array([3.0, 5.0, 2.0])",
        "good   = np.array([3.0, 4.5, 2.0])",
        "poor   = np.array([0.0, 0.0, 0.0])",
        "try: print('good loss:', mse(y_true, good), '| poor loss:', mse(y_true, poor))",
        "except Exception as e: print('Fill the blank, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''import numpy as np
expect_true("perfect prediction -> loss 0", lambda: mse(np.array([1.0,2.0]), np.array([1.0,2.0])) == 0.0)
expect_true("MSE of [3,5,2] vs [3,4.5,2] == 0.0833...", lambda: abs(float(mse(np.array([3.0,5.0,2.0]), np.array([3.0,4.5,2.0]))) - 0.25/3) < 1e-6)
expect_true("a better prediction has lower loss", lambda: mse(np.array([3.0,5.0,2.0]), np.array([3.0,4.5,2.0])) < mse(np.array([3.0,5.0,2.0]), np.array([0.0,0.0,0.0])))'''),
      footer(3, "Loss turns 'how good is this model?' into one number a computer can minimise. Next: how it actually shrinks that number -- gradient descent."),
    ]

# ============================================================ LAB 04
@lab(4, "lab-04-gradient-descent", "Beginner",
     "Gradient Descent by Hand", 25,
     "Walk downhill to a function's minimum, and watch how the learning rate changes the journey.",
     ["Gradient", "Descent step", "Learning rate"])
def _l4(sol):
    return [
      header(4, "Gradient Descent by Hand", "Beginner", 25,
        ["Understand gradient descent as 'repeatedly step downhill'",
         "Implement the gradient and the update step",
         "See how the learning rate speeds up or destabilises learning"],
        "Gradient descent"),
      setup(4),
      md('''## Concept
To minimise a function we **step downhill**: repeatedly move in the opposite direction of the
**gradient** (slope). The step size is the **learning rate**. We minimise `f(x) = (x - 3)^2`,
whose minimum is at `x = 3` and whose gradient is `2*(x - 3)`.'''),
      code('''# DEMO -- one step downhill from x = 0
def f(x): return (x - 3) ** 2
x = 0.0
grad = 2 * (x - 3)          # slope at x = 0  -> -6 (downhill is to the right)
x = x - 0.1 * grad          # take a step
print("after one step, x =", round(x, 3), "f(x) =", round(f(x), 3))'''),
      md('''## Your Turn
Implement the **gradient** and the **update step**, then run descent.'''),
      code(render([
        "def grad(x):",
        {"s": '    return ___   # TODO: derivative of (x-3)^2  =  2*(x-3)',
         "a": '    return 2 * (x - 3)'},
        "",
        "def descend(x0=0.0, lr=0.1, steps=60):",
        "    x = x0",
        "    for _ in range(steps):",
        {"s": '        x = ___   # TODO: step downhill: x - lr * grad(x)',
         "a": '        x = x - lr * grad(x)'},
        "    return x",
        "",
        "try: print('converged to x =', round(descend(), 4))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("gradient is zero at the minimum (x=3)", lambda: grad(3) == 0)
expect_true("descent converges near x = 3", lambda: abs(descend() - 3) < 0.05)
expect_true("a tiny learning rate moves slowly (not there in 5 steps)", lambda: abs(descend(lr=0.001, steps=5) - 3) > 1.0)'''),
      footer(4, "Every neural network trains this way: compute the gradient of the loss, step downhill, repeat. The learning rate is the single most important knob."),
    ]

# ============================================================ LAB 05
@lab(5, "lab-05-single-neuron-learns", "Beginner",
     "A Single Neuron Learns", 25,
     "Train one linear neuron with gradient descent to fit a line, tracking the loss as it falls.",
     ["Training loop", "Gradient update", "Loss tracking"])
def _l5(sol):
    return [
      header(5, "A Single Neuron Learns", "Beginner", 25,
        ["Put loss + gradient descent together into a training loop",
         "Train a linear neuron to discover the rule y = 2x",
         "Track the loss falling epoch by epoch"],
        "The training loop"),
      setup(5),
      md('''## Concept
Now we **train**. A linear neuron `pred = w * x` should learn `y = 2x` from data. Each epoch:
predict, measure MSE, compute the gradient of the loss w.r.t. `w`, and nudge `w` downhill. The
gradient of the MSE here is `mean(2 * (pred - y) * x)`.'''),
      code('''# DEMO -- the data
import numpy as np
X = np.array([0, 1, 2, 3, 4], dtype=float)
Y = 2 * X    # the hidden rule the neuron must discover
print("X:", X, "  Y:", Y)'''),
      md('''## Your Turn
Fill in the **gradient** and the **weight update**. Watch `w` head toward 2 and the loss toward 0.'''),
      code(render([
        "import numpy as np",
        "X = np.array([0, 1, 2, 3, 4], dtype=float); Y = 2 * X",
        "",
        "def train(lr=0.02, epochs=400):",
        "    w = 0.0; history = []",
        "    for _ in range(epochs):",
        "        pred = w * X",
        "        loss = np.mean((pred - Y) ** 2); history.append(loss)",
        {"s": '        gradient = ___   # TODO: mean(2 * (pred - Y) * X)',
         "a": '        gradient = np.mean(2 * (pred - Y) * X)'},
        {"s": '        w = ___          # TODO: step downhill: w - lr * gradient',
         "a": '        w = w - lr * gradient'},
        "    return w, history",
        "",
        "try:",
        "    w, hist = train()",
        "    print('learned w =', round(w, 3), '| first loss', round(hist[0],2), '-> last loss', round(hist[-1],4))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("the neuron learned w ~= 2", lambda: abs(train()[0] - 2.0) < 0.1)
expect_true("loss decreased over training", lambda: train()[1][-1] < train()[1][0])
expect_true("final loss is near zero", lambda: train()[1][-1] < 0.01)'''),
      footer(5, "That is the whole of learning: predict, measure loss, step downhill, repeat. Next, let's *look* at the loss curve this produced."),
    ]

# ============================================================ LAB 06
@lab(6, "lab-06-reading-training-curve", "Beginner",
     "Reading a Training Curve", 25,
     "Plot loss over epochs and learn to read what the curve is telling you about training.",
     ["Training curve", "Convergence", "Plotting with matplotlib"])
def _l6(sol):
    return [
      header(6, "Reading a Training Curve", "Beginner", 25,
        ["Record a model's loss at every epoch",
         "Plot the training curve with matplotlib",
         "Read the curve: is it still improving, or has it converged?"],
        "Overfitting & the training curve"),
      setup(6),
      md('''## Concept
A **training curve** plots loss against epoch. A healthy run falls steeply, then flattens as it
**converges**. Reading it tells you whether to train longer, stop, or change the learning rate.

> Needs `matplotlib` (`pip install matplotlib`).'''),
      code('''# DEMO -- produce a loss history by training a linear neuron
import numpy as np
X = np.array([0,1,2,3,4], dtype=float); Y = 2 * X
def run_training(lr=0.02, epochs=300):
    w = 0.0; history = []
    for _ in range(epochs):
        pred = w * X
        history.append(float(np.mean((pred - Y) ** 2)))
        w -= lr * np.mean(2 * (pred - Y) * X)
    return history
history = run_training()
print("epochs:", len(history), "| first loss:", round(history[0],2), "| last:", round(history[-1],5))'''),
      md('''## Your Turn
Read three things off the `history`, then plot it.'''),
      code(render([
        "start_loss = history[0]",
        {"s": 'final_loss = ___          # TODO: the LAST value in history',
         "a": 'final_loss = history[-1]'},
        {"s": 'total_improvement = ___   # TODO: start_loss - final_loss',
         "a": 'total_improvement = start_loss - final_loss'},
        {"s": 'still_improving = ___      # TODO: is the last loss still below the one before it?',
         "a": 'still_improving = history[-1] < history[-2]'},
        "",
        "try:",
        "    import matplotlib.pyplot as plt",
        "    plt.plot(history); plt.xlabel('epoch'); plt.ylabel('loss (MSE)')",
        "    plt.title('Training curve'); plt.tight_layout()",
        "    plt.savefig(WORK + '/training_curve.png', dpi=90); plt.show()",
        "    print('saved:', WORK + '/training_curve.png')",
        "except Exception as e:",
        "    print('Plot needs matplotlib + the blanks filled.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("final_loss is the last point", lambda: final_loss == history[-1])
expect_true("total_improvement = start - final (and positive)", lambda: abs(total_improvement - (history[0]-history[-1])) < 1e-9 and total_improvement > 0)
expect_true("still_improving is a bool", lambda: isinstance(still_improving, bool))'''),
      footer(6, "You can now read a training curve at a glance. The same plot, with a *second* (validation) line, reveals overfitting -- the Intermediate labs."),
    ]

# ============================================================ LAB 07
@lab(7, "lab-07-two-layer-net-from-scratch", "Intermediate",
     "A 2-Layer Neural Net from Scratch", 40,
     "Build a hidden-layer network in pure NumPy -- forward pass and the weight updates -- and train it on a curved dataset.",
     ["Hidden layer", "Forward pass", "Backpropagation (applied)"])
def _l7(sol):
    return [
      header(7, "A 2-Layer Neural Net from Scratch", "Intermediate", 40,
        ["Assemble a 2-layer network (hidden + output) in NumPy",
         "Implement the forward pass through both layers",
         "Apply the gradient-descent weight updates and watch it learn a non-linear boundary"],
        "Backpropagation, intuitively"),
      setup(7),
      md('''## Concept
One neuron can only draw a straight line. A **hidden layer** lets the network bend the boundary.
We classify `make_moons` (two interleaving crescents) with a 2 -> 16 -> 1 network: ReLU hidden
layer, sigmoid output. The gradients (backprop) are given; you wire the **forward pass** and the
**updates**.

> Needs `scikit-learn`.'''),
      code('''# DEMO -- the curved dataset
import numpy as np
from sklearn.datasets import make_moons
X, y = make_moons(n_samples=400, noise=0.2, random_state=0)
y = y.reshape(-1, 1)
print("X shape:", X.shape, "| classes:", np.unique(y))'''),
      code('''# DEMO -- visualise the input: two interleaving crescents
try:
    import matplotlib.pyplot as plt
    c = y.ravel()
    plt.scatter(X[c == 0, 0], X[c == 0, 1], s=20, label="class 0")
    plt.scatter(X[c == 1, 0], X[c == 1, 1], s=20, label="class 1")
    plt.xlabel("feature 1  (X[:,0])"); plt.ylabel("feature 2  (X[:,1])")
    plt.title("make_moons input -- no straight line separates them")
    plt.legend(); plt.tight_layout()
    plt.savefig(WORK + "/moons_input.png", dpi=90); plt.show()
    print("saved:", WORK + "/moons_input.png")
except Exception as e:
    print("Plot needs matplotlib (pip install matplotlib).", type(e).__name__)'''),
      md('''## Your Turn
Complete the forward pass (hidden activation + output activation) and the four weight updates.'''),
      code(render([
        "import numpy as np",
        "from sklearn.datasets import make_moons",
        "",
        "def relu(z): return np.maximum(0, z)",
        "def sigmoid(z): return 1.0 / (1.0 + np.exp(-z))",
        "",
        "def train_net(epochs=5000, lr=0.3):",
        "    X, y = make_moons(n_samples=400, noise=0.2, random_state=0); y = y.reshape(-1, 1)",
        "    rng = np.random.default_rng(0)",
        "    W1 = rng.normal(scale=0.7, size=(2, 16)); b1 = np.zeros((1, 16))",
        "    W2 = rng.normal(scale=0.7, size=(16, 1)); b2 = np.zeros((1, 1))",
        "    history = []",
        "    for _ in range(epochs):",
        "        # ---- forward pass ----",
        "        z1 = X @ W1 + b1",
        {"s": '        a1 = ___          # TODO: ReLU of z1',
         "a": '        a1 = relu(z1)'},
        "        z2 = a1 @ W2 + b2",
        {"s": '        a2 = ___          # TODO: sigmoid of z2 (the prediction)',
         "a": '        a2 = sigmoid(z2)'},
        "        history.append(float(np.mean((a2 - y) ** 2)))   # track the loss each epoch",
        "        # ---- backward pass (gradients given) ----",
        "        dz2 = (a2 - y) / len(X)",
        "        dW2 = a1.T @ dz2; db2 = dz2.sum(0, keepdims=True)",
        "        dz1 = (dz2 @ W2.T) * (z1 > 0)",
        "        dW1 = X.T @ dz1; db1 = dz1.sum(0, keepdims=True)",
        "        # ---- updates ----",
        {"s": '        W2 = ___; b2 = b2 - lr * db2   # TODO: W2 - lr * dW2',
         "a": '        W2 = W2 - lr * dW2; b2 = b2 - lr * db2'},
        {"s": '        W1 = ___; b1 = b1 - lr * db1   # TODO: W1 - lr * dW1',
         "a": '        W1 = W1 - lr * dW1; b1 = b1 - lr * db1'},
        "    preds = (sigmoid(relu(X @ W1 + b1) @ W2 + b2) > 0.5).astype(int)",
        "    acc = float((preds == y).mean())",
        "    return acc, (W1, b1, W2, b2), history   # accuracy + trained weights + loss curve",
        "",
        "try: print('train accuracy:', round(train_net()[0], 3))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      code('''# DEMO -- visualise what your network learned: decision boundary + loss curve
try:
    import numpy as np, matplotlib.pyplot as plt
    acc, (W1, b1, W2, b2), history = train_net()          # uses YOUR filled-in train_net
    Xv, yv = make_moons(n_samples=400, noise=0.2, random_state=0)
    def predict(P): return (sigmoid(relu(P @ W1 + b1) @ W2 + b2) > 0.5).astype(int).ravel()
    xx, yy = np.meshgrid(np.linspace(Xv[:, 0].min() - .5, Xv[:, 0].max() + .5, 200),
                         np.linspace(Xv[:, 1].min() - .5, Xv[:, 1].max() + .5, 200))
    Z = predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    ax1.contourf(xx, yy, Z, alpha=0.25, cmap="coolwarm")   # the net's prediction everywhere
    ax1.scatter(Xv[yv == 0, 0], Xv[yv == 0, 1], s=15, label="class 0")
    ax1.scatter(Xv[yv == 1, 0], Xv[yv == 1, 1], s=15, label="class 1")
    ax1.set_title(f"Decision boundary it learned (acc = {acc:.2f})")
    ax1.set_xlabel("feature 1"); ax1.set_ylabel("feature 2"); ax1.legend()
    ax2.plot(history)                                      # the epoch loop, made visible
    ax2.set_title("Training loss vs epoch"); ax2.set_xlabel("epoch"); ax2.set_ylabel("loss (MSE)")
    ax2.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(WORK + "/decision_boundary.png", dpi=90); plt.show()
    print("saved:", WORK + "/decision_boundary.png")
except Exception as e:
    print("Fill the blanks above (and install matplotlib), then re-run.", type(e).__name__)'''),
      grader('''expect_true("the 2-layer net trains and returns accuracy", lambda: 0.0 < train_net()[0] <= 1.0)
expect_true("accuracy >= 0.90 (it learned the curved boundary)", lambda: train_net()[0] >= 0.90)'''),
      footer(7, "You just built and trained a real neural network from first principles. Frameworks (next labs) automate exactly this forward/backward/update loop."),
    ]

# ============================================================ LAB 08
@lab(8, "lab-08-overfitting-early-stopping", "Intermediate",
     "Overfitting & Early Stopping", 35,
     "Make a network memorise noise, measure the train/validation gap, then stop it early to generalise better.",
     ["Overfitting", "Train/validation gap", "Early stopping"])
def _l8(sol):
    return [
      header(8, "Overfitting & Early Stopping", "Intermediate", 35,
        ["Measure the gap between training and validation accuracy",
         "See a high-capacity network memorise noisy training data",
         "Use early stopping to halt before it overfits"],
        "Fighting overfitting"),
      setup(8),
      md('''## Concept
A network with too much capacity **memorises** the training data -- including its noise -- and
fails on new data. The **train/validation gap** exposes it. **Early stopping** halts training
once validation stops improving.

> Needs `scikit-learn`.'''),
      code('''# DEMO -- a small, noisy dataset and a held-out validation set
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
X, y = make_classification(n_samples=400, n_features=20, n_informative=5, flip_y=0.2, random_state=0)
X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.4, random_state=0)
print("train:", len(X_tr), "validation:", len(X_val))'''),
      code('''# DEMO -- visualise the 20-feature input as a 2D PCA projection
try:
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA
    XY = PCA(n_components=2, random_state=0).fit_transform(X)   # 20-D -> 2-D for plotting only
    plt.scatter(XY[y == 0, 0], XY[y == 0, 1], s=20, label="class 0")
    plt.scatter(XY[y == 1, 0], XY[y == 1, 1], s=20, label="class 1")
    plt.xlabel("PCA 1"); plt.ylabel("PCA 2")
    plt.title("make_classification input (20-D, shown in 2-D via PCA)")
    plt.legend(); plt.tight_layout()
    plt.savefig(WORK + "/classification_input.png", dpi=90); plt.show()
    print("saved:", WORK + "/classification_input.png")
except Exception as e:
    print("Plot needs matplotlib (pip install matplotlib).", type(e).__name__)'''),
      md('''## Your Turn
Compute the validation accuracy of an overfit network, and turn **early stopping** on.'''),
      code(render([
        "from sklearn.neural_network import MLPClassifier",
        "from sklearn.metrics import accuracy_score",
        "",
        "# a big network, trained hard -> memorises the training set",
        "big = MLPClassifier(hidden_layer_sizes=(200, 200), max_iter=2000, random_state=0).fit(X_tr, y_tr)",
        "def train_acc(): return accuracy_score(y_tr, big.predict(X_tr))",
        "def val_acc():",
        {"s": '    return ___   # TODO: accuracy of big on the VALIDATION set',
         "a": '    return accuracy_score(y_val, big.predict(X_val))'},
        "def gap(): return train_acc() - val_acc()",
        "",
        "def make_early_stopped():",
        "    clf = MLPClassifier(hidden_layer_sizes=(200, 200), max_iter=500,",
        {"s": '                        early_stopping=___, random_state=0)   # TODO: True',
         "a": '                        early_stopping=True, random_state=0)'},
        "    return clf.fit(X_tr, y_tr)",
        "",
        "try:",
        "    es = make_early_stopped()",
        "    print(f'train={train_acc():.2f} val={val_acc():.2f} gap={gap():.2f} | early-stopped at {es.n_iter_} iters')",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      code('''# DEMO -- visualise the gap: overfit big net vs your early-stopped net
try:
    import numpy as np, matplotlib.pyplot as plt
    es = make_early_stopped()                              # uses YOUR early_stopping choice
    es_train = accuracy_score(y_tr, es.predict(X_tr))
    es_val   = accuracy_score(y_val, es.predict(X_val))
    labels = ["overfit big net", "early-stopped"]
    train_scores = [train_acc(), es_train]
    val_scores   = [val_acc(),   es_val]
    x = np.arange(len(labels)); w = 0.35
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.bar(x - w/2, train_scores, w, label="train accuracy")
    ax.bar(x + w/2, val_scores,   w, label="validation accuracy")
    for i in range(len(labels)):                           # annotate the train/val gap
        ax.annotate(f"gap {train_scores[i]-val_scores[i]:+.2f}",
                    (x[i], max(train_scores[i], val_scores[i]) + 0.02), ha="center")
    ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylim(0, 1.12)
    ax.set_ylabel("accuracy"); ax.set_title("The train/validation gap is overfitting")
    ax.legend(loc="lower right")
    fig.tight_layout(); fig.savefig(WORK + "/overfit_gap.png", dpi=90); plt.show()
    print("saved:", WORK + "/overfit_gap.png")
except Exception as e:
    print("Fill the blanks above (and install matplotlib), then re-run.", type(e).__name__)'''),
      grader('''from sklearn.neural_network import MLPClassifier
expect_true("training accuracy is very high (memorised)", lambda: train_acc() >= 0.95)
expect_true("validation accuracy is clearly lower (the gap)", lambda: gap() > 0.1)
expect_true("early stopping halts before max_iter (500)", lambda: make_early_stopped().n_iter_ < 500)'''),
      footer(8, "More capacity is not always better. The validation gap is your early-warning system; early stopping is one of the cheapest cures."),
    ]

# ============================================================ LAB 09
@lab(9, "lab-09-hyperparameters", "Intermediate",
     "Hyperparameters: Tuning the Network", 35,
     "Sweep hidden-layer size and watch accuracy change -- a first taste of hyperparameter tuning.",
     ["Hyperparameters", "Model capacity", "Experimentation"])
def _l9(sol):
    return [
      header(9, "Hyperparameters: Tuning the Network", "Intermediate", 35,
        ["Identify what a hyperparameter is (you set it; training does not)",
         "Sweep hidden-layer size on a real digit dataset",
         "Observe how capacity affects accuracy"],
        "The learning rate"),
      setup(9),
      md('''## Concept
**Hyperparameters** are the dials *you* choose before training: hidden-layer size, learning rate,
epochs. They are not learned -- you tune them by experiment. Here we sweep the **hidden-layer
size** on the offline 8x8 digits and watch accuracy respond.

> Needs `scikit-learn`.'''),
      code('''# DEMO -- the data and a helper that trains one configuration
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
X, y = load_digits(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0)
def acc_for(hidden):
    clf = MLPClassifier(hidden_layer_sizes=hidden, max_iter=600, random_state=0).fit(X_tr, y_tr)
    return accuracy_score(y_te, clf.predict(X_te))
print("tiny (2,) network accuracy:", round(acc_for((2,)), 3))'''),
      code('''# DEMO -- visualise the input: the first 10 of the 8x8 digit images
try:
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 5, figsize=(6, 2.6))
    for i, ax in enumerate(axes.ravel()):
        ax.imshow(X[i].reshape(8, 8), cmap="gray_r")   # each row is a flattened 8x8 image
        ax.set_title(str(y[i])); ax.axis("off")
    fig.suptitle("load_digits input -- each sample is an 8x8 image")
    fig.tight_layout()
    fig.savefig(WORK + "/digits_input.png", dpi=90); plt.show()
    print("saved:", WORK + "/digits_input.png")
except Exception as e:
    print("Plot needs matplotlib (pip install matplotlib).", type(e).__name__)'''),
      md('''## Your Turn
Choose **three** hidden sizes to compare (include a tiny one and a big one) and run the sweep.'''),
      code(render([
        {"s": 'SIZES = ___   # TODO: a list of 3 hidden-layer tuples, e.g. [(2,), (16,), (64,)]',
         "a": 'SIZES = [(2,), (16,), (64,)]'},
        "",
        "def run_sweep():",
        "    return {h: acc_for(h) for h in SIZES}",
        "",
        "try:",
        "    results = run_sweep()",
        "    for h, a in results.items(): print(f'hidden {h}: accuracy {a:.3f}')",
        "except Exception as e: print('Fill the blank, then re-run.', type(e).__name__)",
      ], sol)),
      code('''# DEMO -- visualise your sweep: accuracy vs hidden-layer size
try:
    import matplotlib.pyplot as plt
    results = run_sweep()                                  # uses YOUR list of SIZES
    if len(results) < 2:                                   # SIZES not filled in yet
        raise ValueError("fill in SIZES above (need >= 2 sizes to compare)")
    labels = [str(h) for h in results]
    scores = list(results.values())
    fig, ax = plt.subplots(figsize=(7, 4.2))
    bars = ax.bar(labels, scores, color="#4f46e5")
    for b, s in zip(bars, scores):                         # label each bar with its accuracy
        ax.annotate(f"{s:.2f}", (b.get_x() + b.get_width()/2, s + 0.02), ha="center")
    ax.set_ylim(0, 1.12); ax.set_xlabel("hidden-layer size"); ax.set_ylabel("test accuracy")
    ax.set_title("More capacity -> higher accuracy (up to a point)")
    fig.tight_layout(); fig.savefig(WORK + "/hp_sweep.png", dpi=90); plt.show()
    print("saved:", WORK + "/hp_sweep.png")
except Exception as e:
    print("Fill the blank above (and install matplotlib), then re-run.", type(e).__name__)'''),
      grader('''expect_true("swept exactly 3 configurations", lambda: len(run_sweep()) == 3)
expect_true("all accuracies are valid fractions", lambda: all(0.0 < a <= 1.0 for a in run_sweep().values()))
expect_true("a bigger hidden layer beats the smallest one", lambda: max(run_sweep().values()) > min(run_sweep().values()) + 0.1)'''),
      footer(9, "Tuning hyperparameters is an experimental loop: change one dial, measure, repeat. Frameworks make running these experiments fast -- which is where we go next."),
    ]

# ============================================================ LAB 10
@lab(10, "lab-10-first-keras-network", "Advanced",
     "Your First Keras Network", 40,
     "Build, compile and train a neural network with Keras -- the real deep-learning toolkit -- on image data.",
     ["Keras Sequential", "compile & fit", "The toolkit"])
def _l10(sol):
    return [
      header(10, "Your First Keras Network", "Advanced", 40,
        ["Build a network with the Keras Sequential API",
         "Compile it with an optimizer and loss, then fit it",
         "Train on real image data and evaluate on a test set"],
        "The deep-learning toolkit"),
      setup(10),
      md('''## Concept
From-scratch NumPy taught you the mechanics; in practice we use a **framework**. **Keras**
(part of TensorFlow) lets you declare layers, `compile` with an optimizer + loss, and `fit`.

> Needs `tensorflow` (`pip install tensorflow-cpu`). **Target dataset: MNIST** (handwritten digits).
> If MNIST cannot download, the loader below falls back to the offline 8x8 digits so the lab still runs.'''),
      code(LOADER + '''

(X_tr, y_tr), (X_te, y_te), DATA_NAME, SIDE, NFEAT = load_image_data()
print("dataset:", DATA_NAME, "| train:", X_tr.shape, "| features:", NFEAT)'''),
      md('''## Your Turn
Add a **hidden layer**, set the **loss**, and **fit** the model.'''),
      code(render([
        "from tensorflow import keras",
        "from tensorflow.keras import layers",
        "",
        "def build_model():",
        "    model = keras.Sequential([",
        "        layers.Input((NFEAT,)),",
        {"s": '        layers.Dense(___, activation=___),   # TODO: 64 units, "relu"',
         "a": '        layers.Dense(64, activation="relu"),'},
        "        layers.Dense(10, activation=\"softmax\"),   # 10 digit classes",
        "    ])",
        {"s": '    model.compile(optimizer="adam", loss=___, metrics=["accuracy"])   # TODO loss',
         "a": '    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])'},
        "    return model",
        "",
        "model = None; test_acc = None",
        "try:",
        "    model = build_model()",
        {"s": '    model.fit(X_tr, y_tr, epochs=___, batch_size=64, verbose=0)   # TODO: ~3 epochs',
         "a": '    model.fit(X_tr, y_tr, epochs=3, batch_size=64, verbose=0)'},
        "    test_acc = float(model.evaluate(X_te, y_te, verbose=0)[1])",
        "    print('test accuracy:', round(test_acc, 3))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("a Keras model was built", lambda: model is not None and hasattr(model, "predict"))
expect_true("test accuracy >= 0.85", lambda: test_acc >= 0.85)'''),
      footer(10, "A few lines of Keras did what dozens of lines of NumPy did -- and scales to far bigger networks. Next: the full MNIST run with training curves."),
    ]

# ============================================================ LAB 11
@lab(11, "lab-11-mnist-classifier", "Advanced",
     "Image Classification on MNIST", 45,
     "Train a neural network to recognise handwritten digits and plot its train vs validation curves.",
     ["MNIST", "Validation split", "Training curves"])
def _l11(sol):
    return [
      header(11, "Image Classification on MNIST", "Advanced", 45,
        ["Train a network to classify handwritten digits (MNIST)",
         "Hold out a validation split and capture the training history",
         "Plot train vs validation curves and reach high accuracy"],
        "The same model, two frameworks"),
      setup(11),
      md('''## Concept
The classic deep-learning 'hello world': **MNIST** handwritten digits. You'll train a network,
keep a **validation split** to watch generalisation, and plot the **training curves**.

> Needs `tensorflow` and `matplotlib`. Target: MNIST; offline fallback to 8x8 digits if needed.'''),
      code(LOADER + '''

(X_tr, y_tr), (X_te, y_te), DATA_NAME, SIDE, NFEAT = load_image_data()
print("dataset:", DATA_NAME, "| train:", X_tr.shape, "| test:", X_te.shape)'''),
      md('''## Your Turn
Set the **validation split** and **epochs**, fit while capturing `history`, then read the final
validation accuracy.'''),
      code(render([
        "from tensorflow import keras",
        "from tensorflow.keras import layers",
        "",
        "def build():",
        "    m = keras.Sequential([layers.Input((NFEAT,)),",
        "                          layers.Dense(128, activation='relu'),",
        "                          layers.Dense(10, activation='softmax')])",
        "    m.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])",
        "    return m",
        "",
        "model = None; history = None; test_acc = None; final_val_acc = None",
        "try:",
        "    model = build()",
        {"s": '    history = model.fit(X_tr, y_tr, validation_split=___, epochs=___,',
         "a": '    history = model.fit(X_tr, y_tr, validation_split=0.2, epochs=8,'},
        "                        batch_size=128, verbose=0)",
        "    test_acc = float(model.evaluate(X_te, y_te, verbose=0)[1])",
        {"s": '    final_val_acc = ___   # TODO: last value of history.history["val_accuracy"]',
         "a": '    final_val_acc = history.history["val_accuracy"][-1]'},
        "    print('test accuracy:', round(test_acc, 3), '| final val accuracy:', round(final_val_acc, 3))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''expect_true("training captured a validation curve", lambda: "val_accuracy" in history.history)
expect_true("test accuracy >= 0.90", lambda: test_acc >= 0.90)
expect_true("final validation accuracy read correctly", lambda: abs(final_val_acc - history.history["val_accuracy"][-1]) < 1e-9)'''),
      md('''## Bonus: plot the training curves (not graded)
Run this to see accuracy and loss for train vs validation across epochs.'''),
      code('''try:
    import matplotlib.pyplot as plt
    h = history.history
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6))
    ax1.plot(h["accuracy"], label="train"); ax1.plot(h["val_accuracy"], label="val")
    ax1.set_title("Accuracy"); ax1.set_xlabel("epoch"); ax1.legend()
    ax2.plot(h["loss"], label="train"); ax2.plot(h["val_loss"], label="val")
    ax2.set_title("Loss"); ax2.set_xlabel("epoch"); ax2.legend()
    plt.tight_layout(); plt.savefig(WORK + "/mnist_curves.png", dpi=90); plt.show()
    print("saved:", WORK + "/mnist_curves.png")
except Exception as e:
    print("Plot needs matplotlib + a trained model.", type(e).__name__)'''),
      footer(11, "You trained a real digit classifier and watched it generalise. Next, the capstone: open the box and *see how it decides*."),
    ]

# ============================================================ LAB 12
@lab(12, "lab-12-visualizing-decisions", "Advanced",
     "Capstone: Visualizing How the Network Decides", 45,
     "Open up a trained digit classifier -- confusion matrix, per-class accuracy, and the digits it gets wrong.",
     ["Confusion matrix", "Per-class accuracy", "Error analysis"])
def _l12(sol):
    return [
      header(12, "Capstone: Visualizing How the Network Decides", "Advanced", 45,
        ["Read a confusion matrix to see which digits get mixed up",
         "Compute per-class accuracy to find the model's weak spots",
         "Surface and view the digits the model gets wrong"],
        "This connects to your labs"),
      setup(12),
      md('''## Concept &mdash; the module's payoff
A single accuracy number hides *how* a model decides. This capstone opens the box: a
**confusion matrix** (which true digit gets predicted as what), **per-class accuracy** (where it
struggles), and a look at the **misclassified** images themselves -- real error analysis.

> Needs `tensorflow`, `scikit-learn`, `matplotlib`. Target: MNIST; offline fallback to digits.'''),
      code(LOADER + '''
from tensorflow import keras
from tensorflow.keras import layers

(X_tr, y_tr), (X_te, y_te), DATA_NAME, SIDE, NFEAT = load_image_data(n_train=10000, n_test=2000)
# train a quick classifier for us to inspect
model = keras.Sequential([layers.Input((NFEAT,)),
                          layers.Dense(64, activation="relu"),
                          layers.Dense(10, activation="softmax")])
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(X_tr, y_tr, epochs=3, batch_size=64, verbose=0)
import numpy as np
preds = model.predict(X_te, verbose=0).argmax(axis=1)
print("trained on", DATA_NAME, "| test samples:", len(y_te))'''),
      md('''## Your Turn
Build the **confusion matrix**, compute **per-class accuracy**, and find the **misclassified** indices.'''),
      code(render([
        "from sklearn.metrics import confusion_matrix",
        "import numpy as np",
        "",
        "def conf_matrix():",
        {"s": '    return ___   # TODO: confusion_matrix(y_te, preds)',
         "a": '    return confusion_matrix(y_te, preds)'},
        "",
        "def per_class_accuracy():",
        "    cm = conf_matrix()",
        {"s": '    return cm.diagonal() / ___   # TODO: divide by each row sum -> cm.sum(axis=1)',
         "a": '    return cm.diagonal() / cm.sum(axis=1)'},
        "",
        "def misclassified_idx():",
        {"s": '    return ___   # TODO: indices where preds != y_te  (np.where(...)[0])',
         "a": '    return np.where(preds != y_te)[0]'},
        "",
        "try:",
        "    pca = per_class_accuracy()",
        "    print('confusion matrix shape:', conf_matrix().shape)",
        "    print('weakest digit:', int(np.argmin(pca)), 'acc', round(float(pca.min()), 3))",
        "    print('misclassified count:', len(misclassified_idx()))",
        "except Exception as e: print('Fill the blanks, then re-run.', type(e).__name__)",
      ], sol)),
      grader('''import numpy as np
expect_true("confusion matrix is 10x10 (ten digit classes)", lambda: conf_matrix().shape == (10, 10))
expect_true("per-class accuracy has 10 values in [0,1]", lambda: len(per_class_accuracy()) == 10 and all(0.0 <= a <= 1.0 for a in per_class_accuracy()))
expect_true("misclassified indices are consistent with accuracy", lambda: abs((1 - len(misclassified_idx())/len(y_te)) - (preds == y_te).mean()) < 1e-9)''')
      ,
      md('''## Bonus: see the mistakes (not graded)
Visualise the confusion matrix and a few digits the model got wrong.'''),
      code('''try:
    import matplotlib.pyplot as plt
    import numpy as np
    cm = conf_matrix(); wrong = misclassified_idx()
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    im = ax[0].imshow(cm, cmap="Blues"); ax[0].set_title("Confusion matrix")
    ax[0].set_xlabel("predicted"); ax[0].set_ylabel("true"); fig.colorbar(im, ax=ax[0])
    if len(wrong):
        i = wrong[0]
        ax[1].imshow(X_te[i].reshape(SIDE, SIDE), cmap="gray_r")
        ax[1].set_title(f"pred {preds[i]} but true {y_te[i]}", color="red")
        ax[1].axis("off")
    plt.tight_layout(); plt.savefig(WORK + "/decisions.png", dpi=90); plt.show()
    print("saved:", WORK + "/decisions.png")
except Exception as e:
    print("Visualisation needs matplotlib + the blanks filled.", type(e).__name__)'''),
      footer(12, "You can now explain not just *how accurate* a model is but *how it decides* and *where it fails* -- the heart of responsible AI (Day 5). That completes Day 1."),
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
        banner = md(f'''> ## SOLUTION / ANSWER KEY &mdash; Lab 2.{nn}
> This is the **completed** notebook (all `___` blanks filled). For the student version, open
> [`../{info['slug']}.ipynb`](../{info['slug']}.ipynb). Trainer use &mdash; or self-check after you've tried it yourself.''')
        sol_cells = [banner] + info["build"](True)
        with open(os.path.join(SOL_DIR, fname), "w") as f:
            json.dump(notebook(sol_cells), f, indent=1, ensure_ascii=False)

print(f"Wrote {len(NB)} notebooks to {OUT_DIR}" + (f" and solutions to {SOL_DIR}" if SOL_DIR else ""))

with open(os.path.join(_HERE, "_meta.json"), "w") as f:
    json.dump({str(nn): {k: NB[nn][k] for k in ("slug","level","title","mins","summary","concepts")}
               for nn in NB}, f, indent=1)
