import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / 'frontend'
DATA_DIR = ROOT_DIR / 'data'
UPLOADS_DIR = ROOT_DIR / 'uploads'

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434').rstrip('/')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen3-vl:2b')
OLLAMA_TIMEOUT = float(os.getenv('OLLAMA_TIMEOUT', '180'))
DEMO_MODE = os.getenv('DEMO_MODE', 'false').lower() in {'1','true','yes','on'}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.jpg','.jpeg','.png','.webp'}

def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
