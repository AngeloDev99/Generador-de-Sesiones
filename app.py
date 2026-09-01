# app.py
import os
import streamlit as st
from google import genai
from google.genai import types
from prompts import PROMPT_PROYECTO, PROMPT_SESION, PROMPT_FICHA
from utils.document_parser import extract_text_from_file
from utils.docx_generator import create_docx_from_text
from prompts import PROMPT_PROYECTO, PROMPT_EXTRAER_SECUENCIA, PROMPT_SESION, PROMPT_FICHA
from google.genai import errors

# Configuración de Streamlit
st.set_page_config(page_title="Asistente MINEDU - Nivel Inicial", layout="wide")
st.title("Plataforma de Automatización Docente - Educación Inicial (MINEDU)")

# Inicialización de Client Gemini
api_key = st.sidebar.text_input("Ingrese Gemini API Key:", type="password")
client = genai.Client(api_key=api_key) if api_key else None

# Estado global de la sesión
if "proyecto_generado" not in st.session_state:
    st.session_state.proyecto_generado = None
if "sesiones_generadas" not in st.session_state:
    st.session_state.sesiones_generadas = {}

tab1, tab2, tab3 = st.tabs([
    "1. Creación de Proyecto", 
    "2. Creación de Sesiones", 
    "3. Fichas de Trabajo"
])

# -------------------------------------------------------------------
# PESTAÑA 1: PROYECTO DE APRENDIZAJE
# -------------------------------------------------------------------
with tab1:
    st.header("1. Elaboración del Proyecto de Aprendizaje")
    
    col1, col2 = st.columns(2)
    with col1:
        titulo = st.text_input("Título del Proyecto:", "Descubriendo los seres vivos de nuestro entorno")
        duracion = st.text_input("Duración (ej. 2 semanas / 10 días):", "2 semanas")
        archivo_referencia = st.file_uploader("Adjuntar archivo de estructura de referencia (.docx o .pdf):", type=["docx", "pdf"])

    if st.button("Generar Proyecto de Aprendizaje"):
        if not client:
            st.error("Por favor, ingrese su API Key de Google GenAI.")
        elif not archivo_referencia:
            st.warning("Adjunte un archivo de referencia para mantener la estructura requerida.")
        else:
            with st.spinner("Generando Proyecto de Aprendizaje según especificaciones del MINEDU..."):
                texto_ref = extract_text_from_file(archivo_referencia)
                prompt_final = PROMPT_PROYECTO.format(
                    titulo=titulo,
                    duracion=duracion,
                    contenido_referencia=texto_ref
                )
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt_final,
                )
                
                st.session_state.proyecto_generado = response.text
                st.success("¡Proyecto generado exitosamente!")

    if st.session_state.proyecto_generado:
        st.subheader("Proyecto Generado")
        st.text_area("Vista previa:", st.session_state.proyecto_generado, height=300)
        
        docx_buffer = create_docx_from_text(st.session_state.proyecto_generado, f"Proyecto: {titulo}")
        st.download_button(
            label="Descargar Proyecto en Word (.docx)",
            data=docx_buffer,
            file_name=f"Proyecto_{titulo.replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# -------------------------------------------------------------------
# PESTAÑA 2: SESIONES DE APRENDIZAJE
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# PESTAÑA 2: SESIONES DE APRENDIZAJE
# -------------------------------------------------------------------
with tab2:
    st.header("2. Generación de Sesiones de Aprendizaje Diarias")
    
    # Verificación de que el proyecto ya fue generado en la Pestaña 1
    if not st.session_state.proyecto_generado:
        st.info("📌 Primero debes generar un Proyecto de Aprendizaje en la Pestaña 1.")
    else:
        st.success("✅ Proyecto de Aprendizaje detectado correctamente.")
        
        # Subida del modelo/formato de Sesión (Word o PDF)
        formato_sesion = st.file_uploader(
            "Adjuntar modelo/formato de referencia de Sesión de Aprendizaje (.docx o .pdf):", 
            type=["docx", "pdf"], 
            key="sesion_uploader"
        )
        
        # Botón para extraer la secuencia general automáticamente
        if st.button("🔍 Analizar Secuencia General del Proyecto"):
            if not client:
                st.error("Por favor, ingrese su API Key de Google GenAI en la barra lateral.")
            else:
                with st.spinner("Analizando la secuencia de días del proyecto..."):
                    try:
                        prompt_ext = PROMPT_EXTRAER_SECUENCIA.format(
                            proyecto_contexto=st.session_state.proyecto_generado
                        )
                        res_secuencia = client.models.generate_content(
                            model='gemini-3.6-flash',
                            contents=prompt_ext
                        )
                        st.session_state.secuencia_dias = res_secuencia.text
                        st.success("¡Secuencia de días analizada con éxito!")
                    except errors.APIError as e:
                        st.error(f"Error de API (Código {e.code}): {e.message}")
                    except Exception as e:
                        st.error(f"Error al analizar la secuencia: {str(e)}")

        # Mostrar y permitir editar la secuencia detectada si existe
        secuencia_texto = st.session_state.get("secuencia_dias", "")
        dias_input = st.text_area(
            "Días/Temas detectados para la generación de sesiones (puedes editarlos si deseas):", 
            value=secuencia_texto, 
            height=200
        )

        st.markdown("---")

        # Generación masiva de sesiones en formato .docx
        if st.button("🚀 Generar Todas las Sesiones en Archivos Word (.docx)"):
            if not client:
                st.error("Por favor, ingrese su API Key.")
            elif not formato_sesion:
                st.warning("⚠️ Debe adjuntar el archivo de formato/modelo de la sesión en PDF o Word.")
            elif not dias_input.strip():
                st.warning("⚠️ No se han detectado días. Haga clic en 'Analizar Secuencia General' o ingrese los días manualmente.")
            else:
                lista_dias = [d.strip() for d in dias_input.split('\n') if d.strip()]
                texto_formato = extract_text_from_file(formato_sesion)
                
                progress_bar = st.progress(0)
                st.session_state.sesiones_generadas = {}
                
                for idx, dia in enumerate(lista_dias):
                    st.write(f"⏳ Generando sesión para: **{dia}**...")
                    prompt_sesion = PROMPT_SESION.format(
                        proyecto_contexto=st.session_state.proyecto_generado,
                        dia_tema=dia,
                        formato_referencia=texto_formato
                    )
                    
                    try:
                        res = client.models.generate_content(
                            model='gemini-3.6-flash',
                            contents=prompt_sesion
                        )
                        st.session_state.sesiones_generadas[dia] = res.text
                    except errors.APIError as e:
                        st.error(f"Error generando {dia} (Código {e.code}): {e.message}")
                    except Exception as e:
                        st.error(f"Error en {dia}: {str(e)}")
                        
                    progress_bar.progress((idx + 1) / len(lista_dias))
                
                st.success("🎉 ¡Todas las sesiones de aprendizaje han sido generadas!")

        # Zona de descarga individual de archivos .docx por día
        if st.session_state.get("sesiones_generadas"):
            st.subheader("📥 Descargar Sesiones de Aprendizaje")
            st.caption("Cada archivo incluye el formato exacto con tablas, pasos metodológicos y procesos pedagógicos.")
            
            for dia, contenido in st.session_state.sesiones_generadas.items():
                buf = create_docx_from_text(contenido, f"Sesión de Aprendizaje: {dia}")
                
                # Formatear el nombre del archivo descargable
                nombre_archivo = f"Sesion_{dia.replace(':', '_').replace(' ', '_')}.docx"
                
                st.download_button(
                    label=f"📄 Descargar {dia} (.docx)",
                    data=buf,
                    file_name=nombre_archivo,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"btn_{dia}"
                )

# -------------------------------------------------------------------
# PESTAÑA 3: FICHAS DE TRABAJO (IMÁGENES ILUSTRADAS)
# -------------------------------------------------------------------
import base64
import requests

# PESTAÑA 3: FICHAS DE TRABAJO (IMÁGENES ILUSTRADAS)
with tab3:
    st.header("3. Creación de Fichas de Trabajo para Colorear/Trazar")
    
    if not st.session_state.get("sesiones_generadas"):
        st.info("📌 Genere las sesiones en la Pestaña 2 para crear las fichas de trabajo.")
    else:
        sesion_seleccionada = st.selectbox(
            "Seleccione la Sesión:", 
            list(st.session_state.sesiones_generadas.keys())
        )
        actividad_especifica = st.text_input(
            "Instrucción o actividad para la ficha:", 
            "Dibuja y colorea los elementos mencionados en la sesión"
        )
        
        if st.button("Generar Ficha de Trabajo (Imagen)"):
            if not api_key:
                st.error("Por favor, ingrese su API Key en la barra lateral.")
            else:
                with st.spinner("Generando ilustración en blanco y negro para la ficha..."):
                    prompt_imagen = PROMPT_FICHA.format(
                        tema_sesion=sesion_seleccionada,
                        actividad_especifica=actividad_especifica
                    )
                    
                    # Endpoint oficial de Imagen 3 REST API
                    url = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict"
                    
                    headers = {
                        "Content-Type": "application/json",
                        "x-goog-api-key": api_key.strip()  # Header de autenticación obligatorio
                    }
                    
                    payload = {
                        "instances": [
                            {"prompt": prompt_imagen}
                        ],
                        "parameters": {
                            "sampleCount": 1,
                            "aspectRatio": "3:4"
                        }
                    }
                    
                    try:
                        response = requests.post(url, json=payload, headers=headers)
                        res_data = response.json()
                        
                        if response.status_code == 200 and "predictions" in res_data:
                            b64_image = res_data["predictions"][0]["bytesBase64Encoded"]
                            image_bytes = base64.b64decode(b64_image)
                            
                            st.image(image_bytes, caption=f"Ficha de Trabajo: {sesion_seleccionada}")
                            
                            # Formatear el nombre del archivo limpiando caracteres especiales
                            nombre_img = f"Ficha_{sesion_seleccionada.replace(':', '_').replace(' ', '_')}.png"
                            
                            st.download_button(
                                label="Descargar Ficha para Imprimir (PNG)",
                                data=image_bytes,
                                file_name=nombre_img,
                                mime="image/png"
                            )
                        else:
                            mensaje_error = res_data.get("error", {}).get("message", response.text)
                            st.error(f"Error de la API (Código {response.status_code}): {mensaje_error}")
                            
                    except Exception as e:
                        st.error(f"Error inesperado al generar la imagen: {str(e)}")