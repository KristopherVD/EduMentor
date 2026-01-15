import sqlite3

DB_PATH = r"C:/Users/kvela/Documents/Ux/5to semestre/Agentes Inteligentes/3er Parcial/Examen/edumentor.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# --------------------------------------------------
# TABLA: intermediate_quiz
# --------------------------------------------------
c.execute("""
CREATE TABLE IF NOT EXISTS intermediate_quiz (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic INTEGER NOT NULL,
    score INTEGER DEFAULT 0,
    passed INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# --------------------------------------------------
# TABLA: quiz_questions
# --------------------------------------------------
c.execute("""
CREATE TABLE IF NOT EXISTS quiz_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    question_type TEXT NOT NULL,
    question TEXT NOT NULL,
    options TEXT,
    correct_answer TEXT NOT NULL,
    student_answer TEXT,
    is_correct INTEGER DEFAULT 0,
    points REAL DEFAULT 0,
    FOREIGN KEY (quiz_id) REFERENCES intermediate_quiz(id)
)
""")

conn.commit()
conn.close()

print("✅ Tablas intermediate_quiz y quiz_questions creadas correctamente")
