import csv
import io
import os
from collections import defaultdict
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException

from models.data_sync import (
    CropSyncMetric,
    DataSyncResponse,
    MandiVolumeSync,
    WarehouseTransitSync,
)

router = APIRouter(prefix="/data-sync", tags=["data-sync"])

REPO_RAW_BASE = "https://raw.githubusercontent.com/aarshdeepkkaur/AgentIQ-Datathon/main/data/cleaned"
CSV_FILES = {
    "crop_distribution": "crop_distribution.csv",
    "prices": "price_and_msp_cleaned.csv",
    "below_msp": "below_msp_by_crop.csv",
    "top_mandis": "top_mandis.csv",
    "warehouse_transit": "warehouse_transit.csv",
}


def canonical_crop(name: str) -> str:
    aliases = {
        "Chawal": "Rice",
        "Basmati": "Rice",
        "Dhaan": "Rice",
        "Makki": "Maize",
        "Sarso": "Mustard",
        "Narma": "Cotton",
        "Ganne": "Sugarcane",
    }
    return aliases.get(name.strip(), name.strip())


def to_float(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    try:
        return float(value)
    except ValueError:
        return None


async def fetch_csv(client: httpx.AsyncClient, filename: str) -> list[dict[str, str]]:
    base = os.environ.get("AGENTIQ_DATA_REPO_BASE", REPO_RAW_BASE).rstrip("/")
    response = await client.get(f"{base}/{filename}")
    response.raise_for_status()
    return list(csv.DictReader(io.StringIO(response.text)))


@router.get("", response_model=DataSyncResponse)
async def sync_cleaned_data() -> DataSyncResponse:
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(12.0, connect=4.0), follow_redirects=True) as client:
            datasets = {key: await fetch_csv(client, filename) for key, filename in CSV_FILES.items()}
    except (httpx.HTTPError, OSError) as exc:
        raise HTTPException(status_code=502, detail=f"GitHub cleaned-data sync unavailable: {exc}") from exc

    arrival_totals: dict[str, float] = defaultdict(float)
    for row in datasets["crop_distribution"]:
        crop = canonical_crop(row.get("crop_name", ""))
        amount = to_float(row.get("arrival_quantity_qtl"))
        if crop and amount is not None:
            arrival_totals[crop] += amount

    prices: dict[str, list[float]] = defaultdict(list)
    msps: dict[str, list[float]] = defaultdict(list)
    for row in datasets["prices"]:
        crop = canonical_crop(row.get("crop_name", ""))
        modal = to_float(row.get("modal_price"))
        msp = to_float(row.get("msp"))
        if crop and modal is not None:
            prices[crop].append(modal)
        if crop and msp is not None:
            msps[crop].append(msp)

    below_rates: dict[str, list[float]] = defaultdict(list)
    for row in datasets["below_msp"]:
        crop = canonical_crop(row.get("crop_name", ""))
        percentage = to_float(row.get("below_msp_percentage"))
        if crop and percentage is not None:
            below_rates[crop].append(percentage)

    all_crops = sorted(set(arrival_totals) | set(prices) | set(below_rates))
    crop_metrics = [
        CropSyncMetric(
            crop_name=crop,
            arrivals_qtl=round(arrival_totals.get(crop, 0), 2),
            avg_modal_price=round(sum(prices[crop]) / len(prices[crop]), 2) if prices[crop] else 0,
            avg_msp=round(sum(msps[crop]) / len(msps[crop]), 2) if msps[crop] else 0,
            below_msp_percentage=round(sum(below_rates[crop]) / len(below_rates[crop]), 2) if below_rates[crop] else 0,
            record_count=len(prices[crop]),
        )
        for crop in all_crops
    ]

    top_mandis = [
        MandiVolumeSync(
            mandi_id=row.get("mandi_id", ""),
            mandi_name=row.get("mandi_name", ""),
            district=row.get("district", ""),
            state=row.get("state", ""),
            arrival_quantity_qtl=round(to_float(row.get("arrival_quantity_qtl")) or 0, 2),
        )
        for row in datasets["top_mandis"]
        if row.get("mandi_id")
    ]
    warehouse_transit = [
        WarehouseTransitSync(
            destination_warehouse=row.get("destination_warehouse", ""),
            transit_hours=round(to_float(row.get("transit_hours")) or 0, 2),
        )
        for row in datasets["warehouse_transit"]
        if row.get("destination_warehouse")
    ]

    return DataSyncResponse(
        source="github-cleaned-data",
        fetched_at=datetime.now(timezone.utc),
        rows_loaded={key: len(rows) for key, rows in datasets.items()},
        crop_metrics=crop_metrics,
        top_mandis=top_mandis,
        warehouse_transit=warehouse_transit,
    )