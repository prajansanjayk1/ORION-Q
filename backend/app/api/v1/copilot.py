from fastapi import APIRouter
from backend.app.services.copilot_engine import copilot_engine, CopilotRequest, CopilotResponse

router = APIRouter()


@router.post("/copilot", response_model=CopilotResponse)
def ask_copilot(request: CopilotRequest):
    return copilot_engine.ask(request)
