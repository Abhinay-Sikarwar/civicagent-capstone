# examples/test_research_agent.py
import os
from src.agents.research_agent import ResearchAgent

os.environ.setdefault("GEMINI_API_KEY", "YOUR_KEY_HERE")  # optional if key already set globally
agent = ResearchAgent(gemini_api_key=os.environ.get("GEMINI_API_KEY"))
out = agent.find_department(location="123 Main St", issue_description="Huge pothole causing car damage")
print(out)