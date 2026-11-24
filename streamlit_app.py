import base64
import os
import requests
import streamlit as st

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="MeteoUy",
    page_icon="🌤️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# CATÁLOGO DE VÍDEOS POR ESCENARIO METEOROLÓGICO
# Podés poner URLs .mp4 o rutas locales (ej: "videos/llovizna.mp4")
# ---------------------------------------------------------
VIDEOS = {
    "clear": "https://assets.mixkit.co/videos/preview/mixkit-sun-shining-through-the-trees-11860-large.mp4",
    "partly_cloudy": "https://assets.mixkit.co/videos/preview/mixkit-time-lapse-of-clouds-moving-fast-4105-large.mp4",
    "cloudy": "https://assets.mixkit.co/videos/preview/mixkit-time-lapse-of-clouds-moving-fast-4105-large.mp4",
    "fog": "https://assets.mixkit.co/videos/preview/mixkit-time-lapse-of-clouds-moving-fast-4105-large.mp4",
    "drizzle": "https://assets.mixkit.co/videos/preview/mixkit-rain-drops-falling-on-a-window-pane-17482-large.mp4",
    "rain": "https://assets.mixkit.co/videos/preview/mixkit-rain-drops-falling-on-a-window-pane-17482-large.mp4",
    "thunder": "https://assets.mixkit.co/videos/preview/mixkit-lightning-strike-in-a-cloudy-sky-42861-large.mp4",
}

ETIQUETAS_CLIMA = {
    "clear": "☀️ Cielo despejado",
    "partly_cloudy": "⛅ Parcialmente nublado",
    "cloudy": "☁️ Nublado",
    "fog": "🌫️ Neblina / Niebla",
    "drizzle": "🌦️ Llovizna",
    "rain": "🌧️ Lluvia / Chubascos",
    "thunder": "⛈️ Tormenta",
}

FRASES_PRONOSTICO = {
    "clear": "Jornada soleada y de cielo despejado, ideal para actividades al aire libre.",
    "partly_cloudy": "Cielo con intervalos de sol y nubes pasajeras a lo largo del día.",
    "cloudy": "Ambiente mayormente nublado y gris, con baja presencia de sol.",
    "fog": "Presencia de neblina o niebla; precaución por visibilidad reducida.",
    "drizzle": "Posibilidad de lloviznas aisladas; llevá paraguas o abrigo liviano.",
    "rain": "Episodios de lluvia o chubascos; se recomienda planificar bajo techo.",
    "thunder": "Actividad eléctrica y tormentas; extremá las precauciones.",
}

# ---------------------------------------------------------
# CONTROL DE ESTADO DE NAVEGACIÓN
# ---------------------------------------------------------
if "resultado_activo" not in st.session_state:
    st.session_state.resultado_activo = False
if "lugar_actual" not in st.session_state:
    st.session_state.lugar_actual = ""


# ---------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------
def obtener_tipo_clima(wcode: int) -> str:
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
        return "rain"
    elif wcode in [95, 96, 99]:
        return "thunder"
    return "partly_cloudy"


@st.cache_data(ttl=600)
def obtener_video_src(fuente: str) -> str:
    """Devuelve una URL o un data URI base64 si el vídeo es un archivo local."""
    if os.path.exists(fuente):
        with open(fuente, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:video/mp4;base64,{b64}"
    return fuente


@st.cache_data(ttl=600)
def buscar_coordenadas_uy(lugar: str):
    url_geo = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{lugar}, Uruguay",
        "format": "json",
        "countrycodes": "uy",
        "limit": 1,
    }
    res = requests.get(
        url_geo,
        params=params,
        headers={"User-Agent": "MeteoUy-App/1.0 (contacto@meteouy.local)"},
        timeout=10,
    )
    res.raise_for_status()
    datos = res.json()
    if datos:
        return (
            float(datos[0]["lat"]),
            float(datos[0]["lon"]),
            datos[0].get("display_name", lugar),
        )
    return None


@st.cache_data(ttl=600)
def obtener_pronostico_3_dias(lat: float, lon: float) -> dict:
    url_meteo = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "forecast_days": 3,
        "timezone": "auto",
    }
    res = requests.get(url_meteo, params=params, timeout=10)
    res.raise_for_status()
    return res.json().get("daily", {})


def mostrar_logo():
    posibles_nombres = [
        "logo.jpeg",
        "logo.jpg",
        "logo.png",
        "LOGO.JPEG",
        "LOGO.JPG",
        "LOGO.PNG",
    ]
    logo_encontrado = next((n for n in posibles_nombres if os.path.exists(n)), None)

    if logo_encontrado:
        st.image(logo_encontrado, use_container_width=True)
    else:
        st.markdown(
            "<h1 style='text-align: center; color: #111827; font-size: 3.5rem; background: transparent;'>MeteoUy</h1>",
            unsafe_allow_html=True,
        )


# =========================================================
# PANTALLA 1: INICIO (PANTALLA 100% BLANCA + LOGO LIMPIO)
# =========================================================
if not st.session_state.resultado_activo:
    st.markdown(
        """
        <style>
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"],
        .main,
        .block-container {
            background-color: #ffffff !important;
            background: #ffffff !important;
        }

        div[data-testid="stForm"] {
            background-color: #ffffff !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }

        div[data-baseweb="input"] {
            border-radius: 45px !important;
            padding: 8px 20px !important;
            border: 1.5px solid #cbd5e1 !important;
            background-color: #ffffff !important;
            box-shadow: none !important;
        }
        div[data-baseweb="input"] input {
            font-size: 1.1rem !important;
            background-color: #ffffff !important;
            color: #111827 !important;
        }

        .stButton > button,
        div[data-testid="stColumn"] .stButton > button {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #111827 !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 30px !important;
            box-shadow: none !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:hover,
        div[data-testid="stColumn"] .stButton > button:hover {
            background: #f8fafc !important;
            border-color: #94a3b8 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([0.2, 5.6, 0.2])
    with col2:
        mostrar_logo()

    with st.form(key="search_form"):
        lugar_input = st.text_input(
            label="",
            placeholder="🔍 Escribe un barrio, pueblo o departamento (ej: Cordón, Salto, Salinas...)",
            label_visibility="collapsed",
        )
        submit = st.form_submit_button("VER PRONÓSTICO", use_container_width=True)

    st.markdown(
        "<p style='text-align: center; color: #334155; font-size: 0.9rem; font-weight: 700; letter-spacing: 1px; margin-top: 24px; margin-bottom: 10px;'>CONTACTATE CON METEO UY</p>",
        unsafe_allow_html=True,
    )

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
# PANTALLA 2: RESULTADOS (VÍDEO TENUE DE FONDO + 3 CUADROS BLANCOS)
# =========================================================
else:
    lugar = st.session_state.lugar_actual

    try:
        geo = buscar_coordenadas_uy(lugar)
    except requests.RequestException:
        st.error("Hubo un problema al consultar el servicio de ubicación. Intentá nuevamente.")
        if st.button("Volver"):
            st.session_state.resultado_activo = False
            st.rerun()
        st.stop()

    if geo:
        lat, lon, _ = geo
        try:
            daily = obtener_pronostico_3_dias(lat, lon)
        except requests.RequestException:
            st.error("No se pudo obtener el pronóstico en este momento.")
            if st.button("Volver"):
                st.session_state.resultado_activo = False
                st.rerun()
            st.stop()

        wcodes = daily.get("weathercode", [0])
        wcode_hoy = int(wcodes[0]) if wcodes else 0
        tipo_clima = obtener_tipo_clima(wcode_hoy)

        video_fuente = VIDEOS.get(tipo_clima, VIDEOS["partly_cloudy"])
        video_src = obtener_video_src(video_fuente)
        etiqueta_escenario = ETIQUETAS_CLIMA.get(tipo_clima, "🌤️ Condición actual")

        st.markdown(
            f"""
            <style>
            #video-fondo {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                z-index: -10;
                object-fit: cover;
                filter: brightness(0.45) contrast(0.95) saturate(0.85);
                pointer-events: none;
            }}

            #velo-video {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                z-index: -9;
                background: rgba(15, 23, 42, 0.28);
                pointer-events: none;
            }}

            .stApp,
            [data-testid="stAppViewContainer"],
            [data-testid="stHeader"] {{
                background: transparent !important;
            }}

            .badge-escenario {{
                display: inline-block;
                background: rgba(255, 255, 255, 0.88);
                color: #0f172a;
                padding: 6px 16px;
                border-radius: 999px;
                font-weight: 700;
                font-size: 0.95rem;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }}

            .cuadrado-pronostico {{
                background: rgba(255, 255, 255, 0.94);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 24px 18px;
                border: 1px solid rgba(255, 255, 255, 0.95);
                color: #1e293b;
                text-align: center;
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
                margin-bottom: 20px;
            }}

            .frase-pronostico {{
                font-size: 0.92em;
                color: #334155;
                font-style: italic;
                margin: 10px 0 14px 0;
                line-height: 1.35;
            }}
            </style>

            <video autoplay loop muted playsinline id="video-fondo" key="{tipo_clima}">
                <source src="{video_src}" type="video/mp4">
            </video>
            <div id="velo-video"></div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("⬅️ Buscar otra ubicación"):
            st.session_state.resultado_activo = False
            st.session_state.lugar_actual = ""
            st.rerun()

        st.markdown(
            f"<h1 style='text-align: center; color: white; text-shadow: 2px 2px 10px rgba(0,0,0,0.85); margin-bottom: 8px;'>📍 {lugar.title()}</h1>"
            f"<div style='text-align: center; margin-bottom: 24px;'><span class='badge-escenario'>{etiqueta_escenario}</span></div>",
            unsafe_allow_html=True,
        )

        fechas = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        lluvia = daily.get("precipitation_sum", [])
        viento = daily.get("windspeed_10m_max", [])

        cols = st.columns(3)
        etiquetas = ["Hoy", "Mañana", "Pasado Mañana"]

        for i in range(min(3, len(fechas))):
            wcode_dia = obtener_tipo_clima(int(wcodes[i])) if i < len(wcodes) else tipo_clima
            icono_dia = ETIQUETAS_CLIMA.get(wcode_dia, "").split(" ")[0]
            frase_dia = FRASES_PRONOSTICO.get(
                wcode_dia, "Condiciones variables previstas para esta jornada."
            )
            with cols[i]:
                st.markdown(
                    f"""
                    <div class="cuadrado-pronostico">
                        <div style="font-size: 1.8rem; margin-bottom: 4px;">{icono_dia}</div>
                        <h2 style="color: #0f172a; margin-bottom: 4px; font-weight: 700; font-size: 1.4rem;">{etiquetas[i]}</h2>
                        <p style="font-size: 0.88em; color: #64748b; margin-bottom: 8px; font-weight: 600;">{fechas[i]}</p>
                        <p class="frase-pronostico">“{frase_dia}”</p>
                        <hr style="border-color: #e2e8f0; margin-bottom: 14px;">
                        <p style="font-size: 1.1em; margin: 8px 0;"><b>🌡️ Máx:</b> {t_max[i]} °C</p>
                        <p style="font-size: 1.1em; margin: 8px 0;"><b>❄️ Mín:</b> {t_min[i]} °C</p>
                        <p style="font-size: 1.1em; margin: 8px 0;"><b>🌧️ Lluvia:</b> {lluvia[i]} mm</p>
                        <p style="font-size: 1.1em; margin: 8px 0;"><b>💨 Viento:</b> {viento[i]} km/h</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.error("No se encontró la ubicación ingresada en Uruguay.")
        if st.button("Volver"):
            st.session_state.resultado_activo = False
            st.rerun()
