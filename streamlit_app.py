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
# RUTAS DE VIDEOS LOCALES Y RESPALDO EN LÍNEA
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
        82: "Chubascos Violentos ⛈️",
        95: "Tormenta Eléctrica ⛈️⚡",
        96: "Tormenta con Granizo 🌩️🧊",
        99: "Tormenta con Granizo Fuerte 🌩️🧊"
    }
    return descripciones.get(wcode, "Tiempo Variable 🌤️")

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
        st.markdown("<h1 style='text-align: center; color: #0284c7; font-size: 3.5rem; font-weight: 800;'>MeteoUy</h1>", unsafe_allow_html=True)

# =========================================================
# PANTALLA 1: INICIO (BUSCADOR Y BOTONES)
# =========================================================
if not st.session_state.resultado_activo:
    st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff !important;
    }
    
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.3); border-color: #38bdf8; }
        50% { box-shadow: 0 0 25px rgba(14, 165, 233, 0.75); border-color: #0284c7; }
        100% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.3); border-color: #38bdf8; }
    }

    div[data-baseweb="input"] {
        border-radius: 45px !important;
        padding: 8px 20px !important;
        border: 2.5px solid #38bdf8 !important;
        animation: pulseGlow 2.5s infinite ease-in-out !important;
        font-size: 1.25rem !important;
        background-color: #f8fafc !important;
    }
    div[data-baseweb="input"] input {
        font-size: 1.15rem !important;
    }

    /* Botón VER PRONÓSTICO */
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

    /* Botones de redes sociales */
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

    col1, col2, col3 = st.columns([0.2, 5.6, 0.2])
    with col2:
        mostrar_logo()

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form(key="search_form"):
        lugar_input = st.text_input(
            label="Ubicación",
            placeholder="🔍 Escribe un barrio, pueblo o departamento (ej: Cordón, Centro, Salto...)",
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

    if submit and lugar_input.strip():
        st.session_state.lugar_actual = lugar_input.strip()
        st.session_state.resultado_activo = True
        st.rerun()

# =========================================================
# PANTALLA 2: RESULTADOS (VIDEO DE FONDO + NUBECITA DE RETORNO)
# =========================================================
else:
    lugar = st.session_state.lugar_actual
    
    url_geo = f"https://nominatim.openstreetmap.org/search?q={lugar}, Uruguay&format=json&countrycodes=uy&limit=1"
    res_geo = requests.get(url_geo, headers={"User-Agent": "MeteoUy-App"}).json()
    
    if res_geo:
        lat = float(res_geo[0]["lat"])
        lon = float(res_geo[0]["lon"])
        
        url_meteo = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max&forecast_days=3&timezone=auto"
        data = requests.get(url_meteo).json()
        daily = data.get("daily", {})
        
        wcodes = daily.get("weathercode", [0])
        wcode_hoy = wcodes[0] if wcodes else 0
        
        tipo_fondo = obtener_clave_video(wcode_hoy)
        src_video = obtener_fuente_video(tipo_fondo)
        
        st.markdown(f"""
        <style>
        .stApp {{
            background: transparent !important;
        }}
        
        /* Video tenue de fondo en pantalla completa */
        .video-fondo-absoluto {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            z-index: -99999;
            pointer-events: none;
            filter: brightness(0.4) contrast(1.1);
        }}

        /* Tarjetas de pronóstico con altura unificada */
        .cuadrado-pronostico {{
            background: rgba(255, 255, 255, 0.88);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 24px;
            padding: 24px 18px;
            border: 1.5px solid rgba(255, 255, 255, 0.95);
            color: #0f172a;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
            height: 385px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .cuadrado-pronostico:hover {{
            transform: translateY(-6px);
            background: rgba(255, 255, 255, 0.95);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
        }}

        /* Botón estilo Nubecita Azul de retorno */
        div[data-testid="stButton"] button[kind="secondary"] {{
            background: linear-gradient(135deg, #38bdf8, #0284c7) !important;
            border: 2px solid rgba(255, 255, 255, 0.9) !important;
            border-radius: 30px !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            font-size: 1.05rem !important;
            padding: 8px 22px !important;
            box-shadow: 0 8px 25px rgba(14, 165, 233, 0.45) !important;
            transition: all 0.3s ease !important;
        }}
        div[data-testid="stButton"] button[kind="secondary"]:hover {{
            background: linear-gradient(135deg, #0284c7, #0369a1) !important;
            transform: translateY(-2px) scale(1.03) !important;
            box-shadow: 0 12px 30px rgba(14, 165, 233, 0.65) !important;
        }}
        </style>

        <video autoplay muted loop playsinline class="video-fondo-absoluto">
            <source src="{src_video}" type="video/mp4">
        </video>
        """, unsafe_allow_html=True)
        
        if st.button("🌧️↩️ Buscar otra localidad", help="Hacé clic para consultar el tiempo en otra zona o barrio"):
            st.session_state.resultado_activo = False
            st.session_state.lugar_actual = ""
            st.rerun()
            
        st.markdown(f"<h1 style='text-align: center; color: white; text-shadow: 2px 3px 12px rgba(0,0,0,0.9); font-size: 3rem; font-weight: 800; margin-top: 5px; margin-bottom: 25px;'>📍 {lugar.title()}</h1>", unsafe_allow_html=True)
        
        fechas = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        lluvia = daily.get("precipitation_sum", [])
        viento = daily.get("windspeed_10m_max", [])
        
        cols = st.columns(3)
        etiquetas = ["Hoy", "Mañana", "Pasado Mañana"]
        
        for i in range(min(3, len(fechas))):
            codigo_clima = wcodes[i] if i < len(wcodes) else 0
            estado_texto = obtener_descripcion_clima(codigo_clima)
            
            with cols[i]:
                st.markdown(f"""
                <div class="cuadrado-pronostico">
                    <div>
                        <h2 style="color: #0284c7; margin-bottom: 2px; font-weight: 800; font-size: 1.4rem;">{etiquetas[i]}</h2>
                        <p style="font-size: 0.85em; color: #64748b; margin-bottom: 8px; font-weight: 600;">{fechas[i]}</p>
                        <p style="font-size: 0.9rem; color: #1e293b; font-weight: 700; margin-bottom: 10px; line-height: 1.2;">{estado_texto}</p>
                    </div>
                    <div>
                        <hr style="border-color: #cbd5e1; margin: 8px 0 12px 0;">
                        <p style="font-size: 1.05em; margin: 6px 0;"><b>🌡️ Máx:</b> {t_max[i]} °C</p>
                        <p style="font-size: 1.05em; margin: 6px 0;"><b>❄️ Mín:</b> {t_min[i]} °C</p>
                        <p style="font-size: 1.05em; margin: 6px 0;"><b>🌧️ Lluvia:</b> {lluvia[i]} mm</p>
                        <p style="font-size: 1.05em; margin: 6px 0;"><b>💨 Viento:</b> {viento[i]} km/h</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("No se encontró la ubicación ingresada en Uruguay. Por favor, intenta escribiendo otra zona o departamento.")
        if st.button("🌧️↩️ Buscar otra localidad", help="Hacé clic para volver al buscador"):
            st.session_state.resultado_activo = False
            st.rerun()
