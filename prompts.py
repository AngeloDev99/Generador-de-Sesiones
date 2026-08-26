# prompts.py

PROMPT_PROYECTO = """
Actúa como docente experta del nivel inicial y elabora un Proyecto de Aprendizaje completo y coherente dirigido a niños de 5 AÑOS, basándote en el Programa Curricular de Educación Inicial del MINEDU (2016).

Título del Proyecto: {titulo}
Duración: {duracion}

Toma como referencia estricta la estructura y contenido del documento adjunto:
---
{contenido_referencia}
---

Instrucciones adicionales:
- Genera la propuesta completa sin omitir áreas, competencias ni desempeños.
- Adapta las actividades exactamente a la duración de {duracion}.
- Incluye la planificación del cronograma de actividades por cada día.
"""

PROMPT_SESION = """
Actúa como una profesora experta del nivel inicial y genera una sesión de aprendizaje detallada para niños de 5 años del nivel inicial, tomando como referencia el Programa Curricular de Educación Inicial del MINEDU (2016).

Contexto del Proyecto:
---
{proyecto_contexto}
---

Día/Tema de la Sesión: {dia_tema}

Toma como modelo exacto de formato y pasos metodológicos por área el siguiente archivo de referencia:
---
{formato_referencia}
---

Requisitos estrictos:
- Proporciona información coherente, amplia y sin resúmenes.
- Mantén los procesos pedagógicos (Problematización, Propósito y Organización, Motivación, Saberes Previos, Gestión y Acompañamiento, Evaluación) y los procesos didácticos específicos del área.
"""

PROMPT_FICHA = """
Actúa como un ilustrador de material educativo infantil. Genera una ficha de trabajo interactiva en blanco y negro (dibujo de línea fina / line art), sin colores ni sombras, ideal para que niños de 5 años puedan colorear, trazar o dibujar.

Tema de la sesión: {tema_sesion}
Actividad recomendada: {actividad_especifica}

Estilo visual:
- Ilustración vectorial limpia, trazo negro sobre fondo blanco.
- Personajes y objetos animados infantiles con contornos gruesos y claros.
"""