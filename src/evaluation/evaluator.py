# src/evaluation/evaluator.py
"""
Evaluation harness for the Civic Agent Capstone.

Features:
- Runs a set of golden test cases through the Orchestrator
- Computes Goal Completion Rate (GCR)
- Computes simple trajectory precision / recall (did orchestrator call expected agents)
- Estimates token usage (very lightweight heuristic)
- Measures latency (wall-clock)
- Outputs ndjson-style per-test results and a short summary

Notes:
- This is intentionally deterministic and small so it runs locally without mocks.
- Token estimate: tokens = ceil(char_count / 4)
"""
import time
import json
import math
from typing import List, Dict, Any
from pathlib import Path

from src.agents.orchestrator import Orchestrator

GOLDEN_PATH = Path("src/evaluation/golden_tests.json")
OUTPUT_PATH = Path("evaluation_results.ndjson")


class Evaluator:
    def __init__(self, gemini_api_key: str = None):
        self.orch = Orchestrator(gemini_api_key=gemini_api_key)

    @staticmethod
    def _token_estimate(text: str) -> int:
        # conservative simple estimator: 1 token ~= 4 chars
        n = len(text or "")
        return (n + 3) // 4  # integer ceiling division

    def _score_ticket(self, ticket: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """
        Basic correctness scoring:
         - department match
         - issue_category match (case-insensitive substring)
         - severity match (normalize low/medium/high)
        Returns dict with booleans and score summary.
        """
        dep_match = (ticket.get("department", "").lower() == expected.get("department", "").lower())
        cat_match = expected.get("issue_category", "").lower() in ticket.get("issue_category", "").lower()
        def norm(s): 
            return (s or "").strip().lower()
        sev_match = norm(ticket.get("severity", "")) == norm(expected.get("severity", ""))
        success = dep_match and cat_match and sev_match
        return {
            "department_match": dep_match,
            "category_match": cat_match,
            "severity_match": sev_match,
            "success": success
        }

    def run_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        user = case.get("user_id", "eval-user")
        location = case["location"]
        description = case["description"]
        images = case.get("images", [])
        expected = case.get("expected", {})

        start = time.time()
        res = self.orch.create_ticket(user_id=user, location=location, description=description, image_paths=images)
        elapsed = time.time() - start

        ticket = res.get("ticket", {})
        score = self._score_ticket(ticket, expected)

        # simple trajectory metrics via session events stored in SessionManager
        session_id = res.get("session_id")
        session = self.orch.sessions.get_session(session_id)
        events = session.get("events", []) if session else []
        # check whether both research & evidence events present
        called_research = any(e["event"].get("type") == "research" or "research" in str(e["event"]).lower() for e in events)
        called_evidence = any(e["event"].get("type") == "evidence" or "evidence" in str(e["event"]).lower() for e in events)

        # estimate token usage from text fields we sent to LLM (description + summary)
        token_est = self._token_estimate(description) + self._token_estimate(ticket.get("summary", ""))

        result = {
            "case_id": case.get("id"),
            "session_id": session_id,
            "ticket_id": ticket.get("ticket_id"),
            "elapsed_s": elapsed,
            "called_research": called_research,
            "called_evidence": called_evidence,
            "token_estimate": token_est,
            "score": score,
            "ticket": ticket,
            "raw_orch_response": res
        }
        return result

    def run_all(self, out_path: Path = OUTPUT_PATH) -> Dict[str, Any]:
        assert GOLDEN_PATH.exists(), f"Golden tests not found: {GOLDEN_PATH}"
        with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
            tests = json.load(f)

        results = []
        success_count = 0
        total = len(tests)
        for case in tests:
            r = self.run_case(case)
            results.append(r)
            if r["score"]["success"]:
                success_count += 1
            # append to ndjson file
            with open(out_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + "\n")

        gcr = success_count / total if total else 0.0
        summary = {
            "total_cases": total,
            "successful_cases": success_count,
            "GCR": gcr,
            "results_file": str(out_path)
        }
        return {"summary": summary, "results": results}