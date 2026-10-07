# 🌿 TrailLens — Offline AI Nature Explorer

**Phase 1 MVP** · Built for the Hacktoberfest Open-Source AI Challenge, Week 1 — *Touch Grass*.

TrailLens is an outdoor-first AI nature companion. You step outside, photograph
something wild — a tree, flower, leaf, bird, insect, rock — and TrailLens identifies
it, explains it, teaches you three facts, challenges you to do something outdoors,
and awards XP for your journal.

**The AI runs 100% locally.** No cloud APIs. No OpenAI, Gemini, Claude or anything else.

---

## How it works

```
Photo → FastAPI → Ollama (Qwen3-VL 2B, local) → structured JSON → XP → SQLite journal
```

1. **Home** → Start Exploring
2. **Upload / take a photo** (camera capture supported on mobile)
3. **Local AI analysis** — Ollama runs Qwen3-VL 2B on your machine
4. **Identification** — name, category, confidence, beginner-friendly description
5. **Three facts** about your discovery
6. **Outdoor challenge** (prominent card)
7. **XP awarded** (50 base + confidence bonus)
8. **Saved to your journal** (SQLite)

## Tech stack

- **Python** + **FastAPI** + **Uvicorn**
- **Ollama** + **Qwen3-VL 2B** (local open-weight vision model)
- **SQLite** (discoveries, XP, journal)
- **HTML / CSS / vanilla JavaScript** (no frameworks)

## Project structure

```
backend/
  main.py        FastAPI app, API routes, static serving
  ai.py          Ollama + Qwen3-VL integration & structured response parsing
  database.py    SQLite persistence, journal, stats, levels
  xp.py          XP rules
  config.py      paths, model settings, XP tuning
frontend/
  index.html     Home → upload → analysis → result → saved flow
  journal.html   Discovery journal + XP/level stats
  css/styles.css Nature-inspired responsive UI
  js/app.js      Main explore flow
  js/journal.js  Journal rendering
tests/           pytest suite (parsing, XP, API)
data/            SQLite database (created automatically)
uploads/         Photos you analyze
```

## Run it

### 1. Prerequisites (install manually)

- **Python 3.10+**
- **Ollama** — https://ollama.com/download
- The model (1.9 GB, one-time download):

```bash
ollama pull qwen3-vl:2b
```

### 2. Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Start

```bash
# make sure Ollama is running (the Ollama app does this, or:)
ollama serve

# start TrailLens
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Then open **http://127.0.0.1:8000**

### 4. Tests

```bash
python -m pytest
```

## API

| Method | Route | Purpose |
| ------ | ----- | ------- |
| `GET`  | `/api/health` | App + Ollama connectivity |
| `POST` | `/api/analyze` | Upload photo → local AI → structured result |
| `POST` | `/api/discoveries` | Save discovery, award XP |
| `GET`  | `/api/discoveries` | Discovery journal |
| `GET`  | `/api/stats` | XP, level, discovery counts |

## Configuration

All configuration is optional — TrailLens works with the defaults out of the
box and needs **no API keys**. Copy `.env.example` for reference (placeholder
values only) and export the variables in your shell:

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server |
| `OLLAMA_MODEL` | `qwen3-vl:2b` | Local vision model |
| `OLLAMA_TIMEOUT` | `300` | Model timeout (seconds) |
| `TRAILLENS_DB` | `data/trailens.db` | SQLite path |

## AI response schema

```json
{
  "name": "...",
  "category": "...",
  "confidence": "High/Medium/Low",
  "description": "...",
  "facts": ["...", "...", "..."],
  "outdoor_challenge": "..."
}
```

The parser tolerates markdown fences, surrounding prose, nested wrappers and
missing fields — a malformed model reply can never crash a request.

## Local mode vs online demo

TrailLens has two ways to run — **local mode is the default and the point of
the project**:

| | Local mode (default) | Online demo (optional) |
| - | -------------------- | ---------------------- |
| AI | Ollama + Qwen3-VL 2B on **your machine** | Same stack hosted so others can try it |
| Internet | Not needed after setup | Needed to reach the deployment |
| Data | SQLite + photos stay on your disk | Lives on the host |
| Cost | Free | Free tier / your plan |
| Purpose | Daily use, full privacy | Sharing a live demo link |

**Backboard is optional.** Nothing in the codebase depends on it — TrailLens
is a plain FastAPI app that runs anywhere a Python server runs. If you want a
public demo for Hacktoberfest, deploy it on Backboard (or Render, Fly.io, your
own VPS) and point `OLLAMA_URL` at an Ollama instance the host can reach.
Skipping deployment entirely is a perfectly valid Phase 1 outcome.

## Not included (on purpose — Phase 1 only)

No auth, no extra features, no cloud AI — deployment config (Backboard/Render)
is optional and not required to use the app.

## License

MIT — see [LICENSE](LICENSE).

## Contributing

PRs and issue reports are welcome, especially during Hacktoberfest. Read
[AGENTS.md](AGENTS.md) first if you're using an AI coding agent — it lists the
project's hard rules (local AI only, no secrets, keep the stack simple).
