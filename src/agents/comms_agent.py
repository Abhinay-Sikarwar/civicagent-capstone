# src/agents/comms_agent.py

from typing import Dict, Any, Optional
from src.llm.gemini_client import get_gemini_client


class CommsAgent:
    """
    Multi-channel communication agent.
    Produces SMS, Email, and App-Notification messages for the user.
    Powered by Gemini.
    """

    def __init__(self, llm_api_key: Optional[str] = None):
        self.llm = get_gemini_client(llm_api_key)

    def generate_sms(self, ticket: Dict[str, Any]) -> str:
        prompt = (
            "Create a VERY short SMS-style message confirming a municipal incident "
            "submission. Max 160 characters. Info:\n"
            f"{ticket}"
        )
        return self.llm.generate_text(prompt).strip()

    def generate_email(self, ticket: Dict[str, Any]) -> str:
        prompt = (
            "Write a polished, professional EMAIL confirming an incident report "
            "submission to a city government. Include:\n"
            "- Issue category\n"
            "- Location\n"
            "- Severity\n"
            "- Ticket ID\n"
            "- Expected next steps\n\n"
            f"Ticket data:\n{ticket}"
        )
        return self.llm.generate_text(prompt).strip()

    def generate_app_notification(self, ticket: Dict[str, Any]) -> str:
        prompt = (
            "Write a concise, friendly APP NOTIFICATION message acknowledging "
            "an incident report submission. Keep it under 2 sentences.\n\n"
            f"Details:\n{ticket}"
        )
        return self.llm.generate_text(prompt).strip()

    def generate_all_channels(self, ticket: Dict[str, Any]) -> Dict[str, str]:
        """
        Master method returning all communication formats.
        """
        return {
            "sms": self.generate_sms(ticket),
            "email": self.generate_email(ticket),
            "app_notification": self.generate_app_notification(ticket),
        }