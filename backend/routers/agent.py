from fastapi import APIRouter

from models.agent import AgentAnswer, AgentAskRequest
from routers.data_sync import canonical_crop, sync_cleaned_data

router = APIRouter(prefix="/agent", tags=["agent"])


def money(value: float) -> str:
    return f"₹{value:,.2f}"


@router.post("/ask", response_model=AgentAnswer)
async def ask_agent(request: AgentAskRequest) -> AgentAnswer:
    sync = await sync_cleaned_data()
    requested_crop = canonical_crop(request.crop_name)
    metrics = {metric.crop_name: metric for metric in sync.crop_metrics}
    crop = requested_crop if requested_crop in metrics else "Wheat"
    metric = metrics.get(crop) or next(iter(sync.crop_metrics))
    query = request.query.lower()
    price_gap = metric.avg_modal_price - metric.avg_msp

    if any(word in query for word in ("weather", "rain", "temperature", "humidity")):
        intent = "weather-impact"
        answer = (
            f"The cleaned weather baseline averages {sync.weather.avg_temperature_c:.1f}°C, "
            f"{sync.weather.avg_rainfall_mm:.1f} mm rainfall, and {sync.weather.avg_humidity_percent:.1f}% humidity. "
            f"Rainfall and arrivals move together at {sync.weather.rainfall_arrivals_correlation:.2f} correlation."
        )
        evidence = [
            f"{sync.weather.readings_count:,} weather sensor rows",
            f"{sync.weather.rainfall_arrivals_correlation:.2f} rainfall–arrivals correlation",
            "Source: weather_cleaned.csv + daily_rainfall.csv + daily_arrivals.csv",
        ]
    elif any(word in query for word in ("transit", "warehouse", "route", "delay", "logistics")):
        intent = "route-health"
        fastest = min(sync.warehouse_transit, key=lambda item: item.transit_hours)
        slowest = max(sync.warehouse_transit, key=lambda item: item.transit_hours)
        answer = (
            f"{fastest.destination_warehouse} is the fastest cleaned route at {fastest.transit_hours:.2f} hours. "
            f"{slowest.destination_warehouse} is the slowest at {slowest.transit_hours:.2f} hours. "
            f"For {crop}, the current modal signal is {money(metric.avg_modal_price)} per quintal."
        )
        evidence = [
            f"Fastest: {fastest.destination_warehouse} · {fastest.transit_hours:.2f}h",
            f"Slowest: {slowest.destination_warehouse} · {slowest.transit_hours:.2f}h",
            "Source: warehouse_transit.csv",
        ]
    elif any(word in query for word in ("compare", "crop", "grain")) and len(metrics) > 1:
        intent = "crop-comparison"
        ranked = sorted(metrics.values(), key=lambda item: item.avg_modal_price, reverse=True)[:3]
        comparison = "; ".join(f"{item.crop_name} {money(item.avg_modal_price)} modal" for item in ranked)
        answer = f"Across the synced crop profiles, the highest modal signals are {comparison}. {crop} is at {money(metric.avg_modal_price)} with {metric.below_msp_percentage:.1f}% of records below MSP."
        evidence = [
            f"{metric.record_count:,} price rows for {crop}",
            "Ranking uses average modal_price from price_and_msp_cleaned.csv",
        ]
    else:
        intent = "msp-risk"
        direction = "above" if price_gap >= 0 else "below"
        top_hubs = ", ".join(item.mandi_id for item in sync.top_mandis[:3])
        answer = (
            f"{crop} is {money(abs(price_gap))} {direction} MSP: modal {money(metric.avg_modal_price)} vs "
            f"MSP {money(metric.avg_msp)} per quintal. {metric.below_msp_percentage:.1f}% of synced price records are below MSP. "
            f"Review the highest-volume hubs first: {top_hubs}."
        )
        evidence = [
            f"{metric.record_count:,} price rows for {crop}",
            f"{metric.below_msp_percentage:.2f}% below-MSP records",
            "Source: price_and_msp_cleaned.csv + below_msp_by_crop.csv",
        ]

    return AgentAnswer(
        answer=answer,
        intent=intent,
        source=sync.source,
        grounded_at=sync.fetched_at,
        evidence=evidence,
    )