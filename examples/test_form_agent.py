# examples/test_form_agent.py

from src.agents.form_agent import FormAgent


def main():
    agent = FormAgent()

    ticket = {
        "issue_category": "Pothole",
        "severity": "High",
        "location": "123 Main St",
        "summary": "Large pothole causing vehicle damage near the crosswalk.",
        "priority": "High",
        "attachments": [],
        "evidence_quality": "Moderate",
        "department": "Public Works",
    }

    out = agent.submit_form(ticket)

    print("\n=== Form Agent Output ===")
    from pprint import pprint
    pprint(out)


if __name__ == "__main__":
    main()