# examples/test_evidence_agent.py

import os
from src.agents.evidence_agent import EvidenceAgent

# Provide your Gemini key
os.environ.setdefault("GEMINI_API_KEY", "YOUR_KEY")

def main():
    agent = EvidenceAgent(gemini_api_key=os.environ["GEMINI_API_KEY"])

    # OPTIONAL: Add an actual local image path to test vision.
    # You can skip images and just test text-only.
    out = agent.analyze_evidence(
        issue_description="This pothole looks very deep and dangerous near the crosswalk.",
        image_paths=[]  # add ["E:/test_images/pothole.jpg"] etc.
    )

    print("\n=== Evidence Agent Output ===")
    print(out)

if __name__ == "__main__":
    main()