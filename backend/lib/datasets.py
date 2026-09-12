"""Load the five cleaned Datathon datasets: GitHub raw first, bundled CSVs as offline fallback."""

import asyncio
import io
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pandas as pd

logger = logging.getLogger(__name__)

REPO_RAW_BASE = "https://raw.githubusercontent.com/aarshdeepkkaur/AgentIQ-Datathon/main/data/cleaned"
LOCAL_DIR = Path(__file__).resolve().parent.parent / "data" / "cleaned"
CACHE_TTL_SECONDS = 30 * 60

FILES = {
    "master": "mandi_master_cleaned.csv",
    "arrivals": "mandi_arrivals_cleaned.csv",
    "prices": "price_and_msp_cleaned.csv",
    "transport": "transport_cleaned.csv",
    "weather": "weather_cleaned.csv",
}

CROP_ALIASES = {
    "Chawal": "Rice",
    "Basmati": "Rice",
    "Dhaan": "Rice",
    "Makki": "Maize",
    "Sarso": "Mustard",
    "Narma": "Cotton",
    "Ganne": "Sugarcane",
}
CROPS = ["Wheat", "Rice", "Maize", "Cotton", "Mustard", "Sugarcane"]


def canonical_crop(name: str) -> str:
    cleaned = (name or "").strip().title()
    return CROP_ALIASES.get(cleaned, cleaned)


@dataclass
class DatasetBundle:
    master: pd.DataFrame
    arrivals: pd.DataFrame
    prices: pd.DataFrame
    transport: pd.DataFrame
    weather: pd.DataFrame
    source: str
    fetched_at: datetime


_cache: dict[str, object] = {"bundle": None, "loaded_at": 0.0}
_lock = asyncio.Lock()


def _prepare(frames: dict[str, pd.DataFrame], source: str) -> DatasetBundle:
    master = frames["master"].copy()
    arrivals = frames["arrivals"].copy()
    prices = frames["prices"].copy()
    transport = frames["transport"].copy()
    weather = frames["weather"].copy()

    for frame in (arrivals, prices):
        frame["crop_name"] = frame["crop_name"].astype(str).map(canonical_crop)
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    arrivals["arrival_quantity_qtl"] = pd.to_numeric(arrivals["arrival_quantity_qtl"], errors="coerce")
    arrivals["farmer_count"] = pd.to_numeric(arrivals["farmer_count"], errors="coerce")
    for column in ("min_price", "max_price", "modal_price", "msp"):
        prices[column] = pd.to_numeric(prices[column], errors="coerce")
    transport["transit_hours"] = pd.to_numeric(transport["transit_hours"], errors="coerce")
    transport["distance_km"] = pd.to_numeric(transport["distance_km"], errors="coerce")
    weather["timestamp_ist"] = pd.to_datetime(weather["timestamp_ist"], errors="coerce", utc=True)
    for column in ("temperature_c", "rainfall_mm", "humidity_percent"):
        weather[column] = pd.to_numeric(weather[column], errors="coerce")
    master["total_area_acres"] = pd.to_numeric(master["total_area_acres"], errors="coerce")
    master["mandi_type"] = master["mandi_type"].fillna("Unclassified").astype(str).str.upper().replace({"APMC": "APMC"})
    master["mandi_type"] = master["mandi_type"].map(lambda value: value if value == "APMC" else value.title())
    return DatasetBundle(master, arrivals, prices, transport, weather, source, datetime.now(timezone.utc))


async def _fetch_github() -> dict[str, pd.DataFrame]:
    base = os.environ.get("AGENTIQ_DATA_REPO_BASE", REPO_RAW_BASE).rstrip("/")
    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=5.0), follow_redirects=True) as client:
        async def pull(filename: str) -> pd.DataFrame:
            response = await client.get(f"{base}/{filename}")
            response.raise_for_status()
            return pd.read_csv(io.StringIO(response.text))

        results = await asyncio.gather(*(pull(filename) for filename in FILES.values()))
    return dict(zip(FILES.keys(), results))


def _read_local() -> dict[str, pd.DataFrame]:
    return {key: pd.read_csv(LOCAL_DIR / filename) for key, filename in FILES.items()}


async def load_datasets(force: bool = False) -> DatasetBundle:
    cached = _cache["bundle"]
    if cached is not None and not force and time.monotonic() - float(_cache["loaded_at"]) < CACHE_TTL_SECONDS:
        return cached  # type: ignore[return-value]
    async with _lock:
        cached = _cache["bundle"]
        if cached is not None and not force and time.monotonic() - float(_cache["loaded_at"]) < CACHE_TTL_SECONDS:
            return cached  # type: ignore[return-value]
        try:
            frames = await _fetch_github()
            bundle = _prepare(frames, "github-cleaned-data")
        except (httpx.HTTPError, OSError, ValueError) as exc:
            logger.warning("GitHub dataset sync failed (%s); using bundled CSVs", exc)
            bundle = await asyncio.to_thread(lambda: _prepare(_read_local(), "bundled-cleaned-data"))
        _cache["bundle"] = bundle
        _cache["loaded_at"] = time.monotonic()
        return bundle
