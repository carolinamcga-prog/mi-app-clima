import base64
import os
import streamlit as st

# ==========================================
# 1. MAPEO DE CÓDIGOS WMO A VIDEOS
# ==========================================
MAPA_VIDEOS_CLIMA = {
    # Soleado / Despejado
    0: "assets/videos/soleado.mp4",
    1: "assets/videos/soleado.mp4",
    # Parcialmente nublado
    2: "assets/videos/parcialmente_nublado.mp4",
    # Nublado / Muy nublado
    3: "assets/videos/nublado.mp4",
    # Niebla / Neblina
    45: "assets/videos/niebla.mp4",
    48: "assets/videos/niebla.mp4",
    # Llovizna
    51: "assets/videos/llovizna.mp4",
    53: "assets/videos/llovizna.mp4",
    55: "assets/videos/llovizna.mp4",
    56: "assets/videos/llovizna.mp4",
    57: "assets/videos/llovizna.mp4",
    # Lluvia moderada / constante
    61: "assets/videos/lluvia.mp4",
    63: "assets/videos/lluvia.mp4",
    80: "assets/videos/lluvia.mp4",
    # Lluvia torrencial / chubascos fuertes
    65: "assets/videos/lluvia_torrencial.mp4",
    81: "assets/videos/lluvia_torrencial.mp4",
    82: "assets/videos/lluvia_torrencial.mp4",
    # Granizo
    85: "assets/videos/granizo.mp4",
    86: "assets/videos/granizo.mp4",
    # Tormenta eléctrica
    95: "assets/videos/tormenta.mp4",
    96: "assets/videos/tormenta.mp4",
    99: "assets/videos/tormenta.mp4",
}


def obtener_ruta_video(wmo_code):
    """Devuelve la ruta del video según el código WMO o un video por defecto."""
    return MAPA_VIDEOS_CLIMA.get(wmo_code, "assets/videos/soleado.mp4")


# ==========================================
# 2. INYECCIÓN DEL VIDEO TENUE EN EL FONDO
# ==========================================
def set_video_background(video_path):
    """Carga el video local en base64 y lo inyecta como fondo de pantalla con una capa tenue."""
    if os.path.exists(video_path):
        with open(video_path, "rb") as f:
            video_bytes = f.read()
            video_b64 = base64.b64encode(video_bytes).decode("utf-8")

        video_html = f"""
        <style>
            /* Fondo de la app transparente para ver el video */
            .stApp {{
                background: transparent !important;
            }}
            /* Contenedor fijo del video de fondo */
            .video-bg-container {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                overflow: hidden;
                z-index: -2;
            }}
            .video-bg-container video {{
                min-width: 100%;
                min-height: 100%;
                width: auto;
                height: auto;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                object-fit: cover;
            }}
            /* Capa oscura/tenue sobre el video para mejorar contraste */
            .video-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(0, 0, 0, 0.35); /* Ajusta 0.35 para más o menos brillo */
                z-index: -1;
            }}
        </style>
        <div class="video-bg-container">
            <video autoplay loop muted playsinline>
                <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
            </video>
        </div>
        <div class="video-overlay"></div>
        """
        st.markdown(video_html, unsafe_allow_html= Otro_flag=True)


# ==========================================
# 3. ESTILOS DE CUADROS BLANCOS (TARJETAS)
# ==========================================
def aplicar_estilos_tarjetas_blancas():
    """Aplica CSS para que los cuadros de pronóstico se vean blancos y legibles."""
    st.markdown(
        """
        <style>
            .tarjeta-clima {
                background-color: rgba(255, 255, 255, 0.90) !important;
                border-radius: 16px;
                padding: 20px;
                margin: 10px 0px;
                box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15);
                color: #1E1E1E !important;
                text-align: center;
                backdrop-filter: blur(5px);
            }
            .tarjeta-clima h3 {
                color: #111111 !important;
                margin-bottom: 5px;
                font-weight: 700;
            }
            .tarjeta-clima .temp-max {
                font-size: 26px;
                font-weight: bold;
                color: #D9534F;
            }
            .tarjeta-clima .temp-min {
                font-size: 22px;
                color: #0275D8;
            }
            .tarjeta-clima .estado {
                font-size: 16px;
                color: #555555;
                margin-top: 5px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def renderizar_cuadro_dia(titulo, temp_max, temp_min, condicion):
    """Muestra un cuadro/tarjeta blanca con los datos del día."""
    st.markdown(
        f"""
        <div class="tarjeta-clima">
            <h3>{titulo}</h3>
            <div class="estado">{condicion}</div>
            <hr style="margin: 10px 0; border: 0; border-top: 1px solid #eee;">
            <div><span class="temp-max">{temp_max}°C</span> / <span class="temp-min">{temp_min}°C</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
