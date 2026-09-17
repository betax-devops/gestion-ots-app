import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io

#----------------------------------------------------------------------
#Implemento un Login por Contraseña
#----------------------------------------------------------------------
import streamlit as st

def verificar_password():
    """Retorna True si el usuario ingresó la contraseña correcta."""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if st.session_state.autenticado:
        return True

    st.subheader("🔒 Acceso Restringido - AnálisisRED")
    
    # 1. Obtener la contraseña desde los Secrets
    try:
        correct_password = st.secrets["APP_PASSWORD"]
    except KeyError:
        st.error("⚠️ La contraseña del sistema no está configurada en los Secrets de Streamlit.")
        return False

    # 2. Formulario de ingreso
    password_ingresada = st.text_input("Ingresa la contraseña de acceso:", type="password")
    
    if st.button("Ingresar"):
        if password_ingresada == correct_password:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
            
    return False

# Control de acceso principal
if not verificar_password():
    st.stop()  # Detiene la ejecución si no está autenticado
#----------------------------------------------------------------------


st.set_page_config(page_title="Gestión de Ordenes de Trabajo - CCP", layout="wide")
st.title("🌐 Analisis OTs")

# --- CONEXIÓN A GOOGLE DRIVE VÍA SECRETS ---
# --- FUNCIÓN PARA CONECTAR A GOOGLE DRIVE Y CARGAR EL CSV ---
@st.cache_data(ttl=300)  # Reutiliza los datos cargados durante 5 minutos
def cargar_csv_desde_drive(nombre_archivo):
    # 1. Autenticación con las credenciales guardadas en Secrets
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )
    service = build("drive", "v3", credentials=creds)

    # 2. Buscar el id del archivo en Google Drive
    query = f"name = '{nombre_archivo}' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get("files", [])

    if not items:
        st.error(f"No se encontró el archivo '{nombre_archivo}' en Google Drive.")
        return None

    file_id = items[0]["id"]

    # 3. Descargar el contenido del archivo a la memoria
    request = service.files().get_media(fileId=file_id)
    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    file_stream.seek(0)

    # 4. Leer el CSV con Pandas (ajustando separador de punto y coma)
    try:
        # Intenta primero con utf-8-sig / utf-8
        return pd.read_csv(file_stream, sep=";", quotechar='"', encoding="utf-8-sig")
    except (UnicodeDecodeError, Exception):
        file_stream.seek(0)
        try:
            # Si falla, intenta con latin1 (muy común en Windows / Latinoamérica)
            return pd.read_csv(file_stream, sep=";", quotechar='"', encoding="latin1")
        except Exception:
            file_stream.seek(0)
            # Como último recurso, lee ignorando errores de caracteres extraños
            return pd.read_csv(file_stream, sep=";", quotechar='"', encoding="utf-8", encoding_errors="ignore")

# --- CARGA Y VISUALIZACIÓN DE TABLA ---
NOMBRE_ARCHIVO = "report.csv"

# Cargar el dataframe desde Google Drive
df = cargar_csv_desde_drive(NOMBRE_ARCHIVO)

if df is not None:
    st.subheader("📋 Todos los Resultados")
    st.write(f"Resultados encontrados: **{len(df)}**")
    st.dataframe(df, use_container_width=True)
