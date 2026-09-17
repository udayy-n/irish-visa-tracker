import pandas as pd


def find_new_decisions(existing_applications, new_data):

    new_decisions = new_data[
        ~new_data["application_number"].isin(
            existing_applications
        )
    ].copy()

    return new_decisions


def calculate_daily_statistics(new_decisions):

    total = len(new_decisions)

    approved = (
        new_decisions["decision"] == "Approved"
    ).sum()

    refused = (
        new_decisions["decision"] == "Refused"
    ).sum()

    if total > 0:
        approval_rate = approved / total * 100
        refusal_rate = refused / total * 100
    else:
        approval_rate = 0
        refusal_rate = 0

    return {
        "total": total,
        "approved": approved,
        "refused": refused,
        "approval_rate": approval_rate,
        "refusal_rate": refusal_rate
    }