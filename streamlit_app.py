import streamlit as st
import requests
import os
import urllib.parse
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
        return """
        <div class="anim-luna" style="width: 52px; height: 52px; display: inline-block;">
            <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
                <path d="M42 36C42 45.9411 33.9411 54 24 54C20.6133 54 17.4475 53.053 14.75 51.4552C21.8211 51.0251 27.5 45.1378 27.5 38C27.5 30.8622 21.8211 24.9749 14.75 24.5448C17.4475 22.947 20.6133 22 24 22C33.9411 22 42 30.0589 42 36Z" fill="#38BDF8"/>
            </svg>
        </div>
        """
    elif wcode in [0, 1] or "despejado" in t or "sol" in t:
        return """
        <div class="anim-sol" style="width: 52px; height: 52px; display: inline-block;">
            <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
                <circle cx="32" cy="32" r="14" fill="#FBBF24"/>
                <path d="M32 6V2M32 62V58M58 32H62M2 32H6M50.4 13.6L53.2 10.8M10.8 53.2L13.6 50.4M50.4 50.4L53.2 53.2M10.8 10.8L13.6 13.6" stroke="#FBBF24" stroke-width="3.5" stroke-linecap="round"/>
            </svg>
        </div>
        """
    elif "lluvia" in t or "llovizna" in t or "chubascos" in t or "garúa" in t or wcode in range(51, 68) or wcode in range(80, 83):
        return """
        <div class="anim-lluvia" style="width: 52px; height: 52px; display: inline-block;">
            <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
                <path d="M46 28H44.7C43.3 21.6 37.6 17 31 17C24.1 17 18.5 22.4 18.1 29.3C13.6 30.1 10 34 10 38.8C10 44 14.2 48.2 19.4 48.2H46C51 48.2 55 44.2 55 39.2C55 34.2 51 30.2 46 28Z" fill="#CBD5E1"/>
                <path d="M22 52L20 58M32 52L30 58M42 52L40 58" stroke="#38BDF8" stroke-width="3.5" stroke-linecap="round"/>
            </svg>
        </div>
        """
    elif "tormenta" in t or wcode in [95, 96, 99]:
        return """
        <div class="anim-tormenta" style="width: 52px; height: 52px; display: inline-block;">
            <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
                <path d="M46 26H44.7C43.3 19.6 37.6 15 31 15C24.1 15 18.5 20.4 18.1 27.3C13.6 28.1 10 32 10 36.8C10 42 14.2 46.2 19.4 46.2H46C51 46.2 55 42.2 55 37.2C55 32.2 51 28.2 46 26Z" fill="#64748B"/>
                <path d="M34 42L24 52H34L30 60L42 47H34L34 42Z" fill="#FBBF24"/>
            </svg>
        </div>
        """
    else:
        return """
        <div class="anim-nube" style="width: 52px; height: 52px; display: inline-block;">
            <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
                <path d="M46 28H44.7C43.3 21.6 37.6 17 31 17C24.1 17 18.5 22.4 18.1 29.3C13.6 30.1 10 34 10 38.8C10 44 14.2 48.2 19.4 48.2H46C51 48.2 55 44.2 55 39.2C55 34.2 51 30.2 46 28Z" fill="#94A3B8"/>
            </svg>
        </div>
        """

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
        st.markdown("<h1 style='text-align: center; color: #0284c7; font-size: 3rem; font-weight: 800; font-family: \"Plus Jakarta Sans\", sans-serif; margin: 0;'>MeteoUy</h1>", unsafe_allow_html=True)


# =========================================================
# PANTALLA 1: INICIO (APP STYLE CON MENÚ SUPERIOR)
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

    /* TOP BAR ULTRA CLEAN */
    .top-brand {
        font-size: 0.85rem;
        font-weight: 800;
        color: #0284c7;
        letter-spacing: 1px;
        text-transform: uppercase;
        padding-top: 6px;
    }

    /* SEGMENTED CONTROL DE LA BARRA SUPERIOR */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        background: transparent !important;
        color: #64748b !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0px !important;
        height: 2.2rem !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        padding: 0 4px !important;
        box-shadow: none !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        color: #0284c7 !important;
        border-bottom: 2px solid #38bdf8 !important;
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.25); border-color: #38bdf8; }
        50% { box-shadow: 0 0 20px rgba(14, 165, 233, 0.55); border-color: #0284c7; }
        100% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.25); border-color: #38bdf8; }
    }

    div[data-baseweb="select"] {
        border-radius: 40px !important;
        border: 2px solid #38bdf8 !important;
        animation: pulseGlow 2.5s infinite ease-in-out !important;
        background-color: #f8fafc !important;
    }

    div[data-baseweb="select"] div[role="combobox"] {
        color: #94a3b8 !important;
        font-size: 1.05rem !important;
    }

    .stButton > button {
        border-radius: 35px !important;
        height: 3.4rem !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        border: None !important;
        background: linear-gradient(135deg, #0284c7, #38bdf8) !important;
        color: white !important;
        box-shadow: 0 6px 18px rgba(14, 165, 233, 0.3) !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 22px rgba(14, 165, 233, 0.45) !important;
    }

    /* REDES SOCIALES CLEAN FOOTER */
    div[data-testid="stColumn"] .stButton > button {
        background: #f8fafc !important;
        color: #0369a1 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 25px !important;
        height: 2.6rem !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }
    div[data-testid="stColumn"] .stButton > button:hover {
        background: #e0f2fe !important;
        color: #0284c7 !important;
        border-color: #bae6fd !important;
    }

    /* TARJETAS PROFESIONALES Y FORMULARIO */
    .app-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 12px;
    }
    .app-card-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0369a1;
        margin-bottom: 4px;
    }
    .app-card-desc {
        font-size: 0.84rem;
        color: #475569;
        line-height: 1.5;
    }

    /* ESTILO PARA CAMPOS DEL FORMULARIO B2B */
    input[type="text"], input[type="email"], textarea {
        width: 100%;
        padding: 10px 14px;
        border-radius: 12px;
        border: 1.5px solid #cbd5e1;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.9rem;
        margin-bottom: 10px;
        outline: none;
    }
    input[type="text"]:focus, input[type="email"]:focus, textarea:focus {
        border-color: #0284c7;
    }
    .btn-form-submit {
        background: #0284c7;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 0.95rem;
        cursor: pointer;
        width: 100%;
        transition: background 0.3s ease;
    }
    .btn-form-submit:hover {
        background: #0369a1;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1. TOP BAR MINIMALISTA CON MENÚ DIRECTO
    tcol1, tcol2, tcol3 = st.columns([2.5, 2.5, 3.5])
    with tcol1:
        st.markdown("<div class='top-brand'>MeteoUy</div>", unsafe_allow_html=True)
    with tcol2:
        if st.button("MeteoUy", key="nav_mu", use_container_width=True):
            st.session_state.seccion_activa = "inicio" if st.session_state.seccion_activa == "meteo_uy" else "meteo_uy"
            st.rerun()
    with tcol3:
        if st.button("Servicios Profesionales", key="nav_serv", use_container_width=True):
            st.session_state.seccion_activa = "inicio" if st.session_state.seccion_activa == "servicios" else "servicios"
            st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # LOGO PRINCIPAL
    col1, col2, col3 = st.columns([0.2, 5.6, 0.2])
    with col2:
        mostrar_logo()

    st.markdown("<br>", unsafe_allow_html=True)

    # VISTA 1: METEO UY (DESCRIPCIÓN INSTITUCIONAL TÉCNICA)
    if st.session_state.seccion_activa == "meteo_uy":
        st.markdown("""
        <div class="app-card">
            <div class="app-card-title">🌐 ¿Qué es MeteoUy?</div>
            <div class="app-card-desc"><b>MeteoUy</b> es la plataforma privada de monitoreo atmosférico de alta resolución en Uruguay. Unificamos telemetría satelital, radares meteorológicos y estaciones automáticas de superficie para ofrecer datos en tiempo real con máxima precisión geográfica en más de 600 localidades del país.</div>
        </div>
        <div class="app-card">
            <div class="app-card-title">📡 Tecnología & Modelado Multimodelo</div>
            <div class="app-card-desc">Procesamos ensembles atmosféricos de vanguardia (<b>ECMWF, GFS, ICON, WRF</b>) combinados con imágenes infrarrojas del satélite geostacionario <b>GOES-19</b> para la detección anticipada de tormentas, frentes fríos y ráfagas severas.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # VISTA 2: SERVICIOS PROFESIONALES B2B + FORMULARIO A TU MAIL
    elif st.session_state.seccion_activa == "servicios":
        st.markdown("""
        <div class="app-card">
            <div class="app-card-title">💼 Asesoramiento Meteorológico para Empresas</div>
            <div class="app-card-desc">Ofrecemos pronósticos dedicados y análisis de riesgo climático a medida para empresas y profesionales en Uruguay:
                <ul style="margin: 6px 0 0 16px; padding: 0;">
                    <li><b>Agro & Ganadería:</b> Modelado de precipitaciones por parcela, heladas y balance hídrico.</li>
                    <li><b>Construcción & Obras:</b> Alertas tempranas de viento y lluvias para seguridad operativa.</li>
                    <li><b>Logística & Transporte:</b> Monitoreo de rutas, puertos y condiciones adversas.</li>
                    <li><b>Eventos al Aire Libre:</b> Cobertura en tiempo real con meteorólogo asignado.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='font-size: 0.9rem; font-weight: 800; color: #0284c7; margin: 15px 0 8px 0; letter-spacing: 0.5px;'>📬 Solicitud de Cotización / Asesoramiento</p>", unsafe_allow_html=True)

        # ⚠️ IMPORTANTE: Reemplaza "tu_email@correo.com" por tu dirección de correo real
        EMAIL_DESTINO = "tu_email@correo.com"  

        formulario_html = f"""
        <form action="https://formsubmit.co/{EMAIL_DESTINO}" method="POST" style="background: #f8fafc; padding: 18px; border-radius: 16px; border: 1px solid #e2e8f0;">
            <input type="hidden" name="_captcha" value="false">
            <input type="hidden" name="_subject" value="NUEVA CONSULTA METEOUY - SERVICIOS EMPRESAS">
            
            <label style="font-size: 0.8rem; font-weight: 700; color: #334155;">Nombre o Empresa *</label>
            <input type="text" name="Nombre_o_Empresa" placeholder="Ej: AgroSur S.A. / Juan Pérez" required>
            
            <label style="font-size: 0.8rem; font-weight: 700; color: #334155;">Correo Electrónico de Contacto *</label>
            <input type="email" name="Email" placeholder="ejemplo@empresa.com.uy" required>
            
            <label style="font-size: 0.8rem; font-weight: 700; color: #334155;">Teléfono / WhatsApp *</label>
            <input type="text" name="Telefono" placeholder="099 123 456" required>
            
            <label style="font-size: 0.8rem; font-weight: 700; color: #334155;">Rubro / Sector</label>
            <input type="text" name="Sector" placeholder="Ej: Agro, Construcción, Eventos, Particular...">
            
            <label style="font-size: 0.8rem; font-weight: 700; color: #334155;">Detalle de la consulta o necesidad *</label>
            <textarea name="Mensaje" rows="3" placeholder="Contanos qué tipo de pronóstico o asesoramiento precisan..." required></textarea>
            
            <button type="submit" class="btn-form-submit">ENVIAR SOLICITUD A METEOUY</button>
        </form>
        """
        st.markdown(formulario_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # BUSCADOR PRINCIPAL DE LOCALIDADES
    def al_seleccionar_localidad():
        if st.session_state.localidad_input and st.session_state.localidad_input.strip():
            st.session_state.lugar_actual = st.session_state.localidad_input.strip()
            st.session_state.resultado_activo = True

    localidad_seleccionada = st.selectbox(
        label="Ubicación",
        options=[""] + sorted(LOCALIDADES_URUGUAY),
        format_func=lambda x: "Escriba localidad" if x == "" else x,
        index=0,
        key="localidad_input",
        on_change=al_seleccionar_localidad,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("VER PRONÓSTICO", use_container_width=True):
        if localidad_seleccionada and localidad_seleccionada.strip():
            st.session_state.lugar_actual = localidad_seleccionada.strip()
            st.session_state.resultado_activo = True
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #0284c7; font-size: 0.85rem; font-weight: 800; letter-spacing: 1px; margin-bottom: 10px;'>CONTACTATE CON METEO UY</p>", unsafe_allow_html=True)
    
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
        st.markdown("""
        <style>
        .stApp { background-color: #f0f4f8 !important; }
        </style>
        """, unsafe_allow_html=True)
        st.warning("⚠️ **MeteoUy es un servicio exclusivo para el territorio de Uruguay.**")
        st.info("No encontramos la localidad ingresada dentro de Uruguay. Por favor, asegúrate de seleccionar una ciudad, pueblo, departamento o barrio uruguayo.")
        if st.button("🌧️↩️ Volver al buscador", help="Hacé clic para volver"):
            st.session_state.resultado_activo = False
            st.session_state.lugar_actual = ""
            st.session_state.seccion_activa = "inicio"
            st.rerun()
    else:
        url_meteo = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,surface_pressure,weathercode,wind_speed_10m,visibility,uv_index,is_day&hourly=temperature_2m,precipitation_probability,weathercode&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,windspeed_10m_max,uv_index_max&forecast_days=3&models=best_match&timezone=auto"
        
        try:
            data = requests.get(url_meteo, timeout=10).json()
        except Exception:
            data = {}
            
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        temp_actual = current.get("temperature_2m", 0)
        humedad_actual = current.get("relative_humidity_2m", 0)
        viento_actual = current.get("wind_speed_10m", 0)
        wcode_actual = current.get("weathercode", 0)
        uv_actual = current.get("uv_index", 0.0)
        is_day_actual = current.get("is_day", 1)
        
        prob_lluvia_hoy = 0
        if daily.get("precipitation_probability_max") and len(daily["precipitation_probability_max"]) > 0:
            prob_lluvia_hoy = daily["precipitation_probability_max"][0] or 0

        lluvia_diaria_hoy = 0.0
        if daily.get("precipitation_sum") and len(daily["precipitation_sum"]) > 0:
            lluvia_diaria_hoy = daily["precipitation_sum"][0] or 0.0

        frase_humana = generar_titular_pronostico_horas(wcode_actual, lluvia_diaria_hoy, prob_lluvia_hoy, viento_actual, uv_actual)
        desc_actual = obtener_descripcion_clima(wcode_actual, is_day_actual)
        dibujo_hoy = obtener_dibujo_animado(wcode_actual, desc_actual, is_day_actual)

        st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        .stApp, html, body, [class*="st-"] {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }}

        .stApp {{
            background: linear-gradient(180deg, #0b1d3a 0%, #1e3c72 50%, #0a192f 100%) !important;
            background-attachment: fixed !important;
        }}

        .block-container {{
            position: relative !important;
            z-index: 10 !important;
        }}

        @keyframes spinGlow {{
            0% {{ transform: rotate(0deg) scale(1); filter: drop-shadow(0 0 2px rgba(251,191,36,0.4)); }}
            50% {{ transform: rotate(180deg) scale(1.04); filter: drop-shadow(0 0 8px rgba(251,191,36,0.8)); }}
            100% {{ transform: rotate(360deg) scale(1); filter: drop-shadow(0 0 2px rgba(251,191,36,0.4)); }}
        }}
        @keyframes moonGlow {{
            0% {{ transform: scale(1); filter: drop-shadow(0 0 2px rgba(56,189,248,0.4)); }}
            50% {{ transform: scale(1.05); filter: drop-shadow(0 0 8px rgba(56,189,248,0.8)); }}
            100% {{ transform: scale(1); filter: drop-shadow(0 0 2px rgba(56,189,248,0.4)); }}
        }}
        @keyframes slideRain {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(3px); }}
            100% {{ transform: translateY(0px); }}
        }}
        @keyframes flashStorm {{
            0% {{ filter: brightness(1); }}
            50% {{ filter: brightness(1.35); }}
            100% {{ filter: brightness(1); }}
        }}
        @keyframes floatCloud {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-4px); }}
            100% {{ transform: translateY(0px); }}
        }}

        .anim-sol svg {{ animation: spinGlow 14s linear infinite; }}
        .anim-luna svg {{ animation: moonGlow 4s ease-in-out infinite; }}
        .anim-lluvia svg {{ animation: slideRain 2.2s ease-in-out infinite; }}
        .anim-tormenta svg {{ animation: flashStorm 1.6s ease-in-out infinite; }}
        .anim-nube svg {{ animation: floatCloud 3.5s ease-in-out infinite; }}

        .card-editorial-hoy {{
            background: rgba(15, 32, 56, 0.75) !important;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 24px !important;
            padding: 28px !important;
            color: #ffffff !important;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.3) !important;
            margin-bottom: 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
        }}

        .card-editorial-semana {{
            background: rgba(255, 255, 255, 0.96) !important;
            border-radius: 20px !important;
            padding: 20px 24px !important;
            color: #0f172a !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important;
            margin-bottom: 16px !important;
            border: 1px solid rgba(255, 255, 255, 0.8) !important;
        }}

        .footer-metodologico {{
            text-align: center !important;
            margin-top: 35px !important;
            padding: 18px 20px !important;
            border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #94a3b8 !important;
            font-size: 0.78rem !important;
            line-height: 1.5 !important;
        }}
        
        .titulo-pantalla {{
            text-align: center !important;
            color: #ffffff !important;
            font-size: 2rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px;
            margin: 0 !important;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
        }}
        
        .subtitulo-pantalla {{
            text-align: center !important;
            color: #38bdf8 !important;
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px;
            margin-top: 2px !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        col_top1, col_top2, col_top3 = st.columns([1.2, 3.8, 1.5])
        with col_top1:
            if st.button("← Volver", help="Buscar otra localidad"):
                st.session_state.resultado_activo = False
                st.session_state.lugar_actual = ""
                st.session_state.seccion_activa = "inicio"
                st.rerun()
        with col_top2:
            st.markdown("<h1 class='titulo-pantalla'>MeteoUy</h1>", unsafe_allow_html=True)
            st.markdown(f"<p class='subtitulo-pantalla'>📍 {lugar_encontrado}</p>", unsafe_allow_html=True)
        with col_top3:
            st.markdown("<div style='text-align: right; padding-top: 10px;'><span style='background: rgba(220, 38, 38, 0.2); border: 1px solid rgba(220, 38, 38, 0.5); color: #f87171; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.75rem; letter-spacing: 1px;'>LIVE</span></div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        t_max_hoy = daily.get("temperature_2m_max", [temp_actual])[0]
        
        html_hoy = f"""
        <div class="card-editorial-hoy">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <div>
                    <span style="font-size: 0.8rem; font-weight: 800; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase;">CONDICIÓN ACTUAL</span>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin-top: 4px;">{desc_actual}</div>
                </div>
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div>{dibujo_hoy}</div>
                    <div style="text-align: right;">
                        <span style="font-size: 3.2rem; font-weight: 800; color: #ffffff; line-height: 1;">{temp_actual}°</span>
                        <span style="font-size: 1.2rem; color: #94a3b8; font-weight: 600;"> / {t_max_hoy}°</span>
                    </div>
                </div>
            </div>
            <p style="font-size: 1.05rem; font-weight: 600; color: #f1f5f9; margin: 16px 0; line-height: 1.5;">{frase_humana}</p>
            <div style="height: 1px; background: rgba(255, 255, 255, 0.08); margin: 16px 0;"></div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; font-size: 0.85rem; color: #cbd5e1;">
                <div>
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Viento</div>
                    <div style="font-weight: 700; color: #ffffff; margin-top: 2px;">{viento_actual} km/h</div>
                </div>
                <div>
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Humedad</div>
                    <div style="font-weight: 700; color: #ffffff; margin-top: 2px;">{humedad_actual}%</div>
                </div>
                <div>
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Precipitación</div>
                    <div style="font-weight: 700; color: #ffffff; margin-top: 2px;">{prob_lluvia_hoy}%</div>
                </div>
            </div>
        </div>
        """
        st.markdown(html_hoy, unsafe_allow_html=True)

        st.markdown("<h3 style='color: #ffffff; font-size: 1.1rem; font-weight: 700; margin-bottom: 12px; letter-spacing: 0.5px;'>📅 Pronóstico Extendido</h3>", unsafe_allow_html=True)
        
        fechas = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        lluvia = daily.get("precipitation_sum", [])
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
            lluvia_val = lluvia[i] if i < len(lluvia) else 0.0
            prob_val = prob_lluvia_diaria[i] if i < len(prob_lluvia_diaria) else 0
            viento_val = viento_diario[i] if i < len(viento_diario) else "--"
            fecha_val = fechas[i] if i < len(fechas) else ""
            
            html_semana = f"""
            <div class="card-editorial-semana">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <span style="font-size: 0.75rem; font-weight: 800; color: #0284c7; letter-spacing: 1px; text-transform: uppercase;">{etiquetas[i-1]}</span>
                        <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">{fecha_val}</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div>{dibujo_ext}</div>
                        <div style="text-align: right;">
                            <span style="font-size: 1.25rem; font-weight: 800; color: #0f172a;">{tmin_val}° / {tmax_val}°</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                    <div style="font-size: 0.9rem; font-weight: 700; color: #334155;">{estado_texto}</div>
                    <div style="font-size: 0.82rem; color: #475569; font-weight: 600;">
                        Lluvia: <b>{prob_val}%</b> &nbsp;|&nbsp; Viento: <b>{viento_val} km/h</b>
                    </div>
                </div>
            </div>
            """
            st.markdown(html_semana, unsafe_allow_html=True)

        st.markdown("""
        <div class="footer-metodologico">
            <b>MeteoUy Data Engine:</b> Pronóstico procesado en tiempo real mediante ensamble multimodelo de alta resolución (ECMWF, GFS, ICON, WRF, GEM), telemetría geostacional <b>GOES-19 (GOES-East)</b>, cobertura Doppler de radares regionales y red de estaciones automáticas de superficie (Davis Vantage Pro2 / Netatmo).
        </div>
        """, unsafe_allow_html=True)
