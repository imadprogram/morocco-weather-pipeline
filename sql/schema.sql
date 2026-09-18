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