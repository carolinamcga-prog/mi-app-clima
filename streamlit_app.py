import streamlit as st
import requests
import os
import random
import urllib.parse
import plotly.graph_objects as go
from data.localidades import LOCALIDADES_URUGUAY

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="MeteoUy - Pronóstico Profesional",
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
if "seccion_activa" not in st.session_state:
    st.session_state.seccion_activa = "inicio"
if "favoritos" not in st.session_state:
    st.session_state.favoritos = ["Montevideo", "Punta del Este", "Salto"]

# BASE DE DATOS LOCAL EXCLUSIVA PARA URUGUAY
COORDS_URUGUAY = {
    "montevideo": (-34.9011, -56.1645),
    "artigas": (-30.4033, -56.4733),
    "canelones": (-34.5228, -56.2822),
    "cerro largo": (-32.3667, -54.1833),
    "melo": (-32.3667, -54.1833),
    "colonia": (-34.4625, -57.8397),
    "colonia del sacramento": (-34.4625, -57.8397),
    "durazno": (-33.4167, -55.5333),
    "flores": (-33.5167, -56.7000),
    "trinidad": (-33.5167, -56.7000),
    "florida": (-34.1000, -56.2167),
    "lavalleja": (-34.3667, -55.2333),
    "minas": (-34.3667, -55.2333),
    "maldonado": (-34.9000, -54.9500),
    "paysandú": (-32.3167, -58.0750),
    "río negro": (-32.7333, -58.2833),
    "fray bentos": (-33.1333, -58.3000),
    "rivera": (-30.9053, -55.5505),
    "rocha": (-34.4833, -54.3333),
    "salto": (-31.3833, -57.9667),
    "salinas": (-34.7833, -55.8500),
    "san josé": (-34.3375, -56.7136),
    "soriano": (-33.2500, -58.3000),
    "mercedes": (-33.2500, -58.3000),
    "tacuarembó": (-31.7333, -55.9833),
    "treinta y tres": (-33.2333, -54.3833),
    "punta del este": (-34.9580, -54.9410),
    "piriápolis": (-34.8628, -55.2747),
    "atlántida": (-34.7719, -55.7583),
    "ciudad de la costa": (-34.8231, -55.9525),
    "carrasco": (-34.8760, -56.0520),
    "pocitos": (-34.9120, -56.1470),
    "centro": (-34.9050, -56.1910)
}

FRASES_POR_CLIMA = {
    "sol": [
        "«No hay nada más bello que la luz del sol tras disipar la niebla.»",
        "«Camina hacia el sol y las sombras quedarán siempre detrás de ti.» — Walt Whitman",
        "«El sol es el pincel con el que la naturaleza dibuja cada mañana.»",
        "«Un día despejado no solo aclara el horizonte, también renueva la mente.»",
        "«Sal al sol, respira profundo y deja que la luz haga su trabajo.»",
        "«El sol siempre vuelve a salir, recordándonos que cada día es un nuevo comienzo.»",
        "«Hay una paz especial en las mañanas claras e iluminadas.»"
    ],
    "lluvia": [
        "«La lluvia de hoy es la abundancia y la cosecha verde de mañana.»",
        "«El olor a tierra mojada nos recuerda las cosas sencillas de la vida.»",
        "«Cualquiera que diga que el sol trae felicidad nunca ha disfrutado la calma de la lluvia.»",
        "«Sin lluvia, nada crece. Aprende a abrazar las precipitaciones de la vida.»",
        "«El agua sobre el tejado es la melodía perfecta para una jornada tranquila.»",
        "«Las nubes se cargan de agua para darle vida al campo.»",
        "«Un día de lluvia invita a la pausa, al mate y a la reflexión.»"
    ],
    "tormenta": [
        "«Para apreciar la serenidad del cielo, primero hay que aprender de la tormenta.»",
        "«Las tormentas prueban la fortaleza de nuestras raíces.»",
        "«Por más fuerte que parezca el temporal, ninguna tormenta dura para siempre.»",
        "«El trueno impresiona, pero la lluvia constante es la que da fruto.»",
        "«En medio de la tormenta es donde se reconoce la calma que vendrá.»",
        "«Acepta los truenos de hoy con la certeza del cielo limpio de mañana.»"
    ],
    "viento": [
        "«No podemos cambiar la dirección del viento, pero sí ajustar las velas.» — H. Jackson Brown Jr.",
        "«El viento fuerte prueba las ramas, pero fortalece el tronco.»",
        "«Donde el viento sopla con fuerza, el aire se renueva y se vuelve puro.»",
        "«Deja que el viento se lleve lo viejo para darle espacio a lo nuevo.»",
        "«El viento nos recuerda que todo en la naturaleza está en constante movimiento.»"
    ],
    "nublado": [
        "«Incluso detrás de las nubes más densas, el sol nunca deja de brillar.»",
        "«El cielo gris posee una elegancia sobria que invita a la contemplación.»",
        "«El clima es lo que esperamos, pero el tiempo es lo que nos toca disfrutar.» — Mark Twain",
        "«Las nubes son solo la preparación de la naturaleza para el cambio.»",
        "«Un día templado y nublado es la excusa perfecta para bajar un cambio y disfrutar.»",
        "«El horizonte nublado nos enseña que el cambio es parte del ciclo natural.»"
    ]
}

def agregar_favorito(lugar):
    lugar_fmt = lugar.title()
    if lugar_fmt not in st.session_state.favoritos:
        st.session_state.favoritos.insert(0, lugar_fmt)
        if len(st.session_state.favoritos) > 4:
            st.session_state.favoritos.pop()

def obtener_frase_dinamica_clima():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=-34.9011&longitude=-56.1645&current=weathercode,wind_speed_10m"
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            data = res.json()
            current = data.get("current", {})
            wcode = current.get("weathercode", 0)
            viento = current.get("wind_speed_10m", 0)

            if wcode in [95, 96, 99]:
                categoria = "tormenta"
            elif wcode in range(51, 68) or wcode in range(80, 83):
                categoria = "lluvia"
            elif viento > 28:
                categoria = "viento"
            elif wcode in [0, 1]:
                categoria = "sol"
            else:
                categoria = "nublado"
        else:
            categoria = "nublado"
    except Exception:
        categoria = "nublado"

    return random.choice(FRASES_POR_CLIMA[categoria])

def es_coordenada_uruguay(lat, lon):
    return (-35.5 <= lat <= -30.0) and (-58.6 <= lon <= -53.0)

def obtener_descripcion_clima(wcode, is_day=1):
    if wcode == 0:
        return "Noche Despejada" if is_day == 0 else "Cielo Despejado"
    if wcode == 1:
        return "Noche Poco Nubosa" if is_day == 0 else "Poco Nuboso"
    
    descripciones = {
        2: "Parcialmente Nublado",
        3: "Nublado / Cubierto",
        45: "Niebla",
        48: "Neblina Helada",
        51: "Llovizna Leve",
        53: "Llovizna Moderada",
        55: "Garúa Densa",
        61: "Lluvia Leve",
        63: "Lluvia Moderada",
        65: "Lluvia Torrencial",
        80: "Chubascos Leves",
        81: "Chubascos Moderados",
        82: "Chubascos Violentos",
        95: "Tormenta Eléctrica",
        96: "Tormenta con Granizo",
        99: "Tormenta con Granizo Fuerte"
    }
    return descripciones.get(wcode, "Tiempo Variable")

def generar_titular_pronostico_horas(wcode, lluvia_hoy, prob_lluvia, viento, uv_actual):
    if wcode in [95, 96, 99]:
        return "Alerta por tormentas eléctricas. Evitá permanecer en espacios abiertos y resguardá vehículos."
    if lluvia_hoy > 1.5 or prob_lluvia > 60 or wcode in range(51, 68) or wcode in range(80, 100):
        return f"Inestabilidad alta ({prob_lluvia}% prob. de lluvia). Llevá paraguas o piloto si salís."
    if viento > 28:
        return "Viento fuerte en la zona. Precaución al conducir en rutas y objetos sueltos en balcones."
    if uv_actual and uv_actual >= 8.0:
        return f"Radiación UV en nivel {uv_actual:.1f} (Muy Alto). Usá protector solar SPF 50+ y lentes de sol."
    if wcode in [0, 1]:
        return "Condiciones estables y agradables para el momento del día."
    return "Cielo variable sin precipitaciones significativas previstas."

def obtener_dibujo_animado(wcode, texto_clima, is_day=1):
    t = texto_clima.lower()
    if is_day == 0 and (wcode in [0, 1] or "despejado" in t or "claro" in t or "nocturn" in t):
        return '<div class="anim-luna" style="width: 52px; height: 52px; display: inline-block;"><svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;"><path d="M42 36C42 45.9411 33.9411 54 24 54C20.6133 54 17.4475 53.053 14.75 51.4552C21.8211 51.0251 27.5 45.1378 27.5 38C27.5 30.8622 21.8211 24.9749 14.75 24.5448C17.4475 22.947 20.6133 22 24 22C33.9411 22 42 30.0589 42 36Z" fill="#38BDF8"/></svg></div>'
    elif wcode in [0, 1] or "despejado" in t or "sol" in t:
        return '<div class="anim-sol" style="width: 52px; height: 52px; display: inline-block;"><svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;"><circle cx="32" cy="32" r="14" fill="#FBBF24"/><path d="M32 6V2M32 62V58M58 32H62M2 32H6M50.4 13.6L53.2 10.8M10.8 53.2L13.6 50.4M50.4 50.4L53.2 53.2M10.8 10.8L13.6 13.6" stroke="#FBBF24" stroke-width="3.5" stroke-linecap="round"/></svg></div>'
    elif "lluvia" in t or "llovizna" in t or "chubascos" in t or "garúa" in t or wcode in range(51, 68) or wcode in range(80, 83):
        return '<div class="anim-lluvia" style="width: 52px; height: 52px; display: inline-block;"><svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;"><path d="M46 28H44.7C43.3 21.6 37.6 17 31 17C24.1 17 18.5 22.4 18.1 29.3C13.6 30.1 10 34 10 38.8C10 44 14.2 48.2 19.4 48.2H46C51 48.2 55 44.2 55 39.2C55 34.2 51 30.2 46 28Z" fill="#CBD5E1"/><path d="M22 52L20 58M32 52L30 58M42 52L40 58" stroke="#38BDF8" stroke-width="3.5" stroke-linecap="round"/></svg></div>'
    elif "tormenta" in t or wcode in [95, 96, 99]:
        return '<div class="anim-tormenta" style="width: 52px; height: 52px; display: inline-block;"><svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;"><path d="M46 26H44.7C43.3 19.6 37.6 15 31 15C24.1 15 18.5 20.4 18.1 27.3C13.6 28.1 10 32 10 36.8C10 42 14.2 46.2 19.4 46.2H46C51 46.2 55 42.2 55 37.2C55 32.2 51 28.2 46 26Z" fill="#64748B"/><path d="M34 42L24 52H34L30 60L42 47H34L34 42Z" fill="#FBBF24"/></svg></div>'
    else:
        return '<div class="anim-nube" style="width: 52px; height: 52px; display: inline-block;"><svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;"><path d="M46 28H44.7C43.3 21.6 37.6 17 31 17C24.1 17 18.5 22.4 18.1 29.3C13.6 30.1 10 34 10 38.8C10 44 14.2 48.2 19.4 48.2H46C51 48.2 55 44.2 55 39.2C55 34.2 51 30.2 46 28Z" fill="#94A3B8"/></svg></div>'

def obtener_ruta_logo():
    posibles_nombres = ["logo.jpeg", "logo.jpg", "logo.png", "LOGO.JPEG", "LOGO.JPG", "LOGO.PNG"]
    for nombre in posibles_nombres:
        if os.path.exists(nombre):
            return nombre
    return None

def mostrar_logo():
    logo_path = obtener_ruta_logo()
    if logo_path:
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #0284c7; font-size: 3.2rem; font-weight: 800; font-family: \"Plus Jakarta Sans\", sans-serif; margin: 0;'>MeteoUy</h1>", unsafe_allow_html=True)


# =========================================================
# PANTALLA 1: INICIO
# =========================================================
if not st.session_state.resultado_activo:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    .stApp, html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .stApp {
        background-color: #ffffff !important;
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.3); border-color: #38bdf8; }
        50% { box-shadow: 0 0 22px rgba(14, 165, 233, 0.7); border-color: #0284c7; }
        100% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.3); border-color: #38bdf8; }
    }

    div[data-testid="stTextInput"] input {
        border-radius: 45px !important;
        border: 2.5px solid #38bdf8 !important;
        animation: pulseGlow 2.5s infinite ease-in-out !important;
        background-color: #f8fafc !important;
        height: 3.6rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #0f172a !important;
        padding-left: 20px !important;
    }

    .stButton > button {
        border-radius: 40px !important;
        height: 3.6rem !important;
        font-size: 1.2rem !important;
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

    div[data-testid="stHorizontalBlock"] .stButton > button {
        background: #f0f9ff !important;
        color: #0369a1 !important;
        border: 1.5px solid #bae6fd !important;
        border-radius: 20px !important;
        height: 2.5rem !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }

    .card-pro {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 24px;
        padding: 32px;
        color: #ffffff;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.25);
        border: 1.5px solid rgba(56, 189, 248, 0.3);
        margin-bottom: 20px;
    }

    .frase-dia {
        text-align: center;
        font-style: italic;
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 6px 0 18px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        if st.button("MeteoUy", key="btn_mu", use_container_width=True):
            st.session_state.seccion_activa = "inicio" if st.session_state.seccion_activa == "meteo_uy" else "meteo_uy"
            st.rerun()
    with nav2:
        if st.button("Servicios", key="btn_serv", use_container_width=True):
            st.session_state.seccion_activa = "inicio" if st.session_state.seccion_activa == "servicios" else "servicios"
            st.rerun()
    with nav3:
        if st.button("MeteoUy Pro", key="btn_pro", use_container_width=True):
            st.session_state.seccion_activa = "inicio" if st.session_state.seccion_activa == "pro" else "pro"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([0.2, 5.6, 0.2])
    with col2:
        mostrar_logo()

    frase_hoy = obtener_frase_dinamica_clima()
    st.markdown(f"<div class='frase-dia'>{frase_hoy}</div>", unsafe_allow_html=True)

    if st.session_state.seccion_activa == "meteo_uy":
        st.subheader("¿Qué es MeteoUy?")
        st.write("**MeteoUy** es la plataforma privada de monitoreo meteorológico de alta resolución en Uruguay. Unificamos telemetría satelital, cobertura de radares regionales y estaciones automáticas para ofrecer pronósticos exactos en más de 600 localidades del país.")

    elif st.session_state.seccion_activa == "servicios":
        st.subheader("Asesoramiento Meteorológico para Empresas")
        st.write("Ofrecemos pronósticos dedicados y análisis de riesgo climático a medida para Agro, Construcción, Logística y Eventos.")

    elif st.session_state.seccion_activa == "pro":
        st.markdown("""
        <div class="card-pro">
            <span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 0.8rem;">PLAN EMPRESARIAL</span>
            <h2 style="color: #ffffff; margin-top: 10px;">MeteoUy Pro ($100 USD/mes)</h2>
            <p style="color: #cbd5e1;">Acceso prioritario a modelos extendidos de 14 días y alertas críticas por WhatsApp.</p>
        </div>
        """, unsafe_allow_html=True)

    def procesar_busqueda():
        val = st.session_state.input_localidad_texto.strip()
        if val:
            st.session_state.lugar_actual = val
            agregar_favorito(val)
            st.session_state.resultado_activo = True

    localidad_ingresada = st.text_input(
        label="Buscador",
        placeholder="Escribí una localidad de Uruguay...",
        key="input_localidad_texto",
        on_change=procesar_busqueda,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    if st.button("VER PRONÓSTICO", use_container_width=True):
        if localidad_ingresada and localidad_ingresada.strip():
            st.session_state.lugar_actual = localidad_ingresada.strip()
            agregar_favorito(localidad_ingresada.strip())
            st.session_state.resultado_activo = True
            st.rerun()
        else:
            st.warning("⚠️ Por favor, escribí una localidad del Uruguay.")

    # RECIENTES / FAVORITOS
    if st.session_state.favoritos:
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.82rem; font-weight: 700; margin-top: 15px;'>📍 BÚSQUEDAS RECIENTES</p>", unsafe_allow_html=True)
        cols_fav = st.columns(len(st.session_state.favoritos))
        for idx, fav in enumerate(st.session_state.favoritos):
            with cols_fav[idx]:
                if st.button(fav, key=f"fav_{idx}", use_container_width=True):
                    st.session_state.lugar_actual = fav
                    st.session_state.resultado_activo = True
                    st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #0284c7; font-size: 0.95rem; font-weight: 700; letter-spacing: 1px; margin-bottom: 12px;'>CONTACTATE CON METEO UY</p>", unsafe_allow_html=True)
    
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.button("✉️", key="btn_contact", use_container_width=True)
    with c2: st.button("📸", key="btn_ig", use_container_width=True)
    with c3: st.button("💼", key="btn_li", use_container_width=True)
    with c4: st.button("▶️", key="btn_yt", use_container_width=True)
    with c5: st.button("🎵", key="btn_tk", use_container_width=True)

# =========================================================
# PANTALLA 2: RESULTADOS DE CLIMA
# =========================================================
else:
    lugar_ingresado = st.session_state.lugar_actual.strip()
    lugar_lower = lugar_ingresado.lower()
    
    lat, lon = None, None
    lugar_encontrado = lugar_ingresado.title()
    
    for clave, coords in COORDS_URUGUAY.items():
        if clave in lugar_lower or lugar_lower in clave:
            lat, lon = coords
            lugar_encontrado = clave.title()
            break
            
    if lat is None and lon is None:
        try:
            query_uy = urllib.parse.quote(f"{lugar_ingresado}, Uruguay")
            url_geo = f"https://geocoding-api.open-meteo.com/v1/search?name={query_uy}&count=5&language=es&format=json"
            res_geo = requests.get(url_geo, timeout=8).json()
            
            if "results" in res_geo and len(res_geo["results"]) > 0:
                for res in res_geo["results"]:
                    cand_lat = float(res["latitude"])
                    cand_lon = float(res["longitude"])
                    pais = res.get("country", "").lower()
                    
                    if "uruguay" in pais or es_coordenada_uruguay(cand_lat, cand_lon):
                        lat, lon = cand_lat, cand_lon
                        lugar_encontrado = res.get("name", lugar_ingresado.title())
                        break
        except Exception:
            pass

    if lat is None or lon is None or not es_coordenada_uruguay(lat, lon):
        st.warning("⚠️ **MeteoUy es un servicio exclusivo para Uruguay.**")
        if st.button("🌧️↩️ Volver al buscador"):
            st.session_state.resultado_activo = False
            st.rerun()
    else:
        url_meteo = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,surface_pressure,weathercode,wind_speed_10m,visibility,uv_index,is_day&hourly=temperature_2m,precipitation_probability,weathercode&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,windspeed_10m_max,uv_index_max&forecast_days=3&models=best_match&timezone=auto"
        
        try:
            data = requests.get(url_meteo, timeout=10).json()
        except Exception:
            data = {}
            
        current = data.get("current", {})
        daily = data.get("daily", {})
        hourly = data.get("hourly", {})
        
        temp_actual = current.get("temperature_2m", 0)
        humedad_actual = current.get("relative_humidity_2m", 0)
        viento_actual = current.get("wind_speed_10m", 0)
        wcode_actual = current.get("weathercode", 0)
        uv_actual = current.get("uv_index", 0.0)
        is_day_actual = current.get("is_day", 1)
        
        prob_lluvia_hoy = daily.get("precipitation_probability_max", [0])[0] or 0
        lluvia_diaria_hoy = daily.get("precipitation_sum", [0.0])[0] or 0.0

        frase_humana = generar_titular_pronostico_horas(wcode_actual, lluvia_diaria_hoy, prob_lluvia_hoy, viento_actual, uv_actual)
        desc_actual = obtener_descripcion_clima(wcode_actual, is_day_actual)
        dibujo_hoy = obtener_dibujo_animado(wcode_actual, desc_actual, is_day_actual)

        st.markdown("""
        <style>
        .stApp { background: linear-gradient(180deg, #0b1d3a 0%, #1e3c72 50%, #0a192f 100%) !important; }
        .card-editorial-hoy { background: rgba(15, 32, 56, 0.75) !important; border-radius: 24px; padding: 24px; color: #fff; margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.12); }
        .card-editorial-semana { background: rgba(255, 255, 255, 0.96) !important; border-radius: 20px; padding: 18px 22px; color: #0f172a; margin-bottom: 14px; }
        .alerta-banner { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #fca5a5; padding: 10px 16px; border-radius: 16px; margin-bottom: 15px; font-weight: 600; font-size: 0.9rem; }
        </style>
        """, unsafe_allow_html=True)
        
        col_top1, col_top2, col_top3 = st.columns([1.2, 3.8, 1.5])
        with col_top1:
            if st.button("← Volver"):
                st.session_state.resultado_activo = False
                st.rerun()
        with col_top2:
            st.markdown(f"<h2 style='text-align: center; color: white; margin: 0;'>MeteoUy</h2><p style='text-align: center; color: #38bdf8; font-weight: 700; margin: 0;'>📍 {lugar_encontrado}</p>", unsafe_allow_html=True)
        with col_top3:
            st.markdown("<div style='text-align: right;'><span style='background: rgba(220, 38, 38, 0.2); color: #f87171; padding: 4px 10px; border-radius: 12px; font-weight: 800; font-size: 0.75rem;'>LIVE</span></div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # BANNER AUTOMÁTICO DE ALERTA TEMPRANA
        if viento_actual > 40 or prob_lluvia_hoy > 70 or wcode_actual in [95, 96, 99]:
            st.markdown(f"<div class='alerta-banner'>⚠️ <b>AVISO METEO UY:</b> Condiciones adversas previstas en la zona ({desc_actual}). Extremar precauciones.</div>", unsafe_allow_html=True)

        t_max_hoy = daily.get("temperature_2m_max", [temp_actual])[0]
        
        st.markdown(f"""
        <div class="card-editorial-hoy">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 0.8rem; font-weight: 800; color: #94a3b8;">CONDICIÓN ACTUAL</span>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin-top: 2px;">{desc_actual}</div>
                </div>
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div>{dibujo_hoy}</div>
                    <div style="text-align: right;">
                        <span style="font-size: 3rem; font-weight: 800; color: #ffffff;">{temp_actual}°</span>
                        <span style="font-size: 1.1rem; color: #94a3b8;"> / {t_max_hoy}°</span>
                    </div>
                </div>
            </div>
            <p style="font-size: 0.95rem; font-weight: 600; color: #f1f5f9; margin: 14px 0 0 0;">{frase_humana}</p>
        </div>
        """, unsafe_allow_html=True)

        # GRÁFICO PLOTLY DE TEMPERATURA PRÓXIMAS 24 HORAS
        if "temperature_2m" in hourly and "time" in hourly:
            horas = [t.split("T")[1][:5] for t in hourly["time"][:24]]
            temps = hourly["temperature_2m"][:24]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=horas, y=temps,
                mode='lines+markers',
                line=dict(color='#38bdf8', width=3, shape='spline'),
                marker=dict(size=6, color='#ffffff'),
                hovertemplate='%{x}hs: <b>%{y}°C</b><extra></extra>'
            ))
            fig.update_layout(
                title=dict(text="📈 Evolución Térmica (Próximas 24hs)", font=dict(color="#ffffff", size=14)),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=35, b=10),
                height=180,
                xaxis=dict(showgrid=False, tickfont=dict(color='#94a3b8', size=10)),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#94a3b8', size=10))
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # EXTENDIDO
        st.markdown("<h3 style='color: white; font-size: 1rem; font-weight: 700; margin: 15px 0 10px 0;'>📅 Pronóstico Extendido</h3>", unsafe_allow_html=True)
        
        fechas = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        prob_lluvia_diaria = daily.get("precipitation_probability_max", [])
        viento_diario = daily.get("windspeed_10m_max", [])
        wcodes_daily = daily.get("weathercode", [])
        
        etiquetas = ["MAÑANA", "PASADO MAÑANA"]
        
        for i in range(1, min(3, len(fechas))):
            codigo_clima = wcodes_daily[i] if i < len(wcodes_daily) else 0
            estado_texto = obtener_descripcion_clima(codigo_clima, is_day=1)
            dibujo_ext = obtener_dibujo_animado(codigo_clima, estado_texto, is_day=1)
            
            tmax_val = t_max[i] if i < len(t_max) else "--"
            tmin_val = t_min[i] if i < len(t_min) else "--"
            prob_val = prob_lluvia_diaria[i] if i < len(prob_lluvia_diaria) else 0
            viento_val = viento_diario[i] if i < len(viento_diario) else "--"
            
            st.markdown(f"""
            <div class="card-editorial-semana">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 0
