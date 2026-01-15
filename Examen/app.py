from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from models.ingestion import extract_text
from models.agent.tutor_agent import (
    get_or_create_current_content,
    submit_student_answer,
    generate_intermediate_quiz
)
import os
import markdown
import json


app = Flask(__name__)

DB_PATH = r"C:/Users/kvela/Documents/Ux/5to semestre/Agentes Inteligentes/3er Parcial/Examen/edumentor.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_connection():
    return sqlite3.connect(DB_PATH)


# ---------------------------------------------------
#  PÁGINA MENÚ PRINCIPAL
# ---------------------------------------------------
@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, profile_pic FROM users")
    users = cursor.fetchall()
    conn.close()

    return render_template("index.html", users=users)


# ---------------------------------------------------
#  SUBIR DOCUMENTOS
# ---------------------------------------------------
@app.route("/upload_documents/<int:user_id>", methods=["GET", "POST"])
def upload_documents(user_id):
    if request.method == "POST":
        files = request.files.getlist("docs")

        if len(files) == 0:
            return "Debes subir al menos un archivo."

        user_folder = f"static/user_docs/{user_id}"
        os.makedirs(user_folder, exist_ok=True)

        collected_text = ""

        # 1. Guardar archivos y extraer texto real
        for f in files:
            save_path = os.path.join(user_folder, f.filename)
            f.save(save_path)
            collected_text += extract_text(save_path) + "\n\n"

        # Guardar texto base en BD
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE users SET stored_text=?, has_course=1 WHERE id=?",
            (collected_text, user_id)
        )
        conn.commit()
        conn.close()

        return redirect(f"/enter_pin/{user_id}")

    return render_template("upload_documents.html", user_id=user_id)


# ---------------------------------------------------
#  SUBIR ARCHIVOS POR USUARIO
# ---------------------------------------------------
@app.route("/upload/<int:user_id>", methods=["GET", "POST"])
def upload(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM users")
    users = cursor.fetchall()

    if request.method == "POST":
        uploaded_files = request.files.getlist("files")

        if len(uploaded_files) == 0:
            return "No se seleccionaron archivos."

        if len(uploaded_files) > 5:
            return "Máximo 5 archivos permitidos."

        uploads_dir = os.path.join(BASE_DIR, "uploads", str(user_id))
        os.makedirs(uploads_dir, exist_ok=True)

        for file in uploaded_files:
            if file.filename:
                file.save(os.path.join(uploads_dir, file.filename))

        return "Archivos subidos correctamente."

    return render_template("upload.html", users=users, user_id=user_id)


# ---------------------------------------------------
#  RUTA PARA SUBIR DOCUMENTOS
# ---------------------------------------------------
@app.route("/upload_docs/<int:user_id>", methods=["GET", "POST"])
def upload_docs(user_id):
    if request.method == "POST":
        files = request.files.getlist("files")

        user_folder = f"static/user_docs/{user_id}"
        os.makedirs(user_folder, exist_ok=True)

        collected_text = ""

        for f in files:
            save_path = os.path.join(user_folder, f.filename)
            f.save(save_path)

            collected_text += extract_text(save_path) + "\n\n"

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET stored_text=? WHERE id=?", (collected_text, user_id))
        conn.commit()
        conn.close()

        return redirect(f"/generate_course/{user_id}")

    return render_template("upload_docs.html", user_id=user_id)


# ---------------------------------------------------
#  RUTA QUE PIDE INGRESAR PIN PARA ACCEDER AL CURSO
# ---------------------------------------------------
@app.route("/enter_pin/<int:user_id>", methods=["GET", "POST"])
def enter_pin(user_id):

    if request.method == "POST":
        pin = request.form["pin"]

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT pin FROM users WHERE id=?", (user_id,))
        row = c.fetchone()

        if not row:
            conn.close()
            return "Usuario no encontrado."

        if pin == row[0]:
            conn.close()
            return redirect(f"/course/{user_id}")
        else:
            conn.close()
            return render_template("enter_pin.html", user_id=user_id, error="PIN incorrecto")

    return render_template("enter_pin.html", user_id=user_id)


# ---------------------------------------------------
#  CREAR NUEVO USUARIO (nombre e imagen opcionales)
# ---------------------------------------------------
@app.route("/new_user", methods=["GET", "POST"])
def new_user():
    if request.method == "POST":
        name = request.form.get("name")
        file = request.files.get("profile_pic")

        conn = get_connection()
        cursor = conn.cursor()

        # obtener número de usuarios actuales
        cursor.execute("SELECT COUNT(*) FROM users")
        current_count = cursor.fetchone()[0]

        # Si no escribió nombre, generar "Usuario X"
        if not name or name.strip() == "":
            name = f"Usuario {current_count + 1}"

        # Manejo de foto de perfil
        filename = "default.png"
        if file and file.filename != "":
            uploads_dir = os.path.join(BASE_DIR, "static", "profile_pics")
            os.makedirs(uploads_dir, exist_ok=True)

            filename = file.filename
            file.save(os.path.join(uploads_dir, filename))

        cursor.execute(
            "INSERT INTO users (name, profile_pic) VALUES (?, ?)",
            (name, filename)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("new_user.html")


# ---------------------------------------------------
#  CREAR USUARIO (solo nombre)
# ---------------------------------------------------
@app.route("/create_user", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        name = request.form.get("name")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users(name, profile_pic) VALUES (?, ?)", (name, "default.png"))
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("create_user.html")


# ---------------------------------------------------
#  SELECCIONAR UN USUARIO → IR A UPLOAD
# ---------------------------------------------------
@app.route("/select_user/<int:user_id>")
def select_user(user_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT has_course FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return "Usuario no encontrado"

    has_course = row[0]

    if has_course == 0:
        return redirect(f"/upload_documents/{user_id}")
    else:
        return redirect(f"/enter_pin/{user_id}")


# ---------------------------------------------------
#  OTRA RUTA (NOMBRE DIFERENTE PARA EVITAR ERROR)
# ---------------------------------------------------
@app.route("/select/<int:user_id>")
def select_message(user_id):
    return f"Usuario {user_id} seleccionado correctamente."


# ---------------------------------------------------
@app.route("/add_user")
def add_user():
    return "Aquí irá el formulario de nuevo usuario."


# ---------------------------------------------------
#  RUTA PARA EDITAR USUARIOS
# ---------------------------------------------------
@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = c.fetchone()

    if not user:
        conn.close()
        return "Usuario no existe."

    if request.method == "POST":
        new_name = request.form.get("name")
        photo = request.files.get("photo")

        # Cambiar nombre
        if new_name:
            c.execute("UPDATE users SET name=? WHERE id=?", (new_name, user_id))

        # Cambiar foto
        if photo and photo.filename != "":
            uploads_dir = os.path.join("static/profile_pics")
            os.makedirs(uploads_dir, exist_ok=True)

            filename = f"user_{user_id}.jpg"
            photo.save(os.path.join(uploads_dir, filename))

            c.execute("UPDATE users SET profile_pic=? WHERE id=?", (filename, user_id))

        conn.commit()
        conn.close()
        return redirect("/")

    conn.close()
    return render_template("edit_user.html", user=user)


# ---------------------------------------------------
#  RUTA PARA ELIMINAR USUARIOS CON PIN
# ---------------------------------------------------
@app.route("/delete_user/<int:user_id>", methods=["GET", "POST"])
def delete_user(user_id):
    conn = get_connection()
    c = conn.cursor()

    # Obtener datos del usuario ANTES de borrar
    c.execute("SELECT name, pin FROM users WHERE id=?", (user_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return "El usuario no existe."

    user_name, real_pin = row
    is_auto_generated = user_name.startswith("Usuario ")

    if request.method == "POST":
        pin = request.form["pin"]

        if pin != real_pin:
            conn.close()
            return render_template(
                "delete_user.html",
                user_id=user_id,
                error="PIN incorrecto"
            )

        # 1) Borrar usuario
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()

        # 2) SOLO renumerar si EL ELIMINADO era auto-generado
        if is_auto_generated:
            c.execute("SELECT id, name FROM users ORDER BY id ASC")
            all_users = c.fetchall()

            auto_count = 1
            for uid, uname in all_users:
                if uname.startswith("Usuario "):
                    new_name = f"Usuario {auto_count}"
                    c.execute("UPDATE users SET name=? WHERE id=?", (new_name, uid))
                    auto_count += 1

            conn.commit()

        conn.close()
        return redirect("/")

    # --- GET: mostrar pantalla ---
    return render_template("delete_user.html", user_id=user_id, user=(user_id, user_name))

 
# ---------------------------------------------------
#  RUTA PARA RENUMERAS USUARIOS
# ---------------------------------------------------
def reorder_users():
    conn = sqlite3.connect("database.db", timeout=10, check_same_thread=False)
    c = conn.cursor()

    # Traer usuarios ordenados por id
    c.execute("SELECT id FROM users ORDER BY id")
    users = c.fetchall()

    # Renombrar a Usuario 1, Usuario 2, ...
    position = 1
    for u in users:
        new_name = f"Usuario {position}"
        c.execute("UPDATE users SET name=? WHERE id=?", (new_name, u[0]))
        position += 1

    conn.commit()
    conn.close()


# ---------------------------------------------------
#  RUTA PARA ENTRAR AL CURSO
# ---------------------------------------------------
@app.route("/course/<int:user_id>")
def course(user_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT current_content, stored_text FROM users WHERE id=?",
        (user_id,)
    )
    row = c.fetchone()
    conn.close()

    current_content, stored_text = row

    # SOLO generar si NO hay contenido
    if not current_content:
        content = get_or_create_current_content(
            user_id=user_id,
            documents_text=stored_text
        )
    else:
        content = current_content

    import re

    def normalize_markdown(text: str) -> str:
        import re

        # 1. Asegurar saltos antes de listas
        text = re.sub(r'([^\n])\n\* ', r'\1\n\n* ', text)

        # 2. Quitar comillas rotas antes de bullets
        text = text.replace('"* ', '* ')

        # 3. Corregir fórmulas con \text{} SIN delimitadores
        text = re.sub(
            r'(\\text\{.*?\}.*?= .*?)(?=\n|$)',
            r'$\1$',
            text
        )

        # ⭐ 3.5 Corregir ecuaciones matemáticas "puras" por línea
        text = re.sub(
            r'(?m)^(?!\s*[\*\-\d])([A-Za-z\\][^$\n]*?=.*?)$',
            r'$$\1$$',
            text
        )

        # 4. Asegurar separación de fórmulas inline
        text = re.sub(r'(\$[^\$]+\$)', r' \1 ', text)

        # 5. Asegurar saltos antes de títulos
        text = re.sub(r'([^\n])\n(## )', r'\1\n\n\2', text)

        return text

    clean_content = normalize_markdown(content)

    html_content = markdown.markdown(
        clean_content,
        extensions=[
            "tables",
            "fenced_code",
            "nl2br",
            "sane_lists"
        ],
        output_format="html5"
    )



    return render_template(
        "course.html",
        content=html_content,
        user_id=user_id
    )


# ---------------------------------------------------
#  RUTA PARA ENVIAR RESPUESTA ABIERTA
# ---------------------------------------------------
@app.route("/submit_answer/<int:user_id>", methods=["POST"])
def submit_answer_route(user_id):
    student_answer = request.form["answer"]

    submit_student_answer(
        user_id=user_id,
        answer=student_answer
    )

    conn = get_connection()
    c = conn.cursor()

    # Obtener tema actual
    c.execute(
        "SELECT current_topic FROM course_progress WHERE user_id=?",
        (user_id,)
    )
    topic = c.fetchone()[0]

    # Obtener texto base
    c.execute(
        "SELECT stored_text FROM users WHERE id=?",
        (user_id,)
    )
    documents_text = c.fetchone()[0]

    conn.close()

    # ✅ GENERAR QUIZ Y OBTENER quiz_id
    quiz_id = generate_intermediate_quiz(
        user_id=user_id,
        topic=topic,
        documents_text=documents_text
    )

    # ✅ REDIRECT CORRECTO
    return redirect(f"/quiz/{quiz_id}")



# ---------------------------------------------------
#  RUTA PARA MOSTRAR QUIZ INTERMEDIO
# ---------------------------------------------------
@app.route("/quiz/<int:quiz_id>")
def show_intermediate_quiz(quiz_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT id, question_type, question, options
        FROM quiz_questions
        WHERE quiz_id = ?
        ORDER BY id
    """, (quiz_id,))

    rows = c.fetchall()
    conn.close()

    questions = []

    for row in rows:
        q_id, q_type, q_text, q_options = row

        # Decodificar opciones SOLO si existen
        if q_options:
            try:
                q_options = json.loads(q_options)
            except json.JSONDecodeError:
                q_options = []
        else:
            q_options = []

        questions.append({
            "id": q_id,
            "type": q_type,
            "question": q_text,
            "options": q_options
        })

    return render_template(
        "quiz.html",
        quiz_id=quiz_id,
        questions=questions
    )


# ---------------------------------------------------
#  RUTA PARA ENVIAR RESPUESTAS
# ---------------------------------------------------
@app.route("/submit_quiz/<int:quiz_id>", methods=["POST"])
def submit_quiz(quiz_id):
    answers = dict(request.form)

    from models.agent.tutor_agent import submit_intermediate_quiz

    passed, score = submit_intermediate_quiz(quiz_id, answers)

    conn = get_connection()
    c = conn.cursor()

    # Obtener user_id
    c.execute(
        "SELECT user_id FROM intermediate_quiz WHERE id=?",
        (quiz_id,)
    )
    user_id = c.fetchone()[0]

    # Obtener preguntas evaluadas
    c.execute("""
        SELECT question, question_type, options,
               student_answer, correct_answer,
               is_correct, feedback
        FROM quiz_questions
        WHERE quiz_id=?
        ORDER BY id
    """, (quiz_id,))

    questions = []
    for row in c.fetchall():
        q, t, opt, stud, corr, ok, fb = row
        questions.append({
            "question": q,
            "type": t,
            "options": json.loads(opt) if opt else [],
            "student": stud,
            "correct": corr,
            "is_correct": ok,
            "feedback": fb
        })

    conn.close()

    return render_template(
        "quiz_result.html",
        questions=questions,
        score=score,
        passed=passed,
        user_id=user_id
    )


# ---------------------------------------------------
#  MAIN DEL SCRIPT
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
    