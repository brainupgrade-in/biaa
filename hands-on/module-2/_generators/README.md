# Module 2 lab generators

The 12 lab notebooks, their answer keys, and the `index.html` landing page in this module are
**generated** from the scripts here. **Do not hand-edit the `.ipynb` files** — your changes will
be overwritten on the next regeneration. Edit the generators instead.

## Files
- `gen_labs.py` — emits the 12 student notebooks to `../lab-*.ipynb` and answer keys to
  `../solutions/lab-*.ipynb`. Each lab is one `@lab(...)`-decorated builder; blanks use the
  `{"s": <student line>, "a": <answer line>}` convention so student/solution stay in lock-step.
  Writes `_meta.json` (here, beside the script) for the index generator.
- `gen_index.py` — reads `_meta.json` and writes `../index.html` (level-grouped lab cards).
- `regenerate.sh` — runs both in order.

## Regenerate
```bash
./regenerate.sh           # or: python3 gen_labs.py && python3 gen_index.py
```
Paths are derived relative to this directory.

## Conventions baked in
- Course prefix `biaa`; each lab works in `/tmp/biaa-lab-02-NN/`.
- Flow per notebook: **Concept → Demo (runnable) → Your Turn (`___` blanks) → auto-grader**.
- Grader prints `[PASS]`/`[FAIL]`/`[TODO]` + `Score: n/total` via `expect()` / `expect_true()`.

## Topic arc (maps to the Module 2 deck — Introduction to Deep Learning)
- Beginner 1–6 (NumPy/matplotlib): the artificial neuron; activation functions; MSE loss;
  gradient descent by hand; a single neuron learns; reading a training curve.
- Intermediate 7–9 (scikit-learn): a 2-layer net from scratch (forward + applied backprop on
  make_moons); overfitting & early stopping; hyperparameter sweep.
- Advanced 10–12 (**Keras / TensorFlow on MNIST**): your first Keras network; the MNIST
  classifier with training curves; visualizing how the network decides (confusion matrix,
  per-class accuracy, misclassified digits).

## Datasets / framework for labs 10–12
Labs 10–12 use **Keras (`tensorflow-cpu`)** and target **real MNIST** via
`keras.datasets.mnist`. The shared `load_image_data()` helper falls back to the offline
`sklearn.datasets.load_digits` (8x8) if MNIST cannot download, so every lab runs with or without
network. Grader accuracy thresholds (0.85 / 0.90) hold on both datasets.

## Verify (graders actually pass)
Generation needs only the Python stdlib. To confirm graders, execute the **solution** notebooks
in a venv with `numpy scikit-learn matplotlib tensorflow-cpu nbconvert ipykernel` and check each
prints a full `Score`. Also run the **student** notebooks top-to-bottom — they must complete
without uncaught errors (blanks land as `[TODO]`). Labs 10–12 train real networks, so execution
takes a little longer.
