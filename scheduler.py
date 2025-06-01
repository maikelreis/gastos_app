import schedule
import time
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
from notify import enviar_relatorio_telegram,send_plot_to_telegram
from db import get_despesas_por_categoria, get_comparativo_semanal

TELEGRAM_TOKEN = '7935477704:AAHI81vaEfaiZEGftm5oO8ZwxNP1BTKGOw8'
TELEGRAM_CHAT_ID = '-4712297495'

def gerar_grafico_pizza():
    df = get_despesas_por_categoria(periodo="semana")
    if df.empty:
        return None, "Nenhum dado de despesas da semana."
    fig, ax = plt.subplots()
    ax.pie(df['total'], labels=df['categoria'], autopct='%1.1f%%')
    return fig, "Gastos por categoria na semana."

def gerar_grafico_comparativo():
    df = get_comparativo_semanal()
    if df.empty:
        return None, "Nenhum dado comparativo semanal."
    fig, ax = plt.subplots()
    for cat in df['categoria'].unique():
        df_cat = df[df['categoria'] == cat]
        ax.plot(df_cat['semana'], df_cat['total'], label=cat)
    ax.legend()
    return fig, "Comparativo semanal de gastos."

def tarefa_notificar():
    fig1, msg1 = gerar_grafico_pizza()
    if fig1:
        send_plot_to_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, fig1, msg1)

    fig2, msg2 = gerar_grafico_comparativo()
    if fig2:
        send_plot_to_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, fig2, msg2)

def notificar_semanalmente():
    enviar_relatorio_telegram(TELEGRAM_TOKEN,TELEGRAM_CHAT_ID)

# Agendamento semanal toda sexta as 20:00
schedule.every().saturday.at("23:35").do(notificar_semanalmente)

# Agendamento semanal todo domingo às 08:00
schedule.every().saturday.at("23:40").do(tarefa_notificar)

if __name__ == "__main__":
    print("Iniciando scheduler...")
    while True:
        schedule.run_pending()
        time.sleep(60)
