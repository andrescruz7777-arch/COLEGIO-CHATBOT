# ============================================
# 📚 CHATBOT EDUCATIVO – COLEGIO ABOGADOS COL
# ============================================

import streamlit as st
import pandas as pd
import hashlib, datetime, io, os
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from openai import OpenAI
import urllib.parse

# =============================
# ⚙️ CONFIGURACIÓN INICIAL
# =============================
st.set_page_config(page_title="🎓 Colegio Abogados Col", layout="centered")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# =============================
# 🎨 ESTILOS
# =============================
st.markdown("""
<style>
html, body, .stApp {
    background-color: #FFFFFF !important;
    color: #1B168C !important;
}
h1, h2, h3 { color:#1B168C !important; text-align:center; }
div.stButton > button {
    background-color:#1B168C !important;
    color:#FFFFFF !important;
    border:none !important;
    border-radius:12px !important;
    padding:10px 40px !important;
    font-weight:600 !important;
}
div.stButton > button:hover {
    background-color:#F43B63 !important;
    transform:scale(1.05);
}
input, textarea { color:#1B168C !important; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# =============================
# 🏫 CABECERA
# =============================
st.markdown("""
<div style='text-align:center;'>
    <img src='https://raw.githubusercontent.com/andrescruz7777-arch/CHATBOT-SERFINANZA/main/logo_serfinanza.png' width='180'/>
    <h1>🎓 Colegio Abogados Col</h1>
    <h4>Asistente Virtual Académico</h4>
</div>
""", unsafe_allow_html=True)

# =============================
# 🧭 MENÚ PRINCIPAL
# =============================
menu = st.sidebar.radio("Navegación", [
    "📊 Estado de Cartera",
    "📜 Certificados (Paz y Salvo)",
    "🧾 PQRS / Derecho de Petición",
    "💬 Atención al Cliente"
])

# =============================
# 🔒 FUNCIONES AUXILIARES
# =============================

def generar_codigo_seguro(documento: str) -> str:
    return hashlib.sha256(str(documento).encode('utf-8')).hexdigest()[:10].upper()

def generar_paz_y_salvo_pdf(data):
    """Genera un PDF desde los datos del estudiante"""
    nombre = data["NOMBRE_COMPLETO"]
    documento = data["DOCUMENTO"]
    curso = data["CURSO"]
    fecha_hoy = datetime.datetime.now()
    fecha_corta = fecha_hoy.strftime("%Y-%m-%d")
    fecha_larga = fecha_hoy.strftime("%d de %B de %Y")
    codigo = generar_codigo_seguro(documento)
    tesorera = "Lic. Carolina Suárez"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    contenido = []

    texto = f"""
    <para align=center><b>COLEGIO ABOGADOS COL</b><br/>
    Educación, Disciplina y Excelencia<br/><br/>
    <b>CERTIFICADO DE PAZ Y SALVO</b></para><br/><br/>
    La Tesorería del <b>Colegio Abogados Col</b>, identificado con NIT 900123456-7,
    certifica que el(la) estudiante <b>{nombre}</b>, identificado(a) con documento <b>{documento}</b>,
    perteneciente al curso <b>{curso}</b>, se encuentra <b>a paz y salvo</b> por todo concepto económico
    con la institución a la fecha <b>{fecha_corta}</b>.<br/><br/>
    Este certificado se expide a solicitud del interesado para los fines que estime convenientes.<br/><br/>
    <b>Código de verificación:</b> {codigo}<br/>
    Puede verificarse en línea o en la Secretaría del colegio.<br/><br/>
    Bogotá D.C., {fecha_larga}<br/><br/><br/>
    ________________________________<br/>
    {tesorera}<br/>
    Tesorería – Colegio Abogados Col
    """
    contenido.append(Paragraph(texto, styles["Normal"]))
    doc.build(contenido)
    buffer.seek(0)
    return buffer

# =============================
# 📊 ESTADO DE CARTERA
# =============================
if menu == "📊 Estado de Cartera":
    st.header("📊 Estado actual de cartera")
    try:
        df = pd.read_excel("base_cartera_colegio.xlsx", sheet_name="CARTERA_ESTUDIANTES")
    except Exception as e:
        st.error(f"No se pudo cargar la base: {e}")
        st.stop()

    docu = st.text_input("🪪 Ingrese el número de documento del estudiante:")
    if st.button("Consultar"):
        if not docu.strip():
            st.warning("Por favor ingrese un documento válido.")
            st.stop()

        data = df[df["DOCUMENTO"].astype(str) == docu.strip()]
        if data.empty:
            st.error("No se encontró información para este documento.")
        else:
            est = data.iloc[0].to_dict()
            nombre = est["NOMBRE_COMPLETO"]
            st.success(f"Estudiante: {nombre} ({est['CURSO']})")
            st.markdown("### Detalle de cartera:")
            st.dataframe(data[["MES","TOTAL_MENSUAL","ESTADO_PAGO","FECHA_PAGO","MEDIO_PAGO"]], use_container_width=True)

            if "PENDIENTE" in data["ESTADO_PAGO"].values:
                st.warning("El estudiante presenta pagos pendientes ⚠️")
                monto_total = data.loc[data["ESTADO_PAGO"]=="PENDIENTE","TOTAL_MENSUAL"].sum()
                codigo = generar_codigo_seguro(docu)
                ref = f"COL{datetime.datetime.now().strftime('%Y%m%d')}-001"
                pse_url = f"https://pse-demo.abogadoscol.edu.co/pay.html?code={codigo}&amount={monto_total}&name={urllib.parse.quote(nombre)}&ref={ref}"
                st.markdown(f"#### 💳 Total pendiente: ${monto_total:,.0f} COP")
                st.markdown(f"[🔗 Pagar ahora vía PSE simulado]({pse_url})", unsafe_allow_html=True)
            else:
                st.success("El estudiante está al día ✅")
                st.markdown("Puedes generar tu certificado en la pestaña **📜 Paz y Salvo**.")

# =============================
# 📜 CERTIFICADO DE PAZ Y SALVO
# =============================
elif menu == "📜 Certificados (Paz y Salvo)":
    st.header("📜 Generar Certificado de Paz y Salvo")
    df = pd.read_excel("base_cartera_colegio.xlsx", sheet_name="CARTERA_ESTUDIANTES")
    docu = st.text_input("🪪 Documento del estudiante para generar certificado:")

    if st.button("Generar Certificado"):
        data = df[df["DOCUMENTO"].astype(str) == docu.strip()]
        if data.empty:
            st.error("No se encontró información.")
        elif "PENDIENTE" in data["ESTADO_PAGO"].values:
            st.warning("No se puede generar certificado: el estudiante tiene pagos pendientes.")
        else:
            est = data.iloc[0].to_dict()
            pdf = generar_paz_y_salvo_pdf(est)
            st.success("✅ Certificado generado exitosamente.")
            st.download_button("⬇️ Descargar PDF",
                               data=pdf,
                               file_name=f"pazysalvo_{docu}.pdf",
                               mime="application/pdf")

# =============================
# 🧾 PQRS / DERECHO DE PETICIÓN
# =============================
elif menu == "🧾 PQRS / Derecho de Petición":
    st.header("🧾 Radicación de PQRS o Derecho de Petición")
    with st.form("form_pqrs"):
        documento = st.text_input("🪪 Documento del estudiante")
        nombre = st.text_input("👤 Nombre completo")
        curso = st.text_input("🏫 Curso")
        email = st.text_input("📧 Correo electrónico")
        telefono = st.text_input("📞 Teléfono de contacto")
        tipo = st.selectbox("Tipo de solicitud", ["Queja","Reclamo","Petición","Sugerencia","Felicitación"])
        asunto = st.text_input("📝 Asunto")
        detalle = st.text_area("📄 Descripción detallada")
        enviado = st.form_submit_button("📨 Radicar solicitud")

        if enviado:
            if not documento or not nombre or not asunto:
                st.warning("Por favor complete todos los campos obligatorios.")
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
                st.success(f"✅ Solicitud radicada exitosamente.\n\nNúmero de radicado: **{radicado}**")

# =============================
# 💬 CHAT INSTITUCIONAL
# =============================
elif menu == "💬 Atención al Cliente":
    st.header("💬 Asistente Académico Virtual")
    client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))

    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f"<div style='text-align:right; background:#F43B63; color:white; padding:8px; border-radius:12px; margin:5px;'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left; background:#FFFFFF; color:#1B168C; border:1.5px solid #1B168C; padding:8px; border-radius:12px; margin:5px;'>{msg['content']}</div>", unsafe_allow_html=True)

    prompt = st.chat_input("✍️ Escribe tu mensaje...")
    if prompt:
        st.session_state["chat_history"].append({"role":"user","content":prompt})
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"Eres un asistente académico del Colegio Abogados Col. Responde con amabilidad sobre pagos, certificados, trámites y horarios."},
                *st.session_state["chat_history"]
            ]
        )
        reply = response.choices[0].message.content
        st.session_state["chat_history"].append({"role":"assistant","content":reply})
        st.experimental_rerun()
