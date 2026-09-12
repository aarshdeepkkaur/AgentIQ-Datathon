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
    WeatherSyncSummary,
)

router = APIRouter(prefix="/data-sync", tags=["data-sync"])

REPO_RAW_BASE = "https://raw.githubusercontent.com/aarshdeepkkaur/AgentIQ-Datathon/main/data/cleaned"
CSV_FILES = {
    "crop_distribution": "crop_distribution.csv",
    "prices": "price_and_msp_cleaned.csv",
    "below_msp": "below_msp_by_crop.csv",
    "top_mandis": "top_mandis.csv",
    "warehouse_transit": "warehouse_transit.csv",
    "weather": "weather_cleaned.csv",
    "daily_arrivals": "daily_arrivals.csv",
    "daily_rainfall": "daily_rainfall.csv",
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


def pearson_correlation(pairs: list[tuple[float, float]]) -> float:
    if len(pairs) < 2:
        return 0.0
    left_mean = sum(left for left, _ in pairs) / len(pairs)
    right_mean = sum(right for _, right in pairs) / len(pairs)
    numerator = sum((left - left_mean) * (right - right_mean) for left, right in pairs)
    left_variance = sum((left - left_mean) ** 2 for left, _ in pairs)
    right_variance = sum((right - right_mean) ** 2 for _, right in pairs)
    denominator = (left_variance * right_variance) ** 0.5
    return round(numerator / denominator, 2) if denominator else 0.0


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

    weather_temperature = [value for row in datasets["weather"] if (value := to_float(row.get("temperature_c"))) is not None]
    weather_rainfall = [value for row in datasets["weather"] if (value := to_float(row.get("rainfall_mm"))) is not None]
    weather_humidity = [value for row in datasets["weather"] if (value := to_float(row.get("humidity_percent"))) is not None]
    rainfall_by_date = {row.get("date", ""): to_float(row.get("rainfall_mm")) for row in datasets["daily_rainfall"]}
    arrivals_by_date = {row.get("date", ""): to_float(row.get("total_arrivals_qtl")) for row in datasets["daily_arrivals"]}
    weather_pairs = [
        (rainfall_by_date[date], arrivals_by_date[date])
        for date in rainfall_by_date.keys() & arrivals_by_date.keys()
        if rainfall_by_date[date] is not None and arrivals_by_date[date] is not None
    ]
    weather = WeatherSyncSummary(
        avg_temperature_c=round(sum(weather_temperature) / len(weather_temperature), 2) if weather_temperature else 0,
        avg_rainfall_mm=round(sum(weather_rainfall) / len(weather_rainfall), 2) if weather_rainfall else 0,
        avg_humidity_percent=round(sum(weather_humidity) / len(weather_humidity), 2) if weather_humidity else 0,
        rainfall_arrivals_correlation=pearson_correlation(weather_pairs),
        readings_count=len(datasets["weather"]),
    )

    return DataSyncResponse(
        source="github-cleaned-data",
        fetched_at=datetime.now(timezone.utc),
        rows_loaded={key: len(rows) for key, rows in datasets.items()},
        crop_metrics=crop_metrics,
        top_mandis=top_mandis,
        warehouse_transit=warehouse_transit,
        weather=weather,
    )