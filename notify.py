import requests
import telegram
from io import BytesIO
from db import get_despesas_semana



def enviar_relatorio_telegram(TELEGRAM_TOKEN,TELEGRAM_CHAT_ID):
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

def send_plot_to_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, fig, caption=""):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bio = BytesIO()
    bio.name = 'plot.png'
    fig.savefig(bio, format='png')
    bio.seek(0)
    bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=bio, caption=caption) 