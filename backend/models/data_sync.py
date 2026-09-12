from datetime import datetime

from pydantic import BaseModel


class CropSyncMetric(BaseModel):
    crop_name: str
    arrivals_qtl: float
    avg_modal_price: float
    avg_msp: float
    below_msp_percentage: float
    record_count: int


class MandiVolumeSync(BaseModel):
    mandi_id: str
    mandi_name: str
    district: str
    state: str
    arrival_quantity_qtl: float


class WarehouseTransitSync(BaseModel):
    destination_warehouse: str
    transit_hours: float


class WeatherSyncSummary(BaseModel):
    avg_temperature_c: float
    avg_rainfall_mm: float
    avg_humidity_percent: float
    rainfall_arrivals_correlation: float
    readings_count: int


class DataSyncResponse(BaseModel):
    source: str
    fetched_at: datetime
    rows_loaded: dict[str, int]
    crop_metrics: list[CropSyncMetric]
    top_mandis: list[MandiVolumeSync]
    warehouse_transit: list[WarehouseTransitSync]
    weather: WeatherSyncSummary