from datetime import datetime

from src.database import (
    create_database,
    is_update_processed_today,
    save_update_day
)


def main():

    create_database()

    today = datetime.now().date().isoformat()

    print(
        f"Today's date: {today}"
    )

    # Check before saving
    before = is_update_processed_today(
        today
    )

    print(
        f"Processed before: {before}"
    )

    # Simulate successful processing
    save_update_day(
        today
    )

    # Check again
    after = is_update_processed_today(
        today
    )

    print(
        f"Processed after: {after}"
    )


if __name__ == "__main__":
    main()