from fastapi import FastAPI
from pydantic import BaseModel
from src.agents.orchestrator import Orchestrator

app = FastAPI(title="CivicAgent API")

orch = Orchestrator()

class TicketRequest(BaseModel):
    user_id: str
    location: str
    description: str
    image_paths: list[str] = []

@app.post("/create_ticket")
def create_ticket(req: TicketRequest):
    return orch.create_ticket(
        user_id=req.user_id,
        location=req.location,
        description=req.description,
        image_paths=req.image_paths
    )