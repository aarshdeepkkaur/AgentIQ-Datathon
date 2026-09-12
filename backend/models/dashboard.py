from datetime import datetime

from pydantic import BaseModel


class CropSummary(BaseModel):
    crop_name: str
    icon: str
    modal_price: float
    msp: float
    price_gap: float
    arrivals_qtl: float
    below_msp_percentage: float
    above_msp_records: int
    below_msp_records: int
    price_records: int
    arrival_records: int
    avg_transit_hours: float
    delay_rate: float
    trend_percentage: float
    season: str
    outlook: str


class MandiRow(BaseModel):
    mandi_id: str
    mandi_name: str
    district: str
    state: str
    mandi_type: str
    total_area_acres: float
    modal_price: float
    msp: float
    price_gap: float
    arrival_quantity_qtl: float
    farmer_count: int
    price_records: int
    below_msp_percentage: float
    transit_hours: float
    delay_rate: float
    trips: int
    destination_warehouse: str
    weather: str
    risk: str
    latitude: float
    longitude: float
    position_x: float
    position_y: float


class TrendPoint(BaseModel):
    label: str
    modal_price: float
    msp: float
    arrivals_qtl: float


class PriceTrend(BaseModel):
    daily: list[TrendPoint]
    weekly: list[TrendPoint]
    monthly: list[TrendPoint]


class WeatherPoint(BaseModel):
    label: str
    temperature_c: float
    rainfall_mm: float
    humidity_percent: float
    arrivals_qtl: float


class WarehousePerformance(BaseModel):
    destination_warehouse: str
    transit_hours: float
    delay_rate: float
    trips: int
    distance_km: float


class MspDistribution(BaseModel):
    crop_name: str
    above_msp: int
    below_msp: int
    below_msp_percentage: float


class WeatherSummary(BaseModel):
    avg_temperature_c: float
    avg_rainfall_mm: float
    avg_humidity_percent: float
    latest_temperature_c: float
    latest_rainfall_mm: float
    latest_humidity_percent: float
    latest_reading_date: str
    rainfall_arrivals_correlation: float
    rainfall_arrivals_correlation_overlap: float
    readings_count: int


class NetworkTotals(BaseModel):
    total_arrivals_qtl: float
    avg_modal_price: float
    avg_msp: float
    below_msp_percentage: float
    avg_transit_hours: float
    delay_rate: float
    active_mandis: int
    price_records: int
    arrival_records: int
    transport_records: int
    weather_records: int
    date_from: str
    date_to: str


class DataQuality(BaseModel):
    arrivals_missing_quantity_pct: float
    arrivals_invalid_flag_pct: float
    weather_missing_temperature_pct: float
    weather_missing_rainfall_pct: float
    transport_invalid_transit_pct: float
    prices_missing_msp_pct: float


class DashboardResponse(BaseModel):
    source: str
    fetched_at: datetime
    selected_crop: str
    crops: list[str]
    states: list[str]
    crop_summary: CropSummary
    crop_summaries: list[CropSummary]
    mandis: list[MandiRow]
    price_trend: PriceTrend
    weather_series: list[WeatherPoint]
    warehouses: list[WarehousePerformance]
    msp_distribution: list[MspDistribution]
    weather: WeatherSummary
    totals: NetworkTotals
    data_quality: DataQuality
