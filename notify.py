import requests
from db import get_despesas_semana

TELEGRAM_TOKEN = '7935477704:AAHI81vaEfaiZEGftm5oO8ZwxNP1BTKGOw8'
TELEGRAM_CHAT_ID = '-4712297495'

def enviar_relatorio_telegram():
    despesas = get_despesas_semana()
    if not despesas:
        return
    
    msg = "📊 *Relatório Semanal de Gastos*\n\n"

    for nome,total,limite in despesas:
        msg += f"- {nome}: Gastos no Total R$ {total:.2f} / Limite R$ {limite:.2f} / Restante: R$ {limite - total}\n"

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    )