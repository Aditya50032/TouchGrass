# 🌿 TrailLens — Offline AI Nature Explorer

TrailLens is an outdoor-first AI nature companion built for the Hacktoberfest Open-Source AI Challenge, Week 1 — **Touch Grass**.

Take a photo of something you find outside. TrailLens identifies it with **Ollama + Qwen3-VL 2B**, explains it in simple language, gives you three facts, and gives you an outdoor challenge.

> **The screen is not the destination. The screen gives you your next reason to go outside.**

## Why open innovation matters

The core image understanding runs locally through Ollama and the open-weight Qwen3-VL 2B vision model. The local experience can analyze photos without sending them to a closed AI provider, and the model can be swapped or changed by the developer.

## Features

- 📷 Camera-friendly photo upload
- 🧠 Local image understanding with Ollama + Qwen3-VL 2B
- 🌿 Beginner-friendly identification and facts
- 🎯 Outdoor challenges designed to get people exploring
- ⚡ XP and levels
- 📓 SQLite discovery journal
- 🌐 Explicit Demo Mode for hosted deployments

## Architecture

```text
Photo
  ↓
FastAPI
  ↓
Ollama
  ↓
Qwen3-VL 2B
  ↓
Identification + Facts + Outdoor Challenge
  ↓
SQLite Journal + XP
```

## Local setup

Requirements:
- Python 3.10+
- Ollama

Pull the model:

```bash
ollama pull qwen3-vl:2b
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000**.

## Local AI vs online demo

**Local Mode** is the core experience:

```text
Your Mac
  ↓
FastAPI
  ↓
Ollama
  ↓
Qwen3-VL 2B
```

No cloud AI is required for image analysis.

A hosted Render service cannot access the Ollama process running on your Mac. For that reason, the included Render configuration enables an explicitly labelled **Demo Mode** instead of pretending that local Ollama is running remotely.

## Render deployment

The repository includes `render.yaml`.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

The hosted service uses Demo Mode. The real local open-weight AI remains available when TrailLens is run locally with Ollama.

## Repository structure

```text
trail-lens/
├── main.py
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── demo.py
│   ├── ollama.py
│   └── xp.py
├── frontend/
│   ├── index.html
│   ├── journal.html
│   ├── app.js
│   ├── journal.js
│   └── styles.css
├── data/
├── uploads/
├── .env.example
├── .gitignore
├── .python-version
├── render.yaml
├── requirements.txt
└── README.md
```

## License

MIT.
