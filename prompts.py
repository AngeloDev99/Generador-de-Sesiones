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

# prompts.py

PROMPT_SESION = """
Actúa como una profesora experta del nivel inicial y elabora una sesión de aprendizaje completa, detallada y contextualizada para niños de 5 años, fundamentada en el Programa Curricular de Educación Inicial del MINEDU (2016).

Contexto del Proyecto de Aprendizaje:
---
{proyecto_contexto}
---

Día y Tema específico a desarrollar: {dia_tema}

Formato y Estructura de referencia obligatoria:
---
{formato_referencia}
---

ENFOQUE INCLUSIVO Y ATENCIÓN A LA DIVERSIDAD (SÍNDROME DE DOWN):
En el aula se encuentra matriculada una niña de 5 años con necesidades educativas especiales asociadas a discapacidad intelectual (Síndrome de Down). Debes integrar de manera transversal y explícita las siguientes adaptaciones en la sesión:
1. Principios DUA:
   - Múltiples formas de implicación: motivación multisensorial, refuerzo positivo tangible y trabajo cooperativo con pares de apoyo.
   - Múltiples formas de representación: uso de material concreto estructurado, pictogramas de alta visibilidad, modelado directo y consignas verbales breves y directas.
   - Múltiples formas de acción y expresión: permitir respuestas mediante manipulación física, señalamiento, gestos, láminas ilustradas o verbalizaciones según su ritmo de desarrollo.
2. Procesos Pedagógicos y Didácticos:
   - En cada momento de la sesión (Inicio, Desarrollo y Cierre), detalla las acciones pedagógicas generales para el grupo y añade las orientaciones y ajustes razonables específicos para el acompañamiento y mediación con la estudiante.
3. Evaluación Formativa Diferenciada:
   - Plantea criterios de evaluación e instrumentos (ej. escala de valoración o lista de cotejo) adaptados a su nivel de logro y progreso individual, evitando la exclusión de las actividades grupales.

REQUISITOS ESTRUCTURALES Y DE FORMATO:
- Genera la respuesta en Markdown puro.
- Para los Datos Informativos, Propósitos de Aprendizaje, Criterios de Evaluación, Ajustes DUA / Adaptaciones Curriculares y Secuencia Metodológica, utiliza estrictamente tablas Markdown (| Columna | Columna |) para asegurar su conversión a formato de tabla nativa en Word.
- Información completa, sin resúmenes, con lenguaje técnico-pedagógico propio del MINEDU.
"""

PROMPT_FICHA = """
Actúa como un ilustrador de material educativo infantil. Genera una ficha de trabajo interactiva en blanco y negro (dibujo de línea fina / line art), sin colores ni sombras, ideal para que niños de 5 años puedan colorear, trazar o dibujar.

Tema de la sesión: {tema_sesion}
Actividad recomendada: {actividad_especifica}

Estilo visual:
- Ilustración vectorial limpia, trazo negro sobre fondo blanco.
- Personajes y objetos animados infantiles con contornos gruesos y claros.
"""

