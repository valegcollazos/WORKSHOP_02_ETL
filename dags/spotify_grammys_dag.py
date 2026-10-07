from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

import pandas as pd

DATA_DIR = "/opt/airflow/data"

def read_db():
    import sqlite3

    conn = sqlite3.connect(f"{DATA_DIR}/grammys_initial.db")
    df = pd.read_sql("SELECT * FROM grammys_raw", conn)
    conn.close()
    df.to_csv(f"{DATA_DIR}/tmp_grammys_raw.csv", index=False)
    print(f"read_db: {len(df)} filas leidas")

def transform_db():
    df = pd.read_csv(f"{DATA_DIR}/tmp_grammys_raw.csv")
    antes = len(df)
    df = df.dropna(subset=["artist"])
    print(f"transform_db: {antes - len(df)} filas sin artista descartadas")

    df["artist_key"] = df["artist"].str.strip().str.lower()
    resumen = (
        df.groupby("artist_key")
        .agg(
            nominaciones=("winner", "size"),
            premios=("winner", "sum"),
            primer_anio=("year", "min"),
            ultimo_anio=("year", "max"),
        )
        .reset_index()
    )
    resumen.to_csv(f"{DATA_DIR}/tmp_grammys_transformed.csv", index=False)
    print(f"transform_db: {len(resumen)} artistas resumidos")

def read_csv():
    from esquema_calidad import validar_spotify

    df = pd.read_csv(f"{DATA_DIR}/spotify.csv")
    ok, fallas = validar_spotify(df)
    if ok:
        print("VALIDACION: PASA")
    else:
        print("VALIDACION: FALLA")
        print(fallas[["column", "check", "failure_case", "index"]])
    df.to_csv(f"{DATA_DIR}/tmp_spotify_raw.csv", index=False)
    print(f"read_csv: {len(df)} filas leidas")


def transform_csv():
    df = pd.read_csv(f"{DATA_DIR}/tmp_spotify_raw.csv")
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")

    antes = len(df)
    df = df.dropna(subset=["track_id", "artists", "track_name"])
    df = df[df["duration_ms"] > 0]
    print(f"transform_csv: {antes - len(df)} filas invalidas descartadas")

    antes = len(df)
    df = df.drop_duplicates(subset="track_id")
    print(f"transform_csv: {antes - len(df)} duplicados por track_id eliminados")

    df["artist_key"] = df["artists"].str.split(";")
    df = df.explode("artist_key")
    df["artist_key"] = df["artist_key"].str.strip().str.lower()

    df.to_csv(f"{DATA_DIR}/tmp_spotify_transformed.csv", index=False)
    print(f"transform_csv: {len(df)} filas (una por cancion-artista)")


def merge():
    print("merge: unir Spotify y Grammys")


def load():
    print("load: cargar a la base final")


def store():
    print("store: guardar el CSV final")


with DAG(
    dag_id="spotify_grammys_etl",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    t_read_db = PythonOperator(task_id="read_db", python_callable=read_db)
    t_transform_db = PythonOperator(task_id="transform_db", python_callable=transform_db)
    t_read_csv = PythonOperator(task_id="read_csv", python_callable=read_csv)
    t_transform_csv = PythonOperator(task_id="transform_csv", python_callable=transform_csv)
    t_merge = PythonOperator(task_id="merge", python_callable=merge)
    t_load = PythonOperator(task_id="load", python_callable=load)
    t_store = PythonOperator(task_id="store", python_callable=store)

    t_read_db >> t_transform_db >> t_merge
    t_read_csv >> t_transform_csv >> t_merge
    t_merge >> t_load >> t_store