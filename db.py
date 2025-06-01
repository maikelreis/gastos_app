import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB = "gastos.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        limite REAL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS despesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria_id INTEGER,
        valor REAL,
        data TEXT,
        FOREIGN KEY (categoria_id) REFERENCES categorias (id)
    )''')
    conn.commit()
    conn.close()

def add_categoria(nome, limite):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO categorias (nome, limite) VALUES (?, ?)", (nome, limite))
    conn.commit()
    conn.close()

def get_categorias():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * FROM categorias")
    categorias = cur.fetchall()
    conn.close()
    return categorias

def add_despesa(categoria_id, valor, data):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO despesas (categoria_id, valor, data) VALUES (?, ?, ?)", (categoria_id, valor, data))
    conn.commit()
    conn.close()

def get_despesas_por_categoria(periodo="semana"):
    conn = sqlite3.connect(DB)
    query = """
    SELECT c.nome as categoria, SUM(d.valor) as total FROM despesas d
    JOIN categorias c ON d.categoria_id = c.id
    WHERE date(d.data) >= date(?)
    GROUP BY c.nome
    """
    hoje = datetime.today()
    inicio = hoje - timedelta(days=7) if periodo == "semana" else hoje.replace(day=1)
    df = pd.read_sql(query, conn, params=(inicio.strftime("%Y-%m-%d"),))
    conn.close()
    return df

def get_despesas_por_semana_ano():
    conn = sqlite3.connect(DB)
    query = """
    SELECT strftime('%W', data) as semana, c.nome as categoria, SUM(valor) as total FROM despesas d
    JOIN categorias c ON c.id = d.categoria_id
    WHERE strftime('%Y', data) = ?
    GROUP BY semana, categoria
    """
    ano = datetime.today().strftime('%Y')
    df = pd.read_sql(query, conn, params=(ano,))
    conn.close()
    return df

def get_comparativo_semanal():
    conn = sqlite3.connect(DB)
    query = """
    SELECT c.nome as categoria, strftime('%W', data) as semana, SUM(valor) as total FROM despesas d
    JOIN categorias c ON d.categoria_id = c.id
    WHERE date(data) >= date(?)
    GROUP BY c.nome, semana
    ORDER BY semana
    """
    inicio = datetime.today() - timedelta(days=14)
    df = pd.read_sql(query, conn, params=(inicio.strftime("%Y-%m-%d"),))
    conn.close()
    return df

def get_despesas_com_limite(filtro_categoria):
    conn = sqlite3.connect(DB)
    query = """
    SELECT c.nome as categoria, SUM(d.valor) as total, c.limite
    FROM despesas d
    JOIN categorias c ON d.categoria_id = c.id
    GROUP BY c.nome
    """
    df = pd.read_sql(query, conn)
    conn.close()
    if filtro_categoria != "Todas":
        df = df[df["categoria"] == filtro_categoria]
    return df

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

def atualizar_categoria(novo_nome,novo_limite,cat_id):
    conn = sqlite3.connect("gastos.db")
    cur = conn.cursor()
    cur.execute("UPDATE categorias SET nome = ?, limite = ? WHERE id = ?", (novo_nome, novo_limite, cat_id))
    conn.commit()
    conn.close()

def remover_categoria(cat_del_id):
    conn = sqlite3.connect("gastos.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM categorias WHERE id = ?", (cat_del_id,))
    conn.commit()
    conn.close()