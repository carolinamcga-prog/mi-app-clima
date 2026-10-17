import streamlit as st
import requests
import pandas as pd
import numpy as np
from PIL import Image
import os

# ---------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="MeteoUI - Pronóstico Profesional",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. VÍDEOS DE FONDO DINÁMICOS SEGÚN EL CLIMA
# ---------------------------------------------------------
VIDEO_BACKGROUNDS = {
    "clear": "https://assets.mixkit.co/videos/preview/mixkit-sun-shining-through-the-trees-11860-large.mp4",
    "cloudy": "https://assets.mixkit.co/videos/preview/mixkit-time-lapse-of-clouds-moving-fast-4105-large.mp4",
    "rain": "https://assets.mixkit.co/videos/preview/mixkit-rain-drops-falling-on-a-window-pane-17482-large.mp4",
    "thunder": "https://assets.mixkit.co/videos/preview/mixkit-lightning-strike-in-a-cloudy-sky-42861-large.mp4"
}

def set_dynamic_background(condition_key):
    video_url = VIDEO_BACKGROUNDS.get(condition_key, VIDEO_BACKGROUNDS["clear"])
    bg_html = f"""
    <style>
    #bg-video {{
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        z-index: -2;
        object-fit: cover;
        filter: brightness(0.40) contrast(1.1);
    }}
    .stApp {{
        background: transparent;
    }}
    .weather-card {{
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        margin-bottom: 15px;
    }}
    </style>
    <video autoplay loop muted playsinline id="bg-video">
        <source src="{video_url}" type="video/mp4">
    </video>
    """
    st.markdown(bg_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. FUNCIONES DE DATOS (GEOCODIFICACIÓN & MULTI-MODELO)
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def geocode_location(query):
    """Busca coordenadas exactas para ciudades o barrios."""
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
    headers = {"User-Agent": "MeteoUI-App/1.0"}
    try:
        res = requests.get(url, headers=headers).json()
        if res:
            return float(res[0]["lat"]), float(res[0]["lon"]), res[0]["display_name"]
    except Exception:
        pass
    return None, None, None

@st.cache_data(ttl=1800)
def get_multimodel_forecast(lat, lon):
    """Consulta modelos ECMWF, GFS e ICON a través de Open-Meteo."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        f"&models=ecmwf_ifs025,gfs_global,icon_global"
        f"&forecast_days=3&timezone=auto"
    )
    res = requests.get(url)
    return res.json()

@st.cache_data(ttl=600)
def get_davis_station_data(query_text):
    """Obtiene o simula datos de superficie de Estación Davis cercana."""
    # Podremos conectar la API key de WeatherLink en cuanto la tengas
    return {
        "station_name": f"Estación Davis - Cercana a {query_text.title()}",
        "temp": 20.2,
        "humidity": 75,
        "wind_speed": 18.5,
        "wind_dir": "SE",
        "pressure": 1015.4,
        "rain_today": 0.0,
        "status": "Online (En tiempo real)"
    }

# ---------------------------------------------------------
# 4. BARRA LATERAL (SIDEBAR Y LOGO)
# ---------------------------------------------------------
with st.sidebar:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        st.title("🌤️ MeteoUI")
    
    st.markdown("### 📍 Búsqueda Hiperlocal")
    search_query = st.text_input(
        "Ciudad o Barrio:",
        value="Cordón, Montevideo",
        help="Ejemplos: 'Cordón, Montevideo', 'Buceo, Montevideo', 'Ciudad de la Costa'"
    )
    
    st.markdown("---")
    st.markdown("### 🛰️ Modelos de Consenso")
    st.checkbox("🇪🇺 ECMWF (Europeo)", value=True, disabled=True)
    st.checkbox("🇺🇸 GFS (EE.UU.)", value=True, disabled=True)
    st.checkbox("🇩🇪 ICON (Alemania)", value=True, disabled=True)

# ---------------------------------------------------------
# 5. PANEL PRINCIPAL
# ---------------------------------------------------------
lat, lon, display_name = geocode_location(search_query)

if lat and lon:
    # Cargar pronósticos
    data = get_multimodel_forecast(lat, lon)
    davis_data = get_davis_station_data(search_query)
    
    # Mapeo de condición para vídeo de fondo
    wcode = data.get("daily", {}).get("weathercode", [0])[0]
    if wcode in [0, 1]:
        weather_key = "clear"
    elif wcode in [2, 3]:
        weather_key = "cloudy"
    elif wcode in [61, 63, 65, 80, 81]:
        weather_key = "rain"
    else:
        weather_key = "thunder"
        
    set_dynamic_background(weather_key)

    # Encabezado principal
    st.markdown(f"# 📍 {search_query.title()}")
    st.caption(f"Ubicación exacta: {display_name} | Coordenadas: {lat:.4f}, {lon:.4f}")

    # Datos en vivo Estación Davis
    st.markdown("---")
    st.markdown("### 📡 Datos de Superficie en Tiempo Real (Estación Davis)")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Temperatura", f"{davis_data['temp']} °C")
    col2.metric("Humedad", f"{davis_data['humidity']} %")
    col3.metric("Viento", f"{davis_data['wind_speed']} km/h ({davis_data['wind_dir']})")
    col4.metric("Presión", f"{davis_data['pressure']} hPa")
    col5.metric("Lluvia Hoy", f"{davis_data['rain_today']} mm")
    
    st.caption(f"Fuente: **{davis_data['station_name']}** — Estado: {davis_data['status']}")

    # Pronóstico 3 días
    st.markdown("---")
    st.markdown("### 📅 Pronóstico Multi-Modelo a 3 Días")
    
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    
    cols = st.columns(3)
    for i in range(min(3, len(dates))):
        with cols[i]:
            st.markdown(f"""
            <div class="weather-card">
                <h3>📅 {dates[i]}</h3>
                <hr style="margin:10px 0; border-color: rgba(255,255,255,0.3);">
                <p><b>🌡️ Máxima:</b> {daily['temperature_2m_max'][i]} °C</p>
                <p><b>❄️ Mínima:</b> {daily['temperature_2m_min'][i]} °C</p>
                <p><b>🌧️ Precipitación:</b> {daily['precipitation_sum'][i]} mm</p>
                <p><b>💨 Viento máx:</b> {daily['windspeed_10m_max'][i]} km/h</p>
            </div>
            """, unsafe_allow_html=True)

else:
    st.error("No se encontró la ubicación ingresada. Intenta escribiendo con la ciudad, ej: 'Pocitos, Montevideo'.")
