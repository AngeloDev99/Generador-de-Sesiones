# app.py
import os
import streamlit as st
from google import genai
from google.genai import types
from prompts import PROMPT_PROYECTO, PROMPT_SESION, PROMPT_FICHA
from utils.document_parser import extract_text_from_file
from utils.docx_generator import create_docx_from_text

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
                    model='gemini-2.5-flash',
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
with tab2:
    st.header("2. Generación de Sesiones Diarias")
    
    if not st.session_state.proyecto_generado:
        st.info("Primero debe generar un Proyecto de Aprendizaje en la pestaña 1.")
    else:
        formato_sesion = st.file_uploader("Adjuntar modelo/formato de Sesión (.pdf o .docx):", type=["pdf", "docx"], key="sesion_uploader")
        dias_input = st.text_area("Ingrese los temas o días del proyecto (uno por línea):", 
                                  "Día 1: Indagamos qué plantas hay en nuestro jardín\nDía 2: Clasificamos las hojas por su forma")
        
        if st.button("Generar Sesiones en Word"):
            if not client:
                st.error("Por favor, ingrese su API Key.")
            elif not formato_sesion:
                st.warning("Adjunte la plantilla de formato en PDF o Word.")
            else:
                lista_dias = [d.strip() for d in dias_input.split('\n') if d.strip()]
                texto_formato = extract_text_from_file(formato_sesion)
                
                progress_bar = st.progress(0)
                for idx, dia in enumerate(lista_dias):
                    st.write(f"Procesando: {dia}...")
                    prompt_sesion = PROMPT_SESION.format(
                        proyecto_contexto=st.session_state.proyecto_generado,
                        dia_tema=dia,
                        formato_referencia=texto_formato
                    )
                    
                    res = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_sesion
                    )
                    
                    st.session_state.sesiones_generadas[dia] = res.text
                    progress_bar.progress((idx + 1) / len(lista_dias))
                
                st.success("¡Todas las sesiones han sido generadas!")

        if st.session_state.sesiones_generadas:
            st.subheader("Descargar Sesiones por Día")
            for dia, contenido in st.session_state.sesiones_generadas.items():
                buf = create_docx_from_text(contenido, f"Sesión: {dia}")
                st.download_button(
                    label=f"Descargar {dia} (.docx)",
                    data=buf,
                    file_name=f"Sesion_{dia.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

# -------------------------------------------------------------------
# PESTAÑA 3: FICHAS DE TRABAJO (IMÁGENES ILUSTRADAS)
# -------------------------------------------------------------------
with tab3:
    st.header("3. Creación de Fichas de Trabajo para Colorear/Trazar")
    
    if not st.session_state.sesiones_generadas:
        st.info("Genere las sesiones en la pestaña 2 para crear las fichas de trabajo.")
    else:
        sesion_seleccionada = st.selectbox("Seleccione la Sesión:", list(st.session_state.sesiones_generadas.keys()))
        actividad_especifica = st.text_input("Instrucción o actividad para la ficha:", "Dibuja 3 hojas y traza el camino hacia la planta")
        
        if st.button("Generar Ficha de Trabajo (Imagen)"):
            if not client:
                st.error("Ingrese su API Key.")
            else:
                with st.spinner("Generando ilustración en blanco y negro para la ficha..."):
                    prompt_imagen = PROMPT_FICHA.format(
                        tema_sesion=sesion_seleccionada,
                        actividad_especifica=actividad_especifica
                    )
                    
                    # Llamada a Imagen 3 mediante la API de Google GenAI
                    result_img = client.models.generate_images(
                        model='imagen-3.0-generate-002',
                        prompt=prompt_imagen,
                        config=types.GenerateImagesConfig(
                            number_of_images=1,
                            aspect_ratio="3:4"
                        )
                    )
                    
                    for generated_image in result_img.generated_images:
                        st.image(generated_image.image.image_bytes, caption=f"Ficha: {sesion_seleccionada}")
                        st.download_button(
                            label="Descargar Ficha para Imprimir (PNG)",
                            data=generated_image.image.image_bytes,
                            file_name=f"Ficha_{sesion_seleccionada.replace(' ', '_')}.png",
                            mime="image/png"
                        )