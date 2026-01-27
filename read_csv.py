from pathlib import Path
import pandas as pd

EXCEL_PATH = Path(r"C:\Users\Alejandro\Downloads\Autobus Neron.xlsx")
SHEET_NAME = "Sheet1"
CURRENT_BILLING_PROVIDER_VALUE = "8303"
BATCH_SIZE = 1000

def esc(s: str) -> str:
    return str(s).replace("'", "''")


df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME, dtype=str).fillna("")
df.columns = [c.strip() for c in df.columns]

number_to_port = df["Phone Number"].str.strip()
fictive_number = df["fictive #"].str.strip()
current_provider_account_number = df["Current Provider Account #"].str.strip()
#current_provider_account_number = "558427618"
# client_authorization_name = (
#     df["First Name/ Prénom"].str.strip() + " " + df["Last Name/ Nom de famille"].str.strip()
# ).str.strip()
client_authorization_name = ["Dave Lessard", "Dave Lessard"]

values_rows = []
indexes = range(len(number_to_port))
for index, nport, fict, acct_num in zip(
    indexes,
    number_to_port,
    fictive_number,
    current_provider_account_number,
):
    i = index % 2
    c_a_n = client_authorization_name[i]
    values_rows.append(
        f"('{esc(nport)}', '{esc(fict)}', '{esc(acct_num)}', '{c_a_n}', {CURRENT_BILLING_PROVIDER_VALUE})"
    )

table = "fictive_number_port_in"
cols = "(number_to_port, fictive_number, current_provider_account_number, client_authorization_name, current_billing_provider_value)"


bulk_sql_lines = []
for i in range(0, len(values_rows), BATCH_SIZE):
    chunk = values_rows[i:i + BATCH_SIZE]
    bulk_sql_lines.append(f"INSERT INTO {table} {cols} VALUES\n  " + ",\n  ".join(chunk) + ";")

print("\n\n".join(bulk_sql_lines))
