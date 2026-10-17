import streamlit as st
import requests
import os
import base64

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="MeteoUy",
    page_icon="🌤️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# RUTAS DE VIDEOS LOCALES Y RESPALDO EN LÍNEA EN VIVO
# ---------------------------------------------------------
VIDEOS_LOCALES = {
    "clear": "assets/videos/despejado.mp4",
    "partly_cloudy": "assets/videos/poco_nuboso.mp4",
    "cloudy": "assets/videos/nublado.mp4",
    "fog": "assets/videos/niebla.mp4",
    "drizzle": "assets/videos/llovizna.mp4",
    "rain_heavy": "assets/videos/lluvia_fuerte.mp4",
    "hail_snow": "assets/videos/granizo_nieve.mp4",
    "thunderstorm": "assets/videos/tormenta.mp4"
}

VIDEOS_BACKUP = {
    "clear": "https://assets.mixkit.co/videos/preview/mixkit-sun-shining-through-the-trees-11860-large.mp4",
    "partly_cloudy": "https://assets.mixkit.co/videos/preview/mixkit-clouds-and-blue-sky-2408-large.mp4",
    "cloudy": "https://assets.mixkit.co/videos/preview/mixkit-time-lapse-of-clouds-moving-fast-4105-large.mp4",
    "fog": "https://assets.mixkit.co/videos/preview/mixkit-thick-fog-in-a-forest-42841-large.mp4",
    "drizzle": "https://assets.mixkit.co/videos/preview/mixkit-rain-drops-falling-on-a-window-pane-17482-large.mp4",
    "rain_heavy": "https://assets.mixkit.co/videos/preview/mixkit-heavy-rain-falling-on-the-ground-42862-large.mp4",
    "hail_snow": "https://assets.mixkit.co/videos/preview/mixkit-snow-falling-silently-in-a-forest-42843-large.mp4",
    "thunderstorm": "https://assets.mixkit.co/videos/preview/mixkit-lightning-strike-in-a-cloudy-sky-42861-large.mp4"
}

def obtener_fuente_video(tipo_fondo):
    ruta_local = VIDEOS_LOCALES.get(tipo_fondo, "")
    if os.path.exists(ruta_local):
        try:
            with open(ruta_local, "rb") as video_file:
                video_bytes = video_file.read()
                b64_video = base64.b64encode(video_bytes).decode("utf-8")
                return f"data:video/mp4;base64,{b64_video}"
        except Exception:
            return VIDEOS_BACKUP.get(tipo_fondo, VIDEOS_BACKUP["clear"])
    else:
        return VIDEOS_BACKUP.get(tipo_fondo, VIDEOS_BACKUP["clear"])

# ---------------------------------------------------------
# ESTADO DE LA SESIÓN
# ---------------------------------------------------------
if "resultado_activo" not in st.session_state:
    st.session_state.resultado_activo = False
if "lugar_actual" not in st.session_state:
    st.session_state.lugar_actual = ""

def obtener_clave_video(wcode):
    if wcode == 0:
        return "clear"
    elif wcode in [1, 2]:
        return "partly_cloudy"
    elif wcode == 3:
        return "cloudy"
    elif wcode in [45, 48]:
        return "fog"
    elif wcode in [51, 53, 55, 56, 57]:
        return "drizzle"
    elif wcode in [61, 63, 65, 66, 67, 80, 81, 82]:
        return "rain_heavy"
    elif wcode in [71, 73, 75, 77, 85, 86]:
        return "hail_snow"
    elif wcode in [95, 96, 99]:
        return "thunderstorm"
    return "clear"

def obtener_descripcion_clima(wcode):
    descripciones = {
        0: "Cielo Despejado ☀️",
        1: "Poco Nuboso 🌤️",
        2: "Parcialmente Nublado ⛅",
        3: "Nublado / Cubierto ☁️",
        45: "Niebla 🌫️",
        48: "Neblina Helada 🌫️",
        51: "Llovizna Leve 🌧️",
        53: "Llovizna Moderada 🌧️",
        55: "Garúa Densa 🌧️",
        61: "Lluvia Leve 🌧️",
        63: "Lluvia Moderada 🌧️",
        65: "Lluvia Torrencial 🌧️⚡",
        80: "Chubascos Leves 🌦️",
        81: "Chubascos Moderados 🌧️",
        82: "Chub
