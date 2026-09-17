from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

silver_path = BASE_DIR / "data" / "silver" / "weather_silver.parquet"
gold_dir = BASE_DIR / "data" / "gold"
gold_dir.mkdir(parents=True, exist_ok=True)
gold_path = gold_dir / "weather_gold.parquet"

df = pd.read_parquet(silver_path)

df["temp_category"] = pd.cut(
    df["temperature_2m_max"],
    bins=[-float("inf"), 10, 30, 38, float("inf")],
    labels=["Cold", "Moderate", "Hot", "Extreme Heat"],
)

df["rain_category"] = pd.cut(
    df["precipitation_sum"],
    bins=[-float("inf"), 0.1, 5, 20, float("inf")],
    labels=["No Rain", "Light Rain", "Moderate Rain", "Heavy Rain"],
)

df["wind_category"] = pd.cut(
    df["wind_gusts_10m_max"],
    bins=[-float("inf"), 20, 40, 60, float("inf")],
    labels=["Light", "Moderate", "Strong", "Storm"],
)

wind_subscore = (df["wind_gusts_10m_max"] / 80).clip(0, 1) * 100
rain_subscore = (df["precipitation_sum"] / 30).clip(0, 1) * 100

heat_impact = ((df["temperature_2m_max"] - 30) / 15).clip(0, 1) * 100
cold_impact = ((5 - df["temperature_2m_min"]) / 10).clip(0, 1) * 100
temp_subscore = np.maximum(heat_impact, cold_impact)

df["risk_score"] = (
    0.40 * wind_subscore + 0.40 * rain_subscore + 0.20 * temp_subscore
).round(1)

df["risk_level"] = pd.cut(
    df["risk_score"],
    bins=[-float("inf"), 25, 50, 75, float("inf")],
    labels=["Low", "Medium", "High", "Critical"],
)

df.to_parquet(gold_path, index=False)
print(f"Gold layer successfully saved to {gold_path} with {len(df)} records.")