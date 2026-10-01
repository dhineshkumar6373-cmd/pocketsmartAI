import json
import re
from pathlib import Path
from typing import Any
from app.config import settings

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover
    genai = None
    types = None


def _extract_json(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise ValueError("Gemini returned non-JSON content")

class GeminiService:
    def __init__(self):
        self.enabled = bool(settings.ai_enabled and settings.gemini_api_key and genai)
        self.client = genai.Client(api_key=settings.gemini_api_key) if self.enabled else None

    def generate_json(self, prompt: str, image_path: Path | None = None) -> dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("Gemini is not configured; use fallback recommendations")
        contents: list[Any] = [prompt]
        if image_path:
            from PIL import Image
            image = Image.open(image_path)
            contents.append(image)
        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.25,
                max_output_tokens=5000,
                response_mime_type="application/json",
            ),
        )
        return _extract_json(response.text)
