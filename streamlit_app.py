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

# Videos de fondo en formato MP4
VIDEOS = {
    "clear": "https://assets.mixkit.co/videos/preview/mixkit-sun-shining-through-the-trees-11860-large.mp4",
    "partly_cloudy": "https://assets.mixkit.co/videos/preview/mixkit-clouds-and-blue-sky-2408-large.mp4",
    "cloudy": "https://assets.mixkit.co/videos/preview/mixkit-time-lapse-of-clouds-moving-fast-4105-large.mp4",
    "fog": "https://assets.mixkit.co/videos/preview/mixkit-thick-fog-in-a-forest-42841-large.mp4",
    "drizzle": "https://assets.mixkit.co/videos/preview/mixkit-rain-drops-falling-on-a-window-pane-17482-large.mp4",
    "rain": "https://assets.mixkit.co/videos/preview/mixkit-heavy-rain-falling-on-the-ground-42862-large.mp4",
    "thunder": "https://assets.mixkit.co/videos/preview/mixkit-lightning-strike-in-a-cloudy-sky-42861-large.mp4",
    "snow": "https://assets.mixkit.co/videos/preview/mixkit-snow-falling-silently-in-a-forest-42843-large.mp4"
}

# Control de estado de navegación
if "resultado_activo" not in st.session_state:
    st.session_state.resultado_activo = False
if "lugar_actual" not in st.session_state:
    st.session_state.lugar_actual = ""

def obtener_clave_video(wcode):
    if wcode in [0]:
        return "clear"
    elif wcode in [1, 2]:
        return "partly_cloudy"
    elif wcode in [3]:
        return "cloudy"
    elif wcode in [45, 48]:
        return "fog"
    elif wcode in [51, 53, 55, 56, 57]:
        return "drizzle"
    elif wcode in [61, 63, 65, 66, 67, 80, 81, 82]:
        return "rain"
    elif wcode in [71, 73, 75, 77, 85, 86]:
        return "snow"
    elif wcode in [95, 96, 99]:
        return "thunder"
    return "clear"

def desc_clima(wcode):
    codigos = {
        0: "☀️ Despejado",
        1: "🌤️ Mayormente despejado",
        2: "⛅ Parcialmente nublado",
        3: "☁️ Nublado",
        45: "🌫️ Niebla",
        48: "🌫️ Niebla con escarcha",
        51: "🌦️ Llovizna ligera",
        53: "🌦️ Llovizna moderada",
        55: "🌧️ Llovizna densa",
        61: "🌧️ Lluvia ligera",
        63: "🌧️ Lluvia moderada",
        65: "🌧️ Lluvia fuerte",
        80: "🌦️ Chubascos ligeros",
        81: "🌧️ Chubascos moderados",
        82: "🌧️ Chubascos violentos",
        95: "🌩️ Tormenta eléctrica",
        96: "⛈️ Tormenta con granizo ligero",
        99: "⛈️ Tormenta con granizo fuerte"
    }
    return codigos.get(wcode, "🌤️ Tiempo variable")

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
        st.markdown("<h1 style='text-align: center; color: #222; font-size: 3.5rem;'>MeteoUy</h1>", unsafe_allow_html=True)

# =========================================================
# PANTALLA 1: INICIO
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
        margin-top: 2vh;
    }
    
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.3); border-color: #38bdf8; }
        50% { box-shadow: 0 0 25px rgba(14, 165, 233, 0.75); border-color: #0284c7; }
        100% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.3); border-color: #38bdf8; }
    }

    div[data-baseweb="input"] {
        border-radius: 45px !important;
        padding: 10px 22px !important;
        border: 2.5px solid #38bdf8 !important;
        animation: pulseGlow 2.5s infinite ease-in-out !important;
        font-size: 1.25rem !important;
        background-color: #f8fafc !important;
    }
    div[data-baseweb="input"] input {
        font-size: 1.2rem !important;
    }

    .stButton > button {
        border-radius: 40px !important;
        height: 3.6rem !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        border: None !important;
        background: linear-gradient(135deg, #0284c7, #38bdf8) !important;
        color: white !important;
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(14, 165, 233, 0.5) !important;
    }

    div[data-testid="stColumn"] .stButton > button {
        background: #e0f2fe !important;
        color: #0369a1 !important;
        border: 1.5px solid #bae6fd !important;
        border-radius: 30px !important;
        height: 3rem !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(56, 189, 248, 0.15) !important;
    }
    div[data-testid="stColumn"] .stButton > button:hover {
        background: #bae6fd !important;
        color: #0284c7 !important;
        border-color: #38bdf8 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.2, 5.6, 0.2])
    with col2:
        mostrar_logo()

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form(key="search_form"):
        lugar_input = st.text_input(
            label="",
            placeholder="🔍 Escribe un barrio, pueblo o departamento (ej: Cordón, Salto, Salinas...)",
            label_visibility="collapsed"
        )
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        submit = st.form_submit_button("VER PRONÓSTICO", use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("<p style='text-align: center; color: #0284c7; font-size: 0.95rem; font-weight: 700; letter-spacing: 1px; margin-bottom: 12px;'>CONTACTATE CON METEO UY</p>", unsafe_allow_html=True)
    
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.button("✉️ Contacto", key="btn_contact", use_container_width=True)
    with c2:
        st.button("📸 Instagram", key="btn_ig", use_container_width=True)
    with c3:
        st.button("💼 LinkedIn", key="btn_li", use_container_width=True)
    with c4:
        st.button("▶️ YouTube", key="btn_yt", use_container_width=True)
    with c5:
        st.button("🎵 TikTok", key="btn_tk", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if submit and lugar_input.strip():
        st.session_state.lugar_actual = lugar_input.strip()
        st.session_state.resultado_activo = True
        st.rerun()

# =========================================================
# PANTALLA 2: RESULTADOS (FONDO DE VIDEO TOTAL Y TARJETAS BLANCAS)
# =========================================================
else:
    lugar = st.session_state.lugar_actual
    
    url_geo = f"https://nominatim.openstreetmap.org/search?q={lugar}, Uruguay&format=json&countrycodes=uy&limit=1"
    try:
        res_geo = requests.get(url_geo, headers={"User-Agent": "MeteoUy-App"}).json()
    except Exception:
        res_geo = []
    
    if res_geo:
        lat = float(res_geo[0]["lat"])
        lon = float(res_geo[0]["lon"])
        
        url_meteo = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&forecast_days=3&timezone=auto"
        data = requests.get(url_meteo).json()
        daily = data.get("daily", {})
        
        wcodes = daily.get("weathercode", [0])
        wcode_hoy = wcodes[0] if wcodes else 0
        
        tipo_fondo = obtener_clave_video(wcode_hoy)
        url_video = VIDEOS.get(tipo_fondo, VIDEOS["clear"])
        
        # Estilos CSS avanzados para el comportamiento hover + atenuación interactiva
        st.markdown(f"""
        <style>
        .stApp {{
            background: transparent !important;
        }}
        
        .video-fondo-absoluto {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            z-index: -99999;
            pointer-events: none;
            filter: brightness(0.5);
        }}

        /* Asegurar que el contenedor de las columnas tenga flex para igualar la altura */
        div[data-testid="stHorizontalBlock"] {{
            align-items: stretch !important;
        }}

        div[data-testid="stColumn"] {{
            display: flex !important;
            flex-direction: column !important;
        }}

        /* Tarjeta base con diseño responsivo */
        .cuadrado-pronostico {{
            background: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 22px;
            padding: 24px 18px;
            border: 1.5px solid rgba(255, 255, 255, 0.9);
            color: #1e293b;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
            min-height: 340px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
            transition: transform 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275), 
                        opacity 0.35s ease, 
                        box-shadow 0.35s ease, 
                        background 0.35s ease;
            cursor: pointer;
        }}

        /* EFECTO HOVER: Agrandar la tarjeta en la que te apoyas */
        .cuadrado-pronostico:hover {{
            transform: translateY(-8px) scale(1.05) !important;
            background: rgba(255, 255, 255, 0.98) !important;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45) !important;
            border-color: #38bdf8 !important;
            z-index: 10;
        }}

        /* ATENUACIÓN: Cuando te apoyas en una tarjeta, las otras dos quedan más tenues */
        div[data-testid="stHorizontalBlock"]:has(.cuadrado-pronostico:hover) .cuadrado-pronostico:not(:hover) {{
            opacity: 0.45 !important;
            transform: scale(0.97) !important;
            filter: blur(0.5px);
        }}

        .estado-clima-txt {{
            font-size: 0.95em;
            color: #0284c7;
            font-weight: 700;
            margin-bottom: 8px;
            min-height: 2.8em;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        </style>

        <video autoplay muted loop playsinline class="video-fondo-absoluto">
            <source src="{url_video}" type="video/mp4">
        </video>
        """, unsafe_allow_html=True)
        
        if st.button("⬅️ Buscar otra ubicación"):
            st.session_state.resultado_activo = False
            st.session_state.lugar_actual = ""
            st.rerun()
            
        st.markdown(f"<h1 style='text-align: center; color: white; text-shadow: 2px 2px 8px rgba(0,0,0,0.9); margin-bottom: 25px;'>📍 {lugar.title()}</h1>", unsafe_allow_html=True)
        
        fechas = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        lluvia = daily.get("precipitation_sum", [])
        viento = daily.get("wind_speed_10m_max", daily.get("windspeed_10m_max", []))
        
        cols = st.columns(3)
        etiquetas = ["Hoy", "Mañana", "Pasado Mañana"]
        
        for i in range(min(3, len(fechas))):
            wc = wcodes[i] if i < len(wcodes) else 0
            estado_txt = desc_clima(wc)
            
            html_tarjeta = f'<div class="cuadrado-pronostico"><div><h2 style="color: #0f172a; margin-bottom: 2px; font-weight: 700;">{etiquetas[i]}</h2><p style="font-size: 0.85em; color: #64748b; margin-bottom: 8px; font-weight: 600;">{fechas[i]}</p><div class="estado-clima-txt">{estado_txt}</div><hr style="border-color: #e2e8f0; margin-bottom: 12px;"></div><div><p style="font-size: 1.1em; margin: 6px 0;"><b>🌡️ Máx:</b> {t_max[i]} °C</p><p style="font-size: 1.1em; margin: 6px 0;"><b>❄️ Mín:</b> {t_min[i]} °C</p><p style="font-size: 1.1em; margin: 6px 0;"><b>🌧️ Lluvia:</b> {lluvia[i]} mm</p><p style="font-size: 1.1em; margin: 6px 0;"><b>💨 Viento:</b> {viento[i]} km/h</p></div></div>'
            
            with cols[i]:
                st.markdown(html_tarjeta, unsafe_allow_html=True)
    else:
        st.error("No se encontró la ubicación ingresada en Uruguay.")
        if st.button("Volver"):
            st.session_state.resultado_activo = False
            st.rerun()
