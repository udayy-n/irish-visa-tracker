import pandas as pd
from src.detection import (
    find_new_decisions,
    calculate_daily_statistics
)


def test_find_new_decisions():

    old_data = pd.DataFrame({
        "application_number": [
            "1001",
            "1002",
            "1003"
        ],
        "decision": [
            "Approved",
            "Approved",
            "Refused"
        ]
    })

    new_data = pd.DataFrame({
        "application_number": [
            "1001",
            "1002",
            "1003",
            "1004",
            "1005"
        ],
        "decision": [
            "Approved",
            "Approved",
            "Refused",
            "Approved",
            "Refused"
        ]
    })

    result = find_new_decisions(
        old_data,
        new_data
    )

    expected = ["1004", "1005"]

    assert result["application_number"].tolist() == expected


def test_calculate_daily_statistics():

    new_decisions = pd.DataFrame({
        "application_number": [
            "1004",
            "1005",
            "1006",
            "1007"
        ],
        "decision": [
            "Approved",
            "Refused",
            "Approved",
            "Approved"
        ]
    })

    result = calculate_daily_statistics(
        new_decisions
    )

    assert result["total"] == 4
    assert result["approved"] == 3
    assert result["refused"] == 1
    assert result["approval_rate"] == 75
    assert result["refusal_rate"] == 25


if __name__ == "__main__":

    test_find_new_decisions()
    test_calculate_daily_statistics()

    print("All tests passed!")