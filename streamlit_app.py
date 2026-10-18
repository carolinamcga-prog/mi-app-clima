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
    """Verifica si las coordenadas pertenecen estrictamente al mapa de Uruguay"""
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

def obtener_categoria_uv(uv):
    if uv is None:
        return "Bajo", "#16a34a"
    if uv < 3:
        return f"{uv:.1f} (Bajo)", "#16a34a"
    elif uv < 6:
        return f"{uv:.1f} (Moderado)", "#ca8a04"
    elif uv < 8:
        return f"{uv:.1f} (Alto)", "#ea580c"
    elif uv < 11:
        return f"{uv:.1f} (Muy Alto)", "#dc2626"
    else:
        return f"{uv:.1f} (Extremo)", "#7c3aed"

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
        return "🌤️", "Condiciones muy estables y agradables. Excelente jornada para actividades al aire libre."
    return "⛅", "Cielo variable sin precipitaciones significativas previstas para las próximas horas."

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
# PANTALLA 1: INICIO (BUSCADOR LIMPIO Y RÁPIDO)
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
            placeholder="🔍 Escribe un barrio, localidad o departamento de Uruguay...",
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
# PANTALLA 2: RESULTADOS Y DATOS PROFESIONALES ENRIQUECIDOS
# =========================================================
else:
    lugar_ingresado = st.session_state.lugar_actual.strip()
    lugar_lower = lugar_ingresado.lower()
    
    lat, lon = None, None
    lugar_encontrado = lugar_ingresado.title()
    
    # 1. Búsqueda directa en base interna uruguaya
    for clave, coords in COORDS_URUGUAY.items():
        if clave in lugar_lower or lugar_lower in clave:
            lat, lon = coords
            lugar_encontrado = clave.title()
            break
            
    # 2. Respaldo vía Geocoding estricto
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
        .stApp { background-color: #f0f9ff !important; }
        </style>
        """, unsafe_allow_html=True)
        st.warning("⚠️ **MeteoUy es un servicio exclusivo para el territorio de Uruguay.**")
        st.info("No encontramos la localidad ingresada dentro de Uruguay. Por favor, asegúrate de escribir una ciudad, pueblo, departamento o barrio uruguayo.")
        if st.button("🌧️↩️ Volver al buscador", help="Hacé clic para volver"):
            st.session_state.resultado_activo = False
            st.session_state.lugar_actual = ""
            st.rerun()
    else:
        # Consulta API completa: Multimodelo, Visibilidad, UV, Probabilidad de Precipitación y Datos Horarios
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
        
        # Selección de fondo dinámico
        if lluvia_diaria_hoy > 1.5 or wcode_actual in range(51, 68) or wcode_actual in range(80, 100):
            bg_url = "https://images.unsplash.com/photo-1519692933481-e162a57d6721?q=80&w=1920&auto=format&fit=crop"
        elif wcode_actual in [2, 3, 45, 48]:
            bg_url = "https://images.unsplash.com/photo-1534088568595-a066f410bcda?q=80&w=1920&auto=format&fit=crop"
        else:
            bg_url = "https://images.unsplash.com/photo-1601297183305-6df142704ea2?q=80&w=1920&auto=format&fit=crop"

        st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        .stApp, html, body, [class*="st-"] {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }}

        @keyframes deslizarFondoTenue {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        .stApp {{
            background: linear-gradient(rgba(11, 19, 41, 0.68), rgba(11, 19, 41, 0.58)), url('{bg_url}') !important;
            background-size: 180% 180% !important;
            background-attachment: fixed !important;
            animation: deslizarFondoTenue 45s ease infinite !important;
        }}

        .block-container {{
            position: relative !important;
            z-index: 10 !important;
        }}

        .panel-actual {{
            background: white !important;
            border-radius: 24px !important;
            padding: 22px 25px !important;
            border: 1.5px solid #bae6fd !important;
            color: #0f172a !important;
            box-shadow: 0 10px 25px rgba(14, 165, 233, 0.15) !important;
            margin-bottom: 20px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-around !important;
        }}

        .human-headline {{
            background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%) !important;
            border-left: 5px solid #0284c7 !important;
            padding: 18px 22px !important;
            border-radius: 0 16px 16px 0 !important;
            margin-bottom: 20px !important;
            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.1) !important;
            border-top: 1.5px solid #bae6fd !important;
            border-right: 1.5px solid #bae6fd !important;
            border-bottom: 1.5px solid #bae6fd !important;
        }}

        .alerta-inumet {{
            background: linear-gradient(135deg, #fef2f2 0%, #ffe4e6 100%) !important;
            border-left: 5px solid #dc2626 !important;
            padding: 14px 18px !important;
            border-radius: 0 12px 12px 0 !important;
            margin-bottom: 20px !important;
            color: #991b1b !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.15) !important;
        }}

        .cuadrado-pronostico {{
            background: white !important;
            border-radius: 20px !important;
            padding: 20px 15px !important;
            border: 1.5px solid #bae6fd !important;
            color: #0f172a !important;
            text-align: center !important;
            box-shadow: 0 10px 25px rgba(14, 165, 233, 0.1) !important;
            margin-bottom: 20px !important;
            height: 380px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: space-between !important;
        }}

        .fuentes-card {{
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 16px !important;
            padding: 16px 20px !important;
            border: 1.5px solid #bae6fd !important;
            margin-top: 25px !important;
            font-size: 0.85rem !important;
            color: #334155 !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        }}
        
        .carrusel-horario {{
            display: flex !important;
            overflow-x: auto !important;
            gap: 12px !important;
            padding: 10px 0 15px 0 !important;
            margin-bottom: 20px !important;
        }}
        .tarjeta-hora {{
            background: rgba(255, 255, 255, 0.92) !important;
            border-radius: 16px !important;
            padding: 12px 16px !important;
            min-width: 85px !important;
            text-align: center !important;
            border: 1px solid #bae6fd !important;
            color: #0f172a !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
        }}
        
        @keyframes pulsoAzul {{
            0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(2, 132, 199, 0.7); }}
            70% {{ transform: scale(1); box-shadow: 0 0 0 8px rgba(2, 132, 199, 0); }}
            100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(2, 132, 199, 0); }}
        }}
        .titulo-marca-lugar {{
            text-align: center !important;
            color: #ffffff !important;
            font-size: 2.4rem !important;
            font-weight: 800 !important;
            margin: 0 !important;
            letter-spacing: -0.5px !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5) !important;
        }}
        .live-circle-container {{
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            gap: 8px !important;
            padding-top: 14px !important;
        }}
        .blue-pulse-circle {{
            width: 12px !important;
            height: 12px !important;
            background-color: #38bdf8 !important;
            border: 2px solid #ffffff !important;
            border-radius: 50% !important;
            display: inline-block !important;
            animation: pulsoAzul 2s infinite ease-in-out !important;
        }}
        .live-text-label {{
            font-size: 0.8rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            letter-spacing: 0.5px !important;
            text-transform: uppercase !important;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.6) !important;
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
            st.markdown(f"<h1 class='titulo-marca-lugar'>{lugar_encontrado}</h1>", unsafe_allow_html=True)
        with col_top3:
            st.markdown("""
            <div class='live-circle-container'>
                <span class='blue-pulse-circle'></span>
                <span class='live-text-label'>En vivo</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # MÓDULO DE ALERTA INUMET
        if wcode_actual in [95, 96, 99] or viento_actual > 35 or lluvia_diaria_hoy > 20:
            st.markdown("""
            <div class="alerta-inumet">
                ⚠️ <b>MONITOREO DE ALERTA METEOROLÓGICA (INUMET):</b> Condiciones de inestabilidad activa en la zona. Manténgase informado ante eventuales actualizaciones de advertencia.
            </div>
            """, unsafe_allow_html=True)

        # PANEL CENTRAL DE DATOS
        txt_uv, _ = obtener_categoria_uv(uv_actual)
        st.markdown(f"""
        <div class="panel-actual">
            <div style="text-align: center;">
                <span style="font-size: 3.8rem; font-weight: 800; color: #0284c7;">{temp_actual}°C</span>
                <p style="font-size: 0.9rem; font-weight: 700; color: #475569; margin: 0;">{obtener_descripcion_clima(wcode_actual)}</p>
            </div>
            <div style="border-left: 2px solid #cbd5e1; height: 95px; margin: 0 10px;"></div>
            <div style="font-size: 0.90rem; font-weight: 600; color: #1e293b; line-height: 1.6;">
                <div>🌡️ Sensación: <b>{sensacion_actual}°C</b></div>
                <div>💧 Humedad: <b>{humedad_actual}%</b></div>
                <div>💨 Viento: <b>{viento_actual} km/h</b></div>
                <div>📊 Presión: <b>{presion_actual} hPa</b></div>
                <div>👁️ Visibilidad: <b>{visibilidad_km} km</b></div>
                <div>☀️ Índice UV: <b>{txt_uv}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # TITULAR HUMANO
        st.markdown(f"""
        <div class="human-headline">
            <p style="margin: 0; color: #0f172a; font-size: 1.05rem; font-weight: 700; line-height: 1.4;">
                {icono_humano} {frase_humana}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # CARRUSEL HORARIO
        st.markdown("<h3 style='color: #ffffff; font-size: 1.2rem; margin-bottom: 10px; text-shadow: 0 2px 8px rgba(0,0,0,0.5);'>⏱️ Tendencia para las Próximas Horas</h3>", unsafe_allow_html=True)
        
        times_h = hourly.get("time", [])
        temps_h = hourly.get("temperature_2m", [])
        probs_h = hourly.get("precipitation_probability", [])
        codes_h = hourly.get("weathercode", [])
        
        if times_h:
            tarjetas_lista = []
            for k in range(min(12, len(times_h))):
                hora_str = times_h[k].split("T")[-1][:5] if "T" in times_h[k] else str(k)
                t_h = temps_h[k] if k < len(temps_h) else "--"
                p_h = probs_h[k] if k < len(probs_h) else 0
                tarjetas_lista.append(
                    f'<div class="tarjeta-hora">'
                    f'<div style="font-weight: 700; font-size: 0.85rem; color: #0284c7;">{hora_str}</div>'
                    f'<div style="font-size: 1.2rem; margin: 4px 0;"><b>{t_h}°C</b></div>'
                    f'<div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">💧 {p_h}%</div>'
                    f'</div>'
                )
            html_carrusel = f'<div class="carrusel-horario">{"".join(tarjetas_lista)}</div>'
            st.markdown(html_carrusel, unsafe_allow_html=True)

        # PRONÓSTICO EXTENDIDO
        st.markdown("<h3 style='color: #ffffff; font-size: 1.3rem; margin-bottom: 15px; text-shadow: 0 2px 8px rgba(0,0,0,0.5);'>📅 Pronóstico Extendido</h3>", unsafe_allow_html=True)
        
        fechas = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        lluvia = daily.get("precipitation_sum", [])
        prob_lluvia_diaria = daily.get("precipitation_probability_max", [])
        viento_diario = daily.get("windspeed_10m_max", [])
        uv_diario = daily.get("uv_index_max", [])
        wcodes_daily = daily.get("weathercode", [])
        
        cols = st.columns(3)
        etiquetas = ["Hoy", "Mañana", "Pasado Mañana"]
        
        for i in range(min(3, len(fechas))):
            codigo_clima = wcodes_daily[i] if i < len(wcodes_daily) else 0
            estado_texto = obtener_descripcion_clima(codigo_clima)
            
            tmax_val = t_max[i] if i < len(t_max) else "--"
            tmin_val = t_min[i] if i < len(t_min) else "--"
            lluvia_val = lluvia[i] if i < len(lluvia) else 0.0
            prob_val = prob_lluvia_diaria[i] if i < len(prob_lluvia_diaria) else 0
            viento_val = viento_diario[i] if i < len(viento_diario) else "--"
            uv_val = uv_diario[i] if i < len(uv_diario) else "--"
            fecha_val = fechas[i] if i < len(fechas) else ""
            
            with cols[i]:
                st.markdown(f"""
                <div class="cuadrado-pronostico">
                    <div>
                        <h4 style="color: #0284c7; margin-bottom: 2px; font-weight: 800; font-size: 1.2rem;">{etiquetas[i]}</h4>
                        <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 6px; font-weight: 600;">{fecha_val}</p>
                        <p style="font-size: 0.85rem; color: #1e293b; font-weight: 700; margin-bottom: 8px; line-height: 1.2;">{estado_texto}</p>
                    </div>
                    <div>
                        <hr style="border-color: #cbd5e1; margin: 6px 0 10px 0;">
                        <p style="font-size: 0.95em; margin: 4px 0;"><b>🌡️ Máx:</b> {tmax_val} °C</p>
                        <p style="font-size: 0.95em; margin: 4px 0;"><b>❄️ Mín:</b> {tmin_val} °C</p>
                        <p style="font-size: 0.95em; margin: 4px 0;"><b>🌧️ Prob. Lluvia:</b> {prob_val}%</p>
                        <p style="font-size: 0.95em; margin: 4px 0;"><b>💧 Acumulado:</b> {lluvia_val} mm</p>
                        <p style="font-size: 0.95em; margin: 4px 0;"><b>💨 Viento:</b> {viento_val} km/h</p>
                        <p style="font-size: 0.95em; margin: 4px 0;"><b>☀️ UV Máx:</b> {uv_val}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # CARTA METODOLÓGICA
        st.markdown("""
        <div class="fuentes-card">
            <p style="margin: 0 0 6px 0; font-weight: 700; color: #0284c7; font-size: 0.9rem;">
                🛡️ Consolidador Metodológico y Fuentes Integradas
            </p>
            <p style="margin: 0; line-height: 1.5; color: #475569;">
                Pronóstico procesado mediante ensamble dinámico de modelos numéricos globales de alta resolución 
                <b>(ECMWF / IFS, GFS, ICON, WRF)</b>, telemetría satelital <b>GOES-16 (NOAA)</b>, monitoreo de alertas 
                oficiales de <b>INUMET / MetSul</b>, y validación de superficie con la red de estaciones meteorológicas automáticas <b>(Davis / Wunderground)</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)
