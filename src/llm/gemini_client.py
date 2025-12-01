# src/llm/gemini_client.py

import os
import json
import time
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
    from google import genai
except ImportError:
    genai = None


class GeminiClient:
    """
    Minimal, stable wrapper compatible with google-genai 2025+.
    Supports:
      - Text generation
      - JSON structured output
    """

    def __init__(self, api_key: Optional[str] = None, default_model: str = "gemini-2.0-flash"):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in the environment.")

        if genai is None:
            raise RuntimeError("google-genai is not installed. Run: pip install google-genai")

        self.client = genai.Client(api_key=api_key)
        self.default_model = default_model

    def _extract_text(self, response):
        """
        Compatible with the newest SDK response format.
        """
        try:
            if hasattr(response, "text") and response.text:
                return response.text.strip()

            # fallback: parse candidate parts
            if hasattr(response, "candidates"):
                parts = []
                for c in response.candidates:
                    if hasattr(c, "content"):
                        for p in c.content.parts:
                            if hasattr(p, "text"):
                                parts.append(p.text)
                if parts:
                    return "\n".join(parts).strip()
        except Exception:
            pass

        return str(response)

    def generate_text(self, prompt: str, temperature: float = 0.0, model: Optional[str] = None):
        """
        Text generation using the NEWEST google-genai SDK call signature.
        NO generation_config is allowed.
        """
        model = model or self.default_model

        start = time.time()
        response = self.client.models.generate_content(
            model=model,
            contents=[prompt],
            config={"temperature": temperature}  # correct param for your SDK version
        )
        dur = time.time() - start
        logger.info(f"[gemini] model={model} duration={dur:.2f}s")

        return self._extract_text(response)

    def generate_structured(self, prompt: str, json_schema: Dict[str, Any], model: Optional[str] = None):
        """
        Ask model to output ONLY JSON.
        Then parse JSON robustly.
        """
        model = model or self.default_model
        wrapper = (
            "Return ONLY valid JSON (no commentary). "
            "If unable, return {}.\n"
            f"SCHEMA: {json_schema}\n\n"
            f"CONTENT:\n{prompt}"
        )

        text = self.generate_text(wrapper, temperature=0.0)

        try:
            # find JSON block
            s = text.find("{")
            e = text.rfind("}")
            if s != -1 and e != -1:
                return json.loads(text[s:e+1])
            return json.loads(text)
        except Exception:
            logger.warning("Failed to parse JSON; returning raw text.")
            return {"_raw": text}

    def generate_structured_vision(
        self,
        prompt: str,
        text_input: str,
        images: List[Dict[str, Any]],
        schema: Dict[str, Any]
    ):
        """
        Gemini Vision + Text → JSON output.
        Compatible with newest google-genai SDK.
        """

        model = self.default_model  # FIX: use correct model attribute

        # Build multimodal message
        parts = [
            {"text": prompt},
            {"text": text_input}
        ]

        # Add images
        for img in images:
            parts.append(
                {
                    "inline_data": {
                        "mime_type": img["mime_type"],
                        "data": img["data"]
                    }
                }
            )

        # Correct param is 'config=', not generation_config
        response = self.client.models.generate_content(
            model=model,
            contents=parts,
            config={"response_mime_type": "application/json"}
        )

        # Parse JSON safely
        try:
            return json.loads(response.text)
        except Exception:
            return {
                "error": "Failed to parse JSON output",
                "raw": response.text
            }




_singleton = None

def get_gemini_client(api_key: Optional[str] = None):
    global _singleton
    if _singleton is None:
        _singleton = GeminiClient(api_key=api_key)
    return _singleton   