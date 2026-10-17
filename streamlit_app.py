import streamlit as st
import requests
import os
import urllib.parse

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
# PANTALLA 2: RESULTADOS (FONDO ANIMADO TENUE, PRONÓSTICO ESTÁTICO)
# =========================================================
else:
    lugar_ingresado = st.session_state.lugar_actual.strip()
    lugar_lower = lugar_ingresado.lower()
    
    lat, lon = None, None
    lugar_encontrado = lugar_ingresado.title()
    
    # 1. Búsqueda en base local
    for clave, coords in COORDS_URUGUAY.items():
        if clave in lugar_lower or lugar_lower in clave:
            lat, lon = coords
            lugar_encontrado = clave.title()
            break
            
    # 2. Búsqueda en API con filtro
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
        st.markdown("<style>.stApp { background-color: #f0f9ff !important; }</style>", unsafe_allow_html=True)
        st.warning("⚠️ **MeteoUy es un servicio exclusivo para el territorio de Uruguay.**")
        st.info("No encontramos la localidad ingresada dentro de Uruguay. Por favor, asegúrate de escribir una ciudad, pueblo, departamento o barrio uruguayo.")
        if st.button("🌧️↩️ Volver al buscador"):
            st.session_state.resultado_activo = False
            st.session_state.lugar_actual = ""
            st.rerun()
    else:
        url_meteo = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,surface_pressure,weathercode,wind_speed_10m&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max&forecast_days=3&timezone=auto"
        
        try:
            data = requests.get(url_meteo, timeout=10).json()
        except Exception:
            data = {}
            
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
        
        # Selección dinámica de imagen atmosférica
        if lluvia_diaria_hoy > 1.5 or wcode_actual in range(51, 68) or wcode_actual in range(80, 100):
            bg_url = "https://images.unsplash.com/photo-1519692933481-e162a57d6721?q=80&w=1920&auto=format&fit=crop" # Lluvia
        elif wcode_actual in [2, 3, 45, 48]:
            bg_url = "https://images.unsplash.com/photo-1534088568595-a066f410bcda?q=80&w=1920&auto=format&fit=crop" # Nublado / Nubes
        else:
            bg_url = "https://images.unsplash.com/photo-1601297183305-6df142704ea2?q=80&w=1920&auto=format&fit=crop" # Despejado / Sol

        st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        .stApp, html, body, [class*="st-"] {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }}

        /* --- ANIMACIÓN TENUE DE LAS NUBES/LLUVIA EN EL FONDO --- */
        @keyframes moverNubesTenue {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        .stApp {{
            background: transparent !important;
            background-color: #0b1329 !important;
            position: relative;
            overflow-x: hidden;
        }}

        /* Capa exclusiva de fondo animado independiente */
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(rgba(11, 19, 41, 0.72), rgba(11, 19, 41, 0.62)), url('{bg_url}');
            background-size: 220% 220%;
            animation: moverNubesTenue 45s ease infinite;
            z-index: 0;
            pointer-events: none;
        }}

        /* --- CONTENIDO DEL PRONÓSTICO TOTALMENTE ESTÁTICO Y FIRME --- */
        .block-container {{
            position: relative !important;
            z-index: 2 !important;
        }}

        .panel-actual {{
            background: rgba(255, 255, 255, 0.94);
            backdrop-filter: blur(12px);
            border-radius: 24px;
            padding: 22px 25px;
            border: 1.5px solid rgba(255, 255, 255, 0.7);
            color: #0f172a;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.35);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-around;
        }}

        .human-headline {{
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.96) 0%, rgba(240, 253, 244, 0.96) 100%);
            backdrop-filter: blur(12px);
            border-left: 5px solid #0284c7;
            padding: 18px 22px;
            border-radius: 0 16px 16px 0;
            margin-bottom: 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
            border-top: 1.5px solid rgba(255, 255, 255, 0.7);
            border-right: 1.5px solid rgba(255, 255, 255, 0.7);
            border-bottom: 1.5px solid rgba(255, 255, 255, 0.7);
        }}

        .cuadrado-pronostico {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(12px);
            border-radius: 20px;
            padding: 20px 15px;
            border: 2px solid #bae6fd;
            color: #0f172a;
            text-align: center;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.28);
            margin-bottom: 20px;
            height: 380px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        
        @keyframes pulsoAzul {{
            0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.8); }}
            70% {{ transform: scale(1); box-shadow: 0 0 0 8px rgba(56, 189, 248, 0); }}
            100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(56, 189, 248, 0); }}
        }}
        .titulo-marca-lugar {{
            text-align: center;
            color: #ffffff;
            font-size: 2.4rem;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.5px;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.6);
        }}
        .live-circle-container {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 8px;
            padding-top: 14px;
        }}
        .blue-pulse-circle {{
            width: 12px;
            height: 12px;
            background-color: #38bdf8;
            border: 2px solid #ffffff;
            border-radius: 50%;
            display: inline-block;
            animation: pulsoAzul 2s infinite ease-in-out;
        }}
        .live-text-label {{
            font-size: 0.8rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.6);
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

        st.markdown(f"""
        <div class="panel-actual">
            <div style="text-align: center;">
                <span style="font-size: 3.8rem; font-weight: 800; color: #0284c7;">{temp_actual}°C</span>
                <p style="font-size: 0.9rem; font-weight: 700; color: #475569; margin: 0;">{obtener_descripcion_clima(wcode_actual)}</p>
            </div>
            <div style="border-left: 2px solid #cbd5e1; height: 75px; margin: 0 10px;"></div>
            <div style="font-size: 0.95rem; font-weight: 600; color: #1e293b; line-height: 1.6;">
                <div>🌡️ Sensación: <b>{sensacion_actual}°C</b></div>
                <div>💧 Humedad: <b>{humedad_actual}%</b></div>
                <div>💨 Viento: <b>{viento_actual} km/h</b></div>
                <div>📊 Presión: <b>{presion_actual} hPa</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="human-headline">
            <p style="margin: 0; color: #0f172a; font-size: 1.1rem; font-weight: 700; line-height: 1.4;">
                {icono_humano} {frase_humana}
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='color: #ffffff; font-size: 1.3rem; margin-bottom: 15px; text-shadow: 0 2px 8px rgba(0,0,0,0.5);'>📅 Pronóstico Extendido</h3>", unsafe_allow_html=True)
        
        fechas = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        lluvia = daily.get("precipitation_sum", [])
        viento_diario = daily.get("windspeed_10m_max", [])
        wcodes_daily = daily.get("weathercode", [])
        
        cols = st.columns(3)
        etiquetas = ["Hoy", "Mañana", "Pasado Mañana"]
        
        for i in range(min(3, len(fechas))):
            codigo_clima = wcodes_daily[i] if i < len(wcodes_daily) else 0
            estado_texto = obtener_descripcion_clima(codigo_clima)
            
            tmax_val = t_max[i] if i < len(t_max) else "--"
            tmin_val = t_min[i] if i < len(t_min) else "--"
            lluvia_val = lluvia[i] if i < len(lluvia) else 0.0
            viento_val = viento_diario[i] if i < len(viento_diario) else "--"
            fecha_val = fechas[i] if i < len(fechas) else ""
            
            with cols[i]:
                st.markdown(f"""
                <div class="cuadrado-pronostico">
                    <div>
                        <h4 style="color: #0284c7; margin-bottom: 2px; font-weight: 800; font-size: 1.35rem; text-transform: uppercase;">{etiquetas[i]}</h4>
                        <p style="font-size: 0.8rem; color: #64748b; margin-bottom: 6px; font-weight: 600;">{fecha_val}</p>
                        <p style="font-size: 0.95rem; color: #0f172a; font-weight: 700; margin-bottom: 10px; line-height: 1.3; background: #e0f2fe; padding: 6px 8px; border-radius: 10px;">{estado_texto}</p>
                    </div>
                    <div>
                        <hr style="border-color: #cbd5e1; margin: 4px 0 10px 0;">
                        <div style="background: #f0fdf4; border: 1.5px solid #bbf7d0; padding: 8px; border-radius: 12px; margin-bottom: 10px;">
                            <span style="font-size: 0.81rem; font-weight: 700; color: #166534; display: block;">PRECIPITACIÓN</span>
                            <span style="font-size: 1.2rem; font-weight: 800; color: #15803d;">🌧️ {lluvia_val} mm</span>
                        </div>
                        <div style="font-size: 1.05rem; margin: 4px 0; color: #1e293b;"><b>🌡️ Máx:</b> {tmax_val} °C</div>
                        <div style="font-size: 1.05rem; margin: 4px 0; color: #475569;"><b>❄️ Mín:</b> {tmin_val} °C</div>
                        <div style="font-size: 0.9rem; margin: 4px 0; color: #64748b;"><b>💨 Viento:</b> {viento_val} km/h</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
