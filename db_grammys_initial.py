import sqlite3
import pandas as pd

df = pd.read_csv("data/grammys.csv")
conn = sqlite3.connect("data/grammys_initial.db")
df.to_sql("grammys_raw", conn, if_exists="replace", index=False)
conn.close()
print(f"Grammys cargado: {len(df)} filas")