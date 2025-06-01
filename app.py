import streamlit as st
from db import init_db,add_categoria,add_despesa,get_categorias
from datetime import date

init_db()
st.title("💰 Controle de Gastos")

menu = st.sidebar.selectbox('menu',['Adicionar Categoria','Lançar Gastos'])

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