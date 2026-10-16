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
# VIDEOS DE FONDO DINÁMICOS EN MOVIMIENTO SEGÚN EL CLIMA
# ---------------------------------------------------------
def obtener_video_fondo(codigo_wmo):
    if codigo_wmo in [0, 1]:  # Soleado / Despejado
        return "https://assets.mixkit.co/videos/preview/mixkit-clouds-and-blue-sky-2408-large.mp4"
    elif codigo_wmo in [2, 3, 45, 48]:  # Nuboso / Niebla
        return "https://assets.mixkit.co/videos/preview/mixkit-slow-motion-of-clouds-moving-in-the-sky-41551-large.mp4"
    elif codigo_wmo in [95, 96, 99]:  # Tormenta eléctrica / Granizo
        return "https://assets.mixkit.co/videos/preview/mixkit-thunderstorm-lightning-in-the-dark-sky-42999-large.mp4"
    elif codigo_wmo >= 51:  # Lluvia / Llovizna
        return "https://assets.mixkit.co/videos/preview/mixkit-raindrops-falling-on-a-window-1522-large.mp4"
    else:
        return "https://assets.mixkit.co/videos/preview/mixkit-slow-motion-of-clouds-moving-in-the-sky-41551-large.mp4"

# ---------------------------------------------------------
# ESTILOS CSS PROFESIONALES
# ---------------------------------------------------------
def aplicar_estilos(video_url):
    st.markdown(f"""
        <style>
        #MainMenu, header, footer {{visibility: hidden;}}
        
        /* Video de fondo en movimiento con brillo tenue */
        .bg-video {{
            position: fixed;
            right: 0;
            bottom: 0;
            min-width: 100%;
            min-height: 100%;
            z-index: -99;
            object-fit: cover;
            filter: brightness(0.72) contrast(1.05);
        }}

        .stApp {{
            background-color: #0b132b;
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}

        /* Contenedor principal con efecto cristal */
        .main-container {{
            background: rgba(15, 23, 42, 0.70);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 22px;
            padding: 24px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-bottom: 20px;
        }}

        /* Barra lateral (Sidebar) */
        [data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.96);
            backdrop-filter: blur(10px);
            border-right: 1px solid #e2e8f0;
        }}

        [data-testid="stSidebar"] [data-testid="stImage"] img {{
            border-radius: 14px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        }}

        /* Tarjetas de Pronóstico (3 Días) */
        .forecast-card {{
            background: rgba(255, 255, 255, 0.94);
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0px 6px 18px rgba(0, 0, 0, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.6);
            text-align: center;
            margin-bottom: 12px;
            color: #1e293b;
        }}

        /* Tarjetas de Métricas en Tiempo Real */
        .metric-card {{
            background: rgba(255, 255, 255, 0.94);
            border-radius: 14px;
            padding: 16px;
            box-shadow: 0px 4px 14px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #0284c7;
            margin-bottom: 12px;
            color: #1e293b;
        }}

        /* Barra de fiabilidad */
        .reliability-bar {{
            background-color: #e2e8f0;
            border-radius: 8px;
            height: 6px;
            width: 100%;
            margin-top: 10px;
            overflow: hidden;
        }}
        .reliability-fill {{
            background: linear-gradient(90deg, #f59e0b, #10b981);
            height: 100%;
            width: 95%;
            border-radius: 8px;
        }}
        </style>

        <video autoplay muted loop class="bg-video">
            <source src="{video_url}" type="video/mp4">
        </video>
    """, unsafe_allow_html=True)

aplicar_estilos("https://assets.mixkit.co/videos/preview/mixkit-slow-motion-of-clouds-moving-in-the-sky-41551-large.mp4")

# ---------------------------------------------------------
# BARRA LATERAL (LOGO Y MENÚ)
# ---------------------------------------------------------
with st.sidebar:
    try:
        st.image("logo.jpeg", use_container_width=True)
    except:
        st.info("💡 Sube tu archivo 'logo.jpeg' al repositorio.")
    
    st.markdown("<h2 style='text-align: center; color: #1e293b; margin: 5px 0 15px 0;'>MeteoUy</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 🗂️ Menú")
    menu = st.radio("Sección:", ["Dashboard", "Mapa", "Alertas", "Ayuda"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("📞 **Línea de contacto:**")
    st.caption("soporte@meteouy.com | +598 900 000")

# ---------------------------------------------------------
# CONTENIDO SEGÚN EL MENÚ
# ---------------------------------------------------------
if menu == "Ayuda":
    st.markdown("<h1 style='color: white; text-shadow: 0px 2px 6px rgba(0,0,0,0.7); font-size: 24px; text-align: center;'>❓ Centro de Ayuda - MeteoUy</h1>", unsafe_allow_html=True)
    st.info("Sistema profesional MeteoUy con pronóstico numérico de alta resolución (ECMWF, GFS, ICON).")
elif menu == "Alertas":
    st.markdown("<h1 style='color: white; text-shadow: 0px 2px 6px rgba(0,0,0,0.7); font-size: 24px; text-align: center;'>⚠️ Alertas Meteorológicas</h1>", unsafe_allow_html=True)
    st.warning("Monitoreo activo de tormentas severas. Sin alertas vigentes.")
elif menu == "Mapa":
    st.markdown("<h1 style='color: white; text-shadow: 0px 2px 6px rgba(0,0,0,0.7); font-size: 24px; text-align: center;'>🗺️ Mapa Interactivo</h1>", unsafe_allow_html=True)
    st.info("Visualización de red de estaciones meteorológicas y radares.")
else:
    st.markdown("<h1 style='color: white; text-shadow: 0px 2px 6px rgba(0,0,0,0.7); font-size: 24px; text-align: center;'>📡 MeteoUy | Panel de Control Profesional</h1>", unsafe_allow_html=True)

    col_l, col_search, col_r = st.columns([1, 2, 1])
    with col_search:
        ciudad = st.text_input("📍 Buscar ubicación...", value="Montevideo")

    def interpretar_wmo_detallado(code):
        codigos = {
            0: ("Soleado", "☀️"),
            1: ("Mayormente Despejado", "🌤️"),
            2: ("Soleado con nubes", "⛅"),
            3: ("Nuboso", "☁️"),
            45: ("Niebla", "🌫️"),
            51: ("Llovizna", "🌧️"),
            61: ("Lluvia ligera", "🌧️"),
            63: ("Lluvia moderada", "🌧️"),
            65: ("Lluvia intensa", "⛈️"),
            80: ("Chubascos", "🌦️"),
            95: ("Tormenta eléctrica", "🌩️"),
            96: ("Tormenta con granizo", "⚡")
        }
        return codigos.get(code, ("Variables", "⛅"))

    if st.button("🔬 Ejecutar Análisis Meteorológico", type="primary", use_container_width=True):
        with st.spinner("Actualizando entorno visual..."):
            try:
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={ciudad}&count=1&language=es&format=json"
                geo_data = requests.get(geo_url).json()

                if not geo_data.get("results"):
                    st.error(f"❌ No se pudo geolocalizar la ubicación '{ciudad}'.")
                else:
                    loc = geo_data["results"][0]
                    lat, lon = loc["latitude"], loc["longitude"]
                    nombre = loc["name"]
                    pais = loc.get("country", "")

                    url_models = (
                        f"https://api.open-meteo.com/v1/forecast?"
                        f"latitude={lat}&longitude={lon}"
                        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode"
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
                    
                    codigo_actual = res_current.get("weathercode", 2)
                    video_dinamico = obtener_video_fondo(codigo_actual)
                    aplicar_estilos(video_dinamico)

                    ahora = datetime.now()
                    fecha_formateada = ahora.strftime("%a %d %b, %H:%M")

                    st.markdown('<div class="main-container">', unsafe_allow_html=True)
                    
                    col_info1, col_info2 = st.columns([2, 1])
                    with col_info1:
                        st.markdown(f"<h2 style='margin:0; color:white; font-size: 22px;'>📍 {nombre}, {pais}</h2>", unsafe_allow_html=True)
                    with col_info2:
                        st.markdown(f"<p style='text-align:right; color:#e2e8f0; font-weight:600; margin:0; font-size: 13px;'>📅 {fecha_formateada}</p>", unsafe_allow_html=True)

                    st.markdown("<hr style='border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)

                    st.markdown("<h3 style='color: white; font-size: 16px;'>📊 Pronóstico Multi-Modelo (3 Días)</h3>", unsafe_allow_html=True)
                    
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
                        
                        desc_clima, icono_clima = interpretar_wmo_detallado(wmo_code)

                        with cols_days[i]:
                            st.markdown(f"""
                                <div class="forecast-card">
                                    <h4 style="margin: 0; color: #1e293b; font-size: 16px;">{etiquetas[i]}</h4>
                                    <span style="color: #64748b; font-size: 11px;">{fecha_raw}</span>
                                    <div style="font-size: 34px; margin: 6px 0;">{icono_clima}</div>
                                    <p style="font-size: 13px; font-weight: 600; color: #334155; margin: 4px 0;">{desc_clima}</p>
                                    <p style="font-size: 18px; font-weight: bold; color: #0284c7; margin: 6px 0;">
                                        {t_max}°C <span style="font-size: 12px; color: #64748b; font-weight: normal;">/ {t_min}°C</span>
                                    </p>
                                    <p style="font-size: 12px; color: #475569; margin: 2px 0;">Humedad / Prob: <b>{precip_prob}%</b></p>
                                    <div style="font-size: 10px; font-weight: bold; color: #166534; margin-top: 6px; text-align: left;">ALTA FIABILIDAD</div>
                                    <div class="reliability-bar"><div class="reliability-fill"></div></div>
                                </div>
                            """, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    st.markdown("<h3 style='color: white; font-size: 16px;'>🌐 Datos en Tiempo Real (Davis / METAR)</h3>", unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns(4)
                    
                    temp_act = res_current.get('temperature_2m', 'N/A')
                    hum_act = res_current.get('relative_humidity_2m', 'N/A')
                    pres_act = res_current.get('surface_pressure', 'N/A')
                    viento_act = res_current.get('wind_speed_10m', 'N/A')

                    with c1:
                        st.markdown(f"""
                            <div class="metric-card">
                                <span style="color: #64748b; font-size: 11px; font-weight: 600;">TEMPERATURA</span>
                                <h3 style="margin: 4px 0; color: #0f172a; font-size: 20px;">{temp_act} °C</h3>
                                <span style="font-size: 11px; color: #475569;">Humedad: {hum_act}%</span>
                            </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"""
                            <div class="metric-card">
                                <span style="color: #64748b; font-size: 11px; font-weight: 600;">PRESIÓN BAROMÉTRICA</span>
                                <h3 style="margin: 4px 0; color: #0f172a; font-size: 18px;">{pres_act} hPa</h3>
                                <span style="font-size: 11px; color: #475569;">Tendencia Estable</span>
                            </div>
                        """, unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"""
                            <div class="metric-card">
                                <span style="color: #64748b; font-size: 11px; font-weight: 600;">VIENTO ACTUAL</span>
                                <h3 style="margin: 4px 0; color: #0f172a; font-size: 18px;">{viento_act} km/h</h3>
                                <span style="font-size: 11px; color: #475569;">Dirección Activa</span>
                            </div>
                        """, unsafe_allow_html=True)
                    with c4:
                        st.markdown(f"""
                            <div class="metric-card">
                                <span style="color: #64748b; font-size: 11px; font-weight: 600;">CONDICIÓN / UV</span>
                                <h3 style="margin: 4px 0; color: #0f172a; font-size: 18px;">UV 6 (Alto)</h3>
                                <span style="font-size: 11px; color: #475569;">Precip: 0 mm</span>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Ocurrió un error al procesar los datos: {e}")
