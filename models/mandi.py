from datetime import datetime

from pydantic import BaseModel


class MandiCropBreakdown(BaseModel):
    crop_name: str
    modal_price: float
    msp: float
    price_gap: float
    arrival_quantity_qtl: float
    farmer_count: int
    price_records: int
    below_msp_percentage: float


class PriceHistoryPoint(BaseModel):
    label: str
    modal_price: float
    min_price: float
    max_price: float
    msp: float
    records: int


class ArrivalHistoryPoint(BaseModel):
    label: str
    arrival_quantity_qtl: float
    farmer_count: int
    records: int


class TripLogEntry(BaseModel):
    trip_id: str
    destination_warehouse: str
    departure_time: str
    arrival_time: str
    transit_hours: float
    distance_km: float
    vehicle_no: str
    driver_id: str
    quality_flag: str | None
    delayed: bool


class WarehouseBreakdown(BaseModel):
    destination_warehouse: str
    trips: int
    transit_hours: float
    delay_rate: float
    distance_km: float


class MandiDetailResponse(BaseModel):
    source: str
    fetched_at: datetime
    selected_crop: str
    mandi_id: str
    mandi_name: str
    district: str
    state: str
    mandi_type: str
    total_area_acres: float
    latitude: float
    longitude: float
    risk: str
    destination_warehouse: str
    modal_price: float
    msp: float
    price_gap: float
    below_msp_percentage: float
    arrival_quantity_qtl: float
    farmer_count: int
    price_records: int
    arrival_records: int
    arrivals_missing_quantity: int
    transit_hours: float
    delay_rate: float
    trips: int
    delayed_trips: int
    invalid_transit_trips: int
    first_date: str
    last_date: str
    crop_breakdown: list[MandiCropBreakdown]
    price_history: list[PriceHistoryPoint]
    arrival_history: list[ArrivalHistoryPoint]
    warehouse_breakdown: list[WarehouseBreakdown]
    trip_log: list[TripLogEntry]
