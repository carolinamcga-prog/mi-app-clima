import streamlit as st
import requests
import os
import random
import urllib.parse
from data.localidades import LOCALIDADES_URUGUAY

# Intentar importar plotly para el gráfico de 24hs
try:
    import plotly.graph_objects as go
    PLOTLY_DISPONIBLE = True
except ImportError:
    PLOTLY_DISPONIBLE = False

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
    "tranqueras": (-31.2056, -55.7394),
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

def mostrar_logo_limpio():
    st.markdown("<h1 style='text-align: center; color: #0284c7; font-size: 3.5rem; font-weight: 800; margin: 0; padding: 0;'>MeteoUy</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #0369a1; font-size: 1rem; font-weight: 700; letter-spacing: 2px; margin-top: 0;'>PRONÓSTICO PROFESIONAL URUGUAY</p>", unsafe_allow_html=True)


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

    /* FONDO CELESTE CLARO PROFESIONAL */
    .stApp {
        background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 50%, #e0f2fe 100%) !important;
        position: relative !important;
        overflow-x: hidden !important;
    }

    /* NUBES FLOTANTES ANIMADAS DE FONDO */
    .cloud-anim-1, .cloud-anim-2 {
        position: fixed;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 100px;
        pointer-events: none;
        z-index: 0;
        filter: blur(1px);
    }

    .cloud-anim-1 {
        width: 180px;
        height: 60px;
        top: 15%;
        left: -200px;
        animation: floatCloud1 35s linear infinite;
    }
    .cloud-anim-1::before, .cloud-anim-1::after {
        content: '';
        position: absolute;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 50%;
    }
    .cloud-anim-1::before { width: 70px; height: 70px; top: -35px; left: 25px; }
    .cloud-anim-1::after { width: 90px; height: 90px; top: -50px; left: 75px; }

    .cloud-anim-2 {
        width: 240px;
        height: 80px;
        top: 65%;
        left: -300px;
        animation: floatCloud2 50s linear infinite;
        animation-delay: 8s;
    }
    .cloud-anim-2::before, .cloud-anim-2::after {
        content: '';
        position: absolute;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 50%;
    }
    .cloud-anim-2::before { width: 90px; height: 90px; top: -45px; left: 40px; }
    .cloud-anim-2::after { width: 110px; height: 110px; top: -60px; left: 100px; }

    @keyframes floatCloud1 {
        0% { transform: translateX(0vw); }
        100% { transform: translateX(120vw); }
    }
    @keyframes floatCloud2 {
        0% { transform: translateX(0vw); }
        100% { transform: translateX(130vw); }
    }

    /* Asegurar contenido por encima de las nubes */
    .block-container {
        position: relative !important;
        z-index: 10 !important;
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.4); border-color: #38bdf8; }
        50% { box-shadow: 0 0 22px rgba(14, 165, 233, 0.8); border-color: #0284c7; }
        100% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.4); border-color: #38bdf8; }
    }

    div[data-testid="stTextInput"] input {
        border-radius: 45px !important;
        border: 2.5px solid #38bdf8 !important;
        animation: pulseGlow 2.5s infinite ease-in-out !important;
        background-color: rgba(255, 255, 255, 0.95) !important;
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
        background: rgba(255, 255, 255, 0.9) !important;
        color: #0369a1 !important;
        border: 1.5px solid #bae6fd !important;
        border-radius: 20px !important;
        height: 2.5rem !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }

    div[data-testid="stColumn"] .stButton > button {
        background: rgba(255, 255, 255, 0.95) !important;
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

    .card-pro {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 24px;
        padding: 32px;
        color: #ffffff;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.25);
        border: 1.5px solid rgba(56, 189, 248, 0.3);
        margin-bottom: 20px;
    }
    </style>
    
    <!-- ELEMENTOS HTML DE LAS NUBES FLOTANTES -->
    <div class="cloud-anim-1"></div>
    <div class="cloud-anim-2"></div>
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
    mostrar_logo_limpio()

    frase_hoy = obtener_frase_dinamica_clima()
    st.markdown(f"<p style='text-align: center; font-style: italic; color: #0369a1; font-size: 0.95rem; font-weight: 600; margin: 10px 0 20px 0;'>{frase_hoy}</p>", unsafe_allow_html=True)

    if st.session_state.seccion_activa == "meteo_uy":
        st.subheader("¿Qué es MeteoUy?")
        st.write("**MeteoUy** es la plataforma privada de monitoreo meteorológico de alta resolución en Uruguay. Unificamos telemetría satelital, cobertura de radares regionales y estaciones automáticas de superficie para ofrecer pronósticos en tiempo real con máxima exactitud en más de 600 localidades del país.")
        
        st.write("Más allá de un simple pronóstico, en MeteoUy creamos un servicio meteorológico integral diseñado para transformar los datos atmosféricos en información práctica y de alto valor, ayudándote a decidir con certeza qué hacer en cada momento y situación.")
        
        st.subheader("Tecnología y Fuentes de Datos")
        st.write("Para garantizar la máxima confiabilidad técnica, nuestro motor procesa e integra en tiempo real:")
        st.markdown("- **Modelos Numéricos Globales y Regionales:** ECMWF, GFS, ICON y WRF.")
        st.markdown("- **Telemetría Satelital:** Imágenes de alta frecuencia en bandas visibles e infrarrojas del satélite **GOES-19 (GOES-East)**.")
        st.markdown("- **Radares & Estaciones de Superficie:** Cobertura Doppler regional integrada con redes de estaciones automáticas (Davis Vantage Pro2, Netatmo y sensores IoT).")
        st.markdown("<br>", unsafe_allow_html=True)

    elif st.session_state.seccion_activa == "servicios":
        st.subheader("Asesoramiento Meteorológico para Empresas y Profesionales")
        st.write("Ofrecemos pronósticos dedicados y análisis de riesgo climático a medida para diversos sectores productivos de Uruguay:")
        st.markdown("- **Agro & Ganadería:** Modelado de precipitaciones por parcela, heladas y balance hídrico.")
        st.markdown("- **Construcción & Obras:** Alertas tempranas de viento y lluvias para seguridad operativa.")
        st.markdown("- **Logística & Transporte:** Monitoreo de rutas, puertos y condiciones adversas.")
        st.markdown("- **Eventos al Aire Libre:** Cobertura meteorológica en tiempo real.")

        st.subheader("Solicitud de Asesoramiento / Cotización")
        
        with st.form(key="form_servicios_profesionales"):
            nombre_empresa = st.text_input("Nombre / Empresa *", placeholder="Ej: AgroSur S.A. / Juan Pérez")
            email_contacto = st.text_input("Correo Electrónico de Contacto *", placeholder="ejemplo@empresa.com.uy")
            telefono_whatsapp = st.text_input("Teléfono / WhatsApp *", placeholder="099 123 456")
            sector_rubro = st.text_input("Rubro o Sector", placeholder="Ej: Agro, Construcción, Eventos, Logística...")
            mensaje_detalle = st.text_area("Detalle de la necesidad o consulta *", placeholder="Describinos en qué consiste tu consulta...")
            
            submit_button = st.form_submit_button(label="ENVIAR SOLICITUD A METEO UY", use_container_width=True)
            
            if submit_button:
                if nombre_empresa and email_contacto and mensaje_detalle:
                    st.success("✅ ¡Gracias por comunicarte! Hemos recibido tu solicitud. Nos contactaremos a la brevedad.")
                else:
                    st.error("⚠️ Por favor completa los campos obligatorios (*) para procesar tu consulta.")

        st.markdown("<br>", unsafe_allow_html=True)

    elif st.session_state.seccion_activa == "pro":
        st.markdown("""
        <div class="card-pro">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 0.8rem; letter-spacing: 1px;">PLAN EMPRESARIAL</span>
                <span style="font-size: 2.2rem; font-weight: 800; color: #ffffff;">$100 <span style="font-size: 0.9rem; color: #94a3b8; font-weight: 500;">USD / mes</span></span>
            </div>
            <h2 style="color: #ffffff; font-size: 1.6rem; font-weight: 800; margin-bottom: 10px;">MeteoUy Pro</h2>
            <p style="color: #cbd5e1; font-size: 1rem; line-height: 1.5; margin-bottom: 20px;">
                Diseñado específicamente para empresas agropecuarias, constructoras, operadores logísticos y profesionales que exigen la máxima precisión meteorológica en tiempo real en Uruguay.
            </p>
            <div style="height: 1px; background: rgba(255, 255, 255, 0.15); margin: 20px 0;"></div>
            <div style="display: grid; gap: 12px; font-size: 0.95rem; color: #e2e8f0; margin-bottom: 25px;">
                <div>✅ <b>Alertas Tempranas Prioritarias:</b> Notificaciones directas por WhatsApp ante eventos severos (vientos fuertes, granizo, heladas).</div>
                <div>✅ <b>Modelos de Alta Resolución Ampliados:</b> Acceso a proyecciones horarias extendidas a 14 días.</div>
                <div>✅ <b>Telemetría Satelital & Radar:</b> Datos crudos y capas de radar Doppler en alta definición.</div>
                <div>✅ <b>Soporte Técnico Dedicado:</b> Consultoría meteorológica directa con especialistas.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("SUSCRIBIRME A METEO UY PRO ($100 USD/MES)", use_container_width=True):
            st.info("🔗 **Próximo paso:** Aquí se integrará el botón de pago automático de Mercado Pago o pasarela de tarjetas para gestionar la suscripción mensual de forma segura.")

        st.markdown("<br>", unsafe_allow_html=True)

    def procesar_busqueda():
        val = st.session_state.input_localidad_texto.strip()
        if val:
            st.session_state.lugar_actual = val
            st.session_state.resultado_activo = True

    localidad_ingresada = st.text_input(
        label="Buscador",
        placeholder="Escribí una localidad o departamento de Uruguay...",
        key="input_localidad_texto",
        on_change=procesar_busqueda,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    if st.button("VER PRONÓSTICO", use_container_width=True):
        if localidad_ingresada and localidad_ingresada
