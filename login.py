import streamlit as st
from servidor_fb import *
import interfaz
from PIL import Image
import base64
from io import BytesIO
import variables


# --- Configuración ---
st.set_page_config(page_title="Login Sistema de Turnos Farmacia", layout="centered", page_icon="🔒")

# --- Cargar imágenes ---
logo_app = Image.open("logo_alain.png")
logo_personal = Image.open("logo app farmacia.png")

# --- Codificar logo_app para cabecera ---
buffered = BytesIO()
logo_app.save(buffered, format="PNG")
img_base64_app = base64.b64encode(buffered.getvalue()).decode()

# --- Codificar logo_personal para footer ---
buffered_footer = BytesIO()
logo_personal.save(buffered_footer, format="PNG")
img_base64_personal = base64.b64encode(buffered_footer.getvalue()).decode()

# --- Verificación de login ---
def verificar_login(usuario, password):
    data_login = leer_registro('login')
    if data_login:
        for _, data in data_login.items():
            if data.get("USER") == usuario and data.get("PASS") == password:
                variables.id_usr = data.get("ID")
                return True
    return False

# --- Página de login ---
def pagina_login():
    # Encabezado con logo de la app
    st.markdown(f"""
        <div style='text-align: center; margin-top: 30px;'>
            <img src='data:image/png;base64,{img_base64_app}' style='max-width: 150px; height: auto;' />
            <h2 style='color: #006699;'>Sistema de gestión de Turnos CESFAM</h2>
        </div>
        <hr>
    """, unsafe_allow_html=True)

    # Estilos personalizados
    st.markdown("""
    <style>
    
    .title {
        font-size: 30px;
        font-weight: bold;
        text-align: center;
        color: #333;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Formulario de login
    with st.form("form_login"):
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="title">🔐 Iniciar sesión</div>', unsafe_allow_html=True)

        usuario_input = st.text_input("Usuario")
        password_input = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar")

        st.markdown('</div>', unsafe_allow_html=True)

        if submit:
            if verificar_login(usuario_input, password_input):
                st.session_state.logged_in = True
                st.session_state.usuario = usuario_input
                st.rerun()  # Forzamos recarga para redirigir
            else:
                st.error("❌ Usuario o contraseña incorrectos.")

    # Footer con tu logo personal
    st.markdown(f"""
        <hr style="margin-top: 3em;">
        <div style='display: flex; align-items: center; justify-content: space-between; color: #888888; font-size: 14px; padding-bottom: 20px;'>
            <img src='data:image/png;base64,{img_base64_personal}' style='height: 40px;' />
            <div style='text-align: right;'>
                💼 Aplicación desarrollada por <strong>Alain César Antinao Sepúlveda</strong><br>
                📧 <a href="mailto:alain.antinao.s@gmail.com" style="color: #4A90E2;">alain.antinao.s@gmail.com</a><br>
                🌐 <a href="https://alain-antinao-s.notion.site/" target="_blank" style="color: #4A90E2;">Mi página personal</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- Ejecución principal ---
if __name__ == "__main__":
    if st.session_state.get("logged_in", False):
        interfaz.pagina_principal()  # ✅ Esto te lleva a interfaz.py si está importado como main
    else:
        pagina_login()

