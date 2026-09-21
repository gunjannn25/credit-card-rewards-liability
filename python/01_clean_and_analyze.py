import pandas as pd
import numpy as np

# 1. Load
df = pd.read_csv("User0_credit_card_transactions.csv")

# 2. Clean
df["transaction_date"] = pd.to_datetime(
    dict(year=df["Year"], month=df["Month"], day=df["Day"]),
    errors="coerce"
)
df["amount_usd"] = (
    df["Amount"].astype(str)
      .str.replace("$", "", regex=False)
      .str.replace(",", "", regex=False)
      .astype(float)
)
df["transaction_month"] = df["transaction_date"].dt.to_period("M").astype(str)
df["transaction_year"] = df["transaction_date"].dt.year
df["is_fraud_flag"] = df["Is Fraud?"].eq("Yes").astype(int)
df["has_error_flag"] = df["Errors?"].notna().astype(int)

# 3. Derived MCC categories (portfolio classification; not issuer-provided)
def mcc_category(mcc):
    m = int(mcc)
    if m in {5811,5812,5813,5814,5815,5816}: return "Dining"
    if m in {5541,5542}: return "Fuel"
    if 3000 <= m <= 3999 or 4000 <= m <= 4799: return "Travel"
    if m == 4900: return "Utilities"
    if 4800 <= m <= 4999: return "Telecom/Utilities"
    if 5200 <= m <= 5999: return "Retail"
    if 7000 <= m <= 7999: return "Services"
    return "Other"

df["spend_category"] = df["MCC"].apply(mcc_category)

# 4. Monthly card analysis
monthly = (
    df.groupby(["Card","transaction_month"], as_index=False)
      .agg(transaction_count=("amount_usd","size"),
           total_spend_usd=("amount_usd","sum"),
           avg_transaction_usd=("amount_usd","mean"),
           median_transaction_usd=("amount_usd","median"),
           fraud_count=("is_fraud_flag","sum"),
           error_count=("has_error_flag","sum"))
)

# 5. Category analysis
category = (
    df.groupby("spend_category", as_index=False)
      .agg(transactions=("amount_usd","size"),
           spend_usd=("amount_usd","sum"),
           avg_transaction_usd=("amount_usd","mean"),
           fraud_count=("is_fraud_flag","sum"))
      .sort_values("spend_usd", ascending=False)
)
category["spend_share"] = category["spend_usd"] / category["spend_usd"].sum()
category["cumulative_spend_share"] = category["spend_share"].cumsum()

# 6. Card analysis
card = (
    df.groupby("Card", as_index=False)
      .agg(transactions=("amount_usd","size"),
           total_spend_usd=("amount_usd","sum"),
           avg_transaction_usd=("amount_usd","mean"),
           fraud_count=("is_fraud_flag","sum"))
      .sort_values("total_spend_usd", ascending=False)
)

# 7. Simple statistical relationship
x = monthly["transaction_count"].to_numpy(float)
y = monthly["total_spend_usd"].to_numpy(float)
X = np.column_stack([np.ones(len(x)), x])
beta = np.linalg.lstsq(X, y, rcond=None)[0]
y_hat = X @ beta
r2 = 1 - np.sum((y-y_hat)**2) / np.sum((y-y.mean())**2)

print("Rows:", len(df))
print("Cards:", df["Card"].nunique())
print("Total spend:", round(df["amount_usd"].sum(), 2))
print("Correlation:", round(monthly[["transaction_count","total_spend_usd"]].corr().iloc[0,1], 3))
print("Regression R-squared:", round(r2, 3))

df.to_csv("data_cleaned_transactions.csv", index=False)
monthly.to_csv("python_monthly_card_analysis.csv", index=False)
category.to_csv("python_category_analysis.csv", index=False)
card.to_csv("python_card_analysis.csv", index=False)
