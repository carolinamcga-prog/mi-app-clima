import streamlit as st
import requests
import os

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="MeteoUy",
    page_icon="🌤️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Vídeos de fondo según la condición meteorológica
VIDEOS = {
    "clear": "https://assets.mixkit.co/videos/preview/mixkit-sun-shining-through-the-trees-11860-large.mp4",
    "cloudy": "https://assets.mixkit.co/videos/preview/mixkit-time-lapse-of-clouds-moving-fast-4105-large.mp4",
    "rain": "https://assets.mixkit.co/videos/preview/mixkit-rain-drops-falling-on-a-window-pane-17482-large.mp4",
    "thunder": "https://assets.mixkit.co/videos/preview/mixkit-lightning-strike-in-a-cloudy-sky-42861-large.mp4"
}

# Control de estado de navegación
if "resultado_activo" not in st.session_state:
    st.session_state.resultado_activo = False
if "lugar_actual" not in st.session_state:
    st.session_state.lugar_actual = ""

# Función para cargar el logo real
def mostrar_logo():
    posibles_nombres = ["logo.jpeg", "logo.jpg", "logo.png", "LOGO.JPEG", "LOGO.JPG", "LOGO.PNG"]
    logo_encontrado = None
    for nombre in posibles_nombres:
        if os.path.exists(nombre):
            logo_encontrado = nombre
            break
            
    if logo_encontrado:
        st.image(logo_encontrado, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #222;'>MeteoUy</h1>", unsafe_allow_html=True)

# =========================================================
# PANTALLA 1: INICIO (FONDO BLANCO + LOGO REAL + BARRA)
# =========================================================
if not st.session_state.resultado_activo:
    st.markdown("""
    <style>
    .stApp {
        background-color: white !important;
    }
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 10vh;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Logo centrado
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        mostrar_logo()

    st.markdown("<br>", unsafe_allow_html=True)

    # Barra de búsqueda limpia debajo del logo
    with st.form(key="search_form"):
        lugar_input = st.text_input(
            label="",
            placeholder="Escribe el barrio o departamento (ej: Cordón, Salto, Salinas...)",
            label_visibility="collapsed"
        )
        submit = st.form_submit_button("Ver Pronóstico", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if submit and lugar_input.strip():
        st.session_state.lugar_actual = lugar_input.strip()
        st.session_state.resultado_activo = True
        st.rerun()

# =========================================================
# PANTALLA 2: RESULTADOS (VÍDEO DE FONDO Y 3 CUADRADOS)
# =========================================================
else:
    lugar = st.session_state.lugar_actual
    
    # Búsqueda de coordenadas en Uruguay
    url_geo = f"https://nominatim.openstreetmap.org/search?q={lugar}, Uruguay&format=json&countrycodes=uy&limit=1"
    res_geo = requests.get(url_geo, headers={"User-Agent": "MeteoUy-App"}).json()
    
    if res_geo:
        lat = float(res_geo[0]["lat"])
        lon = float(res_geo[0]["lon"])
        
        # Pronóstico
        url_meteo = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max&forecast_days=3&timezone=auto"
        data = requests.get(url_meteo).json()
        daily = data.get("daily", {})
        
        # Detectar tipo de clima para el vídeo
        wcodes = daily.get("weathercode", [0])
        wcode = wcodes[0] if wcodes else 0
        if wcode in [0, 1]:
            fondo = "clear"
        elif wcode in [2, 3]:
            fondo = "cloudy"
        elif wcode in [61, 63, 65, 80, 81]:
            fondo = "rain"
        else:
            fondo = "thunder"
            
        url_video = VIDEOS.get(fondo, VIDEOS["clear"])
        
        # Estilos y vídeo de fondo dinámico
        st.markdown(f"""
        <style>
        #video-fondo {{
            position: fixed;
            right: 0;
            bottom: 0;
            min-width: 100%;
            min-height: 100%;
            z-index: -10;
            object-fit: cover;
            filter: brightness(0.4);
        }}
        .stApp {{
            background: transparent !important;
        }}
        .cuadrado-pronostico {{
            background: rgba(0, 0, 0, 0.65);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            text-align: center;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
            margin-bottom: 20px;
        }}
        </style>
        <video autoplay loop muted playsinline id="video-fondo">
            <source src="{url_video}" type="video/mp4">
        </video>
        """, unsafe_allow_html=True)
        
        # Botón para volver al inicio
        if st.button("⬅️ Buscar otra ubicación"):
            st.session_state.resultado_activo = False
            st.session_state.lugar_actual = ""
            st.rerun()
            
        st.markdown(f"<h1 style='text-align: center; color: white; text-shadow: 2px 2px 6px rgba(0,0,0,0.8);'>📍 {lugar.title()}</h1>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        fechas = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        lluvia = daily.get("precipitation_sum", [])
        viento = daily.get("windspeed_10m_max", [])
        
        cols = st.columns(3)
        etiquetas = ["Hoy", "Mañana", "Pasado Mañana"]
        
        for i in range(min(3, len(fechas))):
            with cols[i]:
                st.markdown(f"""
                <div class="cuadrado-pronostico">
                    <h2 style="color: #fff; margin-bottom: 5px;">{etiquetas[i]}</h2>
                    <p style="font-size: 0.95em; opacity: 0.85; margin-bottom: 15px;">{fechas[i]}</p>
                    <hr style="border-color: rgba(255,255,255,0.3); margin-bottom: 15px;">
                    <p style="font-size: 1.2em;"><b>🌡️ Máx:</b> {t_max[i]} °C</p>
                    <p style="font-size: 1.2em;"><b>❄️ Mín:</b> {t_min[i]} °C</p>
                    <p style="font-size: 1.2em;"><b>🌧️ Lluvia:</b> {lluvia[i]} mm</p>
                    <p style="font-size: 1.2em;"><b>💨 Viento:</b> {viento[i]} km/h</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("No se encontró la ubicación ingresada en Uruguay.")
        if st.button("Volver"):
            st.session_state.resultado_activo = False
            st.rerun()
    
