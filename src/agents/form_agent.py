# src/agents/form_agent.py

import uuid
import datetime
from typing import Dict, Any, List, Optional

from src.llm.gemini_client import get_gemini_client


class FormAgent:
    """
    Simulates filling and submitting a realistic municipal incident form.
    This agent demonstrates:
        - Field validation
        - Required/optional structure
        - Automated form assembly
        - Simulated backend submission
    """

    REQUIRED_FIELDS = [
        "issue_category",
        "severity",
        "location",
        "summary",
    ]

    OPTIONAL_FIELDS = [
        "department",
        "evidence_quality",
        "attachments",
        "priority",
    ]

    def __init__(self, llm_api_key: Optional[str] = None):
        self.llm = get_gemini_client(llm_api_key)

    def validate_fields(self, ticket: Dict[str, Any]) -> List[str]:
        """Return list of missing required fields."""
        missing = []
        for field in self.REQUIRED_FIELDS:
            if field not in ticket or ticket[field] in (None, "", []):
                missing.append(field)
        return missing

    def build_form_payload(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assemble a clean, municipal-style form payload.
        """
        payload = {
            "form_id": f"FORM-{uuid.uuid4().hex[:8]}",
            "submitted_at": datetime.datetime.utcnow().isoformat() + "Z",
            "fields": {},
        }

        # Required fields
        for field in self.REQUIRED_FIELDS:
            payload["fields"][field] = ticket.get(field)

        # Optional fields
        for field in self.OPTIONAL_FIELDS:
            if field in ticket:
                payload["fields"][field] = ticket[field]

        return payload

    def simulate_submission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fake external API submission.
        In production this would:
            - POST to an external service
            - Log transaction
            - Return backend response
        """
        return {
            "status": "submitted",
            "form_id": payload["form_id"],
            "received_at": payload["submitted_at"],
            "backend_reference": f"BK-{uuid.uuid4().hex[:6]}",
        }

    def generate_confirmation_message(self, payload: Dict[str, Any], missing: List[str]) -> str:
        """
        Let Gemini generate a nice confirmation or error message.
        """
        if missing:
            prompt = (
                "A municipal incident form submission was attempted but missing fields "
                f"{missing}. Generate a short, helpful message to the user explaining what is missing."
            )
        else:
            prompt = (
                "A municipal incident report form has been successfully prepared. "
                "Create a concise confirmation message summarizing the incident using:\n"
                f"{payload['fields']}"
            )

        msg = self.llm.generate_text(prompt)
        return msg.strip()

    def submit_form(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point — validates fields, builds form,
        submits to fake backend, returns structured result.
        """
        missing = self.validate_fields(ticket)
        payload = self.build_form_payload(ticket)

        if missing:
            confirmation = self.generate_confirmation_message(payload, missing)
            return {
                "success": False,
                "missing_fields": missing,
                "form_payload": payload,
                "message": confirmation,
            }

        backend = self.simulate_submission(payload)
        confirmation = self.generate_confirmation_message(payload, missing)

        return {
            "success": True,
            "form_payload": payload,
            "backend": backend,
            "message": confirmation,
        }