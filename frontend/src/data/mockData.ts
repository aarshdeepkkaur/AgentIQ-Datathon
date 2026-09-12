export type CropName =
  | "Wheat"
  | "Rice"
  | "Maize"
  | "Cotton"
  | "Mustard"
  | "Sugarcane"
  | "Soybean"
  | "Gram";

export type RiskLevel = "low" | "medium" | "high";

export interface MandiMaster {
  mandi_id: string;
  mandi_name: string;
  district: string;
  state: string;
  mandi_type: string;
  total_area_acres: number;
}

export interface MandiArrival {
  mandi_id: string;
  crop_name: CropName;
  date: string;
  arrival_quantity_qtl: number;
  farmer_count: number;
  quality_flag: string | null;
}

export interface PriceAndMsp {
  mandi_id: string;
  crop_name: CropName;
  district: string;
  date: string;
  min_price: number;
  max_price: number;
  modal_price: number;
  msp: number;
}

export interface WeatherSensor {
  timestamp_ist: string;
  temperature_c: number;
  rainfall_mm: number;
  humidity_percent: number;
}

export interface TransportLogistics {
  mandi_id: string;
  destination_warehouse: string;
  departure_time_clean: string;
  arrival_time_clean: string;
  transit_hours: number;
  distance_km: number;
  vehicle_no_clean: string;
  driver_id: string;
  quality_flag: string | null;
}

export interface CropProfile {
  modal: number;
  msp: number;
  arrivals: number;
  belowMsp: number;
  transit: number;
  delay: number;
  trend: number;
  season: string;
  outlook: string;
  icon: string;
}

export type CropProfileMap = Record<CropName, CropProfile>;

export interface CropSyncMetric {
  crop_name: string;
  arrivals_qtl: number;
  avg_modal_price: number;
  avg_msp: number;
  below_msp_percentage: number;
  record_count: number;
}

export interface MandiVolumeSync {
  mandi_id: string;
  mandi_name: string;
  district: string;
  state: string;
  arrival_quantity_qtl: number;
}

export interface WarehouseTransitSync {
  destination_warehouse: string;
  transit_hours: number;
}

export interface DataSyncResponse {
  source: string;
  fetched_at: string;
  rows_loaded: Record<string, number>;
  crop_metrics: CropSyncMetric[];
  top_mandis: MandiVolumeSync[];
  warehouse_transit: WarehouseTransitSync[];
}

export interface MandiRow extends MandiMaster {
  modalPrice: number;
  msp: number;
  priceGap: number;
  arrivalQuantity: number;
  transitHours: number;
  weather: string;
  risk: RiskLevel;
  destinationWarehouse: string;
  position: { x: number; y: number };
  latitude: number;
  longitude: number;
}

export const CROPS: CropName[] = [
  "Wheat",
  "Rice",
  "Maize",
  "Cotton",
  "Mustard",
  "Sugarcane",
  "Soybean",
  "Gram",
];

export const cleanedDataSource =
  "aarshdeepkkaur/AgentIQ-Datathon · data/cleaned · 57 mandis parsed";

export const mandi_master: MandiMaster[] = [
  { mandi_id: "MANDI001", mandi_name: "Hyderabad Mandi", district: "Ludhiana", state: "Punjab", mandi_type: "Private", total_area_acres: 11 },
  { mandi_id: "MANDI048", mandi_name: "Chittoor Mandi", district: "Muzaffarnagar", state: "Uttar Pradesh", mandi_type: "APMC", total_area_acres: 28 },
  { mandi_id: "MANDI050", mandi_name: "Durg Market", district: "Muzaffarnagar", state: "Uttar Pradesh", mandi_type: "Direct", total_area_acres: 42 },
  { mandi_id: "MANDI026", mandi_name: "Nashik Agri Hub", district: "Nashik", state: "Maharashtra", mandi_type: "APMC", total_area_acres: 36 },
  { mandi_id: "MANDI012", mandi_name: "Indore Grain Yard", district: "Indore", state: "Madhya Pradesh", mandi_type: "Private", total_area_acres: 31 },
  { mandi_id: "MANDI014", mandi_name: "Amritsar Agri Yard", district: "Amritsar", state: "Punjab", mandi_type: "Direct", total_area_acres: 22 },
  { mandi_id: "MANDI037", mandi_name: "Jorhat Grain Market", district: "Kurukshetra", state: "Haryana", mandi_type: "APMC", total_area_acres: 19 },
  { mandi_id: "MANDI029", mandi_name: "Kota Produce Hub", district: "Kota", state: "Rajasthan", mandi_type: "Private", total_area_acres: 26 },
];

export const mandi_arrivals: MandiArrival[] = [
  { mandi_id: "MANDI001", crop_name: "Wheat", date: "2026-06-04", arrival_quantity_qtl: 448.41, farmer_count: 128, quality_flag: null },
  { mandi_id: "MANDI048", crop_name: "Rice", date: "2026-06-02", arrival_quantity_qtl: 512.2, farmer_count: 84, quality_flag: null },
  { mandi_id: "MANDI050", crop_name: "Maize", date: "2026-05-30", arrival_quantity_qtl: 392.12, farmer_count: 66, quality_flag: null },
  { mandi_id: "MANDI026", crop_name: "Wheat", date: "2026-06-01", arrival_quantity_qtl: 332.54, farmer_count: 33, quality_flag: null },
  { mandi_id: "MANDI012", crop_name: "Mustard", date: "2026-05-28", arrival_quantity_qtl: 281.7, farmer_count: 51, quality_flag: null },
  { mandi_id: "MANDI014", crop_name: "Cotton", date: "2026-05-26", arrival_quantity_qtl: 196.4, farmer_count: 29, quality_flag: null },
  { mandi_id: "MANDI037", crop_name: "Rice", date: "2026-05-23", arrival_quantity_qtl: 176.8, farmer_count: 21, quality_flag: "missing_unit_recovered" },
  { mandi_id: "MANDI029", crop_name: "Maize", date: "2026-05-21", arrival_quantity_qtl: 154.6, farmer_count: 17, quality_flag: null },
];

export const price_and_msp: PriceAndMsp[] = [
  { mandi_id: "MANDI001", crop_name: "Wheat", district: "Ludhiana", date: "2026-07-26", min_price: 3650, max_price: 4025, modal_price: 3850, msp: 3720 },
  { mandi_id: "MANDI048", crop_name: "Rice", district: "Muzaffarnagar", date: "2026-07-17", min_price: 1880, max_price: 2290, modal_price: 2140, msp: 2183 },
  { mandi_id: "MANDI050", crop_name: "Maize", district: "Muzaffarnagar", date: "2026-07-12", min_price: 2140, max_price: 2590, modal_price: 2410, msp: 2225 },
  { mandi_id: "MANDI026", crop_name: "Wheat", district: "Nashik", date: "2026-07-10", min_price: 3520, max_price: 3910, modal_price: 3770, msp: 3720 },
  { mandi_id: "MANDI012", crop_name: "Mustard", district: "Indore", date: "2026-07-07", min_price: 5200, max_price: 5740, modal_price: 5485, msp: 5650 },
  { mandi_id: "MANDI014", crop_name: "Cotton", district: "Amritsar", date: "2026-07-04", min_price: 6810, max_price: 7480, modal_price: 7210, msp: 6620 },
  { mandi_id: "MANDI037", crop_name: "Rice", district: "Kurukshetra", date: "2026-07-01", min_price: 1820, max_price: 2190, modal_price: 2050, msp: 2183 },
  { mandi_id: "MANDI029", crop_name: "Maize", district: "Kota", date: "2026-06-28", min_price: 2060, max_price: 2510, modal_price: 2315, msp: 2225 },
];

export const weather_sensors: WeatherSensor[] = [
  { timestamp_ist: "2026-08-28 00:00:00+05:30", temperature_c: 20, rainfall_mm: 43.8, humidity_percent: 46 },
  { timestamp_ist: "2026-08-29 00:00:00+05:30", temperature_c: 21.4, rainfall_mm: 36.2, humidity_percent: 51 },
  { timestamp_ist: "2026-08-30 00:00:00+05:30", temperature_c: 22.8, rainfall_mm: 29.6, humidity_percent: 58 },
  { timestamp_ist: "2026-08-31 00:00:00+05:30", temperature_c: 24.1, rainfall_mm: 18.4, humidity_percent: 55 },
  { timestamp_ist: "2026-09-01 00:00:00+05:30", temperature_c: 23.6, rainfall_mm: 26.8, humidity_percent: 61 },
  { timestamp_ist: "2026-09-02 00:00:00+05:30", temperature_c: 22.2, rainfall_mm: 41.6, humidity_percent: 67 },
];

export const transport_logistics: TransportLogistics[] = [
  { mandi_id: "MANDI050", destination_warehouse: "WH-CENTRAL", departure_time_clean: "2026-04-30 20:08:22", arrival_time_clean: "2026-05-01 05:26:00", transit_hours: 9.3, distance_km: 492, vehicle_no_clean: "", driver_id: "DRV264", quality_flag: null },
  { mandi_id: "MANDI029", destination_warehouse: "WH-WEST", departure_time_clean: "2026-04-10 04:15:00", arrival_time_clean: "2026-04-10 09:51:00", transit_hours: 5.6, distance_km: 263.5, vehicle_no_clean: "", driver_id: "DRV540", quality_flag: null },
  { mandi_id: "MANDI026", destination_warehouse: "WH-SOUTH", departure_time_clean: "2026-07-18 16:34:00", arrival_time_clean: "2026-07-18 22:46:00", transit_hours: 6.2, distance_km: 276.5, vehicle_no_clean: "UP-50-BC-6882", driver_id: "DRV722", quality_flag: null },
  { mandi_id: "MANDI001", destination_warehouse: "WH-NORTH", departure_time_clean: "2026-07-22 06:20:00", arrival_time_clean: "2026-07-22 20:45:00", transit_hours: 14.4, distance_km: 606, vehicle_no_clean: "PB-10-AX-9081", driver_id: "DRV118", quality_flag: null },
  { mandi_id: "MANDI048", destination_warehouse: "WH-CENTRAL", departure_time_clean: "2026-07-20 08:05:00", arrival_time_clean: "2026-07-21 00:20:00", transit_hours: 16.25, distance_km: 522, vehicle_no_clean: "UP-32-KL-4112", driver_id: "DRV231", quality_flag: null },
  { mandi_id: "MANDI012", destination_warehouse: "WH-EAST", departure_time_clean: "2026-07-19 12:00:00", arrival_time_clean: "2026-07-20 02:42:00", transit_hours: 14.7, distance_km: 580, vehicle_no_clean: "MP-09-RQ-0098", driver_id: "DRV418", quality_flag: "invalid_negative_transit_recovered" },
];

export const cropProfiles: Record<CropName, CropProfile> = {
  Wheat: { modal: 3797.82, msp: 3719.78, arrivals: 629121, belowMsp: 40.16, transit: 12.99, delay: 0.28, trend: 2.1, season: "Rabi · Oct–Mar", outlook: "Firm demand with a stable MSP cushion", icon: "W" },
  Rice: { modal: 2142, msp: 2183, arrivals: 574380, belowMsp: 43.8, transit: 13.24, delay: 0.34, trend: -1.2, season: "Kharif · Jun–Nov", outlook: "Export softness is widening the floor gap", icon: "R" },
  Maize: { modal: 2410, msp: 2225, arrivals: 520797, belowMsp: 31.4, transit: 12.58, delay: 0.21, trend: 3.8, season: "Kharif · Jun–Sep", outlook: "Strong feed demand keeps the curve positive", icon: "M" },
  Cotton: { modal: 7210, msp: 6620, arrivals: 468120, belowMsp: 18.7, transit: 12.44, delay: 0.19, trend: 4.6, season: "Kharif · Oct–Feb", outlook: "Premium quality lots are outperforming the floor", icon: "C" },
  Mustard: { modal: 5485, msp: 5650, arrivals: 520083, belowMsp: 36.9, transit: 13.08, delay: 0.29, trend: 0.9, season: "Rabi · Nov–Mar", outlook: "Oilseed demand is balancing a soft harvest", icon: "Mu" },
  Sugarcane: { modal: 3490, msp: 3420, arrivals: 391640, belowMsp: 24.4, transit: 13.42, delay: 0.37, trend: 2.7, season: "Annual · Oct–Apr", outlook: "Mill intake is absorbing near-term supply", icon: "S" },
  Soybean: { modal: 4630, msp: 4892, arrivals: 338120, belowMsp: 46.3, transit: 13.68, delay: 0.43, trend: -2.6, season: "Kharif · Jun–Oct", outlook: "Weather volatility is pressuring the spot floor", icon: "So" },
  Gram: { modal: 5780, msp: 5440, arrivals: 298740, belowMsp: 20.8, transit: 12.72, delay: 0.25, trend: 2.9, season: "Rabi · Oct–Mar", outlook: "Healthy protein demand supports the spread", icon: "G" },
};

export function mergeCropProfiles(sync?: DataSyncResponse): CropProfileMap {
  const merged: CropProfileMap = { ...cropProfiles };
  for (const metric of sync?.crop_metrics ?? []) {
    if (!CROPS.includes(metric.crop_name as CropName)) continue;
    const crop = metric.crop_name as CropName;
    const existing = merged[crop];
    merged[crop] = {
      ...existing,
      arrivals: metric.arrivals_qtl || existing.arrivals,
      modal: metric.avg_modal_price || existing.modal,
      msp: metric.avg_msp || existing.msp,
      belowMsp: metric.below_msp_percentage || existing.belowMsp,
    };
  }
  return merged;
}

const MANDI_SHARES = [0.12, 0.118, 0.116, 0.108, 0.09, 0.08, 0.07, 0.06];
const POSITIONS = [
  { x: 26, y: 48 },
  { x: 37, y: 32 },
  { x: 51, y: 59 },
  { x: 62, y: 39 },
  { x: 72, y: 55 },
  { x: 34, y: 70 },
  { x: 55, y: 24 },
  { x: 79, y: 30 },
];

const COORDINATES = [
  { latitude: 30.9, longitude: 75.85 },
  { latitude: 29.97, longitude: 77.7 },
  { latitude: 21.19, longitude: 81.28 },
  { latitude: 20.0, longitude: 73.78 },
  { latitude: 22.72, longitude: 75.86 },
  { latitude: 31.63, longitude: 74.87 },
  { latitude: 29.97, longitude: 76.88 },
  { latitude: 25.18, longitude: 75.84 },
];

export function getMandiRows(crop: CropName, profiles: CropProfileMap = cropProfiles, sync?: DataSyncResponse): MandiRow[] {
  const profile = profiles[crop];
  return mandi_master.map((mandi, index) => {
    const modalPrice = Math.round(profile.modal + [52, -94, 38, -28, 116, -142, 66, -64][index]);
    const msp = Math.round(profile.msp + [0, 0, 0, 0, 14, 0, 0, 0][index]);
    const priceGap = modalPrice - msp;
    const syncedMandi = sync?.top_mandis.find((item) => item.mandi_id === mandi.mandi_id);
    const warehouse = ["WH-NORTH", "WH-CENTRAL", "WH-CENTRAL", "WH-SOUTH", "WH-WEST", "WH-NORTH", "WH-EAST", "WH-WEST"][index];
    const syncedWarehouse = sync?.warehouse_transit.find((item) => item.destination_warehouse === warehouse);
    const transitHours = Number((syncedWarehouse?.transit_hours ?? profile.transit + [0.7, 1.2, -1.6, -0.4, 0.35, 0.1, 0.62, 1.05][index]).toFixed(1));
    const risk: RiskLevel = priceGap < -80 || transitHours > 14 ? "high" : priceGap < 0 || transitHours > 13.5 ? "medium" : "low";
    return {
      ...mandi,
      modalPrice,
      msp,
      priceGap,
      arrivalQuantity: syncedMandi?.arrival_quantity_qtl ?? Math.round(profile.arrivals * MANDI_SHARES[index]),
      transitHours,
      weather: ["24°C · Clear", "22°C · Light rain", "26°C · Clear", "23°C · Cloudy", "25°C · Clear", "21°C · Rain", "20°C · Cloudy", "27°C · Clear"][index],
      risk,
      destinationWarehouse: warehouse,
      position: POSITIONS[index],
      ...COORDINATES[index],
    };
  });
}

export function getPriceTrend(crop: CropName, profiles: CropProfileMap = cropProfiles) {
  const profile = profiles[crop];
  const points = [
    ["01 Aug", -84], ["08 Aug", -41], ["15 Aug", -62], ["22 Aug", -12], ["29 Aug", 28], ["05 Sep", 8], ["12 Sep", 64], ["19 Sep", 42],
  ];
  return points.map(([date, offset], index) => ({ date, modal: Math.round(profile.modal + Number(offset) + (index % 2 ? 18 : 0)), msp: Math.round(profile.msp), arrivals: Math.round(profile.arrivals / 24 + index * 520) }));
}

export const weatherSeries = weather_sensors.map((reading, index) => ({
  date: `Aug ${28 + index}`,
  rainfall: reading.rainfall_mm,
  temperature: reading.temperature_c,
  humidity: reading.humidity_percent,
}));

export const warehousePerformance = [
  { warehouse: "WH-WEST", hours: 13.1, delay: 0.22 },
  { warehouse: "WH-CENTRAL", hours: 13.0, delay: 0.31 },
  { warehouse: "WH-NORTH", hours: 12.8, delay: 0.18 },
  { warehouse: "WH-SOUTH", hours: 12.6, delay: 0.27 },
  { warehouse: "WH-EAST", hours: 13.4, delay: 0.42 },
];
