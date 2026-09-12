from datetime import datetime

from pydantic import BaseModel


class RiskAlert(BaseModel):
    id: str
    type: str  # below_msp | transit_delay | trend_drop
    severity: str  # high | medium
    mandi_id: str | None
    mandi_name: str
    state: str
    crop_name: str
    title: str
    detail: str
    value: float
    unit: str
    occurred_at: str


class AlertsResponse(BaseModel):
    source: str
    fetched_at: datetime
    selected_crop: str
    generated_at: datetime
    total: int
    high: int
    alerts: list[RiskAlert]
