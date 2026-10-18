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
        0: "Cielo Despejado",
        1: "Poco Nuboso",
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
        return "Algo nuboso con períodos de claro. Condiciones estables y agradables."
    return "Cielo variable sin precipitaciones significativas previstas."

# SISTEMA DE ETIQUETAS ESTÉTICAS (BADGES EDITORIALES SIN DIBUJOS)
def obtener_badge_clima(texto_clima):
    t = texto_clima.lower()
    if "despejado" in t or "sol" in t:
        return "<span style='background: rgba(251, 191, 36, 0.15); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.4); padding: 5px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.5px;'>☀️ Despejado</span>"
    elif "lluvia" in t or "llovizna" in t or "chubascos" in t or "garúa" in t:
        return "<span style='background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 5px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.5px;'>🌧️ Precipitaciones</span>"
    elif "tormenta" in t:
        return "<span style='background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); padding: 5px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.5px;'>⚡ Alerta Tormenta</span>"
    elif "nuboso" in t or "nublado" in t or "cubierto" in t:
        return "<span style='background: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.4); padding: 5px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.5px;'>☁️ Nubosidad</span>"
    else:
        return f"<span style='background: rgba(255, 255, 255, 0.1); color: #ffffff; border: 1px solid rgba(255, 255, 255, 0.2); padding: 5px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.5px;'>{texto_clima}</span>"

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
# PANTALLA 2: RESULTADOS (DISEÑO EDITORIAL & UX PREMIUM)
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

        frase_humana = generar_titular_pronostico_horas(wcode_actual, lluvia_diaria_hoy, prob_lluvia_hoy, viento_actual, uv_actual)
        desc_actual = obtener_descripcion_clima(wcode_actual)
        badge_hoy = obtener_badge_clima(desc_actual)

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

        /* TARJETA EDITORIAL HOY */
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
            transition: transform 0.3s ease;
        }}
        .card-editorial-hoy:hover {{
            border-color: rgba(56, 189, 248, 0.4) !important;
        }}

        /* TARJETA EDITORIAL EXTENDIDO */
        .card-editorial-semana {{
            background: rgba(255, 255, 255, 0.96) !important;
            border-radius: 20px !important;
            padding: 20px 24px !important;
            color: #0f172a !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important;
            margin-bottom: 16px !important;
            border: 1px solid rgba(255, 255, 255, 0.8) !important;
        }}

        .fuentes-card {{
            background: rgba(10, 25, 47, 0.85) !important;
            backdrop-filter: blur(10px);
            border-radius: 16px !important;
            padding: 18px 22px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            margin-top: 25px !important;
            font-size: 0.85rem !important;
            color: #cbd5e1 !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.25) !important;
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
                st.rerun()
        with col_top2:
            st.markdown(f"<h1 class='titulo-pantalla'>MeteoUy</h1>", unsafe_allow_html=True)
            st.markdown(f"<p class='subtitulo-pantalla'>📍 {lugar_encontrado}</p>", unsafe_allow_html=True)
        with col_top3:
            st.markdown("<div style='text-align: right; padding-top: 10px;'><span style='background: rgba(220, 38, 38, 0.2); border: 1px solid rgba(220, 38, 38, 0.5); color: #f87171; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.75rem; letter-spacing: 1px;'>LIVE</span></div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # -----------------------------------------------------
        # TARJETA 1: HOY (ESTILO EDITORIAL MINIMALISTA)
        # -----------------------------------------------------
        t_max_hoy = daily.get("temperature_2m_max", [temp_actual])[0]
        t_min_hoy = daily.get("temperature_2m_min", [temp_actual])[0]
        
        st.markdown(f"""
        <div class="card-editorial-hoy">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px;">
                <div>
                    <span style="font-size: 0.8rem; font-weight: 800; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase;">CONDICIÓN ACTUAL</span>
                    <div style="margin-top: 6px;">{badge_hoy}</div>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 3.2rem; font-weight: 800; color: #ffffff; line-height: 1;">{temp_actual}°</span>
                    <span style="font-size: 1.2rem; color: #94a3b8; font-weight: 600;"> / {t_max_hoy}°</span>
                </div>
            </div>
            
            <p style="font-size: 1.05rem; font-weight: 600; color: #f1f5f9; margin: 16px 0 16px 0; line-height: 1.5;">
                {frase_humana}
            </p>
            
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
        """, unsafe_allow_html=True)

        # -----------------------------------------------------
        # TARJETA 2: PRONÓSTICO EXTENDIDO
        # -----------------------------------------------------
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
            estado_texto = obtener_descripcion_clima(codigo_clima)
            badge_ext = obtener_badge_clima(estado_texto)
            
            tmax_val = t_max[i] if i < len(t_max) else "--"
            tmin_val = t_min[i] if i < len(t_min) else "--"
            lluvia_val = lluvia[i] if i < len(lluvia) else 0.0
            prob_val = prob_lluvia_diaria[i] if i < len(prob_lluvia_diaria) else 0
            viento_val = viento_diario[i] if i < len(viento_diario) else "--"
            fecha_val = fechas[i] if i < len(fechas) else ""
            
            st.markdown(f"""
            <div class="card-editorial-semana">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <span style="font-size: 0.75rem; font-weight: 800; color: #0284c7; letter-spacing: 1px; text-transform: uppercase;">{etiquetas[i-1]}</span>
                        <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">{fecha_val}</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.25rem; font-weight: 800; color: #0f172a;">{tmin_val}° / {tmax_val}°</span>
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                    <div>{badge_ext}</div>
                    <div style="font-size: 0.82rem; color: #475569; font-weight: 600;">
                        Lluvia: <b>{prob_val}%</b> &nbsp;|&nbsp; Viento: <b>{viento_val} km/h</b>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # CARTA METODOLÓGICA PROFESIONAL
        st.markdown("""
        <div class="fuentes-card">
            <p style="margin: 0 0 6px 0; font-weight: 700; color: #38bdf8; font-size: 0.85rem; letter-spacing: 0.5px;">
                🛡️ Consolidador Metodológico y Fuentes Integradas
            </p>
            <p style="margin: 0; line-height: 1.5; color: #cbd5e1; font-size: 0.8rem;">
                Pronóstico procesado mediante ensamble dinámico de modelos numéricos globales de alta resolución 
                <b>(ECMWF / IFS, GFS, ICON, WRF)</b>, telemetría satelital <b>GOES-16 (NOAA)</b>, monitoreo de alertas 
                oficiales de <b>INUMET / MetSul</b>, y validación de superficie con la red de estaciones meteorológicas automáticas <b>(Davis / Wunderground)</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)
