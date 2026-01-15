import sqlite3

DB_PATH = r"C:/Users/kvela/Documents/Ux/5to semestre/Agentes Inteligentes/3er Parcial/Examen/edumentor.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabla existente (por seguridad)
    c.execute("""
        CREATE TABLE IF NOT EXISTS course_progress (
            user_id INTEGER PRIMARY KEY,
            current_topic INTEGER DEFAULT 1,
            last_output TEXT
        )
    """)

    # Nueva tabla: interacciones
    c.execute("""
        CREATE TABLE IF NOT EXISTS course_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic INTEGER NOT NULL,
            tutor_question TEXT NOT NULL,
            student_answer TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Nueva tabla: evaluaciones
    c.execute("""
        CREATE TABLE IF NOT EXISTS course_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER NOT NULL,
            score INTEGER,
            feedback TEXT,
            evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(interaction_id) REFERENCES course_interactions(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada / actualizada correctamente")

if __name__ == "__main__":
    init_db()
