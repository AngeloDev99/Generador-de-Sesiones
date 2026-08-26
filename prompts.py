# prompts.py

PROMPT_PROYECTO = """
Actúa como docente experta del nivel inicial y elabora un Proyecto de Aprendizaje completo y coherente dirigido a niños de 5 AÑOS, basándote en el Programa Curricular de Educación Inicial del MINEDU (2016).

Título del Proyecto: {titulo}
Duración: {duracion}

Toma como referencia la estructura del siguiente documento:
---
{contenido_referencia}
---

INSTRUCCIONES ESTRUCTURALES OBLIGATORIAS:
- Usa Markdown puro.
- Para las secciones I (DATOS INFORMATIVOS), III (PROPÓSITO DE APRENDIZAJE), IV (ENFOQUES TRANSVERSALES), V (INCORPORACIÓN DEL DUA), VI (PLANIFICACIÓN CON LOS NIÑOS), VII (SECUENCIA GENERAL DE DÍAS), VIII (DESARROLLO METODOLÓGICO) y IX (EVALUACIÓN FORMATIVA), DEBES GENERAR TABLAS MARKDOWN ESTRICTAS con encabezados y filas.
- Ejemplo de formato de tabla requerido:
| Encabezado 1 | Encabezado 2 |
| :--- | :--- |
| Dato 1 | Dato 2 |

No omitas ninguna sección y mantén un lenguaje amplio, pedagógico y sin resúmenes.
"""

# prompts.py

# Prompt para extraer la Secuencia General de días del Proyecto
PROMPT_EXTRAER_SECUENCIA = """
Analiza el siguiente Proyecto de Aprendizaje y extrae únicamente la lista de los días con sus respectivos temas/actividades según la Secuencia General.

Proyecto:
---
{proyecto_contexto}
---

INSTRUCCIONES DE SALIDA:
- Devuelve SOLO la lista de días y sus títulos o temas principales, uno por línea.
- Ejemplo de formato:
Día 1: Planificación del proyecto y mi silueta única
Día 2: Un vistazo al espejo: ¿Cómo soy por fuera?
Día 3: El motor de mi templo: Mi corazón y mis pulmones
"""

PROMPT_SESION = """
Actúa como una profesora experta del nivel inicial y genera una sesión de aprendizaje detallada para niños de 5 años, tomando como referencia el Programa Curricular de Educación Inicial del MINEDU (2016).

Contexto del Proyecto de Aprendizaje Adjunto:
---
{proyecto_contexto}
---

Día y Tema específico a desarrollar en esta sesión: {dia_tema}

Toma como MODELO EXACTO DE ESTRUCTURA Y PASOS METODOLÓGICOS por área el siguiente archivo de referencia:
---
{formato_referencia}
---

REQUISITOS ESTRUCTURALES Y PEDAGÓGICOS ESTRICTOS:
1. Utiliza Markdown puro.
2. Toda la información debe ser coherente, amplia y con las bases de la MINEDU. No hagas resúmenes ni inventes datos; la información debe ser completa.
3. MANTIENE LOS PASOS METODOLÓGICOS Y PROCESOS PEDAGÓGICOS EXACTOS (Inicio/Problematización, Propósito, Motivación, Saberes Previos; Desarrollo/Gestión y Acompañamiento, Procesos Didácticos del área; Cierre/Evaluación y Metacognición).
4. Genera TABLAS MARKDOWN ESTRICTAS (`| Columna | Columna |`) para los Datos Informativos, Propósitos de Aprendizaje, Evaluación Formativa y Materiales, tal como aparecen en el archivo de referencia.
"""

PROMPT_FICHA = """
Actúa como un ilustrador de material educativo infantil. Genera una ficha de trabajo interactiva en blanco y negro (dibujo de línea fina / line art), sin colores ni sombras, ideal para que niños de 5 años puedan colorear, trazar o dibujar.

Tema de la sesión: {tema_sesion}
Actividad recomendada: {actividad_especifica}

Estilo visual:
- Ilustración vectorial limpia, trazo negro sobre fondo blanco.
- Personajes y objetos animados infantiles con contornos gruesos y claros.
"""

