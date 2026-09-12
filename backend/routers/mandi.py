from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from lib.analytics import DELAY_THRESHOLD_HOURS, build_dashboard, filter_bundle, num, pct, text
from lib.datasets import CROPS, canonical_crop, load_datasets
from models.mandi import (
    ArrivalHistoryPoint,
    MandiCropBreakdown,
    MandiDetailResponse,
    PriceHistoryPoint,
    TripLogEntry,
    WarehouseBreakdown,
)
from routers.dashboard import validate_window

router = APIRouter(prefix="/mandi", tags=["mandi"])


def stamp(value) -> str:
    parsed = pd.to_datetime(value, errors="coerce")
    return parsed.strftime("%Y-%m-%d %H:%M") if pd.notna(parsed) else "—"


@router.get("/{mandi_id}", response_model=MandiDetailResponse)
async def get_mandi_detail(
    mandi_id: str,
    crop: str = Query(default="Wheat", min_length=1, max_length=40),
    date_from: str | None = Query(default=None, max_length=10),
    date_to: str | None = Query(default=None, max_length=10),
) -> MandiDetailResponse:
    selected = canonical_crop(crop)
    if selected not in CROPS:
        raise HTTPException(status_code=404, detail=f"Unknown crop '{crop}'")
    start, end = validate_window(date_from, date_to)
    full = await load_datasets()
    mandi_id = mandi_id.upper()
    dashboard = build_dashboard(full, selected, start, end)
    row = next((item for item in dashboard.mandis if item.mandi_id == mandi_id), None)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Unknown mandi '{mandi_id}'")

    bundle = filter_bundle(full, start, end)
    prices = bundle.prices[bundle.prices["mandi_id"] == mandi_id]
    arrivals = bundle.arrivals[bundle.arrivals["mandi_id"] == mandi_id]
    trips = bundle.transport[bundle.transport["mandi_id"] == mandi_id].copy()
    trips["delayed"] = trips["transit_hours"] > DELAY_THRESHOLD_HOURS

    breakdown: list[MandiCropBreakdown] = []
    for name in CROPS:
        crop_prices = prices[prices["crop_name"] == name]
        crop_arrivals = arrivals[arrivals["crop_name"] == name]
        comparable = crop_prices.dropna(subset=["modal_price", "msp"])
        below = int((comparable["modal_price"] < comparable["msp"]).sum())
        modal = num(crop_prices["modal_price"].mean())
        msp = num(crop_prices["msp"].mean())
        if crop_prices.empty and crop_arrivals.empty:
            continue
        breakdown.append(MandiCropBreakdown(
            crop_name=name, modal_price=modal, msp=msp, price_gap=num(modal - msp), arrival_quantity_qtl=num(crop_arrivals["arrival_quantity_qtl"].sum()),
            farmer_count=int(num(crop_arrivals["farmer_count"].sum(), 0, 0)), price_records=int(crop_prices["modal_price"].notna().sum()), below_msp_percentage=pct(below, len(comparable)),
        ))

    crop_prices = prices[prices["crop_name"] == selected].dropna(subset=["date"])
    monthly_prices = crop_prices.groupby(crop_prices["date"].dt.to_period("M")).agg(modal_price=("modal_price", "mean"), min_price=("min_price", "mean"), max_price=("max_price", "mean"), msp=("msp", "mean"), records=("modal_price", "count")).sort_index()
    price_history = [PriceHistoryPoint(label=period.start_time.strftime("%b %Y"), modal_price=num(item.modal_price), min_price=num(item.min_price), max_price=num(item.max_price), msp=num(item.msp), records=int(item.records)) for period, item in monthly_prices.iterrows()]

    crop_arrivals = arrivals[arrivals["crop_name"] == selected].dropna(subset=["date"])
    monthly_arrivals = crop_arrivals.groupby(crop_arrivals["date"].dt.to_period("M")).agg(arrival_quantity_qtl=("arrival_quantity_qtl", "sum"), farmer_count=("farmer_count", "sum"), records=("mandi_id", "size")).sort_index()
    arrival_history = [ArrivalHistoryPoint(label=period.start_time.strftime("%b %Y"), arrival_quantity_qtl=num(item.arrival_quantity_qtl), farmer_count=int(num(item.farmer_count, 0, 0)), records=int(item.records)) for period, item in monthly_arrivals.iterrows()]

    valid_trips = trips.dropna(subset=["transit_hours"])
    warehouse_groups = valid_trips.groupby("destination_warehouse").agg(trips=("transit_hours", "size"), transit_hours=("transit_hours", "mean"), delayed=("delayed", "sum"), distance_km=("distance_km", "mean"))
    warehouse_breakdown = [WarehouseBreakdown(destination_warehouse=text(name), trips=int(item.trips), transit_hours=num(item.transit_hours), delay_rate=pct(float(item.delayed), int(item.trips)), distance_km=num(item.distance_km)) for name, item in warehouse_groups.sort_values("trips", ascending=False).iterrows()]

    trips["departure_sort"] = pd.to_datetime(trips["departure_time_clean"], errors="coerce")
    recent = trips.sort_values("departure_sort", ascending=False).head(25)
    trip_log = [TripLogEntry(
        trip_id=text(item["trip_id"]), destination_warehouse=text(item["destination_warehouse"], "—"), departure_time=stamp(item["departure_time_clean"]), arrival_time=stamp(item["arrival_time_clean"]),
        transit_hours=num(item["transit_hours"]), distance_km=num(item["distance_km"]), vehicle_no=text(item["vehicle_no_clean"]) or text(item["vehicle_no"]) or "—", driver_id=text(item["driver_id"], "—"),
        quality_flag=text(item["quality_flag"]) or None, delayed=bool(item["delayed"]) if pd.notna(item["transit_hours"]) else False,
    ) for _, item in recent.iterrows()]

    dates = pd.concat([prices["date"], arrivals["date"], trips["departure_sort"]]).dropna()
    return MandiDetailResponse(
        source=bundle.source, fetched_at=bundle.fetched_at, selected_crop=selected, mandi_id=row.mandi_id, mandi_name=row.mandi_name, district=row.district, state=row.state,
        mandi_type=row.mandi_type, total_area_acres=row.total_area_acres, latitude=row.latitude, longitude=row.longitude, risk=row.risk, destination_warehouse=row.destination_warehouse,
        modal_price=row.modal_price, msp=row.msp, price_gap=row.price_gap, below_msp_percentage=row.below_msp_percentage, arrival_quantity_qtl=row.arrival_quantity_qtl, farmer_count=row.farmer_count,
        price_records=row.price_records, arrival_records=int(len(crop_arrivals)), arrivals_missing_quantity=int(crop_arrivals["arrival_quantity_qtl"].isna().sum()),
        transit_hours=row.transit_hours, delay_rate=row.delay_rate, trips=int(len(valid_trips)), delayed_trips=int(valid_trips["delayed"].sum()), invalid_transit_trips=int(trips["quality_flag"].notna().sum()),
        first_date=dates.min().strftime("%Y-%m-%d") if not dates.empty else "", last_date=dates.max().strftime("%Y-%m-%d") if not dates.empty else "",
        crop_breakdown=breakdown, price_history=price_history, arrival_history=arrival_history, warehouse_breakdown=warehouse_breakdown, trip_log=trip_log,
    )
