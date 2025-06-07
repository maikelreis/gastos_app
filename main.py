from reactpy import component, html, run, use_state, use_effect
from reactpy.backend.fastapi import configure
from fastapi import FastAPI
from db import get_categorias, add_despesa
from datetime import datetime
import uvicorn

app = FastAPI()

@component
def Menu(on_select):
    return html.div(
        {
            "style": {
                "display": "flex",
                "gap": "10px",
                "marginBottom": "20px"
            }
        },
        html.button({"onclick": lambda *_: on_select("dashboard")}, "Dashboard"),
        html.button({"onclick": lambda *_: on_select("adicionar")}, "Adicionar Gasto"),
        html.button({"onclick": lambda *_: on_select("editar")}, "Editar Categorias"),
        html.button({"onclick": lambda *_: on_select("relatorios")}, "Relatórios"),
    )


@component
def AdicionarGasto():
    categorias, set_categorias = use_state([])
    selected_cat, set_selected_cat = use_state("")
    valor, set_valor = use_state("")
    data, set_data = use_state("")
    msg, set_msg = use_state("")

    def carregar_categorias():
        
        try:
            cats = get_categorias()
            if cats:
                set_categorias(cats)
                if selected_cat is None:
                    set_selected_cat(str(cats[0][0]))
        except Exception as e:
            print("❌ Erro ao carregar categorias:", e)
        return

    @use_effect
    def on_mount():
        carregar_categorias()
        return  # <- necessário para não tentar retornar função de cleanup

    def handle_select_change(event):
        print("📥 Categoria selecionada:", event["target"]["value"])
        set_selected_cat(event["target"]["value"])

    def handle_valor_change(event):
        print("💸 Valor digitado:", event["target"]["value"])
        set_valor(event["target"]["value"])

    def handle_data_change(event):
        print("📅 Data escolhida:", event["target"]["value"])
        set_data(event["target"]["value"])

    def salvar_gasto(event):
        try:
            if not selected_cat or not valor:
                set_msg("⚠️ Preencha todos os campos.")
                return
            add_despesa(int(selected_cat), float(valor), data)
            set_msg("✅ Gasto salvo com sucesso!")
            set_valor("")
        except Exception as e:
            set_msg(f"❌ Erro ao salvar: {e}")

    return html.div(
        html.h2("Adicionar Gasto"),
        html.label("Categoria:"),
        html.select(
            {"value": selected_cat, "onChange": handle_select_change},
            [html.option({"value": str(cid)}, nome) for cid, nome in categorias]
        ) if categorias else html.p("Nenhuma categoria cadastrada."),
        html.br(),

        html.label("Valor:"),
        html.input({
            "type": "number",
            "value": valor,
            "onChange": handle_valor_change,
        }),
        html.br(),

        html.label("Data:"),
        html.input({
            "type": "date",
            "value": data,
            "onChange": handle_data_change,
        }),
        html.br(),

        html.button({"onClick": salvar_gasto}, "Salvar Gasto"),
        html.p(msg),
    )

@component
def App():
    page, set_page = use_state("dashboard")

    def render_page():
        if page == "dashboard":
            return html.h2("📊 Dashboard - Em construção")
        elif page == "adicionar":
            return AdicionarGasto()
        elif page == "editar":
            return html.h2("Editar Categorias - Em construção")
        elif page == "relatorios":
            return html.h2("Relatórios - Em construção")
        return html.h2("Página não encontrada")

    return html.div(
        html.h1("Controle de Gastos"),
        html.p("Bem-vindo ao seu parceiro de controle financeiro!"),
        Menu(set_page),
        render_page()
    )

configure(app, App)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=10000)
