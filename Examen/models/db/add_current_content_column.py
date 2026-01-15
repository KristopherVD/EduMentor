import sqlite3

DB_PATH = r"C:/Users/kvela/Documents/Ux/5to semestre/Agentes Inteligentes/3er Parcial/Examen/edumentor.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

try:
    c.execute("ALTER TABLE users ADD COLUMN current_content TEXT")
    print("✅ Columna current_content agregada correctamente")
except sqlite3.OperationalError as e:
    print("⚠️ No se pudo agregar la columna (probablemente ya existe):")
    print(e)

conn.commit()
conn.close()
