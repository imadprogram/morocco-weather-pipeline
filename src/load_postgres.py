import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert

DB_USER = "imad"
DB_PASS = "imadpostgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "weather_db"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) UNIQUE NOT NULL,
    admin_name VARCHAR(100),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS weather_forecasts (
    id SERIAL PRIMARY KEY,
    city_id INT REFERENCES cities(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    temp_max DOUBLE PRECISION,
    temp_min DOUBLE PRECISION,
    precipitation DOUBLE PRECISION,
    precipitation_prob DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    wind_gusts DOUBLE PRECISION,
    weather_code INT,
    temp_category VARCHAR(50),
    rain_category VARCHAR(50),
    wind_category VARCHAR(50),
    risk_score DOUBLE PRECISION,
    risk_level VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_city_forecast UNIQUE (city_id, forecast_date)
);
"""

with engine.begin() as connection:
    connection.execute(text(CREATE_TABLES_SQL))

df = pd.read_parquet('data/gold/weather_gold.parquet')

unique_cities = df[['city', 'admin_name', 'latitude', 'longitude']].drop_duplicates()

with engine.begin() as connection:
    for _, row in unique_cities.iterrows():
        city_upsert_query = text("""
            INSERT INTO cities (city_name, admin_name, latitude, longitude)
            VALUES (:city, :admin_name, :latitude, :longitude)
            ON CONFLICT (city_name) DO UPDATE 
            SET admin_name = EXCLUDED.admin_name,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude;
        """)
        connection.execute(city_upsert_query, {
            "city": row['city'],
            "admin_name": row['admin_name'],
            "latitude": row['latitude'],
            "longitude": row['longitude']
        })

cities_db = pd.read_sql("SELECT id AS city_id, city_name FROM cities;", con=engine)
df = pd.merge(df, cities_db, left_on='city', right_on='city_name', how='inner')

forecast_df = df.rename(columns={
    'temperature_2m_max': 'temp_max',
    'temperature_2m_min': 'temp_min',
    'precipitation_sum': 'precipitation',
    'precipitation_probability_max': 'precipitation_prob',
    'wind_speed_10m_max': 'wind_speed',
    'wind_gusts_10m_max': 'wind_gusts'
})

cols_to_insert = [
    'city_id', 'forecast_date', 'temp_max', 'temp_min',
    'precipitation', 'precipitation_prob', 'wind_speed', 'wind_gusts',
    'weather_code', 'temp_category', 'rain_category', 'wind_category',
    'risk_score', 'risk_level'
]
records = forecast_df[cols_to_insert].to_dict(orient='records')

upsert_forecast_sql = text("""
    INSERT INTO weather_forecasts (
        city_id, forecast_date, temp_max, temp_min,
        precipitation, precipitation_prob, wind_speed, wind_gusts,
        weather_code, temp_category, rain_category, wind_category,
        risk_score, risk_level, updated_at
    ) VALUES (
        :city_id, :forecast_date, :temp_max, :temp_min,
        :precipitation, :precipitation_prob, :wind_speed, :wind_gusts,
        :weather_code, :temp_category, :rain_category, :wind_category,
        :risk_score, :risk_level, CURRENT_TIMESTAMP
    )
    ON CONFLICT (city_id, forecast_date) DO UPDATE SET
        temp_max = EXCLUDED.temp_max,
        temp_min = EXCLUDED.temp_min,
        precipitation = EXCLUDED.precipitation,
        precipitation_prob = EXCLUDED.precipitation_prob,
        wind_speed = EXCLUDED.wind_speed,
        wind_gusts = EXCLUDED.wind_gusts,
        weather_code = EXCLUDED.weather_code,
        temp_category = EXCLUDED.temp_category,
        rain_category = EXCLUDED.rain_category,
        wind_category = EXCLUDED.wind_category,
        risk_score = EXCLUDED.risk_score,
        risk_level = EXCLUDED.risk_level,
        updated_at = CURRENT_TIMESTAMP;
""")

with engine.begin() as connection:
    connection.execute(upsert_forecast_sql, records)

print(f"Loaded {len(records)} forecasts into PostgreSQL successfully.")