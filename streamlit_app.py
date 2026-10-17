import streamlit as st
import requests
import os

# ---------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA (LIMPIA Y CENTRADA)
# ---------------------------------------------------------
st.set_page_config(
    page_title="MeteoUI",
    page_icon="🌤️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. VÍDEOS DE FONDO TENUE SEGÚN EL CLIMA
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
        filter: brightness(0.38) contrast(1.1);
    }}
    .stApp {{
        background: transparent;
    }}
    .weather-card {{
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 22px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: rgba(255, 255, 255, 0.25);
        color: white;
        font-weight: bold;
        border: 1px solid rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(10px);
    }}
    .stButton>button:hover {{
        background-color: rgba(255, 255, 255, 0.4);
        color: white;
        border-color: white;
    }}
    </style>
    <video autoplay loop muted playsinline id="bg-video">
        <source src="{video_url}" type="video/mp4">
    </video>
    """
    st.markdown(bg_html, unsafe_allow_html=True)

# Fondo neutro tenue por defecto antes de buscar
set_dynamic_background("clear")

# ---------------------------------------------------------
# 3. BÚSQUEDA GEOGRÁFICA Y OBTENCIÓN DE DATOS
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def geocode_uruguay(query):
    """Busca barrios, ciudades, departamentos y pueblos en Uruguay."""
    clean_query = f"{query.strip()}, Uruguay"
    url = f"https://nominatim.openstreetmap.org/search?q={clean_query}&format=json&countrycodes=uy&limit=1"
    headers = {"User-Agent": "MeteoUI-App/4.0"}
    try:
        res = requests.get(url, headers=headers).json()
        if res:
            return float(res[0]["lat"]), float(res[0]["lon"]), res[0]["display_name"]
    except Exception:
        pass
    return None, None, None

@st.cache_data(ttl=1800)
def get_forecast_3days(lat, lon):
    """Obtiene el pronóstico multi-modelo para 3 días."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        f"&models=ecmwf_ifs025,gfs_global,icon_global"
        f"&forecast_days=3&timezone=auto"
    )
    res = requests.get(url)
    return res.json()

# ---------------------------------------------------------
# 4. INTERFAZ PRINCIPAL (INICIO LIMPIO)
# ---------------------------------------------------------

# Logo en el centro
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: white;'>MeteoUI</h1>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Gran barra de búsqueda
place_input = st.text_input(
    label="",
    placeholder="Escribe el Barrio, Departamento o Pueblo (ej: Cordón, Montevideo, Salto...)",
    label_visibility="collapsed"
)

# Botón para buscar
btn_search = st.button("🔎 VER PRONÓSTICO")

# ---------------------------------------------------------
# 5. PANTALLA DE RESULTADOS (CUADRITOS DE 3 DÍAS + VÍDEO)
# ---------------------------------------------------------
if btn_search or place_input:
    if place_input.strip():
        lat, lon, display_name = geocode_uruguay(place_input)
        
        if lat and lon:
            data = get_forecast_3days(lat, lon)
            daily = data.get("daily", {})
            wcodes = daily.get("weathercode", [0])
            
            # Seleccionar condición meteorológica según el primer día
            wcode = wcodes[0] if len(wcodes) > 0 else 0
            if wcode in [0, 1]:
                weather_key = "clear"
            elif wcode in [2, 3]:
                weather_key = "cloudy"
            elif wcode in [61, 63, 65, 80, 81]:
                weather_key = "rain"
            else:
                weather_key = "thunder"
                
            # Activar vídeo de fondo según el clima del lugar
            set_dynamic_background(weather_key)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align: center; color: white;'>📍 {place_input.title()}</h2>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Los 3 cuadritos para los 3 días
            dates = daily.get("time", [])
            cols = st.columns(3)
            
            for i in range(min(3, len(dates))):
                # Formatear día
                day_label = f"Día {i+1}" if i > 0 else "Hoy"
                if i == 1: day_label = "Mañana"
                if i == 2: day_label = "Pasado Mañana"
                
                with cols[i]:
                    st.markdown(f"""
                    <div class="weather-card">
                        <h3>📅 {day_label}</h3>
                        <p style="font-size: 0.9em; opacity: 0.8;">{dates[i]}</p>
                        <hr style="margin:12px 0; border-color: rgba(255,255,255,0.3);">
                        <p style="font-size: 1.1em;"><b>🌡️ Máx:</b> {daily['temperature_2m_max'][i]} °C</p>
                        <p style="font-size: 1.1em;"><b>❄️ Mín:</b> {daily['temperature_2m_min'][i]} °C</p>
                        <p style="font-size: 1.1em;"><b>🌧️ Lluvia:</b> {daily['precipitation_sum'][i]} mm</p>
                        <p style="font-size: 1.1em;"><b>💨 Viento:</b> {daily['windspeed_10m_max'][i]} km/h</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("No se encontró el lugar. Revisa el nombre e intenta nuevamente.")
    else:
        st.warning("Por favor, ingresa un barrio o departamento en la barra arriba.")
