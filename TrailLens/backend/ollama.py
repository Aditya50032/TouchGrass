import base64
import json
import os
from pathlib import Path

import httpx
from pydantic import BaseModel, Field

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.getenv("OLLAMA_MODEL", "qwen3-vl:2b")


class NatureAnalysis(BaseModel):
    name: str
    category: str
    confidence: str = Field(pattern="^(High|Medium|Low)$")
    description: str
    facts: list[str] = Field(min_length=3, max_length=3)
    outdoor_challenge: str


SYSTEM_PROMPT = """You are TrailLens, a careful, beginner-friendly naturalist. Analyze the provided nature photo.
Do not invent a precise species when the photo is uncertain: use a broader identification and set confidence to Low or Medium.
Be concise, age-friendly, factual, and outdoors-safe. Do not suggest touching wildlife, tasting plants, or disturbing habitats.
Return only JSON matching the supplied schema."""


class OllamaUnavailable(Exception):
    pass


async def check_ollama() -> dict:
    try:
        async with httpx.AsyncClient(timeout=4) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            response.raise_for_status()
    except httpx.HTTPError as error:
        raise OllamaUnavailable("Ollama is not reachable. Start Ollama and try again.") from error
    models = [model.get("name", "") for model in response.json().get("models", [])]
    return {"connected": True, "model": MODEL, "model_ready": MODEL in models}


async def analyze_image(image_path: Path) -> NatureAnalysis:
    payload = {
        "model": MODEL,
        "stream": False,
        "format": NatureAnalysis.model_json_schema(),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Identify this natural object and create the TrailLens discovery.",
             "images": [base64.b64encode(image_path.read_bytes()).decode("ascii")]},
        ],
        "options": {"temperature": 0.2},
    }
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            response.raise_for_status()
        content = response.json()["message"]["content"]
        return NatureAnalysis.model_validate(json.loads(extract_json(content)))
    except httpx.HTTPError as error:
        raise OllamaUnavailable("Local analysis could not reach Ollama. Check that it is running.") from error
    except (KeyError, json.JSONDecodeError, ValueError) as error:
        raise ValueError("The local model returned an invalid analysis. Please try another photo.") from error


def extract_json(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    start, end = content.find("{"), content.rfind("}")
    return content if start == -1 or end == -1 else content[start : end + 1]
