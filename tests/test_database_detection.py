import pandas as pd

from src.database import get_existing_applications
from src.detection import find_new_decisions


def main():

    existing_applications = get_existing_applications()

    print(
        f"Applications already in database: "
        f"{len(existing_applications):,}"
    )

    test_data = pd.DataFrame({
        "application_number": [
            "48850812",
            "48851162",
            "TEST001",
            "TEST002",
            "TEST003"
        ],
        "decision": [
            "Approved",
            "Approved",
            "Approved",
            "Refused",
            "Approved"
        ]
    })

    new_decisions = find_new_decisions(
        existing_applications,
        test_data
    )

    print(
        f"\nNew decisions detected: "
        f"{len(new_decisions)}"
    )

    print("\nNew records:")
    print(new_decisions)


if __name__ == "__main__":
    main()