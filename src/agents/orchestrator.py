# src/agents/orchestrator.py
import uuid
import time
from typing import Optional, List, Dict, Any

from src.session.session_manager import SessionManager
from src.memory.memory_manager import MemoryManager
from src.utils.logging_tracing import TraceSpan, ObservabilityWriter
from src.agents.research_agent import ResearchAgent
from src.agents.evidence_agent import EvidenceAgent
from src.llm.gemini_client import get_gemini_client


# Schema for the final ticket we will ask Gemini to help produce (structured)
TICKET_SCHEMA = {
    "type": "object",
    "properties": {
        "ticket_id": {"type": "string"},
        "location": {"type": "string"},
        "issue_category": {"type": "string"},
        "department": {"type": "string"},
        "severity": {"type": "string"},
        "evidence_quality": {"type": "string"},
        "summary": {"type": "string"},
        "form_url": {"type": "string"},
        "actions": {"type": "array", "items": {"type": "string"}},
        "priority": {"type": "string"}
    },
    "required": ["ticket_id", "location", "issue_category", "department", "severity", "summary"]
}


class Orchestrator:
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.sessions = SessionManager()
        self.memory = MemoryManager()
        self.obs = ObservabilityWriter(output_path="observability_spans.ndjson")
        # instantiate agents
        self.research = ResearchAgent(gemini_api_key=gemini_api_key)
        self.evidence = EvidenceAgent(gemini_api_key=gemini_api_key)
        # LLM summarizer (lightweight)
        self.llm = get_gemini_client(api_key=gemini_api_key)

    def _generate_ticket_id(self) -> str:
        return "TKT-" + uuid.uuid4().hex[:8]

    def _determine_priority(self, severity: str, match_score: int) -> str:
        # simple heuristic mapping
        if severity.lower() == "high" or match_score >= 7:
            return "high"
        if severity.lower() == "medium" or 4 <= match_score < 7:
            return "medium"
        return "low"

    def create_ticket(
        self,
        user_id: str,
        location: str,
        description: str,
        image_paths: Optional[List[str]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates ResearchAgent + EvidenceAgent, then asks Gemini to layout
        actions and produce a final ticket object. Persists session & memory.
        """
        span = TraceSpan(name="orchestrator.create_ticket")
        start_ts = time.time()

        # create session if not provided
        if not session_id:
            session_id = self.sessions.new_session(user_id)
        span.log(event="session_created", session_id=session_id, user_id=user_id)

        # Step 1: Research
        research_out = self.research.classify(description)
        span.log(action="research", research_out=research_out)
        self.sessions.append_event(session_id, {"type": "research", "result": research_out})

        # Step 2: Evidence
        evidence_out = self.evidence.analyze_evidence(issue_description=description, image_paths=image_paths or [])
        span.log(action="evidence", evidence_out=evidence_out)
        self.sessions.append_event(session_id, {"type": "evidence", "result": evidence_out})

        # Merge: basic rule-based merge
        issue_category = (research_out.get("issue_category") or "").lower()

        # strict deterministic department mapping
        if issue_category == "pothole":
            department = "public works"
            form_url = "N/A"
        elif issue_category == "streetlight_outage":
            department = "street lighting"
            form_url = "https://city.gov/forms/general-report"
        elif issue_category == "garbage_overflow":
            department = "sanitation"
            form_url = "N/A"
        else:
            department = "general services"
            form_url = "https://city.gov/forms/general-report"
        

        # ALWAYS prefer rule-based severity for evaluation
        severity = research_out.get("severity_hint", "Medium")
        summary_text = evidence_out.get("summary") if isinstance(evidence_out, dict) else description

        # Step 3: LLM-assisted ticket assembly & action recommendations (light touch)
        prompt = (
        f"Create a short civic ticket summary and a prioritized list of actionable next steps.\n\n"
        f"Context:\n- Location: {location}\n- Issue Category: {issue_category}\n"
        f"- Department: {department}\n- Severity: {severity}\n"
        f"- Evidence Quality: {evidence_out.get('evidence_quality', 'unknown')}\n"
        f"- Description: {description}\n- Evidence Summary: {summary_text}\n\n"
        "Return a strict JSON object matching the schema and recommend 2-4 concise actions."
      )

        ticket_struct = self.llm.generate_structured(prompt, TICKET_SCHEMA)
        span.log(action="llm_ticket_struct", ticket_struct=ticket_struct)

        # Fill defaults & ensure required fields
        ticket = {}
        ticket["ticket_id"] = ticket_struct.get("ticket_id") or self._generate_ticket_id()
        ticket["location"] = ticket_struct.get("location") or location
        ticket["issue_category"] = (ticket_struct.get("issue_category") or issue_category).lower()
        ticket["department"] = ticket_struct.get("department") or department
        ticket["severity"] = ticket_struct.get("severity") or severity
        ticket["evidence_quality"] = ticket_struct.get("evidence_quality") or evidence_out.get("evidence_quality", "unknown")
        ticket["summary"] = ticket_struct.get("summary") or summary_text
        ticket["form_url"] = ticket_struct.get("form_url") or form_url
        ticket["actions"] = ticket_struct.get("actions") or [
            f"Submit report via {ticket['form_url']}",
            "Attach images and summary"
        ]
        ticket["priority"] = ticket_struct.get("priority") or self._determine_priority(ticket["severity"], match_score)

        # Persist memory (simple)
        mem = {
            "ticket_id": ticket["ticket_id"],
            "user_id": user_id,
            "location": ticket["location"],
            "issue_category": ticket["issue_category"],
            "severity": ticket["severity"],
            "created_at": time.time()
        }
        self.memory.create_memory(user_id, "submitted_ticket", mem)
        self.sessions.append_event(session_id, {"type": "ticket_created", "ticket": ticket})

        span.log(result=ticket)
        span.finish()
        self.obs.write_span(span)

        return {"session_id": session_id, "ticket": ticket, "elapsed": time.time() - start_ts}