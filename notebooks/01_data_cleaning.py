import pandas as pd
from pathlib import Path


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"


# Create cleaned directory if it doesn't exist
CLEANED_DIR.mkdir(parents=True, exist_ok=True)


def inspect_file(file_path):
    """Load and inspect a CSV or Excel file."""

    print("=" * 60)
    print(f"FILE: {file_path.name}")
    print("=" * 60)

    if file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path)

    elif file_path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)

    else:
        print("Unsupported file type.")
        return None

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    print("\nFirst 5 rows:")
    print(df.head())

    return df


def main():

    files = list(RAW_DIR.glob("*.csv"))
    files += list(RAW_DIR.glob("*.xlsx"))
    files += list(RAW_DIR.glob("*.xls"))

    if not files:
        print("No CSV or Excel files found in data/raw/")
        return

    print(f"Found {len(files)} file(s).")

    for file_path in files:
        inspect_file(file_path)


if __name__ == "__main__":
    main()