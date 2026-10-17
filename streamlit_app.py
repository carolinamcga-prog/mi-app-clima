import streamlit as st
import streamlit.components.v1 as components
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

# Vídeos directos en formato MP4 de alta compatibilidad
VIDEOS = {
    "clear": "https://cdn.pixabay.com/video/2020/05/25/40130-424128532_large.mp4",
    "cloudy": "https://cdn.pixabay.com/video/2019/06/11/24341-341617042_large.mp4",
    "rain": "https://cdn.pixabay.com/video/2021/08/11/84683-587285114_large.mp4",
    "thunder": "https://cdn.pixabay.com/video/2020/05/02/37575-415848520_large.mp4"
}

# Control de estado de navegación
if "resultado_activo" not in st.session_state:
    st.session_state.resultado_activo = False
if "lugar_actual" not in st.session_state:
    st.session_state.lugar_actual = ""

# Función para cargar el logo real
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
        st.markdown("<h1 style='text-align: center; color: #222; font-size: 3.5rem;'>MeteoUy</h1>", unsafe_allow_html=True)

# =========================================================
# PANTALLA 1: INICIO (LOGO GIGANTE, BARRA TITILANTE Y BOTONES CELESTES)
# =========================================================
if not st.session_state.resultado_activo:
    st.markdown("""
    <style>
    .stApp {
        background-color: white !important;
    }
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 2vh;
    }
    
    @keyframes pulseGlow {
        0% {
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
            border-color: #38bdf8;
        }
        50% {
            box-shadow: 0 0 25px rgba(14, 165, 233, 0.75);
            border-color: #0284c7;
        }
        100% {
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
            border-color: #38bdf8;
        }
    }

    div[data-baseweb="input"] {
        border-radius: 45px !important;
        padding: 10px 22px !important;
        border: 2.5px solid #38bdf8 !important;
        animation: pulseGlow 2.5s infinite ease-in-out !important;
        font-size: 1.25rem !important;
        background-color: #f8fafc !important;
    }
    div[data-baseweb="input"] input {
        font-size: 1.2rem !important;
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
        height: 3
