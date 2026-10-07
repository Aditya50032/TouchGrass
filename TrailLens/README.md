# TrailLens — Offline AI Nature Explorer

TrailLens identifies nature discoveries using **Ollama + Qwen3-VL 2B** running locally. No cloud AI API is used.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen3-vl:2b
uvicorn backend.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Run `ollama serve` first if Ollama is not already running.

## Test

```bash
pytest
```
