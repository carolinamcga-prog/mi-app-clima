import streamlit as st
import requests

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="MeteoUy",
    page_icon="⛅",
    layout="centered"
)

# --- ESTILOS VISUALES LIMPIOS (UX CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .big-temp {
        font-size: 4rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1;
    }
    .card-box {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    .human-headline {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-left: 5px solid #3b82f6;
        padding: 20px;
        border-radius: 0 12px 12px 0;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .metric-card {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAR ESTADO DE NAVEGACIÓN ---
if 'pantalla' not in st.session_state:
    st.session_state.pantalla = 1
if 'datos_clima' not in st.session_state:
    st.session_state.datos_clima = None
if 'nombre_ciudad' not in st.session_state:
    st.session_state.nombre_ciudad = ""

# Diccionario con coordenadas de referencia para Uruguay
CIUDADES_URUGUAY = {
    "Montevideo": {"lat": -34.9011, "lon": -56.1645},
    "Salto": {"lat": -31.3833, "lon": -57.9667},
    "Paysandú": {"lat": -32.3214, "lon": -58.0756},
    "Punta del Este": {"lat": -34.9645, "lon": -54.9433},
    "Maldonado": {"lat": -34.9082, "lon": -54.9536},
    "Rivera": {"lat": -30.9053, "lon": -55.5508},
    "Tacuarembó": {"lat": -31.7333, "lon": -55.9833},
    "Colonia del Sacramento": {"lat": -34.4626, "lon": -57.8402},
    "Canelones": {"lat": -34.5228, "lon": -56.2792},
    "San José de Mayo": {"lat": -34.3375, "lon": -56.7136}
}

# --- FUNCIÓN DE CONSULTA A API ---
def consultar_api(nombre_ciudad):
    coords = CIUDADES_URUGUAY[nombre_ciudad]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            st.session_state.datos_clima = response.json()
            st.session_state.nombre_ciudad = nombre_ciudad
            st.session_state.pantalla = 2
            st.rerun()
        else:
            st.error("No se pudo conectar con el servicio meteorológico.")
    except Exception:
        st.error("Error de conexión. Verifica tu acceso a internet.")

# --- TRADUCTOR INTELIGENTE: EL TITULAR HUMANO ---
def generar_titular_humano(temp, codigo, viento):
    # Lluvia
    if codigo in range(51, 68) or codigo in range(80, 100):
        return "🌧️", "Pésimo momento para colgar ropa. Se vienen chaparrones o lloviznas, ¡llevá paraguas sí o sí!"
    
    # Viento fuerte
    if viento > 25:
        return "🌬️", "Hay un viento bastante fuerte y molesto afuera. Si salís, ponete una buena campera porque refresca."
    
    # Frío
    if temp < 12:
        return "🧥", "Día helado. Ponete abrigo pesado porque la temperatura amerita campera de invierno."
    
    # Calor
    if temp > 26:
        return "☀️", "¡Hermoso sol y calorcito! Día ideal para aprovechar al aire libre, pero no te olvides del protector."
    
    # Templado / Estable
    return "⛅", "Tiempo lindo, estable y agradable. Ideal para salir a dar una vuelta sin grandes complicaciones."


# ==========================================
# PANTALLA 1: BUSCADOR Y ACCESOS RÁPIDOS
# ==========================================
if st.session_state.pantalla == 1:
    st.markdown("## ⛅ **MeteoUy**")
    st.markdown("Tu reporte meteorológico en tiempo real, claro y sin vueltas.")
    st.write("")

    # Accesos rápidos (Quick Pills visuales)
    st.markdown("##### 📍 Accesos rápidos frecuentes:")
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        if st.button("Montevideo", use_container_width=True):
            consultar_api("Montevideo")
    with col_q2:
        if st.button("Punta del Este", use_container_width=True):
            consultar_api("Punta del Este")
    with col_q3:
        if st.button("Salto", use_container_width=True):
            consultar_api("Salto")
    with col_q4:
        if st.button("Colonia", use_container_width=True):
            consultar_api("Colonia del Sacramento")

    st.markdown("---")
    
    # Buscador tradicional por lista desplegable
    ciudad_seleccionada = st.selectbox(
        "O busca tu localidad en el listado completo:",
        options=list(CIUDADES_URUGUAY.keys()),
        index=0
    )

    st.write("")
    
    if st.button("🔍 Consultar Localidad", type="primary", use_container_width=True):
        with st.spinner("Buscando datos en el radar... 🌤️"):
            consultar_api(ciudad_seleccionada)

# ==========================================
# PANTALLA 2: RESULTADOS (CON TITULAR HUMANO)
# ==========================================
elif st.session_state.pantalla == 2:
    datos = st.session_state.datos_clima.get("current", {})
    
    temp = datos.get("temperature_2m", 20.0)
    sensacion = datos.get("apparent_temperature", 20.0)
    humedad = datos.get("relative_humidity_2m", 50)
    viento = datos.get("wind_speed_10m", 10.0)
    codigo_wmo = datos.get("weather_code", 0)
    
    icono_humano, frase_humana = generar_titular_humano(temp, codigo_wmo, viento)

    # Cabecera de ubicación
    st.markdown(f"### 📍 Clima actual en **{st.session_state.nombre_ciudad}**")
    st.write("")

    # 1. EL DATO REY (Temperatura Gigante)
    st.markdown(
        f"""
        <div class="card-box">
            <div class="big-temp">{temp}°C</div>
            <p style="margin: 8px 0 0 0; color: #64748b; font-size: 1rem; font-weight: 500;">Sensación térmica: {sensacion}°C</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. EL TITULAR HUMANO (La frase que le habla directo al usuario)
    st.markdown(
        f"""
        <div class="human-headline">
            <p style="margin: 0; color: #1e293b; font-size: 1.1rem; font-weight: 600; line-height: 1.4;">
                {frase_humana}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("##### 📊 Detalles complementarios")

    # 3. GRILLA DE DATOS SECUNDARIOS
    col_hum, col_vie = st.columns(2)

    with col_hum:
        st.markdown(
            f"""
            <div class="metric-card">
                <p style="margin: 0; color: #64748b; font-size: 0.9rem;">💧 Humedad</p>
                <p style="margin: 5px 0 0 0; color: #0f172a; font-size: 1.4rem; font-weight: 700;">{humedad}%</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_vie:
        st.markdown(
            f"""
            <div class="metric-card">
                <p style="margin: 0; color: #64748b; font-size: 0.9rem;">💨 Viento</p>
                <p style="margin: 5px 0 0 0; color: #0f172a; font-size: 1.4rem; font-weight: 700;">{viento} km/h</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    st.markdown("---")

    # 4. BOTÓN DE RETORNO CÓMODO
    if st.button("⬅️ Consultar otra localidad", use_container_width=True):
        st.session_state.pantalla = 1
        st.rerun()
