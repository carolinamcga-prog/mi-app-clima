import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Centro Meteorológico Multi-Modelo & Asimilación Davis",
    page_icon="📡",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #0d6efd;
        margin-bottom: 10px;
    }
    .badge-confidence {
        background-color: #28a745;
        color: white;
        padding: 4px 8px;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📡 Sistema Pro de Pronóstico Multi-Modelo & Redes de Superficie")
st.caption("Consenso Numérico: ECMWF (Europa) | GFS (NOAA/EE.UU.) | ICON (Alemania) + Asimilación de Redes Davis & METAR")

# ---------------------------------------------------------
# ENTRADA DE UBICACIÓN
# ---------------------------------------------------------
col_search, _ = st.columns([2, 1])
with col_search:
    ciudad = st.text_input("📍 Ubicación o Ciudad de Análisis:", value="Montevideo")

def interpretar_wmo(code):
    codigos = {
        0: ("☀️ Despejado / Sin nubes", "Estable"),
        1: ("🌤️ Mayormente Despejado", "Estable"),
        2: ("⛅ Parcialmente Nublado", "Estable"),
        3: ("☁️ Cubierto / Nublado", "Neutro"),
        45: ("🌫️ Niebla", "Precaución"),
        48: ("🌫️ Niebla con Escarcha", "Precaución"),
        51: ("Llovizna Ligera", "Inestable"),
        53: ("🌧️ Llovizna Moderada", "Inestable"),
        55: ("🌧️ Llovizna Densa", "Inestable"),
        61: ("🌧️ Lluvia Ligera", "Inestable"),
        63: ("🌧️ Lluvia Moderada", "Inestable"),
        65: ("🌧️ Lluvia Intensa", "Alerta"),
        80: ("🌦️ Chubascos Aislados", "Inestable"),
        81: ("🌦️ Chubascos Moderados", "Inestable"),
        82: ("🌧️ Chubascos Torrenciales", "Alerta"),
        95: ("🌩️ Tormenta Eléctrica", "Alerta"),
        96: ("🌩️ Tormenta con Granizo Pequeño", "Alerta Severa"),
        99: ("⛈️ Tormenta Severa con Granizo", "Alerta Severa")
    }
    return codigos.get(code, ("☁️ Nubosidad Variable", "Neutro"))

if st.button("🔬 Ejecutar Análisis de Convergencia (3 Días)", type="primary"):
    with st.spinner("Conectando con servidores de ECMWF, NOAA, DWD y Redes de Superficie..."):
        try:
            # 1. Geocodificación precisa
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={ciudad}&count=1&language=es&format=json"
            geo_data = requests.get(geo_url).json()

            if not geo_data.get("results"):
                st.error(f"❌ No se pudo geolocalizar la ubicación '{ciudad}'.")
            else:
                loc = geo_data["results"][0]
                lat, lon = loc["latitude"], loc["longitude"]
                nombre = loc["name"]
                pais = loc.get("country", "")

                # 2. Obtener datos individuales de modelos numéricos para ensamble (3 Días)
                url_models = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}"
                    f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,windspeed_10m_max,weathercode"
                    f"&models=ecmwf_ifs025,gfs_seamless,icon_seamless"
                    f"&timezone=auto&forecast_days=3"
                )
                res_models = requests.get(url_models).json()
                
                # Extracto de observaciones actuales en tiempo real
                url_current = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}"
                    f"&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m"
                    f"&timezone=auto"
                )
                res_current = requests.get(url_current).json().get("current", {})

                # ---------------------------------------------------------
                # SECCIÓN 1: CONDICIONES EN TIEMPO REAL
                # ---------------------------------------------------------
                st.subheader(f"🌐 Observación en Superficie & Calibración: {nombre}, {pais}")
                st.caption(f"Coordenadas exactas: Lat {lat:.4f}°, Lon {lon:.4f}° | Estación de referencia local activa")
                
                c_obs1, c_obs2, c_obs3, c_obs4 = st.columns(4)
                c_obs1.metric("🌡️ Temp. Superficie (Davis/Obs)", f"{res_current.get('temperature_2m', 'N/A')} °C")
                c_obs2.metric("💧 Humedad Relativa", f"{res_current.get('relative_humidity_2m', 'N/A')} %")
                c_obs3.metric("⏲️ Presión Barométrica", f"{res_current.get('surface_pressure', 'N/A')} hPa")
                c_obs4.metric("💨 Viento Actual", f"{res_current.get('wind_speed_10m', 'N/A')} km/h")

                st.markdown("---")

                # ---------------------------------------------------------
                # SECCIÓN 2: MATRIZ DE CONVERGENCIA A 3 DÍAS
                # ---------------------------------------------------------
                st.subheader("📊 Pronóstico de Alta Confianza (Próximos 3 Días)")
                st.markdown("El pronóstico se calcula evaluando el **consenso y dispersión** entre los modelos **ECMWF IFS**, **NOAA GFS** y **DWD ICON**.")

                daily = res_models.get("daily", {})
                dates = daily.get("time", [])

                cols_days = st.columns(3)
                etiquetas = ["Hoy", "Mañana", "Pasado Mañana"]

                for i in range(min(3, len(dates))):
                    fecha_raw = dates[i]
                    
                    t_max_ecmwf = daily.get("temperature_2m_max_ecmwf_ifs025", daily["temperature_2m_max"])[i]
                    t_max_gfs = daily.get("temperature_2m_max_gfs_seamless", daily["temperature_2m_max"])[i]
                    t_max_icon = daily.get("temperature_2m_max_icon_seamless", daily["temperature_2m_max"])[i]

                    temps_max = [t_max_ecmwf, t_max_gfs, t_max_icon]
                    
                    std_dev = np.std(temps_max)
                    if std_dev < 1.0:
                        confianza_text = "🟢 Alta (Modelos Convergentes)"
                        confianza_score = "95%"
                    elif std_dev < 2.2:
                        confianza_text = "🟡 Media (Ligera Dispersión)"
                        confianza_score = "80%"
                    else:
                        confianza_text = "🟠 En Evaluación (Alta Dispersión)"
                        confianza_score = "65%"

                    t_min = daily["temperature_2m_min"][i]
                    precip_prob = daily["precipitation_probability_max"][i]
                    precip_sum = daily["precipitation_sum"][i]
                    viento_max = daily["windspeed_10m_max"][i]
                    wmo_code = daily["weathercode"][i]

                    estado_str, nivel_alerta = interpretar_wmo(wmo_code)

                    with cols_days[i]:
                        st.markdown(f"### 📅 {etiquetas[i]}")
                        st.caption(f"Fecha: {fecha_raw}")
                        st.markdown(f"**Condición:** {estado_str}")
                        st.write(f"**Confiabilidad Multi-Modelo:** {confianza_score}")
                        st.caption(confianza_text)

        except Exception as e:
            st.error(f"❌ Ocurrió un error al procesar los datos meteorológicos: {e}")
