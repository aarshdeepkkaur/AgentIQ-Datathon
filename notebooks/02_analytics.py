import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"


# ============================================================
# LOAD DATA
# ============================================================

arrivals = pd.read_csv(
    CLEANED_DIR / "mandi_arrivals_cleaned.csv"
)

master = pd.read_csv(
    CLEANED_DIR / "mandi_master_cleaned.csv"
)

prices = pd.read_csv(
    CLEANED_DIR / "price_and_msp_cleaned.csv"
)

weather = pd.read_csv(
    CLEANED_DIR / "weather_cleaned.csv"
)

transport = pd.read_csv(
    CLEANED_DIR / "transport_cleaned.csv"
)


# ============================================================
# DATE CONVERSION
# ============================================================

arrivals["date"] = pd.to_datetime(
    arrivals["date"],
    errors="coerce"
)

prices["date"] = pd.to_datetime(
    prices["date"],
    errors="coerce"
)

weather["timestamp_ist"] = pd.to_datetime(
    weather["timestamp_ist"],
    errors="coerce"
)

transport["departure_time_clean"] = pd.to_datetime(
    transport["departure_time_clean"],
    errors="coerce"
)


# ============================================================
# 1. TOTAL CROP ARRIVALS
# ============================================================

total_arrivals = arrivals[
    "arrival_quantity_qtl"
].sum()

print("\n" + "=" * 70)
print("1. TOTAL CROP ARRIVALS")
print("=" * 70)

print(
    f"Total arrivals: {total_arrivals:,.2f} Quintals"
)


# ============================================================
# 2. AVERAGE WHOLESALE MODAL PRICE
# ============================================================

average_modal_price = prices[
    "modal_price"
].mean()

average_msp = prices[
    "msp"
].mean()

print("\n" + "=" * 70)
print("2. AVERAGE PRICE VS MSP")
print("=" * 70)

print(
    f"Average modal price: ₹{average_modal_price:,.2f}"
)

print(
    f"Average MSP: ₹{average_msp:,.2f}"
)


# ============================================================
# 3. PRICE CRASH INSTANCES
# ============================================================

price_valid = prices[
    ["modal_price", "msp"]
].dropna()

price_crashes = (
    price_valid["modal_price"]
    < price_valid["msp"]
)

crash_count = price_crashes.sum()

crash_rate = (
    crash_count / len(price_valid) * 100
)

print("\n" + "=" * 70)
print("3. PRICE CRASH")
print("=" * 70)

print(
    f"Price crash instances: {crash_count:,}"
)

print(
    f"Price crash rate: {crash_rate:.2f}%"
)


# ============================================================
# 4. TOP 5 MANDIS BY ARRIVAL VOLUME
# ============================================================

top_mandis = (
    arrivals
    .groupby("mandi_id")["arrival_quantity_qtl"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

top_mandis = top_mandis.merge(
    master[
        ["mandi_id", "mandi_name", "district", "state"]
    ],
    on="mandi_id",
    how="left"
)

top_mandis = top_mandis[
    [
        "mandi_id",
        "mandi_name",
        "district",
        "state",
        "arrival_quantity_qtl"
    ]
]

print("\n" + "=" * 70)
print("4. TOP 5 MANDIS")
print("=" * 70)

print(
    top_mandis.to_string(index=False)
)


# ============================================================
# 5. CROP-WISE ARRIVAL DISTRIBUTION
# ============================================================

crop_distribution = (
    arrivals
    .groupby("crop_name")["arrival_quantity_qtl"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

print("\n" + "=" * 70)
print("5. CROP-WISE ARRIVAL DISTRIBUTION")
print("=" * 70)

print(
    crop_distribution.to_string(index=False)
)


# ============================================================
# 6. AVERAGE TRANSIT TIME
# ============================================================

valid_transit = transport[
    "transit_hours"
].dropna()

average_transit = valid_transit.mean()

print("\n" + "=" * 70)
print("6. AVERAGE TRANSIT TIME")
print("=" * 70)

print(
    f"Average transit time: {average_transit:.2f} hours"
)


# ============================================================
# 7. TRANSIT DELAY RATE
# ============================================================
#
# We define a delay as transit time > 24 hours.
# This threshold can be adjusted later based on the dataset.
# ============================================================

delay_threshold = 24

valid_transport = transport[
    transport["transit_hours"].notna()
].copy()

delayed_trips = (
    valid_transport["transit_hours"]
    > delay_threshold
)

delay_count = delayed_trips.sum()

delay_rate = (
    delay_count / len(valid_transport) * 100
)

print("\n" + "=" * 70)
print("7. TRANSIT DELAY RATE")
print("=" * 70)

print(
    f"Delay threshold: {delay_threshold} hours"
)

print(
    f"Delayed trips: {delay_count:,}"
)

print(
    f"Delay rate: {delay_rate:.2f}%"
)


# ============================================================
# 8. AVERAGE TRANSIT TIME BY WAREHOUSE
# ============================================================

warehouse_transit = (
    transport
    .groupby("destination_warehouse")["transit_hours"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

print("\n" + "=" * 70)
print("8. TRANSIT TIME BY WAREHOUSE")
print("=" * 70)

print(
    warehouse_transit.to_string(index=False)
)


# ============================================================
# 9. DAILY ARRIVAL VOLUME
# ============================================================

daily_arrivals = (
    arrivals
    .groupby("date")["arrival_quantity_qtl"]
    .sum()
    .reset_index()
)

daily_arrivals.columns = [
    "date",
    "total_arrivals_qtl"
]

print("\n" + "=" * 70)
print("9. DAILY ARRIVAL TREND")
print("=" * 70)

print(
    daily_arrivals.head(10).to_string(index=False)
)


# ============================================================
# 10. DAILY RAINFALL
# ============================================================

weather["date"] = (
    weather["timestamp_ist"]
    .dt.date
)

daily_rainfall = (
    weather
    .groupby("date")["rainfall_mm"]
    .sum()
    .reset_index()
)

daily_rainfall["date"] = pd.to_datetime(
    daily_rainfall["date"]
)

print("\n" + "=" * 70)
print("10. DAILY RAINFALL")
print("=" * 70)

print(
    daily_rainfall.head(10).to_string(index=False)
)


# ============================================================
# 11. RAINFALL VS ARRIVAL CORRELATION
# ============================================================

weather_arrivals = daily_arrivals.merge(
    daily_rainfall,
    on="date",
    how="inner"
)

correlation = weather_arrivals[
    ["total_arrivals_qtl", "rainfall_mm"]
].corr().iloc[0, 1]

print("\n" + "=" * 70)
print("11. WEATHER IMPACT")
print("=" * 70)

print(
    f"Rainfall vs arrival correlation: {correlation:.4f}"
)


# ============================================================
# 12. PRICE BELOW MSP BY CROP
# ============================================================

prices["below_msp"] = (
    prices["modal_price"]
    < prices["msp"]
)

below_msp_by_crop = (
    prices
    .groupby("crop_name")["below_msp"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
    .reset_index()
)

below_msp_by_crop.columns = [
    "crop_name",
    "below_msp_percentage"
]

print("\n" + "=" * 70)
print("12. PRICE BELOW MSP BY CROP")
print("=" * 70)

print(
    below_msp_by_crop.to_string(index=False)
)


# ============================================================
# 13. SAVE ANALYTICS OUTPUTS
# ============================================================

top_mandis.to_csv(
    CLEANED_DIR / "top_mandis.csv",
    index=False
)

crop_distribution.to_csv(
    CLEANED_DIR / "crop_distribution.csv",
    index=False
)

warehouse_transit.to_csv(
    CLEANED_DIR / "warehouse_transit.csv",
    index=False
)

daily_arrivals.to_csv(
    CLEANED_DIR / "daily_arrivals.csv",
    index=False
)

daily_rainfall.to_csv(
    CLEANED_DIR / "daily_rainfall.csv",
    index=False
)

below_msp_by_crop.to_csv(
    CLEANED_DIR / "below_msp_by_crop.csv",
    index=False
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("ANALYTICS COMPLETE")
print("=" * 70)

print("\nAnalytics files saved in:")
print(CLEANED_DIR)