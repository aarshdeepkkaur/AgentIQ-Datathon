from datetime import datetime

from pydantic import BaseModel, Field


class AgentAskRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    crop_name: str = Field(default="Wheat", min_length=1, max_length=40)
    session_id: str | None = Field(default=None, max_length=64)
    date_from: str | None = Field(default=None, max_length=10)
    date_to: str | None = Field(default=None, max_length=10)


class AgentChartPoint(BaseModel):
    label: str
    value: float
    unit: str


class AgentAnswer(BaseModel):
    answer: str
    intent: str
    source: str
    grounded_at: datetime
    evidence: list[str]
    chart: list[AgentChartPoint] = []
    mode: str = "rules"  # llm | rules
    code: str | None = None
    result_preview: str | None = None


class AgentMessage(BaseModel):
    id: str
    session_id: str
    role: str  # user | agent
    text: str
    crop_name: str
    created_at: datetime
    evidence: list[str] = []
    chart: list[AgentChartPoint] = []
    mode: str | None = None
    code: str | None = None
    result_preview: str | None = None


class AgentHistoryResponse(BaseModel):
    session_id: str
    messages: list[AgentMessage]
