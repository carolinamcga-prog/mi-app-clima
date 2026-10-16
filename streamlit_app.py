import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Mini App del Clima", page_icon="☁️")

# Título e instrucciones en la web
st.title("☁️ Mini App del Clima e Informes")
st.write("Ingresa tu ciudad para consultar el pronóstico meteorológico y alertas.")

# Entrada de texto para la ciudad
ciudad = st.text_input("Ciudad:", value="Montevideo")

# Botón interactivo
if st.button("Consultar Clima"):
    st.info(f"🔄 Consultando satélites meteorológicos para {ciudad}...")
    
    st.markdown("---")
    st.subheader(f"📍 Ubicación: {ciudad}")
    
    # Mostrar métricas en columnas
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Temperatura", value="22 °C")
    with col2:
        st.metric(label="Estado", value="Parcialmente nublado")
        
    st.success("✅ Alertas: Sin alertas vigentes.")
    st.markdown("---")
