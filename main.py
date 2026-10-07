"""TrailLens — Offline AI Nature Explorer.

FastAPI backend serving the API and the static frontend.
All AI runs locally through Ollama (Qwen3-VL 2B). No cloud AI is used.
"""

import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from . import config, database, xp
from .ai import AIError, analyze_image, logger

app = FastAPI(title="TrailLens", version="0.1.0")

config.ensure_dirs()
database.init_db()


# --------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------
@app.get("/api/health")
def health() -> JSONResponse:
    """App health + local Ollama connectivity."""
    ollama_ok = False
    ollama_error = None
    try:
        import httpx

        r = httpx.get(f"{config.OLLAMA_URL}/api/tags", timeout=5)
        ollama_ok = r.status_code == 200
        if ollama_ok:
            models = [m.get("name", "") for m in r.json().get("models", [])]
            if not any(m.split(":")[0] == config.OLLAMA_MODEL.split(":")[0] for m in models):
                ollama_error = f"Model '{config.OLLAMA_MODEL}' not pulled yet"
    except Exception as exc:  # noqa: BLE001
        ollama_error = str(exc)

    return JSONResponse(
        {
            "status": "ok",
            "ollama": {
                "url": config.OLLAMA_URL,
                "model": config.OLLAMA_MODEL,
                "reachable": ollama_ok,
                "detail": ollama_error,
            },
        }
    )


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)) -> JSONResponse:
    """Upload a photo, run local AI analysis, return the structured result."""
    suffix = Path(file.filename or "photo.jpg").suffix.lower()
    if suffix not in config.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Use: "
            + ", ".join(sorted(config.ALLOWED_EXTENSIONS)),
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file.")
    if len(contents) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB).")

    upload_path = config.UPLOADS_DIR / f"{uuid.uuid4().hex}{suffix}"
    upload_path.write_bytes(contents)
    logger.info(
        "POST /api/analyze received | saved as %s | %d bytes | source=%s",
        upload_path.name,
        len(contents),
        file.filename,
    )

    try:
        # Run the blocking Ollama call in a worker thread so the event loop
        # stays free — the site must keep responding while AI is thinking.
        result = await run_in_threadpool(analyze_image, upload_path)
    except AIError as exc:
        upload_path.unlink(missing_ok=True)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        upload_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc

    xp_awarded = xp.compute_xp(result)
    return JSONResponse(
        {
            "result": result,
            "xp": {
                "xp_awarded": xp_awarded,
                "preview_total_xp": database.get_stats()["total_xp"] + xp_awarded,
            },
            "upload_path": upload_path.name,
        }
    )


@app.post("/api/discoveries")
def save_discovery(payload: dict) -> JSONResponse:
    """Save an analyzed discovery to the journal and award XP."""
    result = payload.get("result")
    upload_name = payload.get("upload_path", "")
    if not isinstance(result, dict) or not upload_name:
        raise HTTPException(status_code=400, detail="Missing result or upload_path.")

    image_path = (config.UPLOADS_DIR / Path(upload_name).name).resolve()
    if not image_path.exists() or config.UPLOADS_DIR.resolve() not in image_path.parents:
        raise HTTPException(status_code=404, detail="Uploaded image not found.")

    from .ai import normalize_result

    clean = normalize_result(result)
    xp_awarded = xp.compute_xp(clean)
    discovery_id = database.save_discovery(clean, image_path.name, xp_awarded)
    stats = database.get_stats()

    return JSONResponse(
        {
            "id": discovery_id,
            "xp_awarded": xp_awarded,
            "stats": stats,
        }
    )


@app.get("/api/discoveries")
def journal() -> JSONResponse:
    """Full discovery journal, newest first."""
    return JSONResponse({"discoveries": database.list_discoveries()})


@app.get("/api/stats")
def stats() -> JSONResponse:
    return JSONResponse(database.get_stats())


# --------------------------------------------------------------------------
# Frontend (static files)
# --------------------------------------------------------------------------
app.mount("/uploads", StaticFiles(directory=config.UPLOADS_DIR), name="uploads")
app.mount("/static", StaticFiles(directory=config.FRONTEND_DIR), name="static")


@app.get("/")
def home() -> FileResponse:
    return FileResponse(config.FRONTEND_DIR / "index.html")


@app.get("/journal")
def journal_page() -> FileResponse:
    return FileResponse(config.FRONTEND_DIR / "journal.html")


@app.get("/{full_path:path}")
def spa_fallback(full_path: str) -> FileResponse:
    """Serve frontend files directly (css/js) without the /static prefix."""
    candidate = (config.FRONTEND_DIR / full_path).resolve()
    if candidate.is_file() and config.FRONTEND_DIR.resolve() in candidate.parents:
        return FileResponse(candidate)
    raise HTTPException(status_code=404, detail="Not found")
