import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any

import ollama


logger = logging.getLogger(__name__)


DEFAULT_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:12b")

MIN_TAGS = 5
MAX_TAGS = 20

PROMPT = """
Analyze this image and return only a JSON object in the format:
{"tags": ["tag1", "tag2", "tag3"]}

Rules:
- Output only JSON.
- Tags must be short noun phrases.
- Use 5 to 15 tags.
- Include visible objects, scene type, style, and mood when relevant.
- Do not include explanations.
""".strip()

_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


class TaggingError(Exception):
    """Raised when image tagging cannot be completed."""


def normalize_tags(tags: list[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for tag in tags:
        if not isinstance(tag, str):
            continue
        cleaned = tag.strip().lower()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
        if len(result) >= MAX_TAGS:
            break
    return result


def extract_json(text: str) -> dict[str, Any]:
    if not text:
        raise TaggingError("Model returned empty response")

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = _FENCE_RE.search(text)
        if not match:
            raise TaggingError(f"Model returned non-JSON response: {text!r}") from None
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError as e:
            raise TaggingError(f"Model returned invalid JSON: {text!r}") from e

    if not isinstance(data, dict):
        raise TaggingError(f"Model response is not a JSON object: {data!r}")

    return data


def check_ollama_available(client: ollama.Client, model: str = DEFAULT_MODEL, host: str = DEFAULT_HOST) -> None:
    try:
        response = client.list()
    except ConnectionError as e:
        raise TaggingError(f"Ollama is not running at {host}: {e}") from e
    except ollama.ResponseError as e:
        raise TaggingError(f"Ollama request failed: {e}") from e

    installed = {m.model for m in response.models if m.model}
    if model not in installed:
        available = ", ".join(sorted(installed)) or "(none)"
        raise TaggingError(f"Model '{model}' is not available. Installed models: {available}")


def generate_tags(
    image_path: str | Path,
    model: str = DEFAULT_MODEL,
    host: str = DEFAULT_HOST,
) -> list[str]:
    path = Path(image_path)
    if not path.is_file():
        raise TaggingError(f"Image file does not exist: {image_path}")

    client = ollama.Client(host=host)
    check_ollama_available(client, model=model, host=host)

    try:
        response = client.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": PROMPT,
                    "images": [str(path)],
                }
            ],
            format="json",
            options={"temperature": 0.2},
        )
    except ConnectionError as e:
        raise TaggingError(f"Ollama is not running at {host}: {e}") from e
    except ollama.ResponseError as e:
        raise TaggingError(f"Ollama request failed: {e}") from e

    content = response.message.content or ""
    data = extract_json(content)

    raw_tags = data.get("tags")
    if not isinstance(raw_tags, list):
        raise TaggingError(f"Model response is missing a 'tags' list: {data!r}")

    tags = normalize_tags(raw_tags)
    if len(tags) < MIN_TAGS:
        logger.warning(f"Model returned only {len(tags)} tags (minimum is {MIN_TAGS})")

    logger.info(f"Generated {len(tags)} tags for {image_path}")
    return tags


def run_tag(
    image_path: str,
    model: str = DEFAULT_MODEL,
    host: str = DEFAULT_HOST,
) -> None:
    try:
        tags = generate_tags(image_path=image_path, model=model, host=host)
    except TaggingError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps({"tags": tags}))
