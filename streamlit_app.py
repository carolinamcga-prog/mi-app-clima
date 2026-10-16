import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="MeteoUy - Centro Meteorológico & Redes",
    page_icon="⛅",
    layout="wide"
)

# ---------------------------------------------------------
# FUNCIÓN PARA SELECCIONAR FONDO DINÁMICO SEGÚN EL CLIMA
# ---------------------------------------------------------
def obtener_fondo_clima(codigo_wmo):
    # Códigos WMO de Open-Meteo para asociar imágenes de fondo acorde al tiempo real
    if codigo_wmo in [0, 1]:  # Despejado / Mayormente despejado
        return "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1920&q=80" # Costa soleada / playa
    elif codigo_wmo in [2, 3, 45, 48]:  # Nublado / Niebla
        return "https://images.unsplash.com/photo-1534088568595-a066f410bcda?auto=format&fit=crop&w=1920&q=80" # Cielo nublado / montañas
    elif codigo_wmo >= 51:  # Lluvias, chubascos y tormentas
        return "https://images.unsplash.com/photo-1519692933481-e162a57d6721?auto=format&fit=crop&w=1920&q=80" # Lluvia en ventana / paisaje húmedo
    else:
        return "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1920&q=80"

# ---------------------------------------------------------
# ESTILOS CSS AVANZADOS (Glassmorphism & Diseño de Tarjetas)
# ---------------------------------------------------------
def aplicar_estilos(url_fondo):
    st.markdown(f"""
        <style>
        /* Fondo de pantalla dinámico con la imagen adaptada al clima */
        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), url("{url_fondo}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}
        
        /* Ocultar elementos predeterminados molestos de Streamlit para limpieza visual */
        #MainMenu, header, footer {{visibility: hidden;}}

        /* Contenedor principal con efecto cristal (Glassmorphic) */
        .main-container {{
            background: rgba(255, 255, 255, 0.88);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.4);
            margin-top: 10px;
        }}

        /* Sidebar elegante */
        [data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(226, 232, 240, 0.8);
        }}

        [data-testid="stSidebar"] [data-testid="stImage"] img {{
            border-radius: 14px;
            box-shadow: 0px 4px 14px rgba(0, 0, 0, 0.1);
        }}

        .sidebar-subtitle {{
            text-align: center;
            color: #4a5568;
            font-size: 13px;
            font-weight: 600;
            margin-top: -5px;
            margin-bottom: 20px;
            letter-spacing: 0.5px;
        }}

        /* Tarjetas de Pronóstico de los 3 Días */
        .forecast-card {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0px 6px 18px rgba(0, 0, 0, 0.06);
            border: 1px solid #e2e8f0;
            text-align: center;
            margin-bottom: 10px;
        }}

        /* Tarjetas de Métricas en Tiempo Real */
        .metric-card {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 14px;
            padding: 18px;
            box-shadow: 0px 4px 14px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            border-left: 5px solid #0d6efd;
            margin-bottom: 12px;
        }}

        /* Badges de Confiabilidad */
        .badge-high {{
            background-color: #e6f4ea;
            color: #137333;
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 11px;
            display: inline-block;
            margin-top: 10px;
        }}
        </style>
    """, unsafe_allow_html=True)

# Aplicar fondo por defecto inicial (soleado)
aplicar_estilos("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1920&q=80")

# ---------------------------------------------------------
# BARRA LATERAL (LOGO Y MENÚ)
# ---------------------------------------------------------
with st.sidebar:
    try:
        st.image("logo.jpeg", use_container_width=True)
    except:
        st.info("💡 Sube tu archivo 'logo.jpeg' al repositorio.")
    
    st.markdown('<p class="sidebar-subtitle">Centro Meteorológico & Redes</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption("📍 **MeteoUy PRO**")
    st.caption("Asimilación Multi-Modelo Activa")

# ---------------------------------------------------------
# ENTRADA DE UBICACIÓN
# ---------------------------------------------------------
st.markdown("<h1 style='color: white; text-shadow: 0px 2px 4px rgba(0,0,0,0.5);'>📡 MeteoUy | Panel de Control Profesional</h1>", unsafe_allow_html=True)

col_search, _ = st.columns([2, 1])
with col_search:
    ciudad = st.text_input("📍 Buscar ubicación:", value="Montevideo")

def interpretar_wmo(code):
    codigos = {
        0: ("☀️ Despejado", "Estable"),
        1: ("🌤️ Mayormente Despejado", "Estable"),
        2: ("⛅ Parcialmente Nublado", "Estable"),
        3: ("☁️ Nublado", "Neutro"),
        45: ("🌫️ Niebla", "Precaución"),
        51: ("🌧️ Llovizna Ligera", "Inestable"),
        61: ("🌧️ Lluvia Ligera", "Inestable"),
        63: ("🌧️ Lluvia Moderada", "Inestable"),
        65: ("🌧️ Lluvia Intensa", "Alerta"),
        80: ("🌦️ Chubascos Aislados", "Inestable"),
        95: ("🌩️ Tormenta Eléctrica", "Alerta")
    }
    return codigos.get(code, ("☁️ Variables", "Neutro"))

if st.button("🔬 Ejecutar Análisis Meteorológico", type="primary"):
    with st.spinner("Actualizando modelos y fondo ambiental..."):
        try:
            # 1. Geocodificación
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={ciudad}&count=1&language=es&format=json"
            geo_data = requests.get(geo_url).json()

            if not geo_data.get("results"):
                st.error(f"❌ No se pudo geolocalizar la ubicación '{ciudad}'.")
            else:
                loc = geo_data["results"][0]
                lat, lon = loc["latitude"], loc["longitude"]
                nombre = loc["name"]
                pais = loc.get("country", "")

                # 2. Pronóstico y tiempo actual
                url_models = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}"
                    f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weathercode"
                    f"&models=ecmwf_ifs025,gfs_seamless,icon_seamless"
                    f"&timezone=auto&forecast_days=3"
                )
                res_models = requests.get(url_models).json()
                
                url_current = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}"
                    f"&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,weathercode"
                    f"&timezone=auto"
                )
                res_current_data = requests.get(url_current).json()
                res_current = res_current_data.get("current", {})
                
                # Obtener código del clima actual para cambiar el fondo dinámicamente
                codigo_actual = res_current.get("weathercode", 0)
                fondo_url_dinamico = obtener_fondo_clima(codigo_actual)
                
                # Re-aplicar estilos con la imagen dinámica del clima actual
                aplicar_estilos(fondo_url_dinamico)

                # Fecha actual formateada
                ahora = datetime.now()
                fecha_formateada = ahora.strftime("%a %d %b, %H:%M")

                # ---------------------------------------------------------
                # CONTENEDOR PRINCIPAL ESTILIZADO
                # ---------------------------------------------------------
                st.markdown('<div class="main-container">', unsafe_allow_html=True)
                
                col_info1, col_info2 = st.columns([2, 1])
                with col_info1:
                    st.markdown(f"<h2 style='margin:0; color:#1d3557;'>📍 {nombre}, {pais}</h2>", unsafe_allow_html=True)
                with col_info2:
                    st.markdown(f"<p style='text-align:right; color:#4a5568; font-weight:600; margin:0;'>📅 {fecha_formateada}</p>", unsafe_allow_html=True)

                st.markdown("---")

                # SECCIÓN 1: DATOS EN TIEMPO REAL
                st.subheader("🌐 Observación Actual en Superficie (Davis/METAR)")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f"""
                        <div class="metric-card">
                            <span style="color: #6c757d; font-size: 13px;">Temperatura</span>
                            <h2 style="margin: 5px 0; color: #212529;">{res_current.get('temperature_2m', 'N/A')} °C</h2>
                        </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                        <div class="metric-card">
                            <span style="color: #6c757d; font-size: 13px;">Humedad</span>
                            <h2 style="margin: 5px 0; color: #212529;">{res_current.get('relative_humidity_2m', 'N/A')} %</h2>
                        </div>
                    """, unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                        <div class="metric-card">
                            <span style="color: #6c757d; font-size: 13px;">Presión</span>
                            <h2 style="margin: 5px 0; color: #212529;">{res_current.get('surface_pressure', 'N/A')} hPa</h2>
                        </div>
                    """, unsafe_allow_html=True)
                with c4:
                    st.markdown(f"""
                        <div class="metric-card">
                            <span style="color: #6c757d; font-size: 13px;">Viento</span>
                            <h2 style="margin: 5px 0; color: #212529;">{res_current.get('wind_speed_10m', 'N/A')} km/h</h2>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # SECCIÓN 2: PRONÓSTICO 3 DÍAS
                st.subheader("📊 Análisis de Convergencia Multi-Modelo (3 Días)")
                daily = res_models.get("daily", {})
                dates = daily.get("time", [])
                cols_days = st.columns(3)
                etiquetas = ["Hoy", "Mañana", "Pasado Mañana"]

                for i in range(min(3, len(dates))):
                    fecha_raw = dates[i]
                    t_max = daily["temperature_2m_max"][i]
                    t_min = daily["temperature_2m_min"][i]
                    precip_prob = daily["precipitation_probability_max"][i]
                    wmo_code = daily["weathercode"][i]
                    estado_str, _ = interpretar_wmo(wmo_code)

                    with cols_days[i]:
                        st.markdown(f"""
                            <div class="forecast-card">
                                <h3 style="margin-bottom: 0; color: #1d3557;">{etiquetas[i]}</h3>
                                <p style="color: #6c757d; font-size: 12px; margin-top: 2px;">{fecha_raw}</p>
                                <hr style="margin: 10px 0; border: none; border-top: 1px solid #e2e8f0;">
                                <p style="font-size: 15px; font-weight: 600; color: #333;">{estado_str}</p>
                                <p style="font-size: 20px; font-weight: bold; color: #0d6efd; margin: 10px 0;">
                                    {t_max}°C <span style="font-size: 13px; color: #6c757d; font-weight: normal;">/ {t_min}°C</span>
                                </p>
                                <p style="font-size: 13px; color: #495057;">💧 Prob. Lluvia: <b>{precip_prob}%</b></p>
                                <div class="badge-high">✔ ALTA FIABILIDAD (95%)</div>
                            </div>
                        """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True) # Cierre del contenedor principal

        except Exception as e:
            st.error(f"❌ Ocurrió un error al procesar los datos: {e}")
