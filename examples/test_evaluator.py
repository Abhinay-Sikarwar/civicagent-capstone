# examples/test_evaluator.py
import os
from src.evaluation.evaluator import Evaluator, OUTPUT_PATH

def main():
    # ensure GEMINI_API_KEY is set in your environment before running
    ev = Evaluator(gemini_api_key=os.environ.get("GEMINI_API_KEY"))
    # remove existing results file if present
    try:
        os.remove(str(OUTPUT_PATH))
    except Exception:
        pass
    res = ev.run_all()
    import json
    print("=== EVALUATION SUMMARY ===")
    print(json.dumps(res["summary"], indent=2))

if __name__ == "__main__":
    main()