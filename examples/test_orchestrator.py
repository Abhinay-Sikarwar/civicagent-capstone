# examples/test_orchestrator.py
import os
from src.agents.orchestrator import Orchestrator

def main():
    # ensure GEMINI_API_KEY available or set here temporarily (not recommended to hardcode)
    # os.environ["GEMINI_API_KEY"] = "YOUR_KEY"

    orchestrator = Orchestrator(gemini_api_key=os.environ.get("GEMINI_API_KEY"))
    user_id = "user-xyz"
    location = "123 Main St"
    description = "There is a deep pothole near the crosswalk. My neighbor's wheel got damaged."
    # Provide image paths if you have test images, else leave list empty
    image_paths = []

    out = orchestrator.create_ticket(user_id=user_id, location=location, description=description, image_paths=image_paths)
    import json
    print("=== Orchestrator Result ===")
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()