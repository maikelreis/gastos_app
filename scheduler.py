import sqlite3
from datetime import date, datetime
import requests
import os

# --- CONFIGURAÇÃO ---

DB_PATH = "/app/gastos.db"
BOT_TOKEN = os.environ.get('BOT_TOKEN') 
CHAT_ID = os.environ.get('CHAT_ID')

# --- FUNÇÕES AUXILIARES ---
def get_gastos_mes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    hoje = date.today()
    primeiro_dia = hoje.replace(day=1)
    cursor.execute("""
        SELECT c.nome, c.limite, SUM(d.valor)
        FROM despesas d
        JOIN categorias c ON d.categoria_id = c.id
        WHERE date(d.data) >= ?
        GROUP BY c.id
    """, (primeiro_dia,))
    
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def gerar_alerta(percentual):
    if percentual >= 90:
        return "🔴"
    elif percentual >= 70:
        return "🟠"
    elif percentual >= 50:
        return "🟡"
    return "🟢"

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)

def gerar_relatorio():
    gastos = get_gastos_mes()
    linhas = ["📊 *Relatório de Gastos do Mês*\n"]

    total_gasto = 0
    total_limite = 0

    for nome, limite, total in gastos:
        percentual = (total / limite) * 100 if limite else 0
        diferenca = limite - total
        alerta = gerar_alerta(percentual)
        linhas.append(f"{alerta} *{nome}*: R$ {total:.2f} de R$ {limite:.2f} - *resta* R$ {diferenca:.2f} ({percentual:.1f}%)")
        total_gasto += total
        total_limite += limite

    saldo = total_limite - total_gasto
    linhas.append("\n💰 *Totais:*")
    linhas.append(f"🔹 Gasto: R$ {total_gasto:.2f}")
    linhas.append(f"🔹 Limite: R$ {total_limite:.2f}")
    linhas.append(f"🔹 Saldo disponível: R$ {saldo:.2f}")

    return "\n".join(linhas)

# --- EXECUÇÃO PROGRAMADA ---
def main():
    hoje = date.today()
    #if hoje.weekday() == 4:  # 0 = segunda, 4 = sexta
    #    mensagem = gerar_relatorio()
    #    enviar_telegram(mensagem)
    mensagem = gerar_relatorio()
    enviar_telegram(mensagem)

if __name__ == "__main__":
    main()