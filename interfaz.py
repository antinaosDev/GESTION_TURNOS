import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from io import BytesIO
import base64
import plotly.express as px
import variables

from servidor_fb import *
from clases import Receta


def pagina_principal():

    usr_id = variables.id_usr

    # Control básico de sesión
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = True  # Suponiendo que el usuario está "loggeado" por defecto, ajusta según tu lógica

    def cerrar_sesion():
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

    with st.sidebar:
        if st.session_state.logged_in:
            if st.button("🔒 Cerrar sesión"):
                cerrar_sesion()

    # Cargar imágenes
    logo_dev = Image.open("D:/DESARROLLO PROGRAMACION/STREAMLIT_PROJECTS/sistema_turnos/logo_alain.png")
    logo_app = Image.open("D:/DESARROLLO PROGRAMACION/STREAMLIT_PROJECTS/sistema_turnos/logo app farmacia.png")

    # Mostrar logo del desarrollador en el sidebar
    with st.sidebar:
        st.image(logo_dev, use_container_width=True)

    # Convertir logo_app a base64 para usarlo en HTML
    buffered = BytesIO()
    logo_app.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    # Mostrar logo a la izquierda y texto a la derecha, centrado verticalmente
    st.markdown(f"""
        <div style="
            display: flex; 
            align-items: center; 
            justify-content: space-between; 
            margin-top: 60px; 
            margin-bottom: 20px;
            max-width: 100%;
        ">
            <img src='data:image/png;base64,{img_base64}' style='max-width: 120px; height: auto;' />
            <h2 style='margin: 0; color: #006699; flex-grow: 1; text-align: center; font-weight: bold;'>
                Sistema de gestión de Turnos Medicamentos 🎫
            </h2>
        </div>
        <hr>
    """, unsafe_allow_html=True)





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


    def generar_nro_turno(categoria_sigla, subcat_codigo):
        turnos = leer_registro("turnos")
        hoy = datetime.now().date()
        contador = 0
        for turno in turnos.values():
            # Intentar parsear la fecha del turno a date
            fecha_turno_str = turno.get("Fecha")
            try:
                fecha_turno = datetime.strptime(fecha_turno_str, "%Y-%m-%d").date()
            except:
                continue  # si no puede parsear, lo ignora

            if (turno.get("CATEGORIA") == categoria_sigla and
                turno.get("SUBCAT") == subcat_codigo and
                fecha_turno == hoy):
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
    st.markdown("""
        <style>
            /* Reset márgenes y paddings excesivos */
            .block-container {
                padding-top: 0rem !important;
                padding-bottom: 1rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                max-width: 90% !important; -----------> aqui reajustar ancho
            }

            /* Elimina márgenes innecesarios en headers */
            h1, h2, h3 {
                margin-top: 0.5rem !important;
                margin-bottom: 0.5rem !important;
                color: #006699;
            }

            /* Ajuste en el contenedor del dashboard para evitar márgenes grandes */
            .dashboard-container {
                background-color: #dbe9f9;
                border-radius: 8px;
                padding: 10px !important;
                margin: 0 auto !important;
                max-width: 100% !important;
            }

            /* Ajusta los títulos de categorías y subcategorías con menos padding */
            .categoria-title {
                font-weight: bold;
                font-size: 1.3em;
                padding: 5px 0 !important;
                border-bottom: 2px solid #005b96;
                margin-bottom: 0.5rem !important;
            }

            .subcategoria-title {
                font-weight: 600;
                font-size: 1.1em;
                padding: 3px 0 !important;
                color: #004080;
                border-bottom: 1px solid #b0c4de;
                margin-bottom: 0.3rem !important;
            }

            /* Reduce margen y padding de las cajas de turno */
            .turno-box {
                background-color: #f0f6ff;
                margin: 5px 6px !important;
                padding: 8px !important;
                border-radius: 5px;
                text-align: center;
                font-weight: 700;
                font-size: 1.3em;
                color: #003366;
                box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
                max-width: 100%;
                box-sizing: border-box;
                white-space: normal;
            }

            /* Encabezado de sección */
            .header-row {
                background-color: #9bb9e1;
                font-weight: bold;
                font-size: 1.2em;
                text-align: center;
                padding: 8px 0 !important;
                border-radius: 6px 6px 0 0;
                margin-bottom: 0.5rem !important;
            }

        </style>
    """, unsafe_allow_html=True)





    menu = st.sidebar.radio("Menú", ["📋 Asignar Turno", "🗞️ Ver Turnos (Admin)", "📽️ Pantalla de Turnos", "📊 Dashboard"])


    with st.container():
        st.markdown('<div class="my-container">', unsafe_allow_html=True)

    # ---- SOLICITAR TURNO ----
    if menu == "📋 Asignar Turno":
        st.header("📌 Asignar un turno")

        with st.form("form_turno"):
            nombre = st.text_input("👤 Nombre completo")
            dni = st.text_input("🆔 RUT (sin puntos, con guion. Ej: 12345678-9)")
            categoria = st.selectbox("🏷️ Categoría", list(CATEGORIAS.keys()))
            subcat_nombre = st.selectbox("📄 Tipo de receta", list(SUBCATEGORIAS.keys()))
            enviar = st.form_submit_button("Asignar turno")

        if enviar:
            if nombre and dni and categoria and subcat_nombre:
                try:
                    rut_num, dv = dni.split('-')
                    cat_sigla = CATEGORIAS[categoria]
                    subcat_codigo = SUBCATEGORIAS[subcat_nombre]
                    nro_turno = generar_nro_turno(cat_sigla, subcat_codigo)
                    fecha = str(datetime.now().date())

                    receta = Receta(nombre, rut_num, dv, cat_sigla, subcat_codigo,usr_id)
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
        turnos_dict = leer_registro("turnos")
        turnos = pd.DataFrame.from_dict(turnos_dict, orient='index') if turnos_dict else pd.DataFrame()

        if turnos.empty:
            st.info("No hay turnos asignados aún.")
        else:
            st.subheader("✔️ Marcar turno como atendido")

            pendientes = turnos[(turnos["Estado"] == "Pendiente") & (turnos["Nro Turno"].notna())]
            if not pendientes.empty:
                turno_a_marcar = st.selectbox("Selecciona un Nº de Turno pendiente", pendientes["Nro Turno"].tolist(), key="marcar_turno")
                if st.button("Marcar como atendido"):
                    for id_turno, t in turnos_dict.items():
                        if t["Nro Turno"] == turno_a_marcar:
                            actualizar_registro("turnos", {"Estado": "Atendido"}, id_turno)
                            st.success(f"Turno {turno_a_marcar} marcado como atendido.")
                            st.rerun()
            else:
                st.info("No hay turnos pendientes para marcar como atendidos.")

            st.subheader("📄 Lista de Turnos Asignados")
            st.dataframe(turnos.sort_values(by=["Fecha", "Nro Turno"], ascending=[False, True]), use_container_width=True)

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
                    with st.expander(f"✏️ Editar/Eliminar turno {nro_seleccionado}", expanded=False):
                        with st.form("form_editar_turno"):
                            nuevo_nombre = st.text_input("Nombre", turno_data.get("NOMBRE", ""))
                            nuevo_rut = st.text_input("RUT", turno_data.get("RUT", ""))
                            nueva_categoria = st.selectbox(
                                "Categoría", 
                                list(CATEGORIAS.values()), 
                                index=list(CATEGORIAS.values()).index(turno_data.get("CATEGORIA", "G"))
                            )
                            nueva_subcat = st.selectbox(
                                "Subcategoría", 
                                list(SUBCATEGORIAS.values()), 
                                index=list(SUBCATEGORIAS.values()).index(turno_data.get("SUBCAT", "M"))
                            )
                            nuevo_estado = st.selectbox(
                                "Estado", 
                                ["Pendiente", "Atendido"], 
                                index=0 if turno_data.get("Estado") == "Pendiente" else 1
                            )
                            nueva_fecha = st.date_input(
                                "Fecha", 
                                datetime.strptime(turno_data.get("Fecha"), "%Y-%m-%d").date()
                            )

                            editar = st.form_submit_button("💾 Guardar cambios")
                            eliminar = st.form_submit_button("🗑️ Eliminar turno")

                        if editar:
                            actualizar_registro("turnos", {
                                "NOMBRE": nuevo_nombre,
                                "RUT": nuevo_rut,
                                "CATEGORIA": nueva_categoria,
                                "SUBCAT": nueva_subcat,
                                "Estado": nuevo_estado,
                                "Fecha": str(nueva_fecha),
                                "GENERADOR_TURNO":usr_id
                            }, id_encontrado)
                            st.success("✅ Turno actualizado correctamente.")
                            st.rerun()

                        if eliminar:
                            registro = leer_registro('turnos', id_encontrado)
                            if registro:
                                # Guardar el registro en "reg_eliminados"
                                ingresar_registro_bd("reg_eliminados", {'ID': id_encontrado, 'Registro': registro})
                                # Borrar el registro original
                                borrar_registro("turnos", id_encontrado)
                                st.warning(f"🗑️ Turno {nro_seleccionado} eliminado.")
                                st.rerun()
                            else:
                                st.error("No se encontró el registro para eliminar.")



    # ---- PANTALLA DE TURNOS ----
    elif menu == "📽️ Pantalla de Turnos":
        turnos_dict = leer_registro("turnos")

        if turnos_dict:
            # Filtrar registros que contengan las claves necesarias para evitar KeyErrors
            turnos_dict = {k: v for k, v in turnos_dict.items() if
                        "Estado" in v and "Fecha" in v and "CATEGORIA" in v and "SUBCAT" in v}
        else:
            turnos_dict = {}

        turnos = pd.DataFrame.from_dict(turnos_dict, orient='index') if turnos_dict else pd.DataFrame()

        hoy = str(datetime.now().date())

        if all(col in turnos.columns for col in ["Estado", "Fecha", "CATEGORIA", "SUBCAT"]):
            pendientes = turnos[(turnos["Estado"] == "Pendiente") & (turnos["Fecha"] == hoy)]
        else:
            pendientes = pd.DataFrame()  # DataFrame vacío si no existen las columnas

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
                        if not pendientes.empty:
                            sub_turnos = pendientes[(pendientes["CATEGORIA"] == cat_sigla) & (pendientes["SUBCAT"] == subcat)]
                        else:
                            sub_turnos = pd.DataFrame()
                        if sub_turnos.empty:
                            st.markdown(f"<div class='turno-box'>Sin turnos</div>", unsafe_allow_html=True)
                        else:
                            for _, row in sub_turnos.iterrows():
                                st.markdown(f"<div class='turno-box'>{row['Nro Turno']}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)



    elif menu == "📊 Dashboard":
        st.header("📊 Dashboard Estadístico de Turnos")
        
        turnos_dict = leer_registro("turnos")
        if not turnos_dict:
            st.info("No hay datos disponibles para mostrar.")
        else:
            turnos = pd.DataFrame.from_dict(turnos_dict, orient='index')

            # Convertir columnas relevantes a tipo categórico o fechas si aplica
            if "Fecha" in turnos.columns:
                turnos["Fecha"] = pd.to_datetime(turnos["Fecha"], errors='coerce')

            st.markdown("---")

            # --- Estadísticas generales ---
            total_turnos = len(turnos)
            turnos_pendientes = len(turnos[turnos["Estado"] == "Pendiente"])
            turnos_atendidos = len(turnos[turnos["Estado"] == "Atendido"])

            col1, col2, col3 = st.columns(3)
            col1.metric("🗂 Total de Turnos", total_turnos)
            col2.metric("⏳ Turnos Pendientes", turnos_pendientes)
            col3.metric("✅ Turnos Atendidos", turnos_atendidos)

            st.markdown("---")

            # --- Gráficos interactivos ---
            # 1) Turnos por Categoría
            categoria_counts = turnos["CATEGORIA"].value_counts().reset_index()
            categoria_counts.columns = ["Categoría", "Cantidad"]
            fig_cat = px.pie(categoria_counts, values='Cantidad', names='Categoría',
                            title='Distribución por Categoría',
                            color_discrete_sequence=px.colors.qualitative.Set2)
            
            # 2) Turnos por Subcategoría
            subcat_counts = turnos["SUBCAT"].value_counts().reset_index()
            subcat_counts.columns = ["Subcategoría", "Cantidad"]
            fig_subcat = px.bar(subcat_counts, x="Subcategoría", y="Cantidad", text="Cantidad",
                                title='Turnos por Subcategoría',
                                color="Subcategoría",
                                color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_subcat.update_traces(textposition='outside')
            fig_subcat.update_layout(yaxis=dict(title='Cantidad'), xaxis=dict(title='Subcategoría'), showlegend=False)

            # 3) Turnos por Estado
            estado_counts = turnos["Estado"].value_counts().reset_index()
            estado_counts.columns = ["Estado", "Cantidad"]
            fig_estado = px.bar(estado_counts, x="Estado", y="Cantidad", text="Cantidad",
                                title='Turnos por Estado',
                                color="Estado",
                                color_discrete_sequence=['#FFA07A', '#90EE90'])
            fig_estado.update_traces(textposition='outside')
            fig_estado.update_layout(yaxis=dict(title='Cantidad'), xaxis=dict(title='Estado'), showlegend=False)

            # 4) Turnos por Fecha (línea)
            if "Fecha" in turnos.columns:
                fecha_counts = turnos.groupby(turnos["Fecha"].dt.date).size().reset_index(name='Cantidad')
                fig_fecha = px.line(fecha_counts, x="Fecha", y="Cantidad",
                                title='Turnos por Fecha',
                                markers=True,
                                line_shape='spline',
                                color_discrete_sequence=['#6495ED'])
                fig_fecha.update_layout(xaxis_title='Fecha', yaxis_title='Cantidad de turnos')

            # --- Mostrar gráficos ---
            st.plotly_chart(fig_cat, use_container_width=True)

            col4, col5 = st.columns(2)
            col4.plotly_chart(fig_subcat, use_container_width=True)
            col5.plotly_chart(fig_estado, use_container_width=True)

            if "Fecha" in turnos.columns:
                st.plotly_chart(fig_fecha, use_container_width=True)

            st.markdown("---")

            # --- Botón para exportar Excel ---
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Turnos')
                processed_data = output.getvalue()
                return processed_data

            excel_data = to_excel(turnos)

            st.download_button(
                label="📥 Descargar Base de Datos en Excel",
                data=excel_data,
                file_name="base_datos_turnos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )



    # --- FOOTER CON INFORMACIÓN DE CONTACTO ---
    st.markdown("""
        <hr style="margin-top: 2em; margin-bottom: 1em; border: none; height: 1px; background: #ccc;" />

        <div style='text-align: center; color: #888888; font-size: 14px; padding-bottom: 20px;'>
            💼 Aplicación desarrollada por <strong>AAS</strong> <br>
            🌐 Más información en: <a href="https://alain-antinao-s.notion.site/Alain-C-sar-Antinao-Sep-lveda-1d20a081d9a980ca9d43e283a278053e" target="_blank" style="color: #4A90E2;">Mi Sitio Web</a>
        </div>
    """, unsafe_allow_html=True)
