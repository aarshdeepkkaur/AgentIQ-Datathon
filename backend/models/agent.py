from datetime import datetime

from pydantic import BaseModel, Field


class AgentAskRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    crop_name: str = Field(default="Wheat", min_length=1, max_length=40)


class AgentAnswer(BaseModel):
    answer: str
    intent: str
    source: str
    grounded_at: datetime
    evidence: list[str]