import sqlite3

def inicializar_banco():
    conn = sqlite3.connect("/app/gastos.db")
    cursor = conn.cursor()

    # Tabela de categorias
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        limite REAL
    )
    """)

    # Tabela de despesas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS despesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria_id INTEGER,
        valor REAL,
        data TEXT,
        FOREIGN KEY(categoria_id) REFERENCES categorias(id)
    )
    """)

if __name__ == "__main__":
    inicializar_banco()
