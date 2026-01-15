import sqlite3

# Nombre del archivo de base de datos
DB_PATH = r"C:/Users/kvela/Documents/Ux/5to semestre/Agentes Inteligentes/3er Parcial/Examen/edumentor.db"

def create_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            lesson_number INTEGER,
            title TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            course_id INTEGER,
            current_lesson INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );
    """)

    conn.commit()
    conn.close()
    print("✓ Tablas creadas correctamente.")


def seed_data():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (name) VALUES (?)", ("Kris",))
    cursor.execute("INSERT INTO users (name) VALUES (?)", ("Amy",))

    cursor.execute("INSERT INTO courses (user_id, title) VALUES (?, ?)", (1, "Curso de Prueba"))
    cursor.execute("""
        INSERT INTO lessons (course_id, lesson_number, title, content)
        VALUES (1, 1, 'Introducción', 'Esta es la primera lección.');
    """)

    conn.commit()
    conn.close()
    print("✓ Datos de prueba insertados.")


if __name__ == "__main__":
    create_tables()
    seed_data()
