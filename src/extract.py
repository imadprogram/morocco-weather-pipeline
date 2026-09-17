import json
from pathlib import Path
import time
import pandas as pd
import requests as rq

BASE_DIR = Path(__file__).resolve().parent.parent
raw_data = pd.read_csv(BASE_DIR / "data" / "bronze" / "ma.csv")

url = "https://api.open-meteo.com/v1/forecast"

for index, row in raw_data.iterrows():
    city_name = row["city"]
    lat = row["lat"]
    lng = row["lng"]

    params = {
        "latitude": lat,
        "longitude": lng,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "weather_code",
        ],
        "timezone": "Africa/Casablanca",
    }
    try:
        response = rq.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        clean_city = city_name.lower().replace(" ", "_")
        file_path = BASE_DIR / "data" / "bronze" / f"weather_{clean_city}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except rq.exceptions.RequestException as e:
        print(f"Error fetching data for {city_name}: {e}")

    time.sleep(0.2)