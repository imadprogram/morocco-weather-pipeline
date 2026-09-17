import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

st.set_page_config(page_title="Morocco Weather Risk Monitor", layout="wide")

@st.cache_data(ttl=600)
def load_data():
    db_user = os.getenv("DB_USER", "imad")
    db_pass = os.getenv("DB_PASS", "imadpostgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "weather_db")

    engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

    query = """
    SELECT 
        c.city_name,
        c.admin_name,
        c.latitude,
        c.longitude,
        f.forecast_date,
        f.temp_max,
        f.temp_min,
        f.precipitation,
        f.wind_speed,
        f.wind_gusts,
        f.weather_code,
        f.risk_score,
        f.risk_level
    FROM weather_forecasts f
    JOIN cities c ON c.id = f.city_id
    ORDER BY f.forecast_date ASC;
    """
    df = pd.read_sql(query, con=engine)
    df['forecast_date'] = pd.to_datetime(df['forecast_date']).dt.date
    return df

df = load_data()

st.title("Morocco Logistics & Weather Risk Dashboard")

available_dates = sorted(df['forecast_date'].unique())
selected_date = st.selectbox("Select Forecast Date", available_dates)

current_df = df[df['forecast_date'] == selected_date]

col1, col2, col3, col4 = st.columns(4)
highest_risk_row = current_df.sort_values('risk_score', ascending=False).iloc[0]

col1.metric("Highest Risk City", f"{highest_risk_row['city_name']}")
col2.metric("Max Risk Score", f"{highest_risk_row['risk_score']} / 100")
col3.metric("Critical Alerts", f"{(current_df['risk_level'] == 'Critical').sum()}")
col4.metric("High Alerts", f"{(current_df['risk_level'] == 'High').sum()}")

st.subheader("Geographic Risk Distribution")

color_map = {
    "Lojw": "#2ecc71",
    "Medium": "#f1c40f",
    "High": "#e67e22",
    "Critical": "#e74c3c"
}

fig_map = px.scatter_map(
    current_df,
    lat="latitude",
    lon="longitude",
    color="risk_level",
    size="risk_score",
    hover_name="city_name",
    hover_data={
        "latitude": False,
        "longitude": False,
        "risk_score": True,
        "temp_max": True,
        "wind_gusts": True,
        "precipitation": True
    },
    color_discrete_map=color_map,
    zoom=5,
    center={"lat": 31.7917, "lon": -7.0926},
    map_style="carto-positron",
    height=500
)
st.plotly_chart(fig_map, use_container_width=True)

st.subheader("7-Day Forecast Trend by City")
selected_city = st.selectbox("Select City for Details", sorted(df['city_name'].unique()))
city_df = df[df['city_name'] == selected_city]

fig_trend = px.line(
    city_df,
    x="forecast_date",
    y="risk_score",
    markers=True,
    title=f"7-Day Delivery Risk Score Trend: {selected_city}",
    labels={"forecast_date": "Date", "risk_score": "Risk Score (0-100)"},
    range_y=[0, 100]
)
st.plotly_chart(fig_trend, use_container_width=True)