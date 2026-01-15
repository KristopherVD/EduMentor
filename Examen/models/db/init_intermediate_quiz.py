import sqlite3

DB_PATH = r"C:/Users/kvela/Documents/Ux/5to semestre/Agentes Inteligentes/3er Parcial/Examen/edumentor.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Tabla del quiz intermedio
c.execute("""
CREATE TABLE IF NOT EXISTS intermediate_quiz (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    topic INTEGER,
    score INTEGER DEFAULT 0,
    max_score INTEGER DEFAULT 10,
    passed INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Tabla de preguntas del quiz
c.execute("""
CREATE TABLE IF NOT EXISTS quiz_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER,
    question_type TEXT,
    question TEXT,
    options TEXT,
    correct_answer TEXT,
    points INTEGER,
    student_answer TEXT,
    is_correct INTEGER
)
""")

conn.commit()
conn.close()

print("✅ Tablas intermediate_quiz y quiz_questions creadas correctamente")
