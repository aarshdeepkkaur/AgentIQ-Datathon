import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from lib.analytics import DELAY_THRESHOLD_HOURS, build_dashboard, filter_bundle, num, text
from lib.datasets import CROPS, canonical_crop, load_datasets
from models.alerts import AlertsResponse, RiskAlert
from routers.dashboard import validate_window

router = APIRouter(prefix="/alerts", tags=["alerts"])


def alert_id(*parts: object) -> str:
    return hashlib.sha1("|".join(str(part) for part in parts).encode()).hexdigest()[:12]


@router.get("", response_model=AlertsResponse)
async def get_alerts(
    crop: str = Query(default="Wheat", min_length=1, max_length=40),
    date_from: str | None = Query(default=None, max_length=10),
    date_to: str | None = Query(default=None, max_length=10),
) -> AlertsResponse:
    selected = canonical_crop(crop)
    if selected not in CROPS:
        raise HTTPException(status_code=404, detail=f"Unknown crop '{crop}'")
    start, end = validate_window(date_from, date_to)
    full = await load_datasets()
    dashboard = build_dashboard(full, selected, start, end)
    bundle = filter_bundle(full, start, end)
    names = {row.mandi_id: row for row in dashboard.mandis}
    alerts: list[RiskAlert] = []

    # 1. Mandis whose latest price record for the crop is below MSP.
    prices = bundle.prices[(bundle.prices["crop_name"] == selected)].dropna(subset=["date", "modal_price", "msp"]).sort_values("date")
    latest = prices.groupby("mandi_id").tail(1)
    for _, item in latest.iterrows():
        gap = float(item["modal_price"] - item["msp"])
        if gap >= 0:
            continue
        row = names.get(text(item["mandi_id"]))
        if row is None:
            continue
        severity = "high" if gap <= -100 or row.below_msp_percentage >= 50 else "medium"
        alerts.append(RiskAlert(
            id=alert_id("below_msp", row.mandi_id, selected, item["date"].date()), type="below_msp", severity=severity, mandi_id=row.mandi_id, mandi_name=row.mandi_name, state=row.state, crop_name=selected,
            title=f"{row.mandi_name} slipped below MSP", detail=f"Latest {selected} modal ₹{item['modal_price']:,.0f} vs MSP ₹{item['msp']:,.0f} on {item['date']:%d %b} · {row.below_msp_percentage:.0f}% of its records below floor",
            value=num(gap), unit="₹/qtl", occurred_at=item["date"].strftime("%Y-%m-%d"),
        ))

    # 2. Trips that exceeded the 24 h delay threshold (most recent per mandi).
    trips = bundle.transport.dropna(subset=["transit_hours"]).copy()
    trips["departure_sort"] = pd.to_datetime(trips["departure_time_clean"], errors="coerce")
    delayed = trips[trips["transit_hours"] > DELAY_THRESHOLD_HOURS].sort_values("departure_sort")
    for mandi_id, group in delayed.groupby("mandi_id"):
        row = names.get(text(mandi_id))
        if row is None:
            continue
        last = group.iloc[-1]
        when = last["departure_sort"]
        count = int(len(group))
        alerts.append(RiskAlert(
            id=alert_id("transit_delay", row.mandi_id, count, when), type="transit_delay", severity="high" if count >= 2 or float(last["transit_hours"]) >= 30 else "medium", mandi_id=row.mandi_id, mandi_name=row.mandi_name, state=row.state, crop_name=selected,
            title=f"{row.mandi_name} trip delayed over 24h", detail=f"{text(last['trip_id'])} to {text(last['destination_warehouse'])} took {float(last['transit_hours']):.1f} h · {count} delayed trip{'s' if count != 1 else ''} in window",
            value=num(last["transit_hours"]), unit="h", occurred_at=when.strftime("%Y-%m-%d") if pd.notna(when) else "",
        ))

    # 3. Network-level trend drop for the selected crop.
    summary = dashboard.crop_summary
    if summary.trend_percentage <= -1.0:
        alerts.append(RiskAlert(
            id=alert_id("trend_drop", selected, round(summary.trend_percentage, 1)), type="trend_drop", severity="medium", mandi_id=None, mandi_name="Network", state="All", crop_name=selected,
            title=f"{selected} modal price softening", detail=f"Average modal price fell {abs(summary.trend_percentage):.1f}% over the last 30 days versus the prior 30 days",
            value=summary.trend_percentage, unit="%", occurred_at=dashboard.totals.date_to,
        ))

    alerts.sort(key=lambda item: (item.severity != "high", item.occurred_at), reverse=False)
    alerts.sort(key=lambda item: item.occurred_at, reverse=True)
    alerts.sort(key=lambda item: item.severity != "high")
    return AlertsResponse(
        source=bundle.source, fetched_at=bundle.fetched_at, selected_crop=selected, generated_at=datetime.now(timezone.utc),
        total=len(alerts), high=sum(1 for item in alerts if item.severity == "high"), alerts=alerts,
    )
