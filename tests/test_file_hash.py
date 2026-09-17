from pathlib import Path

from src.file_utils import calculate_file_hash


def main():

    ods_files = list(
        Path("data/raw").glob("*.ods")
    )

    if not ods_files:
        raise FileNotFoundError(
            "No ODS file found."
        )

    file_path = ods_files[0]

    file_hash = calculate_file_hash(
        file_path
    )

    print(f"File: {file_path}")
    print(f"SHA-256: {file_hash}")


if __name__ == "__main__":
    main()