import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io

#----------------------------------------------------------------------
#Implemento un Login por Contraseña
#----------------------------------------------------------------------
def verificar_password():
    """Retorna True si el usuario ingresó la contraseña correcta."""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if st.session_state.autenticado:
        return True

    st.subheader("🔒 Acceso Restringido - AnasilisRED")
    password_ingresada = st.text_input("Ingresa la contraseña de acceso:", type="password")
    
    if st.button("Ingresar"):
        # Compara con la contraseña guardada en los Secrets
        if password_ingresada == st.secrets.get("APP_PASSWORD", "Password"):
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
NOMBRE_ARCHIVO = "report.csv"
