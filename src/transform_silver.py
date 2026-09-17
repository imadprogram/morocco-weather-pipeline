import json
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

bronze_dir = BASE_DIR / "data" / "bronze"
silver_dir = BASE_DIR / "data" / "silver"
silver_dir.mkdir(parents=True, exist_ok=True)

cities_df = pd.read_csv(bronze_dir / "ma.csv")

weather_dfs = []

for filepath in bronze_dir.glob("weather_*.json"):
    city_slug = filepath.stem.replace("weather_", "")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "daily" in data:
        df_city = pd.DataFrame(data["daily"])
        df_city["city_slug"] = city_slug
        weather_dfs.append(df_city)

if not weather_dfs:
    raise ValueError(f"No weather json files found in {bronze_dir}")

all_weather_df = pd.concat(weather_dfs, ignore_index=True)

cities_df["city_slug"] = cities_df["city"].str.lower().str.replace(" ", "_")

silver_df = pd.merge(
    all_weather_df,
    cities_df[["city", "city_slug", "admin_name", "lat", "lng"]],
    on="city_slug",
    how="left",
).drop(columns=["city_slug"])

silver_df = silver_df.rename(
    columns={"time": "forecast_date", "lat": "latitude", "lng": "longitude"}
)

silver_df["forecast_date"] = pd.to_datetime(silver_df["forecast_date"]).dt.date

float_cols = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "latitude",
    "longitude",
]
silver_df[float_cols] = silver_df[float_cols].astype(float)
silver_df["weather_code"] = silver_df["weather_code"].astype(int)

silver_df = silver_df.drop_duplicates(subset=["city", "forecast_date"])

valid_temp = silver_df["temperature_2m_max"].between(-20, 60)
valid_wind = silver_df["wind_speed_10m_max"] >= 0
valid_rain = silver_df["precipitation_sum"] >= 0

silver_df = silver_df[valid_temp & valid_wind & valid_rain]

silver_df.to_parquet(silver_dir / "weather_silver.parquet", index=False)
print(f"Silver layer successfully saved with {len(silver_df)} records.")