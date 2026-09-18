from src.datetime import datetime
from src.zoneinfo import ZoneInfo

from src.downloader import (
    find_ods_url,
    download_ods
)

from src.file_utils import (
    calculate_file_hash
)

from src.database import (
    create_database,
    is_file_processed,
    is_update_processed_today
)

from src.pipeline import (
    process_ods
)


INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")


def check_for_new_file():

    # Get current India date/time
    now = datetime.now(
        INDIA_TIMEZONE
    )

    current_date = now.date().isoformat()

    print("\nChecking for a new ODS file...")

    print(
        f"India time: "
        f"{now.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # --------------------------------------------------
    # Weekday check
    # Monday = 0
    # Sunday = 6
    # --------------------------------------------------

    if now.weekday() >= 5:

        print(
            "Weekend detected."
        )

        print(
            "No checking today."
        )

        return False

    # --------------------------------------------------
    # Create database
    # --------------------------------------------------

    create_database()

    # --------------------------------------------------
    # Check whether today's update
    # has already been processed
    # --------------------------------------------------

    if is_update_processed_today(
        current_date
    ):

        print(
            "Today's update has already "
            "been processed."
        )

        print(
            "No more checking is required today."
        )

        return False

    # --------------------------------------------------
    # Find current ODS
    # --------------------------------------------------

    ods_url = find_ods_url()

    # --------------------------------------------------
    # Download current ODS
    # --------------------------------------------------

    ods_file = download_ods(
        ods_url
    )

    # --------------------------------------------------
    # Calculate hash
    # --------------------------------------------------

    file_hash = calculate_file_hash(
        ods_file
    )

    print(
        f"Current file hash: {file_hash}"
    )

    # --------------------------------------------------
    # Check whether this exact file
    # has already been processed
    # --------------------------------------------------

    if is_file_processed(
        file_hash
    ):

        print(
            "No new ODS file."
        )

        print(
            "Nothing to do."
        )

        return False

    # --------------------------------------------------
    # New file detected
    # --------------------------------------------------

    print(
        "NEW ODS FILE DETECTED!"
    )

    # --------------------------------------------------
    # Process new ODS
    # --------------------------------------------------

    process_ods(
        ods_file,
        ods_url,
        file_hash
    )

    print(
        "\nNew ODS file processed successfully."
    )

    return True


if __name__ == "__main__":

    check_for_new_file()
