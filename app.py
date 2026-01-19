import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# -------------------------------
# Configuración de la página
# -------------------------------
st.set_page_config(
    page_title="Registro de Actividades",
    layout="centered"
)

st.title("📋 Registro Diario de Actividades")

# -------------------------------
# Conexión a Google Sheets
# -------------------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

# 👉 nombre EXACTO del Google Sheet
sheet = client.open("Registro_Actividades").sheet1

# 👀 Conectar catálogos

def cargar_catalogo(nombre_hoja):
    hoja = client.open("Registro_Actividades").worksheet(nombre_hoja)
    valores = hoja.col_values(1)
    return [v for v in valores if v.strip() != ""]

sectores = cargar_catalogo("Sectores")
actividades = cargar_catalogo("Actividades")
capataces = cargar_catalogo("Capataces")

# -------------------------------
# Formulario de registro
# -------------------------------
with st.form("registro_actividades"):
    fecha = st.date_input("📅 Fecha", value=datetime.today())
    sector = st.selectbox("📍 Sector", sectores)
    actividad = st.selectbox("🛠 Actividad", actividades    )
    personas = st.number_input(
        "👷 Personas en cuadrilla",
        min_value=1,
        step=1
    )
    hora_inicio = st.time_input("⏱ Hora inicio")
    hora_fin = st.time_input("⏱ Hora fin")
    capataz = st.selectbox("🧑‍🏭 Capataz responsable", capataces)

    enviar = st.form_submit_button("💾 Guardar")

# -------------------------------
# Guardado en Google Sheets
# -------------------------------
if enviar:
    sheet.append_row([
        str(fecha),
        sector,
        actividad,
        personas,
        str(hora_inicio),
        str(hora_fin),
        capataz,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # timestamp
    ])

    st.success("✅ Registro guardado correctamente")

# Cachear catálogos – performance pro, para que no lea Sheets en cada recarga:

@st.cache_data(ttl=300)
def cargar_catalogo(nombre_hoja):
    hoja = client.open("Registro_Actividades").worksheet(nombre_hoja)
    valores = hoja.col_values(1)
    return [v for v in valores if v.strip() != ""]
