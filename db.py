import sqlite3

def init_db():
    conn = sqlite3.connect('gastos.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    limite REAL DEFAULT 0
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS despesas (
                    id INTEGER PRIMARY KEY,
                    categoria_id INTEGER,
                    valor REAL,
                    data DATE,
                    FOREIGN KEY(categoria_id) REFERENCES categorias(id)
                )''')
    conn.commit()
    conn.close()

def add_categoria(nome, limite):
    conn = sqlite3.connect('gastos.db')
    c = conn.cursor()

    c.execute('INSERT INTO categorias (nome, limite) VALUES (?,?)',(nome,limite))
    conn.commit()
    conn.close()

def get_categorias():
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()
    c.execute("SELECT id, nome, limite FROM categorias")
    result = c.fetchall()
    conn.close()
    return result

def add_despesa(categoria_id, valor, data):
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()
    c.execute("INSERT INTO despesas (categoria_id, valor, data) VALUES (?, ?, ?)", (categoria_id, valor, data))
    conn.commit()
    conn.close()

def get_despesas_semana():
    from datetime import datetime, timedelta
    conn = sqlite3.connect("gastos.db")
    c = conn.cursor()
    semana_passada = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    c.execute('''SELECT categorias.nome, SUM(despesas.valor), categorias.limite
                 FROM despesas
                 JOIN categorias ON despesas.categoria_id = categorias.id
                 WHERE data >= ?
                 GROUP BY categorias.nome''', (semana_passada,))
    result = c.fetchall()
    conn.close()
    return result

add_categoria('Mercado','4000')