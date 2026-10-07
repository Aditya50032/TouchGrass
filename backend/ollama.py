import base64
import json
import logging
from pathlib import Path
import httpx
from pydantic import BaseModel, Field
from .config import OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_URL

logger = logging.getLogger('traillens.ollama')

class NatureAnalysis(BaseModel):
    is_nature: bool
    name: str
    category: str
    confidence: str = Field(pattern='^(High|Medium|Low)
    facts: list[str] = Field(min_length=3, max_length=3)
    outdoor_challenge: str

class OllamaUnavailable(Exception): pass
class AnalysisError(Exception): pass

SYSTEM_PROMPT = '''You are TrailLens, a strict nature-discovery image analyzer.

FIRST decide whether the PRIMARY SUBJECT physically visible in the image is part of the natural world.

Set is_nature=false for:
- books, notebooks, documents, posters, screens or photographs showing nature
- phones, laptops, TVs and other electronics
- buildings, vehicles and manufactured objects
- people as the primary subject
- food, packaging, products and indoor objects
- artwork, illustrations, diagrams or text about nature

A book with a picture of a tree is still a BOOK, so is_nature must be false.

Set is_nature=true for genuine natural subjects such as:
- plants, flowers, trees and leaves
- animals, birds and insects
- fungi and mushrooms
- rocks, soil, sand and water
- mountains, forests, landscapes, sky and clouds

If is_nature=false, explain briefly what the primary subject actually is,
and do not pretend to identify it as nature.

If is_nature=true:
- identify the PRIMARY natural subject only
- do not invent a precise species
- use a broader identification when evidence is weak
- lower confidence when uncertain
- use Low, Medium or High honestly
- do not identify an image printed on a book/screen as the real object
- keep facts factual and beginner-friendly
- never suggest touching wildlife, tasting plants or disturbing habitats
- make the challenge safe and immediately doable outdoors

Return ONLY valid JSON matching the requested schema.'''


async def check_ollama():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f'{OLLAMA_URL}/api/tags')
            response.raise_for_status()
            models = [m.get('name','') for m in response.json().get('models',[])]
    except (httpx.HTTPError, OSError) as error:
        raise OllamaUnavailable('Ollama is not reachable. Start Ollama and try again.') from error
    ready = any(model.split(':')[0] == OLLAMA_MODEL.split(':')[0] for model in models)
    return {'connected': True, 'model': OLLAMA_MODEL, 'model_ready': ready}

async def analyze_image(image_path: Path):
    payload = {'model': OLLAMA_MODEL, 'stream': False, 'format': NatureAnalysis.model_json_schema(), 'messages': [{'role':'system','content':SYSTEM_PROMPT},{'role':'user','content':'Identify this natural object and create the TrailLens discovery.','images':[base64.b64encode(image_path.read_bytes()).decode('ascii')]}], 'options': {'temperature':0.0}}
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            response = await client.post(f'{OLLAMA_URL}/api/chat', json=payload)
            response.raise_for_status()
        content = response.json().get('message',{}).get('content','')
        if not content: raise AnalysisError('The local model returned an empty response.')
        return NatureAnalysis.model_validate(json.loads(extract_json(content)))
    except httpx.HTTPError as error:
        raise OllamaUnavailable('Local analysis could not reach Ollama. Check that Ollama is running.') from error
    except (KeyError, TypeError, json.JSONDecodeError, ValueError) as error:
        raise AnalysisError('The local model returned an invalid analysis. Please try another photo.') from error

def extract_json(content):
    text = content.strip()
    if text.startswith('```'):
        parts = text.split('\n',1)
        text = parts[1] if len(parts)==2 else text
        text = text.rsplit('```',1)[0].strip()
    start,end=text.find('{'),text.rfind('}')
    if start==-1 or end==-1 or end<start: raise ValueError('No JSON object found')
    return text[start:end+1]
)
    description: str
    facts: list[str] = Field(min_length=3, max_length=3)
    outdoor_challenge: str

class OllamaUnavailable(Exception): pass
class AnalysisError(Exception): pass

SYSTEM_PROMPT = '''You are TrailLens, a careful, beginner-friendly naturalist.
Analyze the provided nature photo. Do not invent a precise species when uncertain.
Use a broader identification and lower confidence when needed.
Be concise, factual, beginner-friendly, and safe.
Do not suggest touching wildlife, tasting plants, or disturbing habitats.
Return ONLY valid JSON matching the requested schema.'''


async def check_ollama():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f'{OLLAMA_URL}/api/tags')
            response.raise_for_status()
            models = [m.get('name','') for m in response.json().get('models',[])]
    except (httpx.HTTPError, OSError) as error:
        raise OllamaUnavailable('Ollama is not reachable. Start Ollama and try again.') from error
    ready = any(model.split(':')[0] == OLLAMA_MODEL.split(':')[0] for model in models)
    return {'connected': True, 'model': OLLAMA_MODEL, 'model_ready': ready}

async def analyze_image(image_path: Path):
    payload = {'model': OLLAMA_MODEL, 'stream': False, 'format': NatureAnalysis.model_json_schema(), 'messages': [{'role':'system','content':SYSTEM_PROMPT},{'role':'user','content':'Identify this natural object and create the TrailLens discovery.','images':[base64.b64encode(image_path.read_bytes()).decode('ascii')]}], 'options': {'temperature':0.2}}
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            response = await client.post(f'{OLLAMA_URL}/api/chat', json=payload)
            response.raise_for_status()
        content = response.json().get('message',{}).get('content','')
        if not content: raise AnalysisError('The local model returned an empty response.')
        return NatureAnalysis.model_validate(json.loads(extract_json(content)))
    except httpx.HTTPError as error:
        raise OllamaUnavailable('Local analysis could not reach Ollama. Check that Ollama is running.') from error
    except (KeyError, TypeError, json.JSONDecodeError, ValueError) as error:
        raise AnalysisError('The local model returned an invalid analysis. Please try another photo.') from error

def extract_json(content):
    text = content.strip()
    if text.startswith('```'):
        parts = text.split('\n',1)
        text = parts[1] if len(parts)==2 else text
        text = text.rsplit('```',1)[0].strip()
    start,end=text.find('{'),text.rfind('}')
    if start==-1 or end==-1 or end<start: raise ValueError('No JSON object found')
    return text[start:end+1]
