"""TrailLens — Offline AI Nature Explorer."""
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend import config, database, xp
from backend.demo import DEMO_DISCOVERY
from backend.ollama import AnalysisError, NotNatureImage, OllamaUnavailable, analyze_image, check_ollama

app = FastAPI(title="TrailLens", version="1.0.0")
config.ensure_dirs()
database.init_db()

app.mount("/uploads", StaticFiles(directory=str(config.UPLOADS_DIR)), name="uploads")
app.mount("/static", StaticFiles(directory=str(config.FRONTEND_DIR)), name="static")


@app.get("/api/health")
async def health():
    if config.DEMO_MODE:
        return {
            "status": "ok",
            "mode": "demo",
            "ollama": {"connected": False, "model": config.OLLAMA_MODEL, "model_ready": False},
            "message": "Demo mode. Full local AI runs with Ollama + Qwen3-VL 2B on your computer.",
        }
    try:
        status = await check_ollama()
    except OllamaUnavailable as exc:
        status = {"connected": False, "model": config.OLLAMA_MODEL, "model_ready": False, "detail": str(exc)}
    return {"status": "ok", "mode": "local", "ollama": status}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    suffix = Path(file.filename or "photo.jpg").suffix.lower()
    content_type = (file.content_type or "").lower()
    if suffix not in config.ALLOWED_EXTENSIONS and not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty image.")
    if len(contents) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image too large. Maximum is 10 MB.")

    if config.DEMO_MODE:
        return {
            "mode": "demo",
            "result": DEMO_DISCOVERY,
            "xp": {"xp_awarded": 75},
            "upload_path": None,
        }

    upload_path = config.UPLOADS_DIR / f"{uuid.uuid4().hex}{suffix}"
    upload_path.write_bytes(contents)
    try:
        result = await analyze_image(upload_path)
        if not result.is_nature:
            upload_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=422,
                detail=(
                    "This image is not related to the natural environment. "
                    "Please point the camera at a plant, animal, rock, landscape, "
                    "or another natural subject."
                ),
            )
        clean = result.model_dump()
        xp_awarded = xp.compute_xp(clean)
        return {
            "mode": "local",
            "result": clean,
            "xp": {
                "xp_awarded": xp_awarded,
                "preview_total_xp": database.get_stats()["total_xp"] + xp_awarded,
            },
            "upload_path": upload_path.name,
        }
    except OllamaUnavailable as exc:
        upload_path.unlink(missing_ok=True)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AnalysisError as exc:
        upload_path.unlink(missing_ok=True)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        upload_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Unexpected analysis error.") from exc


@app.post("/api/discoveries")
async def save_discovery(payload: dict):
    result = payload.get("result")
    if not isinstance(result, dict):
        raise HTTPException(status_code=400, detail="Missing discovery result.")

    upload_name = payload.get("upload_path")
    image_filename = ""
    if upload_name:
        image_path = (config.UPLOADS_DIR / Path(upload_name).name).resolve()
        if not image_path.exists() or config.UPLOADS_DIR.resolve() not in image_path.parents:
            raise HTTPException(status_code=404, detail="Uploaded image not found.")
        image_filename = image_path.name

    xp_awarded = int(payload.get("xp_awarded") or xp.compute_xp(result))
    saved = database.save_discovery(result, image_filename, xp_awarded)
    stats = database.get_stats()
    return {"id": saved["id"], "xp_awarded": xp_awarded, "stats": stats}


@app.get("/api/discoveries")
def get_discoveries():
    return {"discoveries": database.list_discoveries()}


@app.get("/api/discoveries/{discovery_id}")
def get_discovery(discovery_id: int):
    discovery = database.get_discovery(discovery_id)
    if not discovery:
        raise HTTPException(status_code=404, detail="Discovery not found.")
    return discovery


@app.get("/api/stats")
def stats():
    current = database.get_stats()
    return {**current, "level": xp.level_for_xp(current["total_xp"])}


@app.get("/")
def home():
    return FileResponse(config.FRONTEND_DIR / "index.html")


@app.get("/journal")
def journal_page():
    return FileResponse(config.FRONTEND_DIR / "journal.html")


@app.get("/{full_path:path}")
def frontend_file(full_path: str):
    candidate = (config.FRONTEND_DIR / full_path).resolve()
    if candidate.is_file() and config.FRONTEND_DIR.resolve() in candidate.parents:
        return FileResponse(candidate)
    raise HTTPException(status_code=404, detail="Not found")
