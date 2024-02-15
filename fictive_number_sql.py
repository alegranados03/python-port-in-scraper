import pandas as pd


archivo_excel = "numbers.xlsx"

df = pd.read_excel(archivo_excel)

SQL = "INSERT INTO `fictive_number_port_in`(`number_to_port`, `fictive_number`, `current_provider_account_number`, `client_authorization_name`, `current_billing_provider_value`) VALUES "
values = []
for index, row in df.iterrows():
    phone_number = row["Phone Number"]
    temporary = row["Temp #"]
    account = row["Account #"]
    rogers = "8821"
    authorization_name = "David Stewart"
    value_template = f"('{phone_number}','{temporary}','{account}','{authorization_name}','{rogers}')"
    values.append(value_template)


print(SQL + (", ").join(values))
