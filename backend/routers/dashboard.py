import re
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from lib.analytics import build_dashboard
from lib.datasets import CROPS, canonical_crop, load_datasets
from models.dashboard import DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_window(date_from: str | None, date_to: str | None) -> tuple[str | None, str | None]:
    for value in (date_from, date_to):
        if value and not ISO_DATE.match(value):
            raise HTTPException(status_code=422, detail=f"Dates must be YYYY-MM-DD, got '{value}'")
        if value:
            try:
                date.fromisoformat(value)
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=f"Invalid calendar date '{value}'") from exc
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="date_from must be on or before date_to")
    return date_from or None, date_to or None


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    crop: str = Query(default="Wheat", min_length=1, max_length=40),
    date_from: str | None = Query(default=None, max_length=10),
    date_to: str | None = Query(default=None, max_length=10),
    refresh: bool = False,
) -> DashboardResponse:
    selected = canonical_crop(crop)
    if selected not in CROPS:
        raise HTTPException(status_code=404, detail=f"Unknown crop '{crop}'. Available crops: {', '.join(CROPS)}")
    start, end = validate_window(date_from, date_to)
    bundle = await load_datasets(force=refresh)
    return build_dashboard(bundle, selected, start, end)
