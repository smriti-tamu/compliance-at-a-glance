from snowflake.snowpark.context import get_active_session
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Compliance at a Glance", layout="wide")

session = get_active_session()

# ---------------------------
# Load and Prepare Data
# ---------------------------
query = """
SELECT
    CONTRACT_ID,
    VENDOR_NAME,
    CATEGORY,
    CONTRACT_VALUE_USD,
    START_DATE,
    END_DATE,
    GOVERNING_LAW,
    LIABILITY_CAP_USD,
    AUTO_RENEWS,
    RISK_FLAGS,
    RISK_LEVEL,
    OWNER_TEAM,
    DATEDIFF('day', CURRENT_DATE(), END_DATE) AS DAYS_TO_EXPIRY,
    CASE
        WHEN DATEDIFF('day', CURRENT_DATE(), END_DATE) < 0 THEN 'Expired'
        WHEN DATEDIFF('day', CURRENT_DATE(), END_DATE) <= 30 THEN '0-30 Days'
        WHEN DATEDIFF('day', CURRENT_DATE(), END_DATE) <= 60 THEN '31-60 Days'
        WHEN DATEDIFF('day', CURRENT_DATE(), END_DATE) <= 90 THEN '61-90 Days'
        ELSE '90+ Days'
    END AS EXPIRY_BUCKET,
    (
        CASE
            WHEN RISK_LEVEL = 'High' THEN 3
            WHEN RISK_LEVEL = 'Medium' THEN 2
            ELSE 1
        END
        +
        CASE
            WHEN DATEDIFF('day', CURRENT_DATE(), END_DATE) < 0 THEN 4
            WHEN DATEDIFF('day', CURRENT_DATE(), END_DATE) <= 30 THEN 3
            WHEN DATEDIFF('day', CURRENT_DATE(), END_DATE) <= 90 THEN 2
            ELSE 1
        END
        +
        CASE
            WHEN AUTO_RENEWS = TRUE THEN 2
            ELSE 0
        END
    ) AS RISK_SCORE
FROM HACKATHON.DATA.CONTRACT_METADATA
"""

df = session.sql(query).to_pandas()

# Convert date columns
df["START_DATE"] = pd.to_datetime(df["START_DATE"])
df["END_DATE"] = pd.to_datetime(df["END_DATE"])

# Create Risk Tier
def get_risk_tier(score):
    if score >= 8:
        return "Critical"
    elif score >= 6:
        return "High"
    elif score >= 4:
        return "Medium"
    else:
        return "Low"

df["RISK_TIER"] = df["RISK_SCORE"].apply(get_risk_tier)

# ---------------------------
# Sidebar Filters
# ---------------------------
st.sidebar.title("Filters")
st.sidebar.caption("Refine the contract portfolio view")

risk_options = sorted(df["RISK_LEVEL"].dropna().unique())
selected_risk = st.sidebar.multiselect(
    "Risk Level", options=risk_options, default=risk_options
)

category_options = sorted(df["CATEGORY"].dropna().unique())
selected_category = st.sidebar.multiselect(
    "Category", options=category_options, default=category_options
)

team_options = sorted(df["OWNER_TEAM"].dropna().unique())
selected_team = st.sidebar.multiselect(
    "Owner Team", options=team_options, default=team_options
)

expiry_options = ["Expired", "0-30 Days", "31-60 Days", "61-90 Days", "90+ Days"]
selected_expiry = st.sidebar.multiselect(
    "Expiry Bucket", options=expiry_options, default=expiry_options
)

filtered_df = df[
    (df["RISK_LEVEL"].isin(selected_risk)) &
    (df["CATEGORY"].isin(selected_category)) &
    (df["OWNER_TEAM"].isin(selected_team)) &
    (df["EXPIRY_BUCKET"].isin(selected_expiry))
].copy()

# ---------------------------
# Key Metrics
# ---------------------------
total_contracts = len(filtered_df)
high_risk_contracts = len(filtered_df[filtered_df["RISK_LEVEL"] == "High"])
critical_contracts = len(filtered_df[filtered_df["RISK_TIER"] == "Critical"])
expiring_90 = len(
    filtered_df[
        (filtered_df["DAYS_TO_EXPIRY"] >= 0) &
        (filtered_df["DAYS_TO_EXPIRY"] <= 90)
    ]
)
total_value = filtered_df["CONTRACT_VALUE_USD"].sum()

# ---------------------------
# Header
# ---------------------------
st.title("Compliance at a Glance")
st.caption(
    "A Snowflake-powered dashboard for monitoring contract expirations, risk exposure, "
    "and financial impact."
)
st.divider()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Contracts", total_contracts)
col2.metric("High-Risk Contracts", high_risk_contracts)
col3.metric("Critical Contracts", critical_contracts)
col4.metric("Expiring in 90 Days", expiring_90)
col5.metric("Portfolio Value", f"${total_value:,.0f}")

st.info(
    f"{expiring_90} contracts are expiring within 90 days, including "
    f"{high_risk_contracts} high-risk and {critical_contracts} critical contracts."
)

# ---------------------------
# Charts
# ---------------------------
expiry_counts = (
    filtered_df["EXPIRY_BUCKET"]
    .value_counts()
    .reindex(
        ["Expired", "0-30 Days", "31-60 Days", "61-90 Days", "90+ Days"],
        fill_value=0
    )
)

value_by_category = (
    filtered_df.groupby("CATEGORY")["CONTRACT_VALUE_USD"]
    .sum()
    .sort_values(ascending=False)
)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Expiry Risk Overview")
    st.bar_chart(expiry_counts)

with chart_col2:
    st.subheader("Financial Exposure by Category")
    st.bar_chart(value_by_category)

# ---------------------------
# Critical Contracts Section
# ---------------------------
st.subheader("Critical Contracts Requiring Immediate Attention")
st.caption(
    "Contracts classified as critical based on risk level, expiry urgency, and auto-renew status."
)

critical_df = filtered_df[filtered_df["RISK_TIER"] == "Critical"][
    [
        "CONTRACT_ID",
        "VENDOR_NAME",
        "CATEGORY",
        "END_DATE",
        "DAYS_TO_EXPIRY",
        "AUTO_RENEWS",
        "RISK_LEVEL",
        "RISK_SCORE",
        "RISK_TIER",
        "OWNER_TEAM",
    ]
].sort_values(by=["RISK_SCORE", "DAYS_TO_EXPIRY"], ascending=[False, True])

st.dataframe(critical_df, use_container_width=True)

# ---------------------------
# Auto-Renew Contracts
# ---------------------------
st.subheader("Auto-Renew Contracts Requiring Review")
st.caption(
    "Contracts set to auto-renew and expiring within the next 60 days."
)

auto_renew_df = filtered_df[
    (filtered_df["AUTO_RENEWS"] == True) &
    (filtered_df["DAYS_TO_EXPIRY"] >= 0) &
    (filtered_df["DAYS_TO_EXPIRY"] <= 60)
][
    [
        "CONTRACT_ID",
        "VENDOR_NAME",
        "CATEGORY",
        "END_DATE",
        "DAYS_TO_EXPIRY",
        "RISK_LEVEL",
        "OWNER_TEAM",
    ]
].sort_values(by="DAYS_TO_EXPIRY")

st.dataframe(auto_renew_df, use_container_width=True)

# ---------------------------
# Contract Portfolio Table
# ---------------------------
st.subheader("Contract Portfolio Details")

show_cols = [
    "CONTRACT_ID",
    "VENDOR_NAME",
    "CATEGORY",
    "CONTRACT_VALUE_USD",
    "START_DATE",
    "END_DATE",
    "DAYS_TO_EXPIRY",
    "EXPIRY_BUCKET",
    "AUTO_RENEWS",
    "RISK_LEVEL",
    "RISK_SCORE",
    "RISK_TIER",
    "OWNER_TEAM",
]

display_df = filtered_df[show_cols].sort_values(by="DAYS_TO_EXPIRY").copy()
display_df["CONTRACT_VALUE_USD"] = display_df["CONTRACT_VALUE_USD"].map(
    lambda x: f"${x:,.2f}"
)

st.dataframe(display_df, use_container_width=True)

# ---------------------------
# Executive Summary
# ---------------------------
st.subheader("Executive Summary")
st.markdown(
    f"""
- **{high_risk_contracts} contracts** are classified as high risk.
- **{critical_contracts} contracts** are categorized as critical based on composite risk scoring.
- **{expiring_90} contracts** are due within the next 90 days.
- The filtered contract portfolio represents **${total_value:,.0f}** in total value.
- Auto-renewing contracts nearing expiry may require immediate review to avoid unintended renewals.
"""
)