import pandas as pd

from src.database import get_existing_applications
from src.detection import (
    find_new_decisions,
    calculate_daily_statistics
)


def main():

    # Get current applications from database
    existing_applications = get_existing_applications()

    print(
        f"Existing applications: "
        f"{len(existing_applications):,}"
    )

    # Simulated newer ODS
    new_data = pd.DataFrame({
        "application_number": [
            "48850812",
            "48851162",
            "TEST001",
            "TEST002",
            "TEST003",
            "TEST004",
            "TEST005"
        ],
        "decision": [
            "Approved",
            "Approved",
            "Approved",
            "Refused",
            "Approved",
            "Refused",
            "Approved"
        ]
    })

    # Find new applications
    new_decisions = find_new_decisions(
        existing_applications,
        new_data
    )

    print(
        f"\nNew decisions detected: "
        f"{len(new_decisions)}"
    )

    print("\nNew decisions:")
    print(new_decisions)

    # Calculate statistics
    statistics = calculate_daily_statistics(
        new_decisions
    )

    print("\nStatistics:")
    print(
        f"Total: {statistics['total']}"
    )
    print(
        f"Approved: {statistics['approved']}"
    )
    print(
        f"Refused: {statistics['refused']}"
    )
    print(
        f"Approval rate: "
        f"{statistics['approval_rate']:.2f}%"
    )
    print(
        f"Refusal rate: "
        f"{statistics['refusal_rate']:.2f}%"
    )


if __name__ == "__main__":
    main()