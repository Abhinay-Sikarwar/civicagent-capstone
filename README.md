---

![Status](https://img.shields.io/badge/GCR-1.0-brightgreen)
![Agents](https://img.shields.io/badge/Multi--Agent-Enabled-blue)
![LLM](https://img.shields.io/badge/Gemini-2.0_Flash-00E3A5)
![API](https://img.shields.io/badge/FastAPI-Production--Ready-009485)
![License](https://img.shields.io/badge/License-MIT-purple)

# **README.md**

# 🏛️ **CivicAgent – Autonomous Multi-Agent Civic Issue Processing System**

### **KaggleXGoogle – Capstone Project (Freestyle Track)**

### Powered by **Gemini 2.0 Flash**

---

## 🚀 Overview

**CivicAgent** is a production-grade **multi-agent system** designed to automatically process civic issue reports such as potholes, streetlight outages, garbage overflow, and more.

It receives user reports, classifies the civic issue, analyzes evidence, synthesizes a complete ticket, and prepares backend-ready payloads and citizen-facing communication.

This project demonstrates advanced concepts from the Kaggle Agents course:

* Multi-agent design
* Tool-using agents
* Sessions + Memory
* Context Engineering
* Structured LLM JSON output
* Observability (logs + traces)
* Evaluation using **GCR (Goal Completion Rate)**
* Lightweight production deployment (FastAPI)

👉 The evaluator shows **GCR = 1.0**, meeting capstone quality standards.

---

## 📌 Features

### ✔ Multi-Agent Architecture

CivicAgent includes specialized sub-agents:

| Agent                 | Purpose                                    |
| --------------------- | ------------------------------------------ |
| **ResearchAgent**     | Classifies issue, department, and severity |
| **EvidenceAgent**     | Analyzes images/text for evidence quality  |
| **OrchestratorAgent** | Merges outputs, generates final ticket     |
| **FormAgent**         | Builds backend-ready incident form payload |
| **CommsAgent**        | Generates email/SMS notifications          |

### ✔ Hybrid Rule-Based + LLM Logic

Structured, deterministic pipelines ensure robust and evaluable behavior.

### ✔ Full Context Engineering

* Short-term state → **SessionManager**
* Long-term knowledge → **MemoryManager**

### ✔ Observability

Produces `observability_spans.ndjson` for debugging and quality analysis.

### ✔ Built for Evaluation

Includes `golden_tests.json` and evaluator capable of producing:

```
GCR = 1.0
```

---

## 🧠 Architecture Diagram

```
User Report
   │
   ▼
ResearchAgent ──► classify(issue)
   │
   ▼
EvidenceAgent ──► analyze(text + images)
   │
   ▼
OrchestratorAgent ──► synthesize final ticket
       │
       ├──► FormAgent  (backend submission object)
       └──► CommsAgent (email + SMS + notifications)
```

---

## 📁 Project Structure

```
civicagent-capstone/
│
├── api/
│   └── main.py
│
├── src/
│   ├── agents/
│   │   ├── research_agent.py
│   │   ├── evidence_agent.py
│   │   ├── orchestrator.py
│   │   ├── form_agent.py
│   │   └── comms_agent.py
│   │
│   ├── llm/gemini_client.py
│   ├── session/session_manager.py
│   ├── memory/memory_manager.py
│   └── evaluation/
│       ├── evaluator.py
│       └── golden_tests.json
│
└── examples/
    └── test_*.py (agent demos)
```

---

## ⚙️ Installation

### 1. Clone

```bash
git clone https://github.com/yourusername/civicagent-capstone
cd civicagent-capstone
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Gemini API Key

Windows:

```powershell
setx GEMINI_API_KEY "YOUR_API_KEY"
```

Mac/Linux:

```bash
export GEMINI_API_KEY="YOUR_API_KEY"
```

---

## 🧪 Agent Tests

### Research Agent

```bash
python -m examples.test_research_agent
```

### Evidence Agent

```bash
python -m examples.test_evidence_agent
```

### Orchestrator (full flow)

```bash
python -m examples.test_orchestrator
```

### Full Evaluation (should pass)

```bash
python -m examples.test_evaluator
```

Expected:

```
successful_cases: 3
GCR: 1.0
```

---

## 🌐 Run API Server

```bash
python -m uvicorn api.main:app --reload
```

Open Swagger UI:

👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Example request:

```json
{
  "user_id": "u123",
  "location": "123 Main St",
  "description": "A large pothole near the crosswalk.",
  "image_paths": []
}
```

---

## 🎯 Sample Ticket Output

```json
{
  "ticket_id": "TKT-9a21c8d2",
  "location": "123 Main St",
  "issue_category": "pothole",
  "department": "public works",
  "severity": "high",
  "evidence_quality": "poor",
  "summary": "Large pothole causing potential vehicle damage.",
  "form_url": "N/A",
  "actions": [
    "Dispatch crew to assess pothole.",
    "Document pothole dimensions.",
    "Schedule repair."
  ],
  "priority": "high"
}
```

---

## 🧩 Capstone Requirements Checklist

| Requirement                    | Status  |
| ------------------------------ | ------- |
| Clear pitch & problem          | ✔       |
| Multi-agent system             | ✔       |
| Uses sessions & memory         | ✔       |
| Uses tools or structured calls | ✔       |
| Evaluator + GCR                | ✔ (1.0) |
| Observability                  | ✔       |
| Gemini-powered agent           | ✔       |
| Optional FastAPI deployment    | ✔       |
| GitHub repository              | ✔       |

---

## 🎥 Optional YouTube Video Structure (3 min)

If you want, I can generate your video script too.

**Say:**
→ *"Generate my capstone video script."*

---

## 📄 License

MIT License.

---

## ✨ Acknowledgements

Built for **KaggleXGoogle – Advanced Agents Cohort**, synthesizing concepts from:

* Agents for Good
* Agents & Tool Use (MCP)
* Context Engineering
* Agent Quality
* Prototype → Production

---