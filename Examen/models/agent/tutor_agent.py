import sqlite3
import os
import time
import json
from google import genai
from google.genai.errors import ClientError

# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================

DB_PATH = r"C:/Users/kvela/Documents/Ux/5to semestre/Agentes Inteligentes/3er Parcial/Examen/edumentor.db"

MODEL_NAME = "models/gemini-flash-latest"

# Cliente Gemini
client = genai.Client(
    api_key=os.getenv("AIzaSyBAZHfgeaQlogMuwfRJhi_45GQD7OFeGwQ")
)

# ======================================================
# UTILIDAD: asegurar tabla de progreso
# ======================================================

def ensure_course_table(conn):
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS course_progress (
            user_id INTEGER PRIMARY KEY,
            current_topic INTEGER DEFAULT 1,
            last_output TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

# ======================================================
# FUNCIÓN PRINCIPAL DEL AGENTE
# ======================================================
    
def save_student_interaction(user_id, topic, tutor_question, student_answer=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT INTO course_interactions (
            user_id,
            topic,
            tutor_question,
            student_answer
        )
        VALUES (?, ?, ?, ?)
    """, (user_id, topic, tutor_question, student_answer))

    conn.commit()
    conn.close()

# ======================================================
# FUNCIÓN GENERAR PREGUNTA INICIAL Y EXPLICACIÓN
# ======================================================
def generate_topic_and_question(user_id, documents_text=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    ensure_course_table(conn)

    # Obtener o crear progreso del usuario
    c.execute(
        "SELECT current_topic FROM course_progress WHERE user_id = ?",
        (user_id,)
    )
    row = c.fetchone()

    if row:
        current_topic = row[0]
    else:
        current_topic = 1
        c.execute(
            "INSERT INTO course_progress (user_id, current_topic) VALUES (?, ?)",
            (user_id, current_topic)
        )
        conn.commit()

    prompt = f"""
Eres un tutor académico.

Explica el Tema {current_topic} de forma clara y estructurada.

REGLAS IMPORTANTES:
- TODA expresión matemática debe ir entre $...$ o $$...$$
- Usa \\text{{}} SOLO dentro de fórmulas LaTeX
- No escribas fórmulas fuera de delimitadores

Después de la explicación, formula UNA pregunta abierta
para comprobar la comprensión del estudiante.

Formato obligatorio:
## Explicación
(texto)

## Pregunta
(pregunta clara y directa)
"""

    if documents_text:
        prompt += f"\nMaterial base del curso:\n{documents_text}\n"

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    content = response.text

    # Guardar interacción (pregunta sin respuesta)
    c.execute("""
        INSERT INTO course_interactions (
            user_id,
            topic,
            tutor_question
        ) VALUES (?, ?, ?)
    """, (user_id, current_topic, content))

    conn.commit()
    conn.close()

    return content

# ======================================================
# FUNCIÓN PARA EVALÚAR USUARIO (FACIL)
# ======================================================
def submit_student_answer(user_id, answer):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT id, topic, tutor_question
        FROM course_interactions
        WHERE user_id = ?
        AND student_answer IS NULL
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return "⚠️ No hay ninguna pregunta pendiente."

    interaction_id, topic, tutor_question = row

    # Guardar respuesta
    c.execute("""
        UPDATE course_interactions
        SET student_answer = ?
        WHERE id = ?
    """, (answer, interaction_id))

    # Evaluar (SOLO feedback, NO decide avance)
    evaluation = evaluate_student_answer(
        interaction_id,
        tutor_question,
        answer
    )

    c.execute("""
        INSERT INTO course_evaluations (
            interaction_id,
            feedback
        ) VALUES (?, ?)
    """, (interaction_id, evaluation))

    # ❌ NO avanzar tema aquí
    # ❌ NO limpiar contenido
    # 👉 El avance ahora SOLO lo controla el quiz

    conn.commit()
    conn.close()

    return evaluation


# ======================================================
# FUNCIÓN PARA OBTENER O GENERAR CONTENIDO
# ======================================================
def get_or_create_current_content(user_id, documents_text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Ver si ya hay contenido actual
    c.execute(
        "SELECT current_content FROM users WHERE id = ?",
        (user_id,)
    )
    row = c.fetchone()

    if row and row[0]:
        conn.close()
        return row[0]

    # Si NO hay contenido, generarlo
    content = generate_topic_and_question(
        user_id=user_id,
        documents_text=documents_text
    )

    # Guardarlo como contenido actual
    c.execute(
        "UPDATE users SET current_content = ? WHERE id = ?",
        (content, user_id)
    )

    conn.commit()
    conn.close()

    return content


# ======================================================
# FUNCIÓN PARA AVUALUAR LAS RESPUESTAS DEL ESTUDIANTE
# ======================================================
def evaluate_student_answer(interaction_id, tutor_question, student_answer):
    prompt = f"""
Eres un tutor académico.

Pregunta original:
{tutor_question}

Respuesta del estudiante:
{student_answer}

Evalúa la respuesta considerando:
- Comprensión conceptual
- Claridad
- Corrección general

Devuelve EXCLUSIVAMENTE en este formato:

Score: <número del 0 al 100>
Feedback:
(texto breve y constructivo)
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text

def safe_json_from_gemini(prompt, retries=2):
    for i in range(retries):
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        raw = response.text.strip()

        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(raw)
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(1)


# ======================================================
# FUNCIÓN PARA GENERAR QUIZ INTERMEDIO
# ======================================================
def generate_intermediate_quiz(user_id, topic, documents_text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Crear quiz
    c.execute("""
        INSERT INTO intermediate_quiz (user_id, topic)
        VALUES (?, ?)
    """, (user_id, topic))
    quiz_id = c.lastrowid

    prompt = f"""
Genera un quiz educativo sobre el Tema {topic}.

Reglas:
- 4 preguntas de opción múltiple (6 puntos total)
- 2 preguntas de verdadero o falso (2 puntos total)
- 1 pregunta abierta corta (2 puntos)

IMPORTANTE:
- Para preguntas abiertas usa "correct": "open"

Devuelve EXCLUSIVAMENTE en formato JSON con esta estructura:

[
  {{
    "type": "multiple_choice",
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "correct": "A",
    "points": 1.5
  }},
  {{
    "type": "true_false",
    "question": "...",
    "correct": "true",
    "points": 1
  }},
  {{
    "type": "open",
    "question": "...",
    "correct": "open",
    "points": 2
  }}
]

Material base:
{documents_text}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    raw = response.text.strip()

    # ❌ Gemini devolvió nada
    if not raw:
        conn.close()
        raise ValueError("Gemini devolvió respuesta vacía al generar el quiz")

    # 🔧 Quitar ```json ``` si vienen
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        questions = json.loads(raw)
    except json.JSONDecodeError as e:
        conn.close()
        raise ValueError(
            f"JSON inválido generado por Gemini:\n{raw}"
        ) from e

    
    try:
        questions = json.loads(response.text)
    except json.JSONDecodeError:
        conn.close()
        raise ValueError("Error al generar quiz: JSON inválido")

    for q in questions:
        c.execute("""
            INSERT INTO quiz_questions (
                quiz_id,
                question_type,
                question,
                options,
                correct_answer,
                points
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            quiz_id,
            q["type"],
            q["question"],
            json.dumps(q.get("options")),
            q["correct"],
            q["points"]
        ))

    conn.commit()
    conn.close()

    return quiz_id


# ======================================================
# FUNCIÓN PARA EVALUAR QUIZ INTERMEDIO Y AVANZAR
# ======================================================
def submit_intermediate_quiz(quiz_id, answers):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    total_score = 0

    for question_id, student_answer in answers.items():
        c.execute("""
            SELECT question, correct_answer, points
            FROM quiz_questions
            WHERE id = ?
        """, (question_id,))
        question_text, correct, points = c.fetchone()

        feedback = None
        is_correct = 0

        # --------------------------------------------------
        # PREGUNTA ABIERTA
        # --------------------------------------------------
        if correct.lower() == "open":
            prompt = f"""
    Eres un tutor académico.

    Pregunta:
    {question_text}

    Respuesta del estudiante:
    {student_answer}

    Evalúa si la respuesta es correcta.

    Devuelve EXCLUSIVAMENTE en este formato:
    Correct: true/false
    Feedback:
    (texto breve)
    """
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            text = response.text.lower()
            is_correct = 1 if "correct: true" in text else 0
            feedback = response.text

            if is_correct:
                total_score += points

        # --------------------------------------------------
        # PREGUNTAS CERRADAS
        # --------------------------------------------------
        else:
            is_correct = int(
                student_answer.strip().lower() ==
                correct.strip().lower()
            )
            if is_correct:
                total_score += points

        # Guardar resultado
        c.execute("""
            UPDATE quiz_questions
            SET student_answer = ?,
                is_correct = ?,
                feedback = ?
            WHERE id = ?
        """, (student_answer, is_correct, feedback, question_id))

    passed = int(total_score >= 7)

    # Guardar resultado del quiz
    c.execute("""
        UPDATE intermediate_quiz
        SET score = ?, passed = ?
        WHERE id = ?
    """, (int(total_score), passed, quiz_id))

    # --------------------------------------------------
    # LÓGICA DE AVANCE / BLOQUEO
    # --------------------------------------------------
    # Obtener usuario y tema del quiz
    c.execute("""
        SELECT user_id, topic
        FROM intermediate_quiz
        WHERE id = ?
    """, (quiz_id,))
    user_id, topic = c.fetchone()

    if passed:
        # AVANZAR AL SIGUIENTE TEMA
        c.execute("""
            UPDATE course_progress
            SET current_topic = current_topic + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (user_id,))

    else:
        # REFORZAR MISMO TEMA (no avanzar)
        c.execute("""
            UPDATE course_progress
            SET updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (user_id,))

    # Limpiar contenido para forzar regeneración
    c.execute("""
        UPDATE users
        SET current_content = NULL
        WHERE id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

    return passed, int(total_score)
