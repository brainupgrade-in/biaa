# Codespaces dev container

Opens this course repo in GitHub Codespaces (or VS Code Dev Containers) with the
full `biaa` lab stack ready to go.

## What you get

- **Python 3.12** base + `biaa-venv` with every lab dependency (built by
  `scripts/setup-linux.sh`), registered as the **`biaa`** Jupyter kernel.
- **Node LTS**, **GitHub CLI**, and the **Ollama** runtime (binary only).
- **OpenCode** pre-installed for rapid app-dev prototyping.
- VS Code extensions for Python, Jupyter, React Native, and Expo (auto-installed).
- Forwarded ports: 8888 (Jupyter), 8000 (demo API), 8081/19006 (Expo), 11434 (Ollama).

## Lifecycle (why two scripts)

| Command | Script | When | Cost |
|---------|--------|------|------|
| `onCreateCommand`  | `on-create.sh`  | during **prebuild** (baked into the image) | heavy: venv + deps + OpenCode |
| `postCreateCommand`| `post-create.sh`| every Codespace start | light: `.env` seed + a safety-net rebuild |

Keeping the expensive work in `onCreateCommand` is what makes prebuilds pay off:
without a prebuild, a fresh Codespace runs the full install (a few minutes); with
one, it starts in seconds because the venv is already in the image.

## Turn on prebuilds (one-time, repo Settings)

Prebuilds are enabled in the GitHub UI, not by a file in the repo:

1. Repo **Settings -> Codespaces -> Set up prebuild**.
2. Branch: `main`. Region(s): pick where you deliver.
3. Trigger: *Every push* (or a schedule) so the image tracks dependency changes.
4. Save. GitHub then manages a `Codespaces Prebuilds` workflow under Actions.

After the first prebuild finishes, **Code -> Codespaces** shows a **Prebuild ready**
badge, and new Codespaces boot from the cached image.

> Prebuilds don't run with your Codespaces **secrets**, so `on-create.sh` is
> secret-free by design. Set `GROQ_API_KEY` (and Serper/Wolfram for M6) under
> **Settings -> Codespaces -> Secrets**; they arrive as env vars at start.

## Not using prebuilds?

Everything still works - the first `postCreateCommand` detects a missing
`biaa-venv` and runs the full setup as a fallback. It's just slower on first boot.

## Ollama (Day 3 / Modules 5-6)

The binary is installed; the ~4.9 GB `llama3.1:8b` model is **not** pulled
automatically (it would bloat every prebuild). Pull it on demand:

```bash
bash scripts/pull-ollama-model.sh
```

Days 4-5 use Groq (cloud) and need no local model.
