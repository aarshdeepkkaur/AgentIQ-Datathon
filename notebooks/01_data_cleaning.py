import pandas as pd
import numpy as np
import re
import json
import openpyxl
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"

CLEANED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean_mandi_id(value):
    """Convert messy mandi IDs to MANDI### format."""

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().upper()

    # Extract digits
    digits = re.findall(r"\d+", value)

    if not digits:
        return pd.NA

    number = int(digits[-1])

    return f"MANDI{number:03d}"


def clean_crop_name(value):
    """Standardize common crop aliases."""

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().lower()

    aliases = {
        # Wheat
        "wheat": "Wheat",
        "gehun": "Wheat",
        "गेहूं": "Wheat",
        "गेंहू": "Wheat",
        "kanak": "Wheat",

        # Rice
        "rice": "Rice",
        "paddy": "Rice",
        "dhan": "Rice",
        "धान": "Rice",
        "चावल": "Rice",

        # Maize / Corn
        "maize": "Maize",
        "corn": "Maize",
        "makka": "Maize",
        "मक्का": "Maize",

        # Cotton
        "cotton": "Cotton",
        "kapas": "Cotton",
        "कपास": "Cotton",

        # Mustard
        "mustard": "Mustard",
        "sarson": "Mustard",
        "सरसों": "Mustard",

        # Soybean
        "soybean": "Soybean",
        "soya": "Soybean",
        "soyabean": "Soybean",
        "सोयाबीन": "Soybean",

        # Gram
        "gram": "Gram",
        "chana": "Gram",
        "चना": "Gram",

        # Sugarcane
        "sugarcane": "Sugarcane",
        "ganna": "Sugarcane",
        "गन्ना": "Sugarcane",
    }

    if value in aliases:
        return aliases[value]

    # Preserve unknown crop names rather than guessing
    return value.title()


def clean_numeric(value):
    """Extract numeric value from messy strings."""

    if pd.isna(value):
        return np.nan

    value = str(value)

    match = re.search(r"-?\d+(?:\.\d+)?", value)

    if match:
        return float(match.group())

    return np.nan


def clean_price(value):
    """Clean currency-formatted price values."""

    if pd.isna(value):
        return np.nan

    value = str(value)

    # Remove currency symbols/text
    value = value.replace(",", "")
    value = value.replace("₹", "")
    value = value.replace("â‚¹", "")
    value = value.replace("Rs.", "")
    value = value.replace("Rs", "")
    value = value.replace("INR", "")

    match = re.search(r"-?\d+(?:\.\d+)?", value)

    if match:
        return float(match.group())

    return np.nan


def clean_date(series):
    """Parse mixed date formats."""

    return pd.to_datetime(
        series,
        format="mixed",
        errors="coerce",
        dayfirst=False
    )


def standardize_vehicle(value):
    """Standardize vehicle registration formatting."""

    if pd.isna(value):
        return pd.NA

    value = str(value).strip().upper()

    if not value:
        return pd.NA

    # Replace spaces and punctuation with hyphen
    value = re.sub(r"[^A-Z0-9]+", "-", value)

    return value.strip("-")


# ============================================================
# 1. MANDI MASTER
# ============================================================

def clean_mandi_master():

    print("\n" + "=" * 70)
    print("CLEANING MANDI MASTER")
    print("=" * 70)

    path = RAW_DIR / "track3_mandi_master.csv"

    df = pd.read_csv(path)

    before = len(df)

    df["mandi_id"] = df["mandi_id"].apply(clean_mandi_id)

    df["mandi_name"] = (
        df["mandi_name"]
        .astype("string")
        .str.strip()
    )

    df["district"] = (
        df["district"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    df["state"] = (
        df["state"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    df["mandi_type"] = (
        df["mandi_type"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    df["total_area_acres"] = pd.to_numeric(
        df["total_area_acres"],
        errors="coerce"
    )

    # Remove duplicate mandi IDs
    df = df.drop_duplicates(
        subset=["mandi_id"],
        keep="first"
    )

    output = CLEANED_DIR / "mandi_master_cleaned.csv"
    df.to_csv(output, index=False)

    print(f"Rows before: {before}")
    print(f"Rows after : {len(df)}")
    print(f"Saved to   : {output}")

    return df


# ============================================================
# 2. MANDI ARRIVALS
# ============================================================

def clean_mandi_arrivals():

    print("\n" + "=" * 70)
    print("CLEANING MANDI ARRIVALS")
    print("=" * 70)

    path = RAW_DIR / "track3_mandi_arrivals.csv"

       # Chunked read to avoid a single large-allocation spike on this file
    chunks = pd.read_csv(path, chunksize=5000)
    df = pd.concat(chunks, ignore_index=True)

    before = len(df)

    # Remove exact duplicates
    df = df.drop_duplicates()

    # IDs
    df["mandi_id"] = df["mandi_id"].apply(clean_mandi_id)

    # Crop names
    df["crop_name"] = df["crop_name"].apply(clean_crop_name)

    # Dates
    df["date"] = clean_date(df["date"])

    # Quantity
    df["arrival_quantity"] = pd.to_numeric(
        df["arrival_quantity"],
        errors="coerce"
    )

    # Normalize unit
    df["unit"] = (
        df["unit"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    unit_map = {
        "qtl": "qtl",
        "quintal": "qtl",
        "quintals": "qtl",

        "kg": "kg",
        "kgs": "kg",

        "t": "tonne",
        "tonne": "tonne",
        "tonnes": "tonne",
        "ton": "tonne",
    }

    df["unit_clean"] = df["unit"].map(unit_map)

    # Convert EVERYTHING to Quintals
    df["arrival_quantity_qtl"] = np.nan

    qtl_mask = df["unit_clean"] == "qtl"
    kg_mask = df["unit_clean"] == "kg"
    tonne_mask = df["unit_clean"] == "tonne"

    df.loc[qtl_mask, "arrival_quantity_qtl"] = (
        df.loc[qtl_mask, "arrival_quantity"]
    )

    df.loc[kg_mask, "arrival_quantity_qtl"] = (
        df.loc[kg_mask, "arrival_quantity"] / 100
    )

    df.loc[tonne_mask, "arrival_quantity_qtl"] = (
        df.loc[tonne_mask, "arrival_quantity"] * 10
    )

    # Negative quantities are invalid
    negative_mask = df["arrival_quantity_qtl"] < 0

    df["quality_flag"] = pd.NA

    df.loc[
        negative_mask,
        "quality_flag"
    ] = "invalid_negative_quantity"

    df.loc[
        negative_mask,
        "arrival_quantity_qtl"
    ] = np.nan

    # Farmer count
    df["farmer_count"] = pd.to_numeric(
        df["farmer_count"],
        errors="coerce"
    )

    output = CLEANED_DIR / "mandi_arrivals_cleaned.csv"

    df.to_csv(output, index=False)

    print(f"Rows before: {before}")
    print(f"Rows after : {len(df)}")
    print(
        f"Negative quantities fixed: "
        f"{negative_mask.sum()}"
    )
    print(
        f"Missing units: "
        f"{df['unit_clean'].isna().sum()}"
    )
    print(f"Saved to: {output}")

    return df


# ============================================================
# 3. PRICE + MSP
# ============================================================

def clean_price_msp():

    print("\n" + "=" * 70)
    print("CLEANING PRICE + MSP")
    print("=" * 70)

    path = RAW_DIR / "track3_price_and_msp.json"

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    before = len(df)

    # IDs
    df["mandi_id"] = df["mandi_id"].apply(clean_mandi_id)

    # Crop
    df["crop_name"] = df["crop_name"].apply(clean_crop_name)

    # District
    df["district"] = (
        df["district"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    # Date
    df["date"] = clean_date(df["date"])

    # Prices
    price_columns = [
        "min_price",
        "max_price",
        "modal_price",
        "msp"
    ]

    for col in price_columns:
        df[col] = df[col].apply(clean_price)

    output = CLEANED_DIR / "price_and_msp_cleaned.csv"

    df.to_csv(output, index=False)

    print(f"Rows before: {before}")
    print(f"Rows after : {len(df)}")

    for col in price_columns:
        print(
            f"Missing {col}: "
            f"{df[col].isna().sum()}"
        )

    print(f"Saved to: {output}")

    return df


# ============================================================
# 4. WEATHER
# ============================================================

def clean_temperature(value, unit):

    if pd.isna(value):
        return np.nan

    value_str = str(value)

    # Extract numeric temperature
    number_match = re.search(
        r"-?\d+(?:\.\d+)?",
        value_str
    )

    if not number_match:
        return np.nan

    temp = float(number_match.group())

    # Try unit column first
    unit_text = "" if pd.isna(unit) else str(unit).lower()

    # Detect unit from value itself
    if "°f" in value_str.lower() or "fahrenheit" in unit_text:
        return (temp - 32) * 5 / 9

    if "°c" in value_str.lower() or "celsius" in unit_text:
        return temp

    if unit_text in ["f", "f."]:
        return (temp - 32) * 5 / 9

    if unit_text in ["c", "c."]:
        return temp

    # Unknown unit
    return np.nan


def clean_rainfall(value, unit):

    if pd.isna(value):
        return np.nan

    value_str = str(value)

    number_match = re.search(
        r"-?\d+(?:\.\d+)?",
        value_str
    )

    if not number_match:
        return np.nan

    rainfall = float(number_match.group())

    unit_text = "" if pd.isna(unit) else str(unit).lower()

    if (
        "inch" in unit_text
        or unit_text in ["in", "in."]
    ):
        return rainfall * 25.4

    if "mm" in unit_text:
        return rainfall

    return np.nan


# Explicit datetime formats found in the raw weather timestamps
# (after any UTC/IST marker has been stripped out). Each format pins
# down day/month position exactly, so pandas never has to guess.
WEATHER_DATETIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",   # 2026-02-21 12:03:50
    "%Y-%m-%dT%H:%M:%S",   # 2026-07-28T05:02:48
    "%d/%m/%Y %H:%M",      # 01/06/2026 20:19    (day first)
    "%d/%m/%Y",            # 28/08/2026          (day first, no time)
    "%m-%d-%Y %I:%M %p",   # 07-01-2026 05:48 PM (month first, 12h clock)
    "%d-%b-%Y %H:%M:%S",   # 12-Aug-2026 16:58:44
]


def parse_weather_timestamp(series):
    """
    Parse a weather timestamp column that mixes several known formats
    and optional UTC/IST markers. Tries each explicit format in turn
    (never automatic/inferred parsing), so day and month are never
    guessed. Values marked UTC are localized as UTC then converted to
    IST; values marked IST, or with no marker at all, are treated as
    already being in IST. Anything that doesn't match a known format
    becomes NaT via errors="coerce".
    """
    raw = series.astype("string").str.strip()

    utc_mask = raw.str.contains("UTC", case=False, na=False)

    # Strip the timezone marker so only the datetime itself remains
    cleaned = (
        raw
        .str.replace(r"\s*UTC\s*", "", regex=True, case=False)
        .str.replace(r"\s*IST\s*", "", regex=True, case=False)
        .str.strip()
    )

    parsed = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")

    for fmt in WEATHER_DATETIME_FORMATS:
        still_missing = parsed.isna()
        if not still_missing.any():
            break
        parsed.loc[still_missing] = pd.to_datetime(
            cleaned[still_missing],
            format=fmt,
            errors="coerce"
        )

    # Localize according to the marker found in the original value
    result = pd.Series(pd.NaT, index=series.index, dtype="object")

    result.loc[utc_mask] = (
        parsed[utc_mask]
        .dt.tz_localize("UTC")
        .dt.tz_convert("Asia/Kolkata")
    )

    local_mask = ~utc_mask
    result.loc[local_mask] = (
        parsed[local_mask]
        .dt.tz_localize("Asia/Kolkata")
    )

    return pd.to_datetime(result)


def clean_weather():

    print("\n" + "=" * 70)
    print("CLEANING WEATHER DATA")
    print("=" * 70)

    path = RAW_DIR / "track3_weather_sensors.xlsx"

    # Stream the worksheet with openpyxl in read-only mode instead of
    # pd.read_excel, which loads the whole workbook at once and can
    # trigger ArrayMemoryError on this file.
    workbook = openpyxl.load_workbook(
        path,
        read_only=True,
        data_only=True
    )

    worksheet = workbook["sensor_logs"]

    rows = worksheet.iter_rows(values_only=True)

    header = next(rows)

    df = pd.DataFrame(rows, columns=header)

    workbook.close()

    before = len(df)
    # Timestamp — parsed with explicit formats, no automatic day/month guessing
    df["timestamp_ist"] = parse_weather_timestamp(df["timestamp"])

    # Temperature → Celsius
    df["temperature_c"] = [
        clean_temperature(value, unit)
        for value, unit
        in zip(df["temperature"], df["temp_unit"])
    ]

    # Rainfall → mm
    df["rainfall_mm"] = [
        clean_rainfall(value, unit)
        for value, unit
        in zip(df["rainfall"], df["rain_unit"])
    ]

    # Humidity
    df["humidity_percent"] = pd.to_numeric(
        df["humidity_percent"],
        errors="coerce"
    )

    output = CLEANED_DIR / "weather_cleaned.csv"

    df.to_csv(output, index=False)

    print(f"Rows before: {before}")
    print(
        f"Missing timestamps: "
        f"{df['timestamp_ist'].isna().sum()}"
    )
    print(
        f"Missing Celsius values: "
        f"{df['temperature_c'].isna().sum()}"
    )
    print(
        f"Missing rainfall values: "
        f"{df['rainfall_mm'].isna().sum()}"
    )
    print(f"Saved to: {output}")

    return df


# ============================================================
# 5. TRANSPORT
# ============================================================

# Explicit datetime formats found in the raw transport data.
# Each format pins the day/month position exactly, so pandas never
# has to guess — that guessing is what causes day/month swaps.
TRANSPORT_DATETIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",   # 2026-07-05 07:34:30
    "%Y-%m-%dT%H:%M:%S",   # 2026-04-30T20:08:22
    "%d/%m/%Y %H:%M",      # 18/07/2026 16:34    (day first)
    "%d/%m/%Y",            # 19/06/2026          (day first, no time)
    "%m-%d-%Y %I:%M %p",   # 04-10-2026 04:15 AM (month first, 12h clock)
    "%d-%b-%Y %H:%M:%S",   # 02-May-2026 10:12:36
]


def parse_transport_timestamp(series):
    """
    Parse a transport timestamp column that mixes several known
    formats. Tries each explicit format in turn (never automatic /
    inferred parsing), so day and month are never guessed. Any value
    that doesn't match a known format becomes NaT via errors="coerce".
    """
    series = series.astype("string")
    parsed = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")

    for fmt in TRANSPORT_DATETIME_FORMATS:
        still_missing = parsed.isna()
        if not still_missing.any():
            break
        parsed.loc[still_missing] = pd.to_datetime(
            series[still_missing],
            format=fmt,
            errors="coerce"
        )

    return parsed


def clean_transport():

    print("\n" + "=" * 70)
    print("CLEANING TRANSPORT LOGISTICS")
    print("=" * 70)

    path = RAW_DIR / "track3_transport_logistics.csv"

    df = pd.read_csv(path)

    before = len(df)

    # Remove exact duplicates
    df = df.drop_duplicates()

    # Mandi ID
    df["mandi_id"] = df["mandi_id"].apply(
        clean_mandi_id
    )

    # Destination warehouse
    df["destination_warehouse"] = (
        df["destination_warehouse"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

       # Timestamps — parsed with explicit formats, no automatic day/month guessing
    df["departure_time_clean"] = parse_transport_timestamp(df["departure_time"])
    df["arrival_time_clean"] = parse_transport_timestamp(df["arrival_time"])

    # Transit hours
    df["transit_hours"] = df["transit_hours"].apply(
        clean_numeric
    )

    # Distance
    df["distance"] = df["distance"].apply(
        clean_numeric
    )

    df["distance_unit"] = (
        df["distance_unit"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    # Normalize distance to KM
    df["distance_km"] = np.nan

    km_mask = df["distance_unit"].isin(
        ["km", "kms", "kilometer", "kilometers"]
    )

    miles_mask = df["distance_unit"].isin(
        ["mile", "miles", "mi"]
    )

    df.loc[km_mask, "distance_km"] = (
        df.loc[km_mask, "distance"]
    )

    df.loc[miles_mask, "distance_km"] = (
        df.loc[miles_mask, "distance"] * 1.609344
    )

      # Calculate transit time from timestamps
    computed_transit = (
        df["arrival_time_clean"]
        - df["departure_time_clean"]
    ).dt.total_seconds() / 3600

    # Use computed value only where original is missing
    missing_transit = df["transit_hours"].isna()

    df.loc[
        missing_transit,
        "transit_hours"
    ] = computed_transit[missing_transit]

    # Flag negative or unrealistically long transit times as invalid
    # (adjust the threshold below if 7 days isn't the right cutoff
    # for your logistics network)
    MAX_REALISTIC_TRANSIT_HOURS = 168

    negative_transit = df["transit_hours"] < 0
    unrealistic_transit = df["transit_hours"] > MAX_REALISTIC_TRANSIT_HOURS

    df["quality_flag"] = pd.NA

    df.loc[
        negative_transit,
        "quality_flag"
    ] = "invalid_negative_transit"

    df.loc[
        unrealistic_transit,
        "quality_flag"
    ] = "invalid_unrealistic_transit"

    df.loc[
        negative_transit | unrealistic_transit,
        "transit_hours"
    ] = np.nan

    # Vehicle registration
    df["vehicle_no_clean"] = (
        df["vehicle_no"]
        .apply(standardize_vehicle)
    )

    # Driver ID
    df["driver_id"] = (
        df["driver_id"]
        .astype("string")
        .str.strip()
    )

    output = CLEANED_DIR / "transport_cleaned.csv"

    df.to_csv(output, index=False)

    print(f"Rows before: {before}")
    print(f"Rows after : {len(df)}")
    print(
        f"Negative transit times fixed: "
        f"{negative_transit.sum()}"
    )
    print(
        f"Missing distance units: "
        f"{df['distance_km'].isna().sum()}"
    )
    print(f"Saved to: {output}")

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("AGENTIQ DATATHON - TRACK 3")
    print("DATA CLEANING PIPELINE")
    print("=" * 70)

    # Run all cleaning functions
    mandi_master = clean_mandi_master()
    arrivals = clean_mandi_arrivals()
    prices = clean_price_msp()
    weather = clean_weather()
    transport = clean_transport()

    print("\n" + "=" * 70)
    print("CLEANING COMPLETE")
    print("=" * 70)

    print("\nCleaned files:")

    for file in sorted(CLEANED_DIR.glob("*")):
        print(f"  ✓ {file.name}")

    print("\nNext step:")
    print("Inspect the cleaned data before building analytics.")


if __name__ == "__main__":
    main()