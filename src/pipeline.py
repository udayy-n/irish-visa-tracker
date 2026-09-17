from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from parser import parse_ods

from database import (
    create_database,
    get_existing_applications,
    insert_applications,
    save_update_statistics,
    save_processed_file,
    save_update_day
)

from detection import (
    find_new_decisions,
    calculate_daily_statistics
)


def process_ods(
    ods_file,
    ods_url,
    file_hash
):

    print("\nProcessing ODS file...")

    # Get applications already stored
    existing_applications = (
        get_existing_applications()
    )

    print(
        f"Existing applications in database: "
        f"{len(existing_applications):,}"
    )

    # Parse ODS
    data = parse_ods(
        ods_file
    )

    print(
        f"Applications in current ODS: "
        f"{len(data):,}"
    )

    # --------------------------------------------------
    # First ever file = baseline
    # --------------------------------------------------

    if not existing_applications:

        print(
            "Database is empty."
        )

        print(
            "Treating current ODS as baseline."
        )

        insert_applications(
            data,
            baseline=True
        )

        filename = Path(
            ods_file
        ).name

        save_processed_file(
            ods_url,
            filename,
            file_hash
        )

        print(
            "Baseline completed."
        )

        return

    # --------------------------------------------------
    # Find new applications
    # --------------------------------------------------

    new_decisions = find_new_decisions(
        existing_applications,
        data
    )

    total_new = len(
        new_decisions
    )

    print(
        f"New decisions detected: "
        f"{total_new:,}"
    )

    # --------------------------------------------------
    # New file but no new applications
    # --------------------------------------------------

    if total_new == 0:

        print(
            "New ODS file contains no new "
            "application numbers."
        )

    else:

        # Calculate statistics
        statistics = calculate_daily_statistics(
            new_decisions
        )

        print("\nNew decision statistics:")

        print(
            f"Total: "
            f"{statistics['total']}"
        )

        print(
            f"Approved: "
            f"{statistics['approved']}"
        )

        print(
            f"Refused: "
            f"{statistics['refused']}"
        )

        print(
            f"Approval rate: "
            f"{statistics['approval_rate']:.2f}%"
        )

        print(
            f"Refusal rate: "
            f"{statistics['refusal_rate']:.2f}%"
        )

        # Store only new applications
        insert_applications(
            new_decisions
        )

        # Store statistics
        save_update_statistics(
            statistics["total"],
            statistics["approved"],
            statistics["refused"]
        )

    # --------------------------------------------------
    # Mark ODS as processed
    # --------------------------------------------------

    filename = Path(
        ods_file
    ).name

    save_processed_file(
        ods_url,
        filename,
        file_hash
    )

    # --------------------------------------------------
    # Mark today as having an update
    # --------------------------------------------------
    INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")
    current_date = datetime.now(
    INDIA_TIMEZONE
).date().isoformat()
    

    save_update_day(
        current_date
    )

    print(
        "\nODS processing completed."
    )


if __name__ == "__main__":

    from downloader import (
        find_ods_url,
        download_ods
    )

    from file_utils import (
        calculate_file_hash
    )

    create_database()

    ods_url = find_ods_url()

    ods_file = download_ods(
        ods_url
    )

    file_hash = calculate_file_hash(
        ods_file
    )

    process_ods(
        ods_file,
        ods_url,
        file_hash
    )