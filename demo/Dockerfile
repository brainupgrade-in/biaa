# biaa demo app — self-contained FastAPI service (chat UI + /chat).
# Build context is the REPO ROOT (see docker-compose.yml), so paths are demo/...
FROM python:3.12-slim

WORKDIR /srv

# Install deps first for layer caching.
COPY demo/requirements.txt /srv/demo/requirements.txt
RUN pip install --no-cache-dir -r /srv/demo/requirements.txt

# App code (the agents + UI). No lab notebooks or heavy ML deps needed.
COPY demo/app /srv/demo/app

ENV PYTHONUNBUFFERED=1 PORT=8000
EXPOSE 8000

# GROQ_API_KEY is injected at run time (docker-compose env_file / -e), never baked in.
CMD ["python", "-m", "demo.app"]
