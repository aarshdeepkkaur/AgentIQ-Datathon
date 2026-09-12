from fastapi import APIRouter, HTTPException, Query

from lib.analytics import build_dashboard
from lib.datasets import CROPS, canonical_crop, load_datasets
from models.dashboard import DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(crop: str = Query(default="Wheat", min_length=1, max_length=40), refresh: bool = False) -> DashboardResponse:
    selected = canonical_crop(crop)
    if selected not in CROPS:
        raise HTTPException(status_code=404, detail=f"Unknown crop '{crop}'. Available crops: {', '.join(CROPS)}")
    bundle = await load_datasets(force=refresh)
    return build_dashboard(bundle, selected)
