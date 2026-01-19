import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from zoneinfo import ZoneInfo
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
spreadsheets = client.list_spreadsheet_files()
st.write([s["name"] for s in spreadsheets])


sheet = client.open("Registro_Actividades").worksheet("Registros")

# 👀 Conectar catálogos

@st.cache_data(ttl=600)  # 10 minutos
def cargar_catalogo(nombre_hoja):
    sh = client.open("Registro_Actividades")
    ws = sh.worksheet(nombre_hoja)
    return ws.col_values(1)[1:]  # 

sectores = cargar_catalogo("Sectores")
actividades = cargar_catalogo("Actividades")
capataces = cargar_catalogo("Capataces")

# Define la hora local de Perú

zona_pe = ZoneInfo("America/Lima")
ahora_pe = datetime.now(zona_pe)

# Cargar Imagen
st.subheader("🗺️ Sectorización")
st.image(
    "assets/sectorizacion.jpg",
    caption="Plano de sectores de trabajo",
    use_column_width=True
)


# -------------------------------
# Formulario de registro
# -------------------------------
with st.form("registro_actividades"):
    fecha = st.date_input("📅 Fecha", value=ahora_pe.today())
    sector = st.selectbox("📍 Sector", sectores)
    actividad = st.selectbox("🛠 Actividad", actividades)
    personas = st.number_input(
        "👷 Personas en cuadrilla",
        min_value=1,
        step=1
    )
    hora_inicio = st.time_input("⏱ Hora inicio", value=ahora_pe.time())
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
        ahora_pe.now().strftime("%d-%m-%Y %H:%M:%S")  # timestamp
    ])

    st.success("✅ Registro guardado correctamente")

# CACHEAR EL SHEET PRINCIPAL TAMBIÉN

@st.cache_resource
def get_sheet():
    sh = client.open("Registro_Actividades")
    return sh.sheet1

sheet = get_sheet()
