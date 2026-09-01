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
import streamlit as st

# PESTAÑA 3: FICHAS DE TRABAJO (IMÁGENES ILUSTRADAS)
# PESTAÑA 3: FICHAS DE TRABAJO (GENERACIÓN SVG VÍA GEMINI)
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
        
        if st.button("Generar Ficha de Trabajo (SVG)"):
            if not client:
                st.error("Por favor, ingrese su API Key en la barra lateral.")
            else:
                with st.spinner("Generando ficha vectorial en blanco y negro..."):
                    prompt_svg = f"""
                    Actúa como un diseñador de material educativo infantil.
                    Crea un código SVG completo y válido para una ficha de trabajo interactiva de nivel inicial (5 años).
                    
                    Tema de la sesión: {sesion_seleccionada}
                    Actividad: {actividad_especifica}
                    
                    REQUISITOS DEL SVG:
                    - Estilo: Dibujo en blanco y negro, contornos negros gruesos (stroke='black', stroke-width='2' u '8'), fondo blanco (fill='none' o fill='white').
                    - Apto para colorear y trazar por niños de 5 años.
                    - Incluye título de la actividad y espacio superior para el Nombre del niño.
                    - Devuelve ÚNICAMENTE el código SVG dentro de un bloque de código markdown (```xml ... ```). Sin texto adicional.
                    """
                    
                    try:
                        res = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt_svg
                        )
                        
                        svg_code = res.text
                        if "```xml" in svg_code:
                            svg_code = svg_code.split("```xml")[1].split("```")[0].strip()
                        elif "```svg" in svg_code:
                            svg_code = svg_code.split("```svg")[1].split("```")[0].strip()
                        elif "```" in svg_code:
                            svg_code = svg_code.split("```")[1].split("```")[0].strip()
                            
                        # Mostrar el gráfico en Streamlit
                        st.image(svg_code, caption=f"Ficha: {sesion_seleccionada}")
                        
                        # Descarga en formato SVG
                        st.download_button(
                            label="Descargar Ficha en Formato Vectorial (.svg)",
                            data=svg_code,
                            file_name=f"Ficha_{sesion_seleccionada.replace(':', '_').replace(' ', '_')}.svg",
                            mime="image/svg+xml"
                        )
                    except Exception as e:
                        st.error(f"Error al generar la ficha: {str(e)}")