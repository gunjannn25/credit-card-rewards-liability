import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parent.parent
input_file = project_folder / "data_modeled" / "modeled_rewards_liability.csv"
output_folder = project_folder / "data_modeled"

df = pd.read_csv(input_file, parse_dates=["transaction_date"])

# MODELED assumption already used in the liability model
REDEMPTION_PERIOD_MONTHS = 24

# -------- MODELED redemption-development triangle --------
triangle_parts = []
monthly_redemption_parts = []

for development_month in range(1, REDEMPTION_PERIOD_MONTHS + 1):
    eligible = df[df["age_months"] >= development_month].copy()

    # Model: expected ultimate redemptions occur evenly over 24 months
    eligible["modeled_redemption_points"] = (
        eligible["expected_ultimate_redemption_points"]
        / REDEMPTION_PERIOD_MONTHS
    )

    eligible["cohort_month"] = (
        eligible["transaction_date"].dt.to_period("M").astype(str)
    )

    eligible["modeled_redemption_date"] = (
        eligible["transaction_date"]
        + pd.DateOffset(months=development_month)
    )
    eligible["redemption_month"] = (
        eligible["modeled_redemption_date"].dt.to_period("M").astype(str)
    )

    triangle_parts.append(
        eligible.groupby(["cohort_month"])
        .agg(modeled_redemption_points=("modeled_redemption_points", "sum"))
        .reset_index()
        .assign(development_month=development_month)
    )

    monthly_redemption_parts.append(
        eligible.groupby(["redemption_month"])
        .agg(modeled_redemption_points=("modeled_redemption_points", "sum"))
        .reset_index()
    )

triangle = pd.concat(triangle_parts, ignore_index=True)
triangle["modeled_redemption_points"] = triangle["modeled_redemption_points"].round(2)
triangle.to_csv(output_folder / "cohort_redemption_triangle.csv", index=False)

monthly_redemptions = (
    pd.concat(monthly_redemption_parts, ignore_index=True)
    .groupby("redemption_month", as_index=False)
    .agg(modeled_redemption_points=("modeled_redemption_points", "sum"))
)
monthly_redemptions["modeled_redemption_points"] = (
    monthly_redemptions["modeled_redemption_points"].round(2)
)
monthly_redemptions.to_csv(
    output_folder / "monthly_modeled_redemptions.csv",
    index=False
)

# -------- Derived dashboard/SQL summary --------
category_summary = (
    df.groupby("spend_category", as_index=False)
    .agg(
        transaction_amount_usd=("transaction_amount_usd", "sum"),
        points_issued=("points_issued", "sum"),
        outstanding_liability_usd=("modeled_liability_usd", "sum")
    )
    .sort_values("outstanding_liability_usd", ascending=False)
)
category_summary.to_csv(
    output_folder / "liability_by_spend_category.csv",
    index=False
)

print("Cohort outputs complete")
print(f"Triangle rows created: {len(triangle):,}")
print(f"Redemption months created: {len(monthly_redemptions):,}")
print("\nLiability by spend category:")
print(category_summary.to_string(index=False))