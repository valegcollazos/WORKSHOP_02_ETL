import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

df = pd.read_csv(BASE_DIR / "data" / "grammys.csv")
conn = sqlite3.connect(BASE_DIR / "data" / "grammys_initial.db")
df.to_sql("grammys_raw", conn, if_exists="replace", index=False)
conn.close()

print(f"Grammys cargado: {len(df)} filas")