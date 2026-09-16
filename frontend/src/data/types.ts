// Hand-written mirrors of the Pydantic models in backend/models/dashboard.py and backend/models/agent.py.

export type CropName = "Wheat" | "Rice" | "Maize" | "Cotton" | "Mustard" | "Sugarcane";
export type RiskLevel = "low" | "medium" | "high";

export const CROPS: CropName[] = ["Wheat", "Rice", "Maize", "Cotton", "Mustard", "Sugarcane"];

export interface CropSummary {
  crop_name: string;
  icon: string;
  modal_price: number;
  msp: number;
  price_gap: number;
  arrivals_qtl: number;
  below_msp_percentage: number;
  above_msp_records: number;
  below_msp_records: number;
  price_records: number;
  arrival_records: number;
  avg_transit_hours: number;
  delay_rate: number;
  trend_percentage: number;
  season: string;
  outlook: string;
}

export interface MandiRow {
  mandi_id: string;
  mandi_name: string;
  district: string;
  state: string;
  mandi_type: string;
  total_area_acres: number;
  modal_price: number;
  msp: number;
  price_gap: number;
  arrival_quantity_qtl: number;
  farmer_count: number;
  price_records: number;
  below_msp_percentage: number;
  transit_hours: number;
  delay_rate: number;
  trips: number;
  destination_warehouse: string;
  weather: string;
  risk: RiskLevel;
  latitude: number;
  longitude: number;
  position_x: number;
  position_y: number;
}

export interface TrendPoint {
  label: string;
  modal_price: number;
  msp: number;
  arrivals_qtl: number;
}

export interface PriceTrend {
  daily: TrendPoint[];
  weekly: TrendPoint[];
  monthly: TrendPoint[];
}

export interface WeatherPoint {
  label: string;
  temperature_c: number;
  rainfall_mm: number;
  humidity_percent: number;
  arrivals_qtl: number;
}

export interface WarehousePerformance {
  destination_warehouse: string;
  transit_hours: number;
  delay_rate: number;
  trips: number;
  distance_km: number;
}

export interface MspDistribution {
  crop_name: string;
  above_msp: number;
  below_msp: number;
  below_msp_percentage: number;
}

export interface WeatherSummary {
  avg_temperature_c: number;
  avg_rainfall_mm: number;
  avg_humidity_percent: number;
  latest_temperature_c: number;
  latest_rainfall_mm: number;
  latest_humidity_percent: number;
  latest_reading_date: string;
  rainfall_arrivals_correlation: number;
  rainfall_arrivals_correlation_overlap: number;
  readings_count: number;
}

export interface NetworkTotals {
  total_arrivals_qtl: number;
  avg_modal_price: number;
  avg_msp: number;
  below_msp_percentage: number;
  avg_transit_hours: number;
  delay_rate: number;
  active_mandis: number;
  price_records: number;
  arrival_records: number;
  transport_records: number;
  weather_records: number;
  date_from: string;
  date_to: string;
}

export interface DataQuality {
  arrivals_missing_quantity_pct: number;
  arrivals_invalid_flag_pct: number;
  weather_missing_temperature_pct: number;
  weather_missing_rainfall_pct: number;
  transport_invalid_transit_pct: number;
  prices_missing_msp_pct: number;
}

export interface DashboardResponse {
  source: string;
  fetched_at: string;
  selected_crop: string;
  filter_from: string | null;
  filter_to: string | null;
  crops: string[];
  states: string[];
  crop_summary: CropSummary;
  crop_summaries: CropSummary[];
  mandis: MandiRow[];
  price_trend: PriceTrend;
  weather_series: WeatherPoint[];
  warehouses: WarehousePerformance[];
  msp_distribution: MspDistribution[];
  weather: WeatherSummary;
  totals: NetworkTotals;
  data_quality: DataQuality;
}

export interface AgentChartPoint {
  label: string;
  value: number;
  unit: string;
}

export interface AgentAnswer {
  answer: string;
  intent: string;
  source: string;
  grounded_at: string;
  evidence: string[];
  chart: AgentChartPoint[];
  mode: "llm" | "rules";
  code: string | null;
  result_preview: string | null;
}

export interface AgentMessage {
  id: string;
  session_id: string;
  role: "user" | "agent";
  text: string;
  crop_name: string;
  created_at: string;
  evidence: string[];
  chart: AgentChartPoint[];
  mode: "llm" | "rules" | null;
  code: string | null;
  result_preview: string | null;
}

export interface AgentHistoryResponse {
  session_id: string;
  messages: AgentMessage[];
}

export type AgentStreamEvent =
  | { event: "stage"; stage: "planning" }
  | { event: "stage"; stage: "executed"; code: string; approach: string; rows: number; preview: string }
  | { event: "stage"; stage: "fallback"; reason: string }
  | { event: "token"; text: string }
  | { event: "done"; answer: AgentAnswer };

// backend/models/alerts.py
export interface RiskAlert {
  id: string;
  type: "below_msp" | "transit_delay" | "trend_drop";
  severity: "high" | "medium";
  mandi_id: string | null;
  mandi_name: string;
  state: string;
  crop_name: string;
  title: string;
  detail: string;
  value: number;
  unit: string;
  occurred_at: string;
}

export interface AlertsResponse {
  source: string;
  fetched_at: string;
  selected_crop: string;
  generated_at: string;
  total: number;
  high: number;
  alerts: RiskAlert[];
}

// backend/models/mandi.py
export interface MandiCropBreakdown {
  crop_name: string;
  modal_price: number;
  msp: number;
  price_gap: number;
  arrival_quantity_qtl: number;
  farmer_count: number;
  price_records: number;
  below_msp_percentage: number;
}

export interface PriceHistoryPoint {
  label: string;
  modal_price: number;
  min_price: number;
  max_price: number;
  msp: number;
  records: number;
}

export interface ArrivalHistoryPoint {
  label: string;
  arrival_quantity_qtl: number;
  farmer_count: number;
  records: number;
}

export interface TripLogEntry {
  trip_id: string;
  destination_warehouse: string;
  departure_time: string;
  arrival_time: string;
  transit_hours: number;
  distance_km: number;
  vehicle_no: string;
  driver_id: string;
  quality_flag: string | null;
  delayed: boolean;
}

export interface WarehouseBreakdown {
  destination_warehouse: string;
  trips: number;
  transit_hours: number;
  delay_rate: number;
  distance_km: number;
}

export interface MandiDetailResponse {
  source: string;
  fetched_at: string;
  selected_crop: string;
  mandi_id: string;
  mandi_name: string;
  district: string;
  state: string;
  mandi_type: string;
  total_area_acres: number;
  latitude: number;
  longitude: number;
  risk: RiskLevel;
  destination_warehouse: string;
  modal_price: number;
  msp: number;
  price_gap: number;
  below_msp_percentage: number;
  arrival_quantity_qtl: number;
  farmer_count: number;
  price_records: number;
  arrival_records: number;
  arrivals_missing_quantity: number;
  transit_hours: number;
  delay_rate: number;
  trips: number;
  delayed_trips: number;
  invalid_transit_trips: number;
  first_date: string;
  last_date: string;
  crop_breakdown: MandiCropBreakdown[];
  price_history: PriceHistoryPoint[];
  arrival_history: ArrivalHistoryPoint[];
  warehouse_breakdown: WarehouseBreakdown[];
  trip_log: TripLogEntry[];
}

export interface DateWindow {
  from: string;
  to: string;
}

export const windowQuery = (window: DateWindow) => `${window.from ? `&date_from=${window.from}` : ""}${window.to ? `&date_to=${window.to}` : ""}`;

export const formatInr = (value: number, digits = 0) => `₹${value.toLocaleString("en-IN", { maximumFractionDigits: digits, minimumFractionDigits: digits })}`;
export const formatQtl = (value: number) => (value >= 1_000_000 ? `${(value / 1_000_000).toFixed(2)}M` : value >= 1000 ? `${(value / 1000).toFixed(1)}k` : value.toFixed(0));
export const formatDate = (iso: string) => (iso ? new Date(`${iso}T00:00:00`).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "—");
