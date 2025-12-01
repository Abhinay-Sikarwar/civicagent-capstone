# examples/test_gemini.py
from src.llm.gemini_client import get_gemini_client
import os

def main():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("GEMINI_API_KEY not set. Export the key and try again.")
        return
    client = get_gemini_client(api_key=key)
    prompt = "In one sentence describe how to report a pothole to local public works."
    out = client.generate_text(prompt)
    print("=== Gemini Text Output ===")
    print(out)

    schema = {
        "type": "object",
        "properties": {
            "issue_category": {"type": "string"},
            "search_query": {"type": "string"}
        },
        "required": ["issue_category", "search_query"]
    }
    structured = client.generate_structured("User reported a pothole near 123 Main St. Produce a short issue_category and a search_query.", schema)
    print("=== Gemini Structured Output ===")
    print(structured)

if __name__ == "__main__":
    main()