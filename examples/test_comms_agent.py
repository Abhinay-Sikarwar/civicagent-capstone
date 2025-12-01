from src.agents.comms_agent import CommsAgent


def main():
    agent = CommsAgent()

    ticket = {
        "ticket_id": "TKT-12345",
        "issue_category": "Pothhole",
        "location": "123 Main St",
        "severity": "High",
        "department": "Public Works",
        "summary": "Large pothole causing vehicle damage.",
    }

    out = agent.generate_all_channels(ticket)

    print("\n=== Comms Agent Output ===")
    from pprint import pprint
    pprint(out)


if __name__ == "__main__":
    main()