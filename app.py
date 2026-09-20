import streamlit as st

from src.database import (
    get_application_decision,
    get_overall_statistics,
    get_latest_update_statistics,
)


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Ireland Visa Decision Tracker",
    page_icon="🇮🇪",
    layout="wide",
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* Make metric cards look cleaner */
    [data-testid="stMetric"] {
        border: 1px solid #343842;
        border-radius: 14px;
        padding: 1rem;
        background: transparent;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.6rem;
    }

    /* Search / result containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px;
    }

    /* Mobile */
    @media (max-width: 768px) {

        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        h1 {
            font-size: 1.8rem !important;
        }

        h2 {
            font-size: 1.35rem !important;
        }

        h3 {
            font-size: 1.15rem !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.35rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# HEADER
# ==================================================

st.title("🇮🇪 Ireland Visa Decision Tracker")

st.caption(
    "New Delhi Visa Decision Dashboard"
)


# ==================================================
# LOAD DATABASE DATA
# ==================================================

overall = get_overall_statistics()
latest = get_latest_update_statistics()


total = overall["total"]
approved = overall["approved"]
refused = overall["refused"]
approval_rate = overall["approval_rate"]
refusal_rate = overall["refusal_rate"]


# ==================================================
# MAIN DESKTOP LAYOUT
#
# LEFT  = SEARCH
# RIGHT = DASHBOARD
#
# On mobile Streamlit stacks these vertically.
# Search comes first.
# ==================================================

search_column, dashboard_column = st.columns(
    [1, 2],
    gap="large",
)


# ==================================================
# LEFT COLUMN
# ==================================================

with search_column:

    st.subheader("🔎 Check Your Application")

    st.write(
        "Enter your application number to check "
        "the tracked visa decision."
    )

    with st.container(border=True):

        application_number = st.text_input(
            "Application Number",
            placeholder="Enter digits only",
            max_chars=20,
        ).strip()

        search_clicked = st.button(
            "Search Decision",
            use_container_width=True,
        )


    # --------------------------------------------------
    # SEARCH RESULT
    # --------------------------------------------------

    if search_clicked:

        if not application_number:

            st.warning(
                "Please enter your application number."
            )

        elif not application_number.isdigit():

            st.error(
                "Application number must contain "
                "digits only."
            )

        else:

            decision = get_application_decision(
                application_number
            )

            if decision:

                decision_clean = decision.strip().lower()


                # ======================================
                # REFUSED
                # ======================================

                if decision_clean == "refused":

                    with st.container(border=True):

                        st.error(
                            "❌ Visa Refused"
                        )

                        st.write(
                            f"**Application Number:** "
                            f"{application_number}"
                        )

                        st.markdown(
                            "### What happens next?"
                        )

                        st.markdown(
                            """
                            - You will receive a refusal letter
                              explaining the reason(s) for the decision.

                            - The refusal letter will tell you whether
                              you have a right of appeal.

                            - If you have a right of appeal, the appeal
                              must generally be received within **2 months
                              of the date on the refusal letter**.

                            - Read the refusal letter carefully before
                              preparing an appeal.
                            """
                        )

                    st.link_button(
                        "Official Appeal Information",
                        "https://www.irishimmigration.ie/appeal-a-negative-decision/",
                        use_container_width=True,
                    )


                # ======================================
                # APPROVED
                # ======================================

                elif decision_clean == "approved":

                    with st.container(border=True):

                        st.success(
                            "🎉 Visa Approved"
                        )

                        st.write(
                            f"**Application Number:** "
                            f"{application_number}"
                        )

                        st.markdown(
                            "### What happens next?"
                        )

                        st.markdown(
                            """
                            **Congratulations! Your visa application
                            has been approved.**

                            - You will be contacted regarding the
                              issuing of your visa.

                            - Your passport/documents will be returned
                              by post or arranged for collection.

                            - Watch for the relevant passport return
                              or dispatch notification.
                            """
                        )


                # ======================================
                # OTHER
                # ======================================

                else:

                    with st.container(border=True):

                        st.info(
                            f"Decision: {decision}"
                        )

                        st.write(
                            f"**Application Number:** "
                            f"{application_number}"
                        )

            else:

                st.info(
                    "No decision found for this application "
                    "number in the tracked database."
                )


# ==================================================
# RIGHT COLUMN — DASHBOARD
# ==================================================

with dashboard_column:

    st.subheader("📊 Visa Statistics")


    # ==================================================
    # OVERALL STATISTICS
    # ==================================================

    st.markdown("### Overall Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Applications",
            f"{total:,}",
        )

    with col2:
        st.metric(
            "Approved",
            f"{approved:,}",
        )

    with col3:
        st.metric(
            "Refused",
            f"{refused:,}",
        )


    # Rates

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Approval Rate",
            f"{approval_rate:.2f}%",
        )

    with col2:
        st.metric(
            "Refusal Rate",
            f"{refusal_rate:.2f}%",
        )


    # --------------------------------------------------
    # OVERALL CHART
    # --------------------------------------------------

    st.markdown("### Approved vs Refused")

    overall_chart = {
        "Approved": approved,
        "Refused": refused,
    }

    st.bar_chart(
        overall_chart,
        height=300,
    )


    # ==================================================
    # LATEST UPDATE
    # ==================================================

    st.divider()

    st.markdown("### 📈 Latest Update")


    if latest:

        total_new = latest["total_new"]
        new_approved = latest["approved"]
        new_refused = latest["refused"]

        new_approval_rate = latest["approval_rate"]
        new_refusal_rate = latest["refusal_rate"]


        st.caption(
            f"Latest update detected: "
            f"{latest['detected_at']}"
        )


        # Latest update numbers

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "New Decisions",
                f"{total_new:,}",
            )

        with col2:
            st.metric(
                "Approved",
                f"{new_approved:,}",
            )

        with col3:
            st.metric(
                "Refused",
                f"{new_refused:,}",
            )


        # Latest update rates

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Approval Rate",
                f"{new_approval_rate:.2f}%",
            )

        with col2:
            st.metric(
                "Refusal Rate",
                f"{new_refusal_rate:.2f}%",
            )


        # Latest update chart

        st.markdown(
            "### Latest Update Breakdown"
        )

        latest_chart = {
            "Approved": new_approved,
            "Refused": new_refused,
        }

        st.bar_chart(
            latest_chart,
            height=250,
        )


    else:

        st.info(
            "No update statistics are available yet."
        )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Statistics are generated from the official Irish "
    "visa decision publications tracked by this project."
)

st.caption(
    "Independent project — not affiliated with the "
    "Department of Foreign Affairs."
)