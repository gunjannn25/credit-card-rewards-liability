import pandas as pd
import numpy as np
from pathlib import Path

# File paths
project_folder = Path(__file__).resolve().parent.parent
input_file = project_folder / "data_cleaned" / "cleaned_transactions.csv"
output_folder = project_folder / "data_modeled"
output_folder.mkdir(exist_ok=True)

df = pd.read_csv(input_file, parse_dates=["transaction_date"])

# -------- MODELED ASSUMPTIONS --------
URR = 0.92                    # Ultimate Redemption Rate: 92%
WAC_PER_POINT_USD = 0.01      # Weighted Average Cost per point
REDEMPTION_PERIOD_MONTHS = 24
EXPIRY_PERIOD_MONTHS = 36

# -------- DERIVED: MCC → spend category --------
def map_spend_category(mcc):
    if 3000 <= mcc <= 3999 or mcc in [4111, 4112, 4411, 4511, 4722, 7011, 7512]:
        return "Travel"
    elif mcc in [5812, 5813, 5814]:
        return "Dining"
    elif mcc in [5411, 5422, 5441, 5451, 5462, 5499]:
        return "Grocery"
    elif mcc in [5541, 5542]:
        return "Fuel"
    elif 5200 <= mcc <= 5999:
        return "Retail"
    else:
        return "Other"

df["spend_category"] = df["mcc"].apply(map_spend_category)

# -------- MODELED: reward earn rates --------
reward_rates = {
    "Travel": 3,
    "Dining": 2,
    "Grocery": 2,
    "Fuel": 1,
    "Retail": 1,
    "Other": 1
}

df["points_per_usd"] = df["spend_category"].map(reward_rates)
df["points_issued"] = (df["transaction_amount_usd"] * df["points_per_usd"]).round().astype(int)

# A transaction-level rewards account identifier
df["rewards_account_id"] = (
    "U" + df["user_id"].astype(str) + "_C" + df["card_id"].astype(str)
)

# -------- MODELED: redemption development and liability --------
valuation_date = df["transaction_date"].max()

df["age_months"] = (
    (valuation_date.year - df["transaction_date"].dt.year) * 12
    + (valuation_date.month - df["transaction_date"].dt.month)
).clip(lower=0)

# Expected redemption develops evenly over 24 months
df["redemption_development_pct"] = (
    df["age_months"] / REDEMPTION_PERIOD_MONTHS
).clip(upper=1)

df["expected_ultimate_redemption_points"] = (
    df["points_issued"] * URR
).round(2)

df["modeled_redeemed_to_date"] = (
    df["expected_ultimate_redemption_points"]
    * df["redemption_development_pct"]
).round(2)

df["is_expired"] = df["age_months"] >= EXPIRY_PERIOD_MONTHS

# Future expected redemptions are the outstanding rewards liability
df["outstanding_expected_redemption_points"] = np.where(
    df["is_expired"],
    0,
    (df["expected_ultimate_redemption_points"] - df["modeled_redeemed_to_date"]).clip(lower=0)
)

df["modeled_liability_usd"] = (
    df["outstanding_expected_redemption_points"] * WAC_PER_POINT_USD
).round(2)

# Keep fields useful for SQL, Excel, and Tableau/Power BI
rewards_model = df[
    [
        "rewards_account_id", "user_id", "card_id", "transaction_date",
        "transaction_amount_usd", "mcc", "spend_category",
        "points_per_usd", "points_issued", "age_months",
        "redemption_development_pct", "expected_ultimate_redemption_points",
        "modeled_redeemed_to_date", "outstanding_expected_redemption_points",
        "modeled_liability_usd", "is_expired"
    ]
]

rewards_model.to_csv(output_folder / "modeled_rewards_liability.csv", index=False)

# Summary for the future dashboard
monthly_summary = (
    rewards_model
    .groupby(rewards_model["transaction_date"].dt.to_period("M"))
    .agg(
        transaction_amount_usd=("transaction_amount_usd", "sum"),
        points_issued=("points_issued", "sum"),
        modeled_liability_usd=("modeled_liability_usd", "sum")
    )
    .reset_index()
)
monthly_summary["transaction_date"] = monthly_summary["transaction_date"].astype(str)
monthly_summary.to_csv(output_folder / "monthly_liability_summary.csv", index=False)

# Document assumptions in a separate file
assumptions = pd.DataFrame({
    "assumption_name": [
        "Ultimate Redemption Rate",
        "Weighted Average Cost per Point",
        "Redemption Development Period",
        "Point Expiry Period"
    ],
    "value": [URR, WAC_PER_POINT_USD, REDEMPTION_PERIOD_MONTHS, EXPIRY_PERIOD_MONTHS],
    "data_label": ["MODELED", "MODELED", "MODELED", "MODELED"]
})
assumptions.to_csv(output_folder / "model_assumptions.csv", index=False)

print("Rewards-liability model complete")
print(f"Valuation date: {valuation_date.date()}")
print(f"Total modeled points issued: {rewards_model['points_issued'].sum():,.0f}")
print(f"Outstanding modeled liability: ${rewards_model['modeled_liability_usd'].sum():,.2f}")
print(f"Cards analyzed: {rewards_model['rewards_account_id'].nunique()}")
print(f"Output folder: {output_folder}")
