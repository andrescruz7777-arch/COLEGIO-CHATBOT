# ==================================================
# 🎓 CHATBOT EDUCATIVO – COLEGIO ABOGADOS COL (Dark)
# ==================================================
import streamlit as st
import pandas as pd
import hashlib, datetime, io, os, urllib.parse
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# =============================
# ⚙️ CONFIGURACIÓN INICIAL
# =============================
st.set_page_config(page_title="🎓 Colegio Abogados Col", layout="centered")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# =============================
# 🎨 ESTILOS MODO OSCURO
# =============================
st.markdown("""
<style>
html, body, .stApp {
    background-color: #000000 !important;
    color: #FFFFFF !important;
}
h1, h2, h3, h4, h5, h6, p, label, div, span {
    color: #FFFFFF !important;
}
div.stButton > button {
    background-color:#1A237E !important;
    color:#FFFFFF !important;
    border:none !important;
    border-radius:10px !important;
    padding:12px 40px !important;
    font-weight:600 !important;
    box-shadow:0 3px 10px rgba(212,175,55,.4);
}
div.stButton > button:hover {
    background-color:#D4AF37 !important;
    color:#000000 !important;
    transform:scale(1.05);
}
.sidebar .sidebar-content {
    background-color:#111111 !important;
}
.stDataFrame, .stTextInput, .stSelectbox, .stTextArea {
    color:#FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

# =============================
# 🏫 CABECERA
# =============================
st.markdown("""
<div style='text-align:center;'>
    <img src="https://raw.githubusercontent.com/andrescruz7777-arch/colegio-chatbot/main/logo_colegio.png" width="160">
    <h1 style="color:#D4AF37;">Colegio Abogados Col</h1>
    <h4 style="color:#FFFFFF;">Excelencia, Ética y Conocimiento</h4>
</div>
""", unsafe_allow_html=True)

# =============================
# 🧭 MENÚ
# =============================
menu = st.sidebar.radio("Navegación", [
    "📊 Estado de Cartera",
    "📜 Certificados (Paz y Salvo)",
    "🧾 PQRS / Derecho de Petición",
    "💬 Atención al Cliente"
])

# =============================
# 🔒 FUNCIONES
# =============================
def generar_codigo_seguro(documento: str) -> str:
    return hashlib.sha256(str(documento).encode('utf-8')).hexdigest()[:10].upper()

def generar_paz_y_salvo_pdf(data):
    """Genera PDF con fondo oscuro y sello institucional"""
    nombre = data["NOMBRE_COMPLETO"]
    documento = data["DOCUMENTO"]
    curso = data["CURSO"]
    fecha = datetime.datetime.now().strftime("%d de %B de %Y")
    codigo = generar_codigo_seguro(documento)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=12, textColor=colors.white, leading=18)
    titulo = ParagraphStyle('Titulo', parent=styles['Title'], fontSize=20, textColor=colors.HexColor("#D4AF37"))

    contenido = []
    try:
        logo = Image("logo_colegio.png", width=1.5*inch, height=1.5*inch)
        logo.hAlign = 'CENTER'
        contenido.append(logo)
    except:
        pass

    contenido += [
        Spacer(1, 0.2*inch),
        Paragraph("COLEGIO ABOGADOS COL", titulo),
        Paragraph("CERTIFICADO DE PAZ Y SALVO", styles["Heading2"]),
        Spacer(1, 0.3*inch)
    ]

    texto = (
        f"Se certifica que el(la) estudiante {nombre}, identificado(a) con documento {documento}, "
        f"perteneciente al curso {curso}, se encuentra a paz y salvo por todo concepto económico "
        f"con la institución educativa al día {fecha}.\n\n"
        "Código de verificación: " + codigo +
        "\n\n______________________________\n"
        "Lic. Carolina Suárez\n"
        "Tesorería – Colegio Abogados Col"
    )

    contenido.append(Paragraph(texto, normal))
    doc.build(contenido)
    buffer.seek(0)
    return buffer

# =============================
# 📊 ESTADO DE CARTERA
# =============================
if menu == "📊 Estado de Cartera":
    st.header("📊 Estado actual de cartera")
    try:
        df = pd.read_excel("base_cartera_colegio.xlsx", engine="openpyxl")
    except Exception as e:
        st.error(f"No se pudo cargar la base: {e}")
        st.stop()

    docu = st.text_input("🪪 Ingrese el número de documento del estudiante:")
    if st.button("Consultar"):
        if not docu.strip():
            st.warning("Ingrese un documento válido.")
            st.stop()
        data = df[df["DOCUMENTO"].astype(str) == docu.strip()]
        if data.empty:
            st.error("No se encontró información.")
        else:
            est = data.iloc[0].to_dict()
            nombre = est["NOMBRE_COMPLETO"]
            st.success(f"Estudiante: {nombre} ({est['CURSO']})")
            st.dataframe(data[["MES","TOTAL_MENSUAL","ESTADO_PAGO","FECHA_PAGO","MEDIO_PAGO"]],
                         use_container_width=True)
            if "PENDIENTE" in data["ESTADO_PAGO"].values:
                monto_total = data.loc[data["ESTADO_PAGO"]=="PENDIENTE","TOTAL_MENSUAL"].sum()
                codigo = generar_codigo_seguro(docu)
                pse_url = f"https://pse-demo.abogadoscol.edu.co/pay.html?code={codigo}&amount={monto_total}&name={urllib.parse.quote(nombre)}"
                st.markdown(f"#### 💳 Total pendiente: ${monto_total:,.0f} COP")
                st.markdown(f"[🔗 Pagar ahora vía PSE simulado]({pse_url})", unsafe_allow_html=True)
            else:
                st.success("El estudiante está al día ✅")

# =============================
# 📜 CERTIFICADOS
# =============================
elif menu == "📜 Certificados (Paz y Salvo)":
    st.header("📜 Generar Certificado de Paz y Salvo")
    try:
        df = pd.read_excel("base_cartera_colegio.xlsx", engine="openpyxl")
    except Exception as e:
        st.error(f"No se pudo cargar la base: {e}")
        st.stop()

    docu = st.text_input("🪪 Documento del estudiante para generar certificado:")
    if st.button("Generar Certificado"):
        data = df[df["DOCUMENTO"].astype(str) == docu.strip()]
        if data.empty:
            st.error("No se encontró información.")
        elif "PENDIENTE" in data["ESTADO_PAGO"].values:
            st.warning("No se puede generar certificado: pagos pendientes.")
        else:
            est = data.iloc[0].to_dict()
            pdf = generar_paz_y_salvo_pdf(est)
            st.success("✅ Certificado generado exitosamente.")
            st.download_button("⬇️ Descargar PDF",
                               data=pdf,
                               file_name=f"pazysalvo_{docu}.pdf",
                               mime="application/pdf")

# =============================
# 🧾 PQRS
# =============================
elif menu == "🧾 PQRS / Derecho de Petición":
    st.header("🧾 Radicación de PQRS o Derecho de Petición")
    with st.form("form_pqrs"):
        documento = st.text_input("🪪 Documento")
        nombre = st.text_input("👤 Nombre completo")
        curso = st.text_input("🏫 Curso")
        email = st.text_input("📧 Correo")
        telefono = st.text_input("📞 Teléfono")
        tipo = st.selectbox("Tipo", ["Queja","Reclamo","Petición","Sugerencia","Felicitación"])
        asunto = st.text_input("📝 Asunto")
        detalle = st.text_area("📄 Descripción detallada")
        enviado = st.form_submit_button("📨 Radicar solicitud")

        if enviado:
            if not documento or not nombre or not asunto:
                st.warning("Complete todos los campos obligatorios.")
            else:
                codigo = generar_codigo_seguro(documento)
                radicado = f"RAD-{datetime.datetime.now().strftime('%Y%m%d')}-{codigo}"
                fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                df_log = pd.DataFrame([{
                    "FechaHora": fecha, "Radicado": radicado, "Documento": documento,
                    "Nombre": nombre, "Curso": curso, "Email": email, "Telefono": telefono,
                    "Tipo": tipo, "Asunto": asunto, "Detalle": detalle, "Estado": "Recibido"
                }])
                log_file = "logs_pqrs.xlsx"
                if os.path.exists(log_file):
                    old = pd.read_excel(log_file)
                    df_log = pd.concat([old, df_log], ignore_index=True)
                df_log.to_excel(log_file, index=False)
                st.success(f"✅ Solicitud radicada.\n\nNúmero de radicado: **{radicado}**")

# =============================
# 💬 ATENCIÓN AL CLIENTE (CHAT CON CONSULTA REAL)
# =============================
elif menu == "💬 Atención al Cliente":
    st.header("💬 Asistente Académico Virtual")

    import requests, json

    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ Falta configurar la clave de OpenAI en Secrets.")
        st.stop()

    # Cargar base de datos
    try:
        df_cartera = pd.read_excel("base_cartera_colegio.xlsx", engine="openpyxl")
    except Exception as e:
        st.warning(f"No se pudo cargar la base de cartera: {e}")
        df_cartera = pd.DataFrame()

    # Encabezado del asistente
    st.markdown("""
    <div style='display:flex; align-items:center; gap:10px; margin-bottom:15px;'>
        <img src="https://cdn-icons-png.flaticon.com/512/4712/4712100.png" width="60">
        <div>
            <div style='font-size:1.3em; font-weight:700; color:#D4AF37;'>🤖 Chris Académico</div>
            <div style='color:#BBBBBB; font-size:0.9em;'>Colegio Abogados Col – Consultas y pagos</div>
        </div>
    </div>
    <hr style='border:1px solid #D4AF37;'>
    """, unsafe_allow_html=True)

    # Mostrar historial
    for msg in st.session_state["chat_history"]:
        color_user = "#D4AF37" if msg["role"] == "user" else "#111"
        text_color = "#000" if msg["role"] == "user" else "#FFF"
        border = "" if msg["role"] == "user" else "border:1.5px solid #D4AF37;"
        align = "right" if msg["role"] == "user" else "left"
        st.markdown(
            f"""
            <div style='text-align:{align}; background:{color_user}; color:{text_color};
                        {border} padding:10px 15px; border-radius:15px; margin:8px 0;
                        display:inline-block; max-width:80%; float:{align};'>
                {msg["content"]}
            </div>
            <div style='clear:both;'></div>
            """,
            unsafe_allow_html=True
        )

    # Chat input
    prompt = st.chat_input("✍️ Escribe tu mensaje o pregunta...")
    if prompt:
        st.session_state["chat_history"].append({"role": "user", "content": prompt})

        # Detectar documento y consulta de pagos
        respuesta_datos = ""
        palabras_clave = ["cuánto debo", "saldo", "pendiente", "meses", "deuda", "pago", "pensiones", "cartera"]

        if any(palabra in prompt.lower() for palabra in palabras_clave):
            doc_match = [s for s in prompt.split() if s.isdigit()]
            if doc_match:
                docu = doc_match[0]
                if not df_cartera.empty:
                    datos = df_cartera[df_cartera["DOCUMENTO"].astype(str) == docu]
                    if not datos.empty:
                        nombre = datos["NOMBRE_COMPLETO"].iloc[0]
                        total_pend = datos.loc[datos["ESTADO_PAGO"] == "PENDIENTE", "TOTAL_MENSUAL"].sum()
                        meses_pend = ", ".join(datos.loc[datos["ESTADO_PAGO"] == "PENDIENTE", "MES"])
                        if total_pend > 0:
                            respuesta_datos = (
                                f"📘 Estudiante {nombre} ({docu}) tiene un saldo pendiente de "
                                f"${total_pend:,.0f} correspondiente a los meses {meses_pend}."
                                "\nPuedes realizar tu pago en línea ingresando al módulo de cartera."
                            )
                        else:
                            respuesta_datos = f"✅ Estudiante {nombre} ({docu}) está al día en sus pagos."
                    else:
                        respuesta_datos = "No se encontró ese número de documento en la base."
                else:
                    respuesta_datos = "No se pudo consultar la base de datos en este momento."

        # Consultar IA de OpenAI
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        mensajes = [
            {"role": "system", "content": (
                "Eres Chris, asistente académico del Colegio Abogados Col. "
                "Responde amablemente y de forma profesional sobre pagos, certificados, PQRS y clases. "
                "Si el sistema adjunta información contable, intégrala en tu respuesta."
            )},
            *st.session_state["chat_history"]
        ]

        if respuesta_datos:
            mensajes.append({"role": "system", "content": respuesta_datos})

        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps({"model": "gpt-4o-mini", "messages": mensajes}),
            timeout=30
        )

        if resp.status_code == 200:
            reply = resp.json()["choices"][0]["message"]["content"]
            st.session_state["chat_history"].append({"role": "assistant", "content": reply})
            st.rerun()
        else:
            st.error(f"⚠️ Error al contactar la IA: {resp.status_code} – {resp.text}")
