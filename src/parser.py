import pandas as pd
from pathlib import Path


def find_header_row(raw_data):
    for row_number, row in raw_data.iterrows():

        values = [
            str(value).strip().lower()
            for value in row.tolist()
            if pd.notna(value)
        ]

        if "application number" in values and "decision" in values:
            return row_number

    return None


def parse_ods(file_path):

    print(f"Reading file: {file_path}")

    # Read the ODS without assuming where the header is
    raw_data = pd.read_excel(
        file_path,
        engine="odf",
        header=None
    )

    print(f"Total rows found: {len(raw_data)}")

    # Find the actual header automatically
    header_row = find_header_row(raw_data)

    if header_row is None:
        raise ValueError(
            "Could not find 'Application Number' and 'Decision' headers."
        )

    print(f"Header found at row: {header_row + 1}")

    # Read the file again using the detected header
    data = pd.read_excel(
        file_path,
        engine="odf",
        header=header_row
    )

    # Clean column names
    data.columns = [
        str(column).strip()
        for column in data.columns
    ]

    # Select only required columns
    data = data[
        ["Application Number", "Decision"]
    ].copy()

    # Rename columns
    data.columns = [
        "application_number",
        "decision"
    ]

    # Clean values
    data["application_number"] = (
        data["application_number"]
        .astype("string")
        .str.strip()
    )

    data["decision"] = (
        data["decision"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    # Remove empty rows
    data = data.dropna(
        subset=[
            "application_number",
            "decision"
        ]
    )

    # Remove accidental repeated headers
    data = data[
        data["application_number"].str.lower()
        != "application number"
    ]

    data = data[
        data["decision"].str.lower()
        != "decision"
    ]

    # Reset index
    data = data.reset_index(drop=True)

    return data


def main():

    raw_folder = Path("data/raw")

    ods_files = list(raw_folder.glob("*.ods"))

    if not ods_files:
        raise FileNotFoundError(
            "No ODS file found in data/raw/"
        )

    # Use the most recently modified ODS file
    latest_file = max(
        ods_files,
        key=lambda file: file.stat().st_mtime
    )

    data = parse_ods(latest_file)

    print("\nParsing completed.")

    print(f"Total records: {len(data):,}")

    print("\nColumns:")
    print(data.columns.tolist())

    print("\nFirst 10 records:")
    print(data.head(10))

    # Save processed data
    output_folder = Path("data/processed")
    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_folder / "clean_decisions.csv"
    )

    data.to_csv(
        output_file,
        index=False
    )

    print(f"\nSaved processed file to: {output_file}")


if __name__ == "__main__":
    main()