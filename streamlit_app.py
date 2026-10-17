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

# ---------------------------------------------------------
# ESTADO DE LA SESIÓN
# ---------------------------------------------------------
if "resultado_activo" not in st.session_state:
    st.session_state.resultado_activo = False
if "lugar_actual" not in st.session_state:
    st.session_state.lugar_actual = ""

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

# --- TITULAR HUMANO ENFOCADO EN LAS PRÓXIMAS HORAS ---
def generar_titular_pronostico_horas(wcode, lluvia_hoy, viento):
    if lluvia_hoy > 1.5 or wcode in range(51, 68) or wcode in range(80, 100):
        return "🌧️", "Se esperan desmejoras y probabilidad de precipitaciones en las próximas horas. Conviene estar prevenido."
    if viento > 28:
        return "🌬️", "Atención: se prevé un incremento notable de la intensidad del viento hacia la tarde y noche."
    if wcode == 0 or wcode == 1:
        return "🌤️", "Condiciones estables que se mantendrán favorables durante el resto de la jornada."
    return "⛅", "Cielo variable con tendencia a mantenerse sin cambios significativos en las horas siguientes."

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
        st.markdown("<h1 style='text-align: center; color: #0284c7; font-size: 3.5rem; font-weight: 800; font-family: \"Plus Jakarta Sans\", sans-serif;'>MeteoUy</h1>", unsafe_allow_html=True)

# =========================================================
# PANTALLA 1: INICIO (BUSCADOR LIMPIO)
# =========================================================
if not st.session_state.resultado_activo:
    st.markdown("""
    <style>
    /* TIPOGRAFÍA GLOBAL */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    .stApp, html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

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

    col1, col2, col3 = st.columns([0.2, 5.6, 0.2])
    with col2:
        mostrar_logo()

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form(key="search_form"):
        lugar_input = st.text_input(
            label="Ubicación",
            placeholder="🔍 Escribe un barrio, pueblo o departamento (ej: Centro, Artigas, Salto...)",
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
# PANTALLA 2: RESULTADOS Y PRONÓSTICO
# =========================================================
else:
    lugar = st.session_state.lugar_actual
    
    url_geo = f"https://nominatim.openstreetmap.org/search?q={lugar}, Uruguay&format=json&countrycodes=uy&limit=1"
    try:
        res_geo = requests.get(url_geo, headers={"User-Agent": "MeteoUy-App"}, timeout=10).json()
    except Exception:
        res_geo = []
    
    if res_geo:
        lat = float(res_geo[0]["lat"])
        lon = float(res_geo[0]["lon"])
        
        url_meteo = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,surface_pressure,weathercode,wind_speed_10m&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max&forecast_days=3&timezone=auto"
        data = requests.get(url_meteo).json()
        
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        temp_actual = current.get("temperature_2m", 0)
        humedad_actual = current.get("relative_humidity_2m", 0)
        sensacion_actual = current.get("apparent_temperature", 0)
        presion_actual = current.get("surface_pressure", 1013)
        viento_actual = current.get("wind_speed_10m", 0)
        wcode_actual = current.get("weathercode", 0)
        
        lluvia_diaria_hoy = 0.0
        if daily.get("precipitation_sum") and len(daily["precipitation_sum"]) > 0:
            lluvia_diaria_hoy = daily["precipitation_sum"][0] or 0.0

        icono_humano, frase_humana = generar_titular_pronostico_horas(wcode_actual, lluvia_diaria_hoy, viento_actual)
        
        st.markdown("""
        <style>
        /* TIPOGRAFÍA GLOBAL */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        .stApp, html, body, [class*="st-"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }

        .stApp {
            background-color: #f0f9ff !important;
        }
        
        .panel-actual {
            background: white;
            border-radius: 24px;
            padding: 22px 25px;
            border: 1.5px solid #bae6fd;
            color: #0f172a;
            box-shadow: 0 10px 25px rgba(14, 165, 233, 0.15);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-around;
        }

        .human-headline {
            background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
            border-left: 5px solid #0284c7;
            padding: 18px 22px;
            border-radius: 0 16px 16px 0;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.1);
            border-top: 1.5px solid #bae6fd;
            border-right: 1.5px solid #bae6fd;
            border-bottom: 1.5px solid #bae6fd;
        }

        .cuadrado-pronostico {
            background: white;
            border-radius: 20px;
            padding: 20px 15px;
            border: 1.5px solid #bae6fd;
            color: #0f172a;
            text-align: center;
            box-shadow: 0 10px 25px rgba(14, 165, 233, 0.1);
            margin-bottom: 20px;
            height: 360px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        @keyframes pulsoAzul {
            0% {
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(2, 132, 199, 0.7);
            }
            70% {
                transform: scale(1);
                box-shadow: 0 0 0 8px rgba(2, 132, 199, 0);
            }
            100% {
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(2, 132, 199, 0);
            }
        }
        .titulo-marca-lugar {
            text-align: center;
            color: #0284c7;
            font-size: 2.4rem;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.5px;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        .live-circle-container {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 8px;
            padding-top: 14px;
        }
        .blue-pulse-circle {
            width: 12px;
            height: 12px;
            background-color: #0284c7;
            border: 2px solid #bae6fd;
            border-radius: 50%;
            display: inline-block;
            animation: pulsoAzul 2s infinite ease-in-out;
        }
        .live-text-label {
            font-size: 0.8rem;
            font-weight: 700;
            color: #0369a1;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col_top1, col_top2, col_top3 = st.columns([1.2, 3.8, 1.5])
        with col_top1:
            if st.button("🌧️↩️ Volver", help="Buscar otra localidad"):
                st.session_state.resultado_activo = False
