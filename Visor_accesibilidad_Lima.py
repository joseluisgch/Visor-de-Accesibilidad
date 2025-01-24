import streamlit as st
import openrouteservice
import folium
from streamlit_folium import st_folium
from folium import GeoJson

# Configurar la clave de API de OpenRouteService
API_KEY = '5b3ce3597851110001cf6248df1c46e4a40f4150a1f9c089c12d69f2'
cliente_ors = openrouteservice.Client(key=API_KEY)

# Función para calcular isocronas ajustando velocidades para tráfico alto
def calcular_isocronas(origen, modo, tiempo_minutos):
    # Simulación de velocidades más lentas para tráfico
    if modo == "driving-car":
        tiempo_minutos = tiempo_minutos * 0.35  # Reducimos el alcance en un 65%

    parametros = {
        "locations": [origen],
        "profile": modo,
        "range": [int(tiempo_minutos * 60)],  # Tiempo en segundos
        "range_type": "time",  # Tipo de rango basado en tiempo
    }
    isocronas = cliente_ors.isochrones(**parametros)
    return isocronas

# Configuración inicial de la aplicación
st.title("Visor de Isocronas")
st.sidebar.header("Parámetros")

# Entrada de datos
coordenadas = st.sidebar.text_input("Coordenadas iniciales (long, lat)", "-77.0428, -12.0464")
modo_transporte = st.sidebar.selectbox(
    "Modo de transporte",
    {"A pie": "foot-walking", "Bicicleta": "cycling-regular", "Automóvil (Hora punta)": "driving-car"}
)
tiempo_minutos = st.sidebar.slider("Tiempo en minutos", 5, 60, 15)

# Procesar las coordenadas ingresadas
try:
    origen = [float(x) for x in coordenadas.split(",")]
except ValueError:
    st.error("Por favor, ingrese coordenadas válidas en formato 'longitud, latitud'")
    st.stop()

# Calcular isocronas
isocronas = calcular_isocronas(origen, modo_transporte, tiempo_minutos)

# Crear el mapa interactivo
mapa = folium.Map(location=[origen[1], origen[0]], zoom_start=12)

# Agregar marcador al mapa
folium.Marker([origen[1], origen[0]], popup="Ubicación inicial").add_to(mapa)

# Dibujar las isocronas
for feature in isocronas['features']:
    GeoJson(
        feature,
        style_function=lambda x: {
            "color": "red" if modo_transporte == "driving-car" else "blue",
            "fillColor": "red" if modo_transporte == "driving-car" else "blue",
            "fillOpacity": 0.3,
            "weight": 2,
        },
    ).add_to(mapa)

# Mostrar el mapa
st_data = st_folium(mapa, width=700, height=500)
