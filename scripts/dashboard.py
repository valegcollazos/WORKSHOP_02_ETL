import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "final_analytics.db"
DOCS_DIR = BASE_DIR / "docs"

def consultar(sql):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(sql, conn)
    conn.close()
    return df


def grafico_popularidad():
    df = consultar(
        """
        SELECT tiene_grammy,
               AVG(popularity) AS popularidad_promedio,
               COUNT(*) AS filas
        FROM spotify_grammys
        GROUP BY tiene_grammy
        """
    )
    df["grupo"] = df["tiene_grammy"].map({0: "Sin Grammy", 1: "Con Grammy"})

    plt.figure(figsize=(6, 4))
    barras = plt.bar(df["grupo"], df["popularidad_promedio"], color=["#9aa5b1", "#e0a100"])
    plt.bar_label(barras, fmt="%.1f")
    plt.title("Popularidad promedio en Spotify")
    plt.ylabel("Popularidad (0-100)")
    plt.tight_layout()
    plt.savefig(DOCS_DIR / "grafico_1_popularidad.png")
    plt.show()


def grafico_perfil_sonoro():
    variables = ["danceability", "energy", "valence", "acousticness", "liveness", "speechiness"]
    columnas = ", ".join(f"AVG({v}) AS {v}" for v in variables)
    df = consultar(
        f"SELECT tiene_grammy, {columnas} FROM spotify_grammys GROUP BY tiene_grammy"
    )

    angulos = np.linspace(0, 2 * np.pi, len(variables), endpoint=False).tolist()
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"polar": True})
    for _, fila in df.iterrows():
        valores = [fila[v] for v in variables]
        valores += valores[:1]
        nombre = "Con Grammy" if fila["tiene_grammy"] == 1 else "Sin Grammy"
        ax.plot(angulos, valores, label=nombre)
        ax.fill(angulos, valores, alpha=0.15)

    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(variables)
    ax.set_title("Perfil sonoro promedio")
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    plt.savefig(DOCS_DIR / "grafico_2_perfil_sonoro.png")
    plt.show()


def grafico_top_premios():
    df = consultar(
        """
        SELECT artist_key,
               MAX(premios) AS premios
        FROM spotify_grammys
        WHERE tiene_grammy = 1
        GROUP BY artist_key
        ORDER BY premios DESC
        LIMIT 10
        """
    )
    df["artista"] = df["artist_key"].str.title()
    df = df.sort_values("premios")

    plt.figure(figsize=(8, 5))
    barras = plt.barh(df["artista"], df["premios"], color="#e0a100")
    plt.bar_label(barras, padding=3)
    plt.title("Top 10 artistas por premios Grammy (con canciones en Spotify)")
    plt.xlabel("Premios ganados")
    plt.tight_layout()
    plt.savefig(DOCS_DIR / "grafico_3_top_premios.png")
    plt.show()


def grafico_premios_vs_popularidad():
    df = consultar(
        """
        SELECT artist_key,
               MAX(premios) AS premios,
               AVG(popularity) AS popularidad_promedio
        FROM spotify_grammys
        WHERE tiene_grammy = 1
        GROUP BY artist_key
        """
    )
    correlacion = df["premios"].corr(df["popularidad_promedio"])
    print(f"Correlacion premios vs popularidad: {correlacion:.2f}")

    plt.figure(figsize=(7, 5))
    plt.scatter(df["premios"], df["popularidad_promedio"], alpha=0.5, color="#e0a100")
    plt.title("Premios Grammy vs popularidad promedio por artista")
    plt.xlabel("Premios ganados")
    plt.ylabel("Popularidad promedio (0-100)")
    plt.tight_layout()
    plt.savefig(DOCS_DIR / "grafico_4_premios_popularidad.png")
    plt.show()


if __name__ == "__main__":
    grafico_popularidad()
    grafico_perfil_sonoro()
    grafico_top_premios()
    grafico_premios_vs_popularidad()