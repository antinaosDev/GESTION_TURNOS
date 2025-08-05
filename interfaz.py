import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from servidor_fb import ingresar_registro_bd, leer_registro, actualizar_registro
from clases import Receta

# Diccionarios
CATEGORIAS = {
    "Preferencial": "P",
    "General": "G"
}

SUBCATEGORIAS = {
    "Receta Controlada": "CT",
    "Receta Morbilidad": "M",
    "Receta Crónico": "CN"
}

CODIGO_A_NOMBRE = {v: k for k, v in SUBCATEGORIAS.items()}

# Generar número secuencial desde Firebase
def generar_nro_turno(categoria_sigla, subcat_codigo):
    turnos = leer_registro("turnos")
    hoy = str(datetime.now().date())
    contador = 0
    for turno in turnos.values():
        if (turno.get("CATEGORIA") == categoria_sigla and
            turno.get("SUBCAT") == subcat_codigo and
            turno.get("Fecha") == hoy):
            contador += 1
    nro = contador + 1
    return f"{categoria_sigla}{subcat_codigo}{str(nro).zfill(3)}"

# Generar ticket en PDF
def generar_ticket_pdf(nombre, dni, nro_turno, categoria, subcategoria, fecha):
    pdf = FPDF(orientation='P', unit='mm', format=(105, 148))
    pdf.add_page()
    pdf.set_font("Arial", size=15)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 10, txt="CESFAM CHOLCHOL", ln=True, align="C")
    pdf.ln(25)
    pdf.set_font("Arial", 'B', size=55)
    pdf.set_text_color(0, 0, 120)
    pdf.cell(0, 30, txt=nro_turno, ln=True, align="C")
    pdf.ln(15)
    pdf.set_font("Arial", '', size=12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, txt=subcategoria.upper(), ln=True, align="C")
    return pdf.output(dest='S').encode('latin1')

# Estilos de la app
st.set_page_config(page_title="Turnos Medicamentos", page_icon="💊", layout="wide")
st.markdown("""
    <style>
        .main { background-color: #f2f6fc; }
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        h1, h2, h3 { color: #006699; }
        .dashboard-container {
            background-color: #dbe9f9;
            border-radius: 8px;
            padding: 10px;
        }
        .categoria-title {
            font-weight: bold;
            font-size: 1.3em;
            padding: 8px 0;
            border-bottom: 2px solid #005b96;
        }
        .subcategoria-title {
            font-weight: 600;
            font-size: 1.1em;
            padding: 5px 0;
            color: #004080;
            border-bottom: 1px solid #b0c4de;
        }
        .turno-box {
            background-color: #f0f6ff;
            margin: 5px 3px;
            padding: 8px;
            border-radius: 5px;
            text-align: center;
            font-weight: 700;
            font-size: 1.4em;
            color: #003366;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        }
        .header-row {
            background-color: #9bb9e1;
            font-weight: bold;
            font-size: 1.2em;
            text-align: center;
            padding: 10px 0;
            border-radius: 6px 6px 0 0;
        }
    </style>
""", unsafe_allow_html=True)

st.title("💊 Sistema de Turnos para Entrega de Medicamentos")

menu = st.sidebar.radio("Menú", ["📋 Solicitar Turno", "🗞️ Ver Turnos (Admin)", "📽️ Pantalla de Turnos"])

# ---- SOLICITAR TURNO ----
if menu == "📋 Solicitar Turno":
    st.header("📌 Solicita tu turno")

    with st.form("form_turno"):
        nombre = st.text_input("👤 Nombre completo")
        dni = st.text_input("🆔 RUT (sin puntos, con guion. Ej: 12345678-9)")
        categoria = st.selectbox("🏷️ Categoría", list(CATEGORIAS.keys()))
        subcat_nombre = st.selectbox("📄 Tipo de receta", list(SUBCATEGORIAS.keys()))
        enviar = st.form_submit_button("Solicitar turno")

    if enviar:
        if nombre and dni and categoria and subcat_nombre:
            try:
                rut_num, dv = dni.split('-')
                cat_sigla = CATEGORIAS[categoria]
                subcat_codigo = SUBCATEGORIAS[subcat_nombre]
                nro_turno = generar_nro_turno(cat_sigla, subcat_codigo)
                fecha = str(datetime.now().date())

                receta = Receta(nombre, rut_num, dv, cat_sigla, subcat_codigo)
                registro = receta.dict_rec()
                registro["Nro Turno"] = nro_turno
                registro["Fecha"] = fecha
                registro["Estado"] = "Pendiente"

                ingresar_registro_bd("turnos", registro)

                st.success("✅ Turno asignado correctamente")
                st.markdown(f"<h2 style='text-align: center; color: green;'>🎫 Nº de Turno: {nro_turno}</h2>", unsafe_allow_html=True)

                pdf_bytes = generar_ticket_pdf(nombre, dni, nro_turno, categoria, subcat_nombre, fecha)

                st.download_button(
                    label="📄 Descargar Ticket en PDF",
                    data=pdf_bytes,
                    file_name=f"Ticket_{nro_turno}.pdf",
                    mime="application/pdf"
                )
            except:
                st.error("❌ Error en el formato del RUT. Usa el formato 12345678-9")
        else:
            st.warning("⚠️ Completa todos los campos antes de enviar.")

# ---- VER TURNOS (ADMIN) ----
elif menu == "🗞️ Ver Turnos (Admin)":
    st.header("📄 Lista de Turnos Asignados")
    turnos_dict = leer_registro("turnos")
    turnos = pd.DataFrame.from_dict(turnos_dict, orient='index') if turnos_dict else pd.DataFrame()

    if turnos.empty:
        st.info("No hay turnos asignados aún.")
    else:
        st.dataframe(turnos.sort_values(by=["Fecha", "Nro Turno"], ascending=[False, True]), use_container_width=True)

        st.subheader("✔️ Marcar turno como atendido")

        pendientes = turnos[(turnos["Estado"] == "Pendiente") & (turnos["Nro Turno"].notna())]
        if not pendientes.empty:
            turno_a_marcar = st.selectbox("Selecciona un Nº de Turno pendiente", pendientes["Nro Turno"].tolist(), key="marcar_turno")
            if st.button("Marcar como atendido"):
                for id_turno, t in turnos_dict.items():
                    if t["Nro Turno"] == turno_a_marcar:
                        actualizar_registro("turnos", {"Estado": "Atendido"}, id_turno)
                        st.success(f"Turno {turno_a_marcar} marcado como atendido.")
                        st.experimental_rerun()
        else:
            st.info("No hay turnos pendientes para marcar como atendidos.")

        st.subheader("📝 Editar o eliminar turnos")

        all_nros = turnos["Nro Turno"].dropna().tolist()
        nro_seleccionado = st.selectbox("Selecciona un Nº de Turno para editar o eliminar", all_nros, key="editar_turno")

        if nro_seleccionado:
            # Buscar el ID del turno en Firebase
            id_encontrado = None
            turno_data = None
            for id_turno, datos in turnos_dict.items():
                if datos.get("Nro Turno") == nro_seleccionado:
                    id_encontrado = id_turno
                    turno_data = datos
                    break

            if turno_data:
                with st.form("form_editar_turno"):
                    nuevo_nombre = st.text_input("Nombre", turno_data.get("NOMBRE", ""))
                    nuevo_rut = st.text_input("RUT", turno_data.get("RUT", ""))
                    nueva_categoria = st.selectbox("Categoría", list(CATEGORIAS.values()), index=list(CATEGORIAS.values()).index(turno_data.get("CATEGORIA", "G")))
                    nueva_subcat = st.selectbox("Subcategoría", list(SUBCATEGORIAS.values()), index=list(SUBCATEGORIAS.values()).index(turno_data.get("SUBCAT", "M")))
                    nuevo_estado = st.selectbox("Estado", ["Pendiente", "Atendido"], index=0 if turno_data.get("Estado") == "Pendiente" else 1)
                    nueva_fecha = st.date_input("Fecha", datetime.strptime(turno_data.get("Fecha"), "%Y-%m-%d").date())

                    editar = st.form_submit_button("💾 Guardar cambios")
                    eliminar = st.form_submit_button("🗑️ Eliminar turno")

                if editar:
                    actualizar_registro("turnos", {
                        "NOMBRE": nuevo_nombre,
                        "RUT": nuevo_rut,
                        "CATEGORIA": nueva_categoria,
                        "SUBCAT": nueva_subcat,
                        "Estado": nuevo_estado,
                        "Fecha": str(nueva_fecha)
                    }, id_encontrado)
                    st.success("✅ Turno actualizado correctamente.")
                    st.experimental_rerun()

                if eliminar:
                    from servidor_fb import borrar_registro
                    borrar_registro("turnos", id_encontrado)
                    st.warning(f"🗑️ Turno {nro_seleccionado} eliminado.")
                    st.experimental_rerun()


# ---- PANTALLA DE TURNOS ----
elif menu == "📽️ Pantalla de Turnos":
    st.markdown("<h2>🎫 Turnos Pendientes</h2>", unsafe_allow_html=True)
    turnos_dict = leer_registro("turnos")
    turnos = pd.DataFrame.from_dict(turnos_dict, orient='index') if turnos_dict else pd.DataFrame()
    hoy = str(datetime.now().date())
    pendientes = turnos[(turnos["Estado"] == "Pendiente") & (turnos["Fecha"] == hoy)]

    col_general, col_preferencial = st.columns([1, 1])

    for cat_sigla, cat_title, container in [("G", "GENERAL", col_general), ("P", "PREFERENCIAL", col_preferencial)]:
        with container:
            st.markdown("<div class='dashboard-container'>", unsafe_allow_html=True)
            st.markdown(f"<div class='header-row'>{cat_title}</div>", unsafe_allow_html=True)
            cols_sub = st.columns(3)
            subcats = ["CT", "M", "CN"]
            for i, subcat in enumerate(subcats):
                with cols_sub[i]:
                    st.markdown(f"<div class='subcategoria-title'>{CODIGO_A_NOMBRE[subcat]}</div>", unsafe_allow_html=True)
                    sub_turnos = pendientes[(pendientes["CATEGORIA"] == cat_sigla) & (pendientes["SUBCAT"] == subcat)]
                    if sub_turnos.empty:
                        st.markdown(f"<div class='turno-box'>Sin turnos</div>", unsafe_allow_html=True)
                    else:
                        for _, row in sub_turnos.iterrows():
                            st.markdown(f"<div class='turno-box'>{row['Nro Turno']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
