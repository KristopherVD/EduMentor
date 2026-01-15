import sqlite3

DB_PATH = r"C:/Users/kvela/Documents/Ux/5to semestre/Agentes Inteligentes/3er Parcial/Examen/edumentor.db"

def update_db_step():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # ===============================
    # USUARIOS
    # ===============================
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    # ===============================
    # TEMAS DEL CURSO (niveles)
    # ===============================
    c.execute("""
        CREATE TABLE IF NOT EXISTS course_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_number INTEGER NOT NULL,
            title TEXT,
            content TEXT
        )
    """)

    # ===============================
    # PROGRESO DEL USUARIO
    # ===============================
    c.execute("""
        CREATE TABLE IF NOT EXISTS course_progress (
            user_id INTEGER PRIMARY KEY,
            current_topic INTEGER DEFAULT 1,
            last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # ===============================
    # INTERACCIONES (pregunta-respuesta)
    # ===============================
    c.execute("""
        CREATE TABLE IF NOT EXISTS course_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic INTEGER NOT NULL,
            tutor_question TEXT NOT NULL,
            student_answer TEXT,
            is_correct INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # ===============================
    # INTENTOS DEL ALUMNO
    # ===============================
    c.execute("""
        CREATE TABLE IF NOT EXISTS course_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER NOT NULL,
            attempt_text TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(interaction_id) REFERENCES course_interactions(id)
        )
    """)

    conn.commit()
    conn.close()

    print("✅ Paso #1 completado: Base de datos lista para curso por niveles")

if __name__ == "__main__":
    update_db_step()
