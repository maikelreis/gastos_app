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