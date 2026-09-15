"""Rule-based AgentIQ answers computed directly from the dashboard aggregates (LLM fallback)."""

from lib.analytics import build_dashboard
from lib.datasets import CROPS, DatasetBundle, canonical_crop
from models.agent import AgentAnswer, AgentChartPoint

STATE_KEYWORDS = {"punjab": "Punjab", "haryana": "Haryana", "uttar pradesh": "Uttar Pradesh", "up ": "Uttar Pradesh"}


def money(value: float) -> str:
    return f"₹{value:,.0f}"


def detect_crop(query: str, fallback: str) -> str:
    for crop in CROPS:
        if crop.lower() in query:
            return crop
    return fallback


def rule_based_answer(bundle: DatasetBundle, question: str, crop_name: str, date_from: str | None = None, date_to: str | None = None) -> AgentAnswer:
    """Deterministic, data-grounded fallback used when the LLM is unavailable."""
    query = question.lower()
    requested = canonical_crop(crop_name)
    crop = detect_crop(query, requested if requested in CROPS else "Wheat")
    data = build_dashboard(bundle, crop, date_from, date_to)
    summary = data.crop_summary
    priced = [row for row in data.mandis if row.price_records > 0]
    state = next((name for keyword, name in STATE_KEYWORDS.items() if keyword in f"{query} "), None)
    scoped = [row for row in priced if row.state == state] if state else priced
    scope_label = f"{state} mandis" if state else "monitored mandis"
    chart: list[AgentChartPoint] = []

    if any(word in query for word in ("weather", "rain", "temperature", "humidity", "monsoon")):
        intent = "weather-impact"
        weather = data.weather
        answer = (
            f"Latest sensor day ({weather.latest_reading_date}) averaged {weather.latest_temperature_c:.1f}°C, "
            f"{weather.latest_rainfall_mm:.1f} mm rainfall and {weather.latest_humidity_percent:.0f}% humidity. Across the cleaned series the mean is "
            f"{weather.avg_temperature_c:.1f}°C / {weather.avg_rainfall_mm:.1f} mm, and daily rainfall correlates with arrivals at r = {weather.rainfall_arrivals_correlation:.2f}."
        )
        evidence = [f"{weather.readings_count:,} weather sensor rows (IST-normalized)", f"{data.data_quality.weather_missing_temperature_pct:.1f}% readings lack a convertible temperature", "Source: weather_cleaned.csv + mandi_arrivals_cleaned.csv"]
        chart = [AgentChartPoint(label=point.label, value=point.rainfall_mm, unit="mm") for point in data.weather_series[-8:]]
    elif any(word in query for word in ("transit", "warehouse", "route", "delay", "logistics", "fastest", "slowest", "transport")):
        intent = "route-health"
        routed = sorted((row for row in scoped if row.trips > 0), key=lambda row: row.transit_hours)
        if not routed:
            routed = sorted((row for row in data.mandis if row.trips > 0), key=lambda row: row.transit_hours)
        if not routed or not data.warehouses:
            return AgentAnswer(answer="No transport trips fall inside the selected window, so route health cannot be computed.", intent=intent, source=data.source, grounded_at=data.fetched_at, evidence=["0 transport rows in window"], mode="rules")
        fastest, slowest = routed[0], routed[-1]
        best_wh, worst_wh = data.warehouses[0], data.warehouses[-1]
        answer = (
            f"{fastest.mandi_name} ({fastest.mandi_id}, {fastest.state}) has the lowest average transit at {fastest.transit_hours:.1f} h over {fastest.trips} trips, "
            f"while {slowest.mandi_name} is the slowest at {slowest.transit_hours:.1f} h. By destination, {best_wh.destination_warehouse} clears fastest "
            f"({best_wh.transit_hours:.2f} h) and {worst_wh.destination_warehouse} slowest ({worst_wh.transit_hours:.2f} h). Network delay rate (>24 h) is {data.totals.delay_rate:.2f}%."
        )
        evidence = [f"{data.totals.transport_records:,} transport trips · {data.data_quality.transport_invalid_transit_pct:.1f}% flagged invalid transit", f"Scope: {scope_label}", "Source: transport_cleaned.csv"]
        chart = [AgentChartPoint(label=row.mandi_id.replace("MANDI", "M"), value=row.transit_hours, unit="h") for row in routed[:6]]


    elif any(phrase in query for phrase in (
        "highest average modal price",
        "highest average price",
        "top 5 mandis",
        "top five mandis",
        "highest modal price"
    )):
        intent = "top-mandis-by-modal-price"

        ranked = sorted(
            scoped,
            key=lambda row: row.modal_price,
            reverse=True
        )[:5]

        if ranked:
            listed = "; ".join(
                f"{row.mandi_id} - {row.mandi_name}: {money(row.modal_price)}/qtl"
                for row in ranked
            )

            answer = (
                f"Top 5 mandis with the highest average modal price for {crop}: "
                f"{listed}."
            )

            evidence = [
                f"{summary.price_records:,} price rows for {crop}",
                "Ranking uses average modal_price per mandi",
                "Source: price_and_msp_cleaned.csv + mandi_master_cleaned.csv"
            ]

            chart = [
                AgentChartPoint(
                    label=row.mandi_id.replace("MANDI", "M"),
                    value=round(row.modal_price, 2),
                    unit="₹"
                )
                for row in ranked
            ]
        else:
            answer = f"No modal-price data was found for {crop}."
            evidence = ["No matching mandi price records"]
            chart = []

    
    elif "compare" in query or state or any(word in query for word in ("across", "versus", " vs ")):
        intent = "crop-comparison"
        if (state or "mandi" in query) and scoped:
            ranked = sorted(scoped, key=lambda row: row.modal_price, reverse=True)
            top = ranked[:5]
            answer = (
                f"{crop} modal prices across {scope_label}: {top[0].mandi_name} leads at {money(top[0].modal_price)}/qtl and {ranked[-1].mandi_name} trails at "
                f"{money(ranked[-1].modal_price)}/qtl against an MSP of {money(summary.msp)}. {sum(1 for row in ranked if row.price_gap < 0)} of {len(ranked)} mandis average below MSP."
            )
            evidence = [f"{sum(row.price_records for row in ranked):,} price rows for {crop} in {scope_label}", "Ranking uses mean modal_price per mandi", "Source: price_and_msp_cleaned.csv + mandi_master_cleaned.csv"]
            chart = [AgentChartPoint(label=row.mandi_id.replace("MANDI", "M"), value=round(row.modal_price, 2), unit="₹") for row in top]
        else:
            ranked = sorted(data.crop_summaries, key=lambda item: item.modal_price, reverse=True)
            comparison = "; ".join(f"{item.crop_name} {money(item.modal_price)} ({item.price_gap:+,.0f} vs MSP)" for item in ranked)
            answer = f"Average modal price by crop: {comparison}. {crop} has {summary.below_msp_percentage:.1f}% of records below MSP."
            evidence = [f"{data.totals.price_records:,} price rows across {len(CROPS)} crops", "Source: price_and_msp_cleaned.csv"]
            chart = [AgentChartPoint(label=item.crop_name, value=round(item.modal_price, 2), unit="₹") for item in ranked]
    else:
        intent = "msp-risk"
        below = sorted((row for row in scoped if row.price_gap < 0), key=lambda row: row.price_gap)
        if below:
            listed = ", ".join(f"{row.mandi_name} ({money(abs(row.price_gap))} under)" for row in below[:5])
            answer = (
                f"{len(below)} of {len(scoped)} {scope_label} average below MSP for {crop}. Deepest gaps: {listed}. "
                f"Network-wide, {crop} modal is {money(summary.modal_price)} vs MSP {money(summary.msp)} with {summary.below_msp_percentage:.1f}% of records below the floor."
            )
        else:
            answer = f"None of the {len(scoped)} {scope_label} average below MSP for {crop}. {crop} modal is {money(summary.modal_price)} vs MSP {money(summary.msp)}; {summary.below_msp_percentage:.1f}% of individual records still fall below the floor."
        evidence = [f"{summary.price_records:,} price rows for {crop}", f"{summary.below_msp_records:,} records below MSP · {summary.above_msp_records:,} above", "Source: price_and_msp_cleaned.csv"]
        chart = [AgentChartPoint(label=row.mandi_id.replace("MANDI", "M"), value=round(row.price_gap, 2), unit="₹") for row in below[:6]]

    return AgentAnswer(answer=answer, intent=intent, source=data.source, grounded_at=data.fetched_at, evidence=evidence, chart=chart, mode="rules")
