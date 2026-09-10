# data_helpers.py
# Reusable data-cleaning helpers for AgentIQ Datathon

import pandas as pd
from rapidfuzz import process, fuzz


# --------------------------------------------------
# 1. Quintal -> KG conversion
# --------------------------------------------------

def quintal_to_kg(x):
    """
    Convert quintals to kilograms.

    1 quintal = 100 kg
    """
    if pd.isna(x):
        return x

    return x * 100


# --------------------------------------------------
# 2. KG -> Quintal conversion
# --------------------------------------------------

def kg_to_quintal(x):
    """
    Convert kilograms to quintals.

    100 kg = 1 quintal
    """
    if pd.isna(x):
        return x

    return x / 100


# --------------------------------------------------
# 3. Normalize timestamps to IST
# --------------------------------------------------

def normalize_to_ist(series):
    """
    Convert a pandas datetime series to Indian Standard Time (IST).

    Handles timestamps that already contain timezone information
    as well as timezone-naive timestamps.
    """

    dt = pd.to_datetime(series, errors="coerce")

    # If timestamps have no timezone, assume UTC first.
    if dt.dt.tz is None:
        dt = dt.dt.tz_localize("UTC")

    return dt.dt.tz_convert("Asia/Kolkata")


# --------------------------------------------------
# 4. Boolean mapper
# --------------------------------------------------

def map_boolean(value):
    """
    Convert common yes/no or true/false values into True/False.
    """

    if pd.isna(value):
        return None

    if isinstance(value, bool):
        return value

    value = str(value).strip().lower()

    true_values = {
        "yes",
        "y",
        "true",
        "1",
        "available",
        "present"
    }

    false_values = {
        "no",
        "n",
        "false",
        "0",
        "not available",
        "absent"
    }

    if value in true_values:
        return True

    if value in false_values:
        return False

    return None


# --------------------------------------------------
# 5. Clean crop names
# --------------------------------------------------

def clean_crop_name(name):
    """
    Basic crop-name cleaning.
    """

    if pd.isna(name):
        return name

    name = str(name).strip().lower()

    # Replace multiple spaces with one space
    name = " ".join(name.split())

    return name.title()


# --------------------------------------------------
# 6. Fuzzy crop-name matching
# --------------------------------------------------

def match_crop_name(name, valid_crop_names, score_cutoff=80):
    """
    Match a crop name against a list of valid crop names
    using RapidFuzz.

    Example:
        'wheat ' -> 'Wheat'
        'whheat' -> 'Wheat'
    """

    if pd.isna(name):
        return None

    cleaned_name = clean_crop_name(name)

    result = process.extractOne(
        cleaned_name,
        valid_crop_names,
        scorer=fuzz.ratio,
        score_cutoff=score_cutoff
    )

    if result is None:
        return None

    matched_name, score, _ = result

    return matched_name


# --------------------------------------------------
# 7. Remove duplicate rows
# --------------------------------------------------

def remove_duplicates(df):
    """
    Remove completely duplicated rows.
    """

    return df.drop_duplicates().reset_index(drop=True)


# --------------------------------------------------
# 8. Basic dataframe information
# --------------------------------------------------

def inspect_dataframe(df):
    """
    Print useful information while exploring a dataset.
    """

    print("Shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())