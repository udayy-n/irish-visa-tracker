import pandas as pd

from src.detection import (
    find_new_decisions,
    calculate_daily_statistics
)


def main():

    file_path = "data/processed/clean_decisions.csv"

    data = pd.read_csv(file_path)

    print(f"Total real records: {len(data):,}")

    # Simulate yesterday's dataset
    old_data = data.iloc[:-100].copy()

    # Today's dataset
    new_data = data.copy()

    print(f"Old dataset: {len(old_data):,}")
    print(f"New dataset: {len(new_data):,}")

    # Find newly appearing applications
    new_decisions = find_new_decisions(
        old_data,
        new_data
    )

    print(f"\nNew decisions found: {len(new_decisions):,}")

    print("\nNew decisions:")
    print(new_decisions)

    # Calculate statistics
    statistics = calculate_daily_statistics(
        new_decisions
    )

    print("\nStatistics:")
    print(f"Total: {statistics['total']}")
    print(f"Approved: {statistics['approved']}")
    print(f"Refused: {statistics['refused']}")
    print(f"Approval rate: {statistics['approval_rate']:.2f}%")
    print(f"Refusal rate: {statistics['refusal_rate']:.2f}%")


if __name__ == "__main__":
    main()