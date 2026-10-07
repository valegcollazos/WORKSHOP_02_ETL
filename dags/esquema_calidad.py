import pandas as pd
import pandera.pandas as pa

spotify_schema = pa.DataFrameSchema(
    {
        "track_id": pa.Column(str, nullable=False),
        "artists": pa.Column(str, nullable=False),
        "track_name": pa.Column(str, nullable=False),
        "popularity": pa.Column(int, pa.Check.in_range(0, 100)),
        "duration_ms": pa.Column(int, pa.Check.gt(0)),
        "explicit": pa.Column(bool),
        "danceability": pa.Column(float, pa.Check.in_range(0, 1)),
        "energy": pa.Column(float, pa.Check.in_range(0, 1)),
    }
)


def validar_spotify(df):
    try:
        spotify_schema.validate(df, lazy=True)
        return True, None
    except pa.errors.SchemaErrors as e:
        return False, e.failure_cases


if __name__ == "__main__":
    df = pd.read_csv("data/spotify.csv")
    ok, fallas = validar_spotify(df)
    if ok:
        print("VALIDACION: PASA")
    else:
        print("VALIDACION: FALLA")
        print(fallas[["column", "check", "failure_case", "index"]])