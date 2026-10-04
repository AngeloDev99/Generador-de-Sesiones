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
import time

# Configuración de Streamlit
st.set_page_config(page_title="Asistente MINEDU - Nivel Inicial", layout="wide")
st.title("Plataforma de Automatización Docente - Educación Inicial (MINEDU)")

# Inicialización de Client Gemini
try:
    # Lee la clave desde los secretos de Streamlit
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("⚠️ Error crítico: No se encontró la GEMINI_API_KEY en la configuración de secretos.")
    st.stop() # Detiene la ejecución si no hay clave

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
# app.py (Bloque completo de la Pestaña 2)
import time
from google.genai import errors

# app.py (Pestaña 2: Sesiones de Aprendizaje)
import time
from google.genai import errors

with tab2:
    st.header("2. Generación de Sesiones de Aprendizaje Diarias")
    
    # 1. Inicialización de estados en memoria
    if "proyecto_generado" not in st.session_state:
        st.session_state.proyecto_generado = None
    if "secuencia_dias" not in st.session_state:
        st.session_state.secuencia_dias = ""
    if "sesiones_generadas" not in st.session_state:
        st.session_state.sesiones_generadas = {}

    # 2. Gestión flexible del Proyecto de Aprendizaje (Memoria o Subida Manual)
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.subheader("📄 Paso 1: Proyecto de Aprendizaje")
        if st.session_state.proyecto_generado:
            st.success("✅ Proyecto activo detectado desde la Pestaña 1.")
            opcion_reemplazar = st.checkbox("Subir un archivo de proyecto diferente o respaldado (.docx/.pdf)")
        else:
            st.info("ℹ️ No hay un proyecto generado en memoria. Sube el archivo que descargaste anteriormente.")
            opcion_reemplazar = True

        if opcion_reemplazar:
            archivo_proyecto_subido = st.file_uploader(
                "Subir Proyecto de Aprendizaje descargado (.docx o .pdf):",
                type=["docx", "pdf"],
                key="uploader_proyecto_respaldo"
            )
            if archivo_proyecto_subido:
                # Extraemos el texto del archivo subido y lo guardamos en la sesión
                st.session_state.proyecto_generado = extract_text_from_file(archivo_proyecto_subido)
                st.success("✅ Proyecto cargado correctamente desde el archivo adjunto.")

    with col_der:
        st.subheader("📋 Paso 2: Formato / Modelo de Sesión")
        formato_sesion = st.file_uploader(
            "Adjuntar modelo/formato de referencia de Sesión (.docx o .pdf):", 
            type=["docx", "pdf"], 
            key="sesion_uploader"
        )

    st.markdown("---")

    # 3. Flujo de análisis y generación (Solo si ya tenemos el proyecto por cualquiera de las 2 vías)
    if not st.session_state.proyecto_generado:
        st.warning("⚠️ Debes contar con un Proyecto de Aprendizaje (generado en la Pestaña 1 o subido aquí arriba) para continuar.")
    else:
       # Inicialización del estado del widget si aún no existe
        if "input_dias_area" not in st.session_state:
            st.session_state["input_dias_area"] = ""

        # Botón para extraer la secuencia general de días
        if st.button("🔍 Analizar Secuencia General del Proyecto"):
            with st.spinner("Analizando la secuencia de días del proyecto..."):
                try:
                    prompt_ext = PROMPT_EXTRAER_SECUENCIA.format(
                        proyecto_contexto=st.session_state.proyecto_generado
                    )
                    res_secuencia = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=prompt_ext
                    )
                    
                    # Asignamos directamente al key del widget
                    texto_detectado = res_secuencia.text or ""
                    st.session_state["input_dias_area"] = texto_detectado
                    
                    st.success("¡Secuencia de días analizada con éxito!")
                    st.rerun()  # Recarga la vista para reflejar el texto de inmediato

                except errors.APIError as e:
                    st.error(f"Error de API (Código {e.code}): {e.message}")
                except Exception as e:
                    st.error(f"Error al analizar la secuencia: {str(e)}")

        # Campo visible de días (se enlaza automáticamente mediante su key)
        dias_input = st.text_area(
            "Días/Temas detectados para la generación de sesiones (puedes editarlos si deseas):", 
            height=180,
            key="input_dias_area"
        )

        st.markdown("---")

        # Botón para disparar la generación en lote
        if st.button("🚀 Generar Todas las Sesiones en Archivos Word (.docx)"):
            if not formato_sesion:
                st.warning("⚠️ Debe adjuntar el archivo de formato/modelo de la sesión en PDF o Word.")
            elif not dias_input or not dias_input.strip():
                st.warning("⚠️ Ingrese o analice los días antes de continuar.")
            else:
                lista_dias = [d.strip() for d in dias_input.split('\n') if d.strip()]
                texto_formato = extract_text_from_file(formato_sesion)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                st.session_state.sesiones_generadas = {}
                total_dias = len(lista_dias)

                for idx, dia in enumerate(lista_dias):
                    status_text.info(f"⏳ Generando sesión ({idx + 1}/{total_dias}): **{dia}**...")
                    prompt_sesion = PROMPT_SESION.format(
                        proyecto_contexto=st.session_state.proyecto_generado,
                        dia_tema=dia,
                        formato_referencia=texto_formato
                    )

                    max_reintentos = 3
                    espera_segundos = 10
                    sesion_exitosa = False

                    for intento in range(max_reintentos):
                        try:
                            res = client.models.generate_content(
                                model='gemini-3.8-flash',
                                contents=prompt_sesion
                            )
                            st.session_state.sesiones_generadas[dia] = res.text
                            sesion_exitosa = True
                            break
                        except errors.APIError as e:
                            if e.code == 429:
                                status_text.warning(
                                    f"Límite de cuota alcanzado en {dia}. Esperando {espera_segundos}s antes de reintentar (Intento {intento + 1}/{max_reintentos})..."
                                )
                                time.sleep(espera_segundos)
                                espera_segundos *= 2
                            else:
                                st.error(f"Error de API en {dia} (Código {e.code}): {e.message}")
                                break
                        except Exception as e:
                            st.error(f"Error inesperado en {dia}: {str(e)}")
                            break

                    if not sesion_exitosa:
                        st.error(f"❌ No se pudo completar la sesión para: {dia}. Se continuará con el siguiente día.")

                    progress_bar.progress((idx + 1) / total_dias)
                    time.sleep(4)

                status_text.success("🎉 Proceso finalizado. Revise las sesiones generadas abajo.")

        # Zona de descargas individuales en Word
        if st.session_state.get("sesiones_generadas"):
            st.subheader("📥 Descargar Sesiones de Aprendizaje")
            for dia, contenido in st.session_state.sesiones_generadas.items():
                buf = create_docx_from_text(contenido, f"Sesión de Aprendizaje: {dia}")
                nombre_archivo = f"Sesion_{dia.replace(':', '_').replace(' ', '_')}.docx"
                st.download_button(
                    label=f"📄 Descargar {dia} (.docx)",
                    data=buf,
                    file_name=nombre_archivo,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"btn_dl_{dia}"
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
                            model='gemini-3.6-flash',
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