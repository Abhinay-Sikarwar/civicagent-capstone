# src/agents/evidence_agent.py

from typing import Any, Dict, Optional, List
import base64
import mimetypes
import os

from src.llm.gemini_client import get_gemini_client
from src.utils.logging_tracing import TraceSpan

# Load schema
import json
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schemas", "evidence_schema.json")
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    EVIDENCE_SCHEMA = json.load(f)


class EvidenceAgent:
    """
    An agent responsible for:
    - analyzing images or textual evidence
    - detecting the visible civic issue
    - assessing severity
    - summarizing findings into structured output
    """

    def __init__(self, observability=None, gemini_api_key: Optional[str] = None):
        self.obs = observability
        self.llm = get_gemini_client(api_key=gemini_api_key)

    def _prepare_image_input(self, image_path: str) -> Dict[str, Any]:
        """
        Convert image to base64 and return Gemini image dict.
        """
        mime = mimetypes.guess_type(image_path)[0] or "image/jpeg"
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return {
            "mime_type": mime,
            "data": b64
        }

    def analyze_evidence(
        self,
        issue_description: str,
        image_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Main entrypoint for evidence evaluation.
        Accepts:
        - textual description (mandatory)
        - optional images (1 or more paths)
        """
        span = TraceSpan(name="evidence.analyze")

        # Prepare inputs
        images_payload = []
        if image_paths:
            for p in image_paths:
                images_payload.append(self._prepare_image_input(p))

        prompt = (
            "You are an expert civic infrastructure inspector.\n"
            "Analyze the user's textual description and the provided images.\n\n"
            "Your job:\n"
            "1. Identify the visible or implied civic issue.\n"
            "2. Assess severity: low, medium, or high.\n"
            "3. Evaluate evidence quality (good, moderate, poor).\n"
            "4. Produce a short text summary.\n\n"
            "Return ONLY JSON following the exact schema provided."
        )

        # Gemini call
        result = self.llm.generate_structured_vision(
            prompt=prompt,
            text_input=issue_description,
            images=images_payload,
            schema=EVIDENCE_SCHEMA
        )

        span.log(action="gemini_evidence", output=result)
        span.finish()

        if self.obs:
            self.obs.write_span(span)

        return result