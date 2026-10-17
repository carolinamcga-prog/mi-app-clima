from datetime import datetime, timedelta
import locale

# Configurar el idioma en español (opcional, según tu sistema operativo)
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    pass

def obtener_dias_actualizados():
    hoy = datetime.now()
    dia_1 = hoy + timedelta(days=1)
    dia_2 = hoy + timedelta(days=2)
    
    # Formatear el nombre de los días con la primera letra en mayúscula
    nombre_hoy = hoy.strftime('%A').capitalize()
    nombre_dia_1 = dia_1.strftime('%A').capitalize()
    nombre_dia_2 = dia_2.strftime('%A').capitalize()
    
    # Imprimir el resultado adaptado
    print(f"Ciudad: [Nombre de la Ciudad]")
    print(f"* Hoy ({nombre_hoy})")
    print(f"* {nombre_dia_1}")
    print(f"* {nombre_dia_2}")

# Ejecutar la función
obtener_dias_actualizados()



  
   
