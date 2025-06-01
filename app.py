import streamlit as st
from db import init_db, add_categoria, get_categorias, add_despesa
from db import get_despesas_por_categoria, get_despesas_por_semana_ano, get_comparativo_semanal, get_despesas_com_limite
from datetime import date
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

init_db()
st.title("💰 Controle de Gastos")

menu = st.sidebar.selectbox('menu',['Lançar Gastos','Adicionar Categoria','Relatório'])

if menu == 'Adicionar Categoria':
    nome = st.text_input('Nome da Categoria')
    limite = st.number_input('Limite de Gastos', min_value=0.0)
    if st.button('Salvar'):
        add_categoria(nome,limite)
        st.success('Categoria adicionada com sucesso')

elif menu == 'Lançar Gastos':
    categorias = get_categorias()
    nomes = [c[1] for c in categorias]
    selected = st.selectbox('Categorias',nomes)
    valor = st.number_input('Valor', min_value=0.0)
    data_gasto = st.date_input("Data",value=date.today())

    if st.button("Salvar Gastos"):
        for c in categorias:
            if c[1] == selected:
                cat_id = c[0]
        add_despesa(cat_id,valor,data_gasto.strftime("%Y-%m-%d"))
        st.success("Gasto Registrado")

elif menu == "Relatório Semanal":
    filtro = st.radio("Filtro para Gráfico de Pizza", ["Semana", "Mês"])

    # 1 - Pizza por categoria
    st.subheader("1. Gastos por Categoria")
    df_cat = get_despesas_por_categoria(periodo=filtro.lower())
    if not df_cat.empty:
        fig1, ax1 = plt.subplots()
        ax1.pie(df_cat['total'], labels=df_cat['categoria'], autopct='%1.1f%%')
        st.pyplot(fig1)
    else:
        st.info("Nenhum dado encontrado para esse filtro.")

    # 2 - Barras por semana/ano
    st.subheader("2. Gasto Semanal por Categoria no Ano")
    df_sem = get_despesas_por_semana_ano()
    if not df_sem.empty:
        fig2 = sns.catplot(data=df_sem, kind="bar", x="semana", y="total", hue="categoria", height=5, aspect=2)
        st.pyplot(fig2)
    else:
        st.info("Nenhum dado semanal encontrado.")

    # 3 - Linha com semana atual vs anterior
    st.subheader("3. Comparativo Semanal por Categoria")
    df_comp = get_comparativo_semanal()
    if not df_comp.empty:
        fig3, ax3 = plt.subplots()
        for cat in df_comp['categoria'].unique():
            df_cat = df_comp[df_comp['categoria'] == cat]
            ax3.plot(df_cat['semana'], df_cat['total'], label=cat)
        ax3.legend()
        st.pyplot(fig3)
    else:
        st.info("Sem dados comparativos.")

    # 4 - Barra com metas
    st.subheader("4. Gasto por Categoria x Limite")
    categorias = get_categorias()
    nomes = [c[1] for c in categorias]
    categoria_opcao = st.selectbox("Categoria", ["Todas"] + nomes)
    df_meta = get_despesas_com_limite(categoria_opcao)
    if not df_meta.empty:
        fig4, ax4 = plt.subplots()
        df_meta.plot(kind='bar', x='categoria', y=['total', 'limite'], ax=ax4)
        st.pyplot(fig4)
    else:
        st.info("Sem dados para essa categoria.")