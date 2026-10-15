
# @title Mini App del Clima Interactiva
import ipywidgets as widgets
from IPython.display import display, clear_output

# Crear elementos visuales simples
ciudad_input = widgets.Text(
    value='Montevideo',
    description='Ciudad:',
    disabled=False
)

boton_consultar = widgets.Button(
    description='Consultar Clima',
    button_style='success', # Cambia a color verde
    icon='cloud'
)

salida = widgets.Output()

def al_hacer_clic(b):
    with salida:
        clear_output()
        ciudad = ciudad_input.value
        print(f"🔄 Consultando satélites para {ciudad}...")
        # Simulación de resultado
        print(f"-----------------------------------")
        print(f"📍 Ubicación: {ciudad}")
        print(f"🌡️ Temperatura: 22°C")
        print(f"☁️ Estado: Parcialmente nublado")
        print(f"⚠️ Alertas: Sin alertas vigentes.")
        print(f"-----------------------------------")

boton_consultar.on_click(al_hacer_clic)

# Mostrar la "app" en pantalla
display(ciudad_input, boton_consultar, salida)
