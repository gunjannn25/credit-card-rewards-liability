import pandas as pd
from pathlib import Path

# Paths
project_folder = Path(__file__).resolve().parent.parent
raw_file = project_folder / "data_raw" / "User0_credit_card_transactions.csv"
output_folder = project_folder / "data_cleaned"
output_folder.mkdir(exist_ok=True)

# SOURCE DATA: read unchanged raw transaction file
df = pd.read_csv(raw_file)

# DERIVED: standardized column names
df.columns = [
    "user_id", "card_id", "year", "month", "day", "time",
    "amount_raw", "use_chip", "merchant_id", "merchant_city",
    "merchant_state", "zip_code", "mcc", "errors", "is_fraud"
]

# DERIVED: transaction date and numeric transaction amount
df["transaction_date"] = pd.to_datetime(
    df[["year", "month", "day"]]
)

df["transaction_amount_usd"] = (
    df["amount_raw"]
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(float)
)

# DERIVED: analysis-friendly fields
df["merchant_state"] = df["merchant_state"].fillna("Unknown")
df["zip_code"] = df["zip_code"].fillna("Unknown").astype(str)
df["has_error"] = df["errors"].notna()
df["is_fraud"] = df["is_fraud"].eq("Yes")

# Keep one record per exact duplicate transaction
rows_before = len(df)
df = df.drop_duplicates()
rows_after = len(df)

# Arrange fields for downstream SQL, Excel, and dashboard work
cleaned_df = df[
    [
        "user_id", "card_id", "transaction_date", "time",
        "transaction_amount_usd", "use_chip", "merchant_id",
        "merchant_city", "merchant_state", "zip_code", "mcc",
        "has_error", "is_fraud"
    ]
].sort_values("transaction_date")

# Save cleaned transaction layer
output_file = output_folder / "cleaned_transactions.csv"
cleaned_df.to_csv(output_file, index=False)

print("Cleaning complete")
print(f"Rows before duplicate removal: {rows_before:,}")
print(f"Rows after duplicate removal:  {rows_after:,}")
print(f"Date range: {cleaned_df['transaction_date'].min().date()} to {cleaned_df['transaction_date'].max().date()}")
print(f"Unique users: {cleaned_df['user_id'].nunique():,}")
print(f"Cleaned file saved to: {output_file}")
print("\nMissing values remaining:")
print(cleaned_df.isnull().sum())