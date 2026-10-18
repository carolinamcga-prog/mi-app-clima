import streamlit as st
import requests
import os
import urllib.parse

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

def generar_titular_pronostico_horas(wcode, lluvia_hoy, prob_lluvia, viento, uv_actual):
    if wcode in [95, 96, 99]:
        return "⛈️", "Alerta por tormentas eléctricas. Evitá permanecer en espacios abiertos y resguardá vehículos."
    if lluvia_hoy > 1.5 or prob_lluvia > 60 or wcode in range(51, 68) or wcode in range(80, 100):
        return "🌧️", f"Inestabilidad alta ({prob_lluvia}% prob. de lluvia). Llevá paraguas o piloto si salís."
    if viento > 28:
        return "🌬️", "Viento fuerte en la zona. Precaución al conducir en rutas y objetos sueltos en balcones."
    if uv_actual and uv_actual >= 8.0:
        return "☀️", f"Radiación UV en nivel {uv_actual:.1f} (Muy Alto). Usá protector solar SPF 50+ y lentes de sol."
    if wcode in [0, 1]:
        return "🌤️", "Algo nuboso con períodos de claro. Condiciones estables y agradables."
    return "⛅", "Cielo variable sin precipitaciones significativas previstas."

# ---------------------------------------------------------
# GENERADOR DE ILUSTRACIONES SVG (GRANDES Y DELICADAS)
# ---------------------------------------------------------
def obtener_svg_clima(icono_texto):
    if "☀️" in icono_texto or "🌤️" in icono_texto:
        # Sol radiante y elegante con animación de brillo rotativo suave
        return """
        <div class="svg-sol-animado" style="display:inline-block; width: 68px; height: 68px;">
            <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
                <circle cx="32" cy="32" r="14" fill="#FBBF24" opacity="0.9"/>
                <path d="M32 8V4M32 60V56M56 32H60M4 32H8M49 15L52 12M12 52L15 49M49 49L52 52M12 12L15 15" stroke="#FBBF24" stroke-width="3" stroke-linecap="round"/>
            </svg>
        </div>
        """
    elif "🌧️" in icono_texto or "🌦️" in icono_texto:
        # Nube con lluvia fluida
        return """
        <div class="svg-lluvia-animado" style="display:inline-block; width: 68px; height: 68px;">
            <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
                <path d="M46 28H44.7C43.3 21.6 37.6 17 31 17C24.1 17 18.5 22.4 18.1 29.3C13.6 30.1 10 34 10 38.8C10 44 14.2 48.2 19.4 48.2H46C51 48.2 55 44.2 55 39.2C55 34.2 51 30.2 46 28Z" fill="#E2E8F0"/>
                <path d="M24 54L22 60M32 54L30 60M40 54L38 60" stroke="#38BDF8" stroke-width="3" stroke-linecap="round"/>
            </svg>
        </div>
        """
    elif "🌬️" in icono_texto or "💨" in icono_texto:
        # Ráfagas de viento elegantes
        return """
        <div class="svg-viento-animado" style="display:inline-block; width: 68px; height: 68px;">
            <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
                <path d="M14 24H44C47.3 24 50 21.3 50 18C50 14.7 47.3 12 44 12C41.8 12 39.9 13.2 38.9 15" stroke="#94A3B8" stroke-width="3" stroke-linecap="round"/>
                <path d="M10 38H34C37.3 38 40 35.3 40 32C40 28.7 37.3 26 34 26C32.9 26 31.8 26.3 31 26.8" stroke="#38BDF8" stroke-width="3" stroke-linecap="round"/>
                <path d="M18 52H28C30.2 52 32 50.2 32 48C32 45.8 30.2 44 28 44" stroke="#94A3B8" stroke-width="3" stroke-linecap="round"/>
            </svg>
        </div>
        """
    elif "⛈️" in icono_texto or "🌩️" in icono_texto or "⚡" in icono_texto:
        # Tormenta con rayo eléctrico
        return """
        <div class="svg-tormenta-animado" style="display:inline-block; width: 68px; height: 68px;">
            <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
                <path d="M46 24H44.7C43.3 17.6 37.6 13 31 13C24.1 13 18.5 18.4 18.1 25.3C13.6 26.1 10 30 10 34.8C10 40 14.2 44.2 19.4 44.2H46C51 44.2 55 40.2 55 35.2C55 30.2 51 26.2 46 24Z" fill="#64748B"/>
                <path d="M34 44L24 54H34L30 62L42 49H34L34 44Z" fill="#FBBF24"/>
            </svg>
        </div>
        """
    else:
        # Nube nublada / parcial flotando suave
        return """
        <div class="svg-nube-animado" style="display:inline-block; width: 68px; height: 68px;">
            <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:100%; height:100%;">
                <path d="M46 28H44.7C43.3 21.6 37.6 17 31 17C24.1 17 18.5 22.4 18.1 29.3C13.6 30.1 10 34 10 38.8C10 44 14.2 48.2 19.4 48.2H46C51 48.2 55 44.2 55 39.2C55 34.2 51 30.2 46 28Z" fill="#CBD5E1"/>
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
        st.markdown("<h1 style='text-align: center; color: #0284c7; font-size: 3.5rem; font-weight: 800; font-family: \"Plus Jakarta Sans\", sans-serif;'>MeteoUy</h1>", unsafe_allow_html=True)

# =========================================================
# PANTALLA 1: INICIO (PANTALLA ORIGINAL Y LIMPIA EN BLANCO)
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
            placeholder="🔍 Escribe una localidad o departamento (Presiona Enter o haz clic)...",
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
# PANTALLA 2: RESULTADOS (ESTILO TARJETAS INUMET)
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
        st.info("No encontramos la localidad ingresada dentro de Uruguay. Por favor, asegúrate de escribir una ciudad, pueblo, departamento o barrio uruguayo.")
        if st.button("🌧️↩️ Volver al buscador", help="Hacé clic para volver"):
            st.session_state.resultado_activo = False
            st.session_state.lugar_actual = ""
            st.rerun()
    else:
        url_meteo = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,surface_pressure,weathercode,wind_speed_10m,visibility,uv_index&hourly=temperature_2m,precipitation_probability,weathercode&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,windspeed_10m_max,uv_index_max&forecast_days=3&models=best_match&timezone=auto"
        
        try:
            data = requests.get(url_meteo, timeout=10).json()
        except Exception:
            data = {}
            
        current = data.get("current", {})
        daily = data.get("daily", {})
        hourly = data.get("hourly", {})
        
        temp_actual = current.get("temperature_2m", 0)
        humedad_actual = current.get("relative_humidity_2m", 0)
        sensacion_actual = current.get("apparent_temperature", 0)
        presion_actual = current.get("surface_pressure", 1013)
        viento_actual = current.get("wind_speed_10m", 0)
        wcode_actual = current.get("weathercode", 0)
        uv_actual = current.get("uv_index", 0.0)
        
        visibilidad_m = current.get("visibility", 10000)
        visibilidad_km = round(visibilidad_m / 1000, 1) if visibilidad_m is not None else 10.0
        
        prob_lluvia_hoy = 0
        if daily.get("precipitation_probability_max") and len(daily["precipitation_probability_max"]) > 0:
            prob_lluvia_hoy = daily["precipitation_probability_max"][0] or 0

        lluvia_diaria_hoy = 0.0
        if daily.get("precipitation_sum") and len(daily["precipitation_sum"]) > 0:
            lluvia_diaria_hoy = daily["precipitation_sum"][0] or 0.0

        icono_humano, frase_humana = generar_titular_pronostico_horas(wcode_actual, lluvia_diaria_hoy, prob_lluvia_hoy, viento_actual, uv_actual)

        st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        .stApp, html, body, [class*="st-"] {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }}

        .stApp {{
            background: linear-gradient(180deg, #1d517c 0%, #3a75a4 40%, #0d2b45 100%) !important;
            background-attachment: fixed !important;
        }}

        .block-container {{
            position: relative !important;
            z-index: 10 !important;
        }}

        /* ---------------------------------------------------------
           ANIMACIONES FLUIDAS, DELICADAS Y SIN EFECTO SALTÓN
        --------------------------------------------------------- */
        
        /* Brillo y rotación suave para el sol */
        @keyframes sunGlow {{
            0% {{ transform: rotate(0deg) scale(1); filter: drop-shadow(0 0 2px rgba(251,191,36,0.4)); }}
            50% {{ transform: rotate(180deg) scale(1.04); filter: drop-shadow(0 0 8px rgba(251,191,36,0.8)); }}
            100% {{ transform: rotate(360deg) scale(1); filter: drop-shadow(0 0 2px rgba(251,191,36,0.4)); }}
        }}

        /* Desplazamiento sutil de gotas de lluvia */
        @keyframes rainSlide {{
            0% {{ transform: translateY(0px); opacity: 0.8; }}
            50% {{ transform: translateY(3px); opacity: 1; }}
            100% {{ transform: translateY(0px); opacity: 0.8; }}
        }}

        /* Balanceo suave horizontal para el viento */
        @keyframes windSway {{
            0% {{ transform: translateX(0px); }}
            50% {{ transform: translateX(4px); }}
            100% {{ transform: translateX(0px); }}
        }}

        /* Parpadeo delicado para tormentas */
        @keyframes stormFlash {{
            0% {{ opacity: 1; filter: brightness(1); }}
            50% {{ opacity: 0.85; filter: brightness(1.3); }}
            100% {{ opacity: 1; filter: brightness(1); }}
        }}

        /* Flotación muy leve para nubes */
        @keyframes cloudFloat {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-3px); }}
            100% {{ transform: translateY(0px); }}
        }}

        .svg-sol-animado svg {{ animation: sunGlow 12s linear infinite; }}
        .svg-lluvia-animado svg {{ animation: rainSlide 2s ease-in-out infinite; }}
        .svg-viento-animado svg {{ animation: windSway 3s ease-in-out infinite; }}
        .svg-tormenta-animado svg {{ animation: stormFlash 1.8s ease-in-out infinite; }}
        .svg-nube-animado svg {{ animation: cloudFloat 4s ease-in-out infinite; }}

        /* TARJETA HOY - ESTILO INUMET AZUL OSCURO */
        .card-inumet-hoy {{
            background: #0f2744 !important;
            border-radius: 20px !important;
            padding: 24px !important;
            color: #ffffff !important;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25) !important;
            margin-bottom: 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}

        /* TARJETA MAÑANA - ESTILO INUMET BLANCA */
        .card-inumet-semana {{
            background: #ffffff !important;
            border-radius: 20px !important;
            padding: 20px !important;
            color: #0f172a !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.18) !important;
            margin-bottom: 20px !important;
        }}

        .fuentes-card {{
            background: rgba(15, 39, 68, 0.85) !important;
            border-radius: 16px !important;
            padding: 16px 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            margin-top: 25px !important;
            font-size: 0.85rem !important;
            color: #e2e8f0 !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        }}
        
        .titulo-pantalla {{
            text-align: center !important;
            color: #ffffff !important;
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            margin: 0 !important;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
        }}
        
        .subtitulo-pantalla {{
            text-align: center !important;
            color: #fbbf24 !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            margin-top: -5px !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        col_top1, col_top2, col_top3 = st.columns([1.2, 3.8, 1.5])
        with col_top1:
            if st.button("🌧️↩️ Volver", help="Buscar otra localidad"):
                st.session_state.resultado_activo = False
                st.session_state.lugar_actual = ""
                st.rerun()
        with col_top2:
            st.markdown(f"<h1 class='titulo-pantalla'>Tiempo según MeteoUy</h1>", unsafe_allow_html=True)
            st.markdown(f"<p class='subtitulo-pantalla'>📍 {lugar_encontrado}</p>", unsafe_allow_html=True)
        with col_top3:
            st.markdown("<div style='text-align: right; padding-top: 10px;'><span style='background: #dc2626; color: white; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.8rem;'>EN VIVO</span></div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # -----------------------------------------------------
        # TARJETA 1: HOY (PLACA AZUL OSCURA ESTILO INUMET)
        # -----------------------------------------------------
        t_max_hoy = daily.get("temperature_2m_max", [temp_actual])[0]
        t_min_hoy = daily.get("temperature_2m_min", [temp_actual])[0]
        
        svg_hoy_html = obtener_svg_clima(icono_humano)

        st.markdown(f"""
        <div class="card-inumet-hoy">
            <div style="font-size: 0.9rem; font-weight: 800; color: #38bdf8; letter-spacing: 1px; margin-bottom: 8px;">
                HOY:
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <span style="font-size: 2.8rem; font-weight: 800; color: #ffffff;">{temp_actual}°C</span>
                    <span style="font-size: 1.5rem; color: #94a3b8; font-weight: 600;"> / {t_max_hoy}°C</span>
                </div>
                <div>{svg_hoy_html}</div>
            </div>
            <hr style="border-color: rgba(255,255,255,0.15); margin: 12px 0;">
            <p style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin-bottom: 10px; line-height: 1.4;">
                {frase_humana}
            </p>
            <div style="font-size: 0.88rem; color: #cbd5e1; line-height: 1.6;">
                <div>💨 <b>Viento:</b> {viento_actual} km/h</div>
                <div>💧 <b>Humedad:</b> {humedad_actual}% &nbsp;|&nbsp; 📊 <b>Presión:</b> {presion_actual} hPa</div>
                <div>🌧️ <b>Probabilidad de lluvia:</b> {prob_lluvia_hoy}% ({lluvia_diaria_hoy} mm)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # -----------------------------------------------------
        # TARJETA 2: EXTENDIDO (PLACAS BLANCAS)
        # -----------------------------------------------------
        st.markdown("<h3 style='color: #ffffff; font-size: 1.2rem; margin-bottom: 12px;'>📅 Pronóstico Extendido</h3>", unsafe_allow_html=True)
        
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
            estado_texto = obtener_descripcion_clima(codigo_clima)
            
            tmax_val = t_max[i] if i < len(t_max) else "--"
            tmin_val = t_min[i] if i < len(t_min) else "--"
            lluvia_val = lluvia[i] if i < len(lluvia) else 0.0
            prob_val = prob_lluvia_diaria[i] if i < len(prob_lluvia_diaria) else 0
            viento_val = viento_diario[i] if i < len(viento_diario) else "--"
            fecha_val = fechas[i] if i < len(fechas) else ""
            
            svg_ext_html = obtener_svg_clima(estado_texto)
            
            st.markdown(f"""
            <div class="card-inumet-semana">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <div>
                        <span style="font-size: 0.9rem; font-weight: 800; color: #0284c7;">{etiquetas[i-1]} ({fecha_val})</span>
                        <p style="font-size: 0.95rem; font-weight: 700; color: #334155; margin: 4px 0 0 0;">{estado_texto}</p>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 1.25rem; font-weight: 800; color: #0f172a;">{tmin_val}°C / {tmax_val}°C</span>
                        <div style="transform: scale(0.65);
