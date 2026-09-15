"""Aggregate the cleaned datasets into the dashboard payload for a selected crop (pandas, no DB)."""

import math
from dataclasses import replace

import pandas as pd

from lib.datasets import CROPS, DatasetBundle
from models.dashboard import (
    CropSummary,
    DashboardResponse,
    DataQuality,
    MandiRow,
    MspDistribution,
    NetworkTotals,
    PriceTrend,
    TrendPoint,
    WarehousePerformance,
    WeatherPoint,
    WeatherSummary,
)

DELAY_THRESHOLD_HOURS = 24

CROP_META = {
    "Wheat": ("W", "Rabi · Oct–Mar"),
    "Rice": ("R", "Kharif · Jun–Nov"),
    "Maize": ("M", "Kharif · Jun–Sep"),
    "Cotton": ("C", "Kharif · Oct–Feb"),
    "Mustard": ("Mu", "Rabi · Nov–Mar"),
    "Sugarcane": ("S", "Annual · Oct–Apr"),
}

DISTRICT_COORDS = {
    "Ludhiana": (30.90, 75.85), "Amritsar": (31.63, 74.87), "Patiala": (30.34, 76.38), "Bathinda": (30.21, 74.95),
    "Ferozepur": (30.93, 74.61), "Jalandhar": (31.33, 75.58), "Moga": (30.82, 75.17),
    "Ambala": (30.38, 76.78), "Fatehabad": (29.52, 75.45), "Hisar": (29.15, 75.72), "Karnal": (29.69, 76.99),
    "Kurukshetra": (29.97, 76.88), "Sirsa": (29.53, 75.02),
    "Agra": (27.18, 78.01), "Bareilly": (28.37, 79.43), "Meerut": (28.98, 77.71), "Muzaffarnagar": (29.47, 77.70),
    "Saharanpur": (29.96, 77.55),
}
STATE_COORDS = {"Punjab": (30.75, 75.40), "Haryana": (29.40, 76.20), "Uttar Pradesh": (28.40, 78.60)}
DISTRICT_STATE = {
    **{district: "Punjab" for district in ("Ludhiana", "Amritsar", "Patiala", "Bathinda", "Ferozepur", "Jalandhar", "Moga")},
    **{district: "Haryana" for district in ("Ambala", "Fatehabad", "Hisar", "Karnal", "Kurukshetra", "Sirsa")},
    **{district: "Uttar Pradesh" for district in ("Agra", "Bareilly", "Meerut", "Muzaffarnagar", "Saharanpur")},
}
LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = 73.6, 80.6, 26.4, 32.4

_dashboard_cache: dict[tuple[str, str, str, str], DashboardResponse] = {}


def filter_bundle(bundle: DatasetBundle, date_from: str | None, date_to: str | None) -> DatasetBundle:
    """Restrict every dated dataset to [date_from, date_to] (inclusive, YYYY-MM-DD). Master is never filtered."""
    if not date_from and not date_to:
        return bundle
    start = pd.Timestamp(date_from) if date_from else pd.Timestamp.min
    end = (pd.Timestamp(date_to) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)) if date_to else pd.Timestamp.max

    def within(series: pd.Series) -> pd.Series:
        return series.notna() & (series >= start) & (series <= end)

    weather_local = bundle.weather["timestamp_ist"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    departures = pd.to_datetime(bundle.transport["departure_time_clean"], errors="coerce")
    return replace(
        bundle,
        arrivals=bundle.arrivals[within(bundle.arrivals["date"])],
        prices=bundle.prices[within(bundle.prices["date"])],
        transport=bundle.transport[within(departures)],
        weather=bundle.weather[within(weather_local)],
    )


def num(value, default: float = 0.0, digits: int = 2) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return default if math.isnan(result) or math.isinf(result) else round(result, digits)


def pct(part: float, whole: float) -> float:
    return num(part / whole * 100) if whole else 0.0


def text(value, default: str = "") -> str:
    return default if value is None or (isinstance(value, float) and math.isnan(value)) else str(value)


def risk_level(price_gap: float, below_pct: float, transit_hours: float) -> str:
    if (price_gap < 0 and below_pct >= 50) or transit_hours > 18:
        return "high"
    if price_gap < 0 or below_pct >= 40 or transit_hours > 15:
        return "medium"
    return "low"


def trend_points(prices: pd.DataFrame, arrivals: pd.DataFrame, freq: str, label_format: str, limit: int) -> list[TrendPoint]:
    priced = prices.dropna(subset=["date", "modal_price"])
    if priced.empty:
        return []
    price_groups = priced.groupby(priced["date"].dt.to_period(freq)).agg(modal_price=("modal_price", "mean"), msp=("msp", "mean"))
    arrived = arrivals.dropna(subset=["date", "arrival_quantity_qtl"])
    arrival_groups = arrived.groupby(arrived["date"].dt.to_period(freq))["arrival_quantity_qtl"].sum()
    merged = price_groups.join(arrival_groups.rename("arrivals_qtl"), how="left").sort_index().tail(limit)
    return [
        TrendPoint(label=period.start_time.strftime(label_format), modal_price=num(row.modal_price), msp=num(row.msp), arrivals_qtl=num(row.arrivals_qtl))
        for period, row in merged.iterrows()
    ]


def build_crop_summary(bundle: DatasetBundle, crop: str, mandi_transit: pd.DataFrame) -> CropSummary:
    prices = bundle.prices[bundle.prices["crop_name"] == crop]
    arrivals = bundle.arrivals[bundle.arrivals["crop_name"] == crop]
    priced = prices.dropna(subset=["modal_price"])
    comparable = prices.dropna(subset=["modal_price", "msp"])
    below = int((comparable["modal_price"] < comparable["msp"]).sum())
    above = int(len(comparable) - below)
    modal = num(priced["modal_price"].mean())
    msp = num(prices["msp"].mean())

    crop_mandis = set(arrivals["mandi_id"].dropna()) | set(prices["mandi_id"].dropna())
    trips = mandi_transit[mandi_transit.index.isin(crop_mandis)]
    transit = num((trips["transit_hours"] * trips["trips"]).sum() / trips["trips"].sum()) if trips["trips"].sum() else 0.0
    delay = num((trips["delayed"].sum() / trips["trips"].sum()) * 100) if trips["trips"].sum() else 0.0

    trend = 0.0
    if not priced.empty:
        end = priced["date"].max()
        recent = priced[priced["date"] > end - pd.Timedelta(days=30)]["modal_price"].mean()
        previous = priced[(priced["date"] <= end - pd.Timedelta(days=30)) & (priced["date"] > end - pd.Timedelta(days=60))]["modal_price"].mean()
        if previous and not math.isnan(previous) and not math.isnan(recent):
            trend = num((recent - previous) / previous * 100)

    gap = num(modal - msp)
    below_pct = pct(below, above + below)
    direction = "firming" if trend > 0.5 else "softening" if trend < -0.5 else "holding steady"
    outlook = (
        f"Modal price is {direction} ({trend:+.1f}% over the last 30 days) and sits ₹{abs(gap):,.0f} "
        f"{'above' if gap >= 0 else 'below'} MSP; {below_pct:.0f}% of price records clear below the floor"
    )
    icon, season = CROP_META.get(crop, (crop[:2], "Season pending"))
    return CropSummary(
        crop_name=crop, icon=icon, modal_price=modal, msp=msp, price_gap=gap,
        arrivals_qtl=num(arrivals["arrival_quantity_qtl"].sum()), below_msp_percentage=below_pct,
        above_msp_records=above, below_msp_records=below, price_records=int(len(priced)), arrival_records=int(len(arrivals)),
        avg_transit_hours=transit, delay_rate=delay, trend_percentage=trend, season=season, outlook=outlook,
    )


def build_dashboard(full_bundle: DatasetBundle, crop: str, date_from: str | None = None, date_to: str | None = None) -> DashboardResponse:
    key = (full_bundle.fetched_at.isoformat(), crop, date_from or "", date_to or "")
    if key in _dashboard_cache:
        return _dashboard_cache[key]
    bundle = filter_bundle(full_bundle, date_from, date_to)

    transport = bundle.transport.dropna(subset=["transit_hours"]).copy()
    transport["delayed"] = transport["transit_hours"] > DELAY_THRESHOLD_HOURS
    mandi_transit = transport.groupby("mandi_id").agg(transit_hours=("transit_hours", "mean"), trips=("transit_hours", "size"), delayed=("delayed", "sum"))
    mandi_warehouse = transport.groupby("mandi_id")["destination_warehouse"].agg(lambda values: values.value_counts().idxmax())

    summaries = [build_crop_summary(bundle, name, mandi_transit) for name in CROPS]
    summary = next(item for item in summaries if item.crop_name == crop)

    crop_prices = bundle.prices[bundle.prices["crop_name"] == crop]
    crop_arrivals = bundle.arrivals[bundle.arrivals["crop_name"] == crop]
    comparable = crop_prices.dropna(subset=["modal_price", "msp"]).assign(below=lambda frame: frame["modal_price"] < frame["msp"])
    mandi_prices = crop_prices.groupby("mandi_id").agg(modal_price=("modal_price", "mean"), msp=("msp", "mean"), price_records=("modal_price", "count"))
    mandi_below = comparable.groupby("mandi_id")["below"].mean() * 100
    mandi_arrivals = crop_arrivals.groupby("mandi_id").agg(arrival_quantity_qtl=("arrival_quantity_qtl", "sum"), farmer_count=("farmer_count", "sum"), latest_date=("date", "max"))

    weather = bundle.weather.dropna(subset=["timestamp_ist"]).copy()
    weather["date"] = weather["timestamp_ist"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None).dt.normalize()
    daily_weather = weather.groupby("date").agg(temperature_c=("temperature_c", "mean"), rainfall_mm=("rainfall_mm", "mean"), humidity_percent=("humidity_percent", "mean"))

    rows: list[MandiRow] = []
    master = bundle.master.sort_values("mandi_id").reset_index(drop=True)
    district_seen: dict[str, int] = {}
    for _, mandi in master.iterrows():
        mandi_id = text(mandi["mandi_id"])
        district = text(mandi.get("district"), "")
        state = text(mandi.get("state"), "") or DISTRICT_STATE.get(district, "Unassigned")
        price = mandi_prices.loc[mandi_id] if mandi_id in mandi_prices.index else None
        modal = num(price["modal_price"], summary.modal_price) if price is not None else summary.modal_price
        msp = num(price["msp"], summary.msp) if price is not None else summary.msp
        arrival = mandi_arrivals.loc[mandi_id] if mandi_id in mandi_arrivals.index else None
        transit = mandi_transit.loc[mandi_id] if mandi_id in mandi_transit.index else None
        transit_hours = num(transit["transit_hours"]) if transit is not None else summary.avg_transit_hours
        trips = int(transit["trips"]) if transit is not None else 0
        delay_rate = pct(float(transit["delayed"]), trips) if transit is not None else 0.0
        below_pct = num(mandi_below.get(mandi_id, float("nan")), summary.below_msp_percentage)
        gap = num(modal - msp)

        weather_label = "No reading"
        latest_date = arrival["latest_date"] if arrival is not None else pd.NaT
        if pd.notna(latest_date) and latest_date in daily_weather.index:
            reading = daily_weather.loc[latest_date]
            weather_label = f"{num(reading['temperature_c'], 0, 0):.0f}°C · {num(reading['rainfall_mm'], 0, 1):.1f}mm"

        base_lat, base_lon = DISTRICT_COORDS.get(district) or STATE_COORDS.get(state, (29.5, 77.0))
        slot = district_seen.get(district or state, 0)
        district_seen[district or state] = slot + 1
        angle = slot * 2.4
        latitude = round(base_lat + 0.12 * slot * math.sin(angle), 4)
        longitude = round(base_lon + 0.14 * slot * math.cos(angle), 4)
        rows.append(MandiRow(
            mandi_id=mandi_id, mandi_name=text(mandi["mandi_name"], mandi_id), district=district or "Unlisted district", state=state,
            mandi_type=text(mandi.get("mandi_type"), "Unclassified"), total_area_acres=num(mandi.get("total_area_acres")),
            modal_price=modal, msp=msp, price_gap=gap,
            arrival_quantity_qtl=num(arrival["arrival_quantity_qtl"]) if arrival is not None else 0.0,
            farmer_count=int(num(arrival["farmer_count"], 0, 0)) if arrival is not None else 0,
            price_records=int(price["price_records"]) if price is not None else 0, below_msp_percentage=below_pct,
            transit_hours=transit_hours, delay_rate=delay_rate, trips=trips,
            destination_warehouse=text(mandi_warehouse.get(mandi_id), "Unrouted"), weather=weather_label,
            risk=risk_level(gap, below_pct, transit_hours), latitude=latitude, longitude=longitude,
            position_x=round(8 + (longitude - LON_MIN) / (LON_MAX - LON_MIN) * 84, 2),
            position_y=round(8 + (LAT_MAX - latitude) / (LAT_MAX - LAT_MIN) * 84, 2),
        ))
    rows.sort(key=lambda row: row.arrival_quantity_qtl, reverse=True)

    price_trend = PriceTrend(
        daily=trend_points(crop_prices, crop_arrivals, "D", "%d %b", 90),
        weekly=trend_points(crop_prices, crop_arrivals, "W", "%d %b", 52),
        monthly=trend_points(crop_prices, crop_arrivals, "M", "%b %Y", 12),
    )

    all_arrivals = bundle.arrivals.dropna(subset=["date", "arrival_quantity_qtl"])
    daily_arrivals = all_arrivals.groupby(all_arrivals["date"].dt.normalize())["arrival_quantity_qtl"].sum()
    daily_rain_total = weather.groupby("date")["rainfall_mm"].sum(min_count=1)
    joined = pd.concat([daily_rain_total.rename("rain"), daily_arrivals.rename("arrivals")], axis=1)
    overlap = joined.dropna()
    correlation_overlap = num(overlap["rain"].corr(overlap["arrivals"])) if len(overlap) > 2 else 0.0
    # Pipeline method: every arrival day is kept and days without a rainfall reading count as 0 mm.
    anchored = joined.dropna(subset=["arrivals"]).fillna({"rain": 0.0})
    correlation = num(anchored["rain"].corr(anchored["arrivals"])) if len(anchored) > 2 else 0.0

    weekly_weather = weather.groupby(weather["date"].dt.to_period("W")).agg(temperature_c=("temperature_c", "mean"), rainfall_mm=("rainfall_mm", "mean"), humidity_percent=("humidity_percent", "mean"))
    weekly_arrivals = all_arrivals.groupby(all_arrivals["date"].dt.to_period("W"))["arrival_quantity_qtl"].sum()
    weekly = weekly_weather.join(weekly_arrivals.rename("arrivals_qtl"), how="left").sort_index()
    weather_series = [
        WeatherPoint(label=period.start_time.strftime("%d %b"), temperature_c=num(row.temperature_c, 0, 1), rainfall_mm=num(row.rainfall_mm, 0, 1), humidity_percent=num(row.humidity_percent, 0, 1), arrivals_qtl=num(row.arrivals_qtl))
        for period, row in weekly.iterrows()
    ]
    latest_day = daily_weather.dropna(how="all").index.max()
    latest = daily_weather.loc[latest_day] if pd.notna(latest_day) else None
    weather_summary = WeatherSummary(
        avg_temperature_c=num(weather["temperature_c"].mean(), 0, 1), avg_rainfall_mm=num(weather["rainfall_mm"].mean(), 0, 1),
        avg_humidity_percent=num(weather["humidity_percent"].mean(), 0, 1),
        latest_temperature_c=num(latest["temperature_c"], 0, 1) if latest is not None else 0.0,
        latest_rainfall_mm=num(latest["rainfall_mm"], 0, 1) if latest is not None else 0.0,
        latest_humidity_percent=num(latest["humidity_percent"], 0, 1) if latest is not None else 0.0,
        latest_reading_date=latest_day.strftime("%Y-%m-%d") if pd.notna(latest_day) else "",
        rainfall_arrivals_correlation=correlation, rainfall_arrivals_correlation_overlap=correlation_overlap, readings_count=int(len(bundle.weather)),
    )

    warehouse_groups = transport.groupby("destination_warehouse").agg(transit_hours=("transit_hours", "mean"), trips=("transit_hours", "size"), delayed=("delayed", "sum"), distance_km=("distance_km", "mean"))
    warehouses = [
        WarehousePerformance(destination_warehouse=text(name), transit_hours=num(row.transit_hours), delay_rate=pct(float(row.delayed), int(row.trips)), trips=int(row.trips), distance_km=num(row.distance_km))
        for name, row in warehouse_groups.sort_values("transit_hours").iterrows()
    ]

    msp_distribution = [
        MspDistribution(crop_name=item.crop_name, above_msp=item.above_msp_records, below_msp=item.below_msp_records, below_msp_percentage=item.below_msp_percentage)
        for item in summaries
    ]

    all_comparable = bundle.prices.dropna(subset=["modal_price", "msp"])
    all_dates = pd.concat([full_bundle.prices["date"], full_bundle.arrivals["date"]]).dropna()
    totals = NetworkTotals(
        total_arrivals_qtl=num(bundle.arrivals["arrival_quantity_qtl"].sum()), avg_modal_price=num(bundle.prices["modal_price"].mean()),
        avg_msp=num(bundle.prices["msp"].mean()), below_msp_percentage=pct(int((all_comparable["modal_price"] < all_comparable["msp"]).sum()), len(all_comparable)),
        avg_transit_hours=num(transport["transit_hours"].mean()), delay_rate=pct(int(transport["delayed"].sum()), len(transport)),
        active_mandis=int(bundle.master["mandi_id"].nunique()), price_records=int(len(bundle.prices)), arrival_records=int(len(bundle.arrivals)),
        transport_records=int(len(bundle.transport)), weather_records=int(len(bundle.weather)),
        date_from=all_dates.min().strftime("%Y-%m-%d") if not all_dates.empty else "", date_to=all_dates.max().strftime("%Y-%m-%d") if not all_dates.empty else "",
    )
    data_quality = DataQuality(
        arrivals_missing_quantity_pct=pct(int(bundle.arrivals["arrival_quantity_qtl"].isna().sum()), len(bundle.arrivals)),
        arrivals_invalid_flag_pct=pct(int(bundle.arrivals["quality_flag"].notna().sum()), len(bundle.arrivals)),
        weather_missing_temperature_pct=pct(int(bundle.weather["temperature_c"].isna().sum()), len(bundle.weather)),
        weather_missing_rainfall_pct=pct(int(bundle.weather["rainfall_mm"].isna().sum()), len(bundle.weather)),
        transport_invalid_transit_pct=pct(int(bundle.transport["quality_flag"].notna().sum()), len(bundle.transport)),
        prices_missing_msp_pct=pct(int(bundle.prices["msp"].isna().sum()), len(bundle.prices)),
    )

    response = DashboardResponse(
        source=bundle.source, fetched_at=bundle.fetched_at, selected_crop=crop, filter_from=date_from, filter_to=date_to, crops=list(CROPS),
        states=sorted({row.state for row in rows}), crop_summary=summary, crop_summaries=summaries, mandis=rows,
        price_trend=price_trend, weather_series=weather_series, warehouses=warehouses, msp_distribution=msp_distribution,
        weather=weather_summary, totals=totals, data_quality=data_quality,
    )
    _dashboard_cache.clear() if len(_dashboard_cache) > 24 else None
    _dashboard_cache[key] = response
    return response
