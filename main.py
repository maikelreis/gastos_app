from reactpy import component, html, run, use_state, use_effect
from reactpy.backend.fastapi import configure
from fastapi import FastAPI
from db import get_categorias, add_despesa
from db import update_categoria, delete_categoria
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
    mensagem, set_mensagem = use_state("")

    def carregar_categorias():
        try:
            cats = get_categorias()
            if cats:
                set_categorias(cats)
                if selected_cat is None:
                    set_selected_cat(str(cats[0][0]))
        except Exception as e:
            print("❌ Erro ao carregar categorias:", e)

    @use_effect
    def on_mount():
        carregar_categorias()
        return

    def salvar(event=None):
        if not selected_cat or not valor:
            set_mensagem("⚠️ Preencha todos os campos!")
            return
        add_despesa(int(selected_cat),float(valor), data)
        set_mensagem("✅ Gasto adicionado com sucesso!")
        set_valor("")
        set_data("")

    return html.div(
        html.h2("Adicionar Gasto"),
        html.div(
            html.label("Categoria:"),
            html.select(
                {
                    "value": selected_cat,
                    "onChange": lambda e: set_selected_cat(e["target"]["value"])
                },
                *[html.option({"value": str(cat[0])}, cat[1]) for cat in categorias]
            ),
            html.br(),
            html.label("Valor:"),
            html.input({"type": "number", "value": valor, "onChange": lambda e: set_valor(e["target"]["value"])}),
            html.br(),
            html.label("Data:"),
            html.input({"type": "Date", "value": data, "onChange": lambda e: set_data(e["target"]["value"])}),
            html.br(),
            html.button({"onClick": salvar}, "Salvar"),
            html.p(mensagem)
        )
    )

@component
def LinhaCategoria(cat, on_update, on_delete):
    cat_id, nome, limite = cat
    nome_state, set_nome_state = use_state(nome)
    limite_state, set_limite_state = use_state(str(limite))

    return html.tr(
        html.td(html.input({
            "type": "text",
            "value": nome_state,
            "onChange": lambda e: set_nome_state(e["target"]["value"])
        })),
        html.td(html.input({
            "type": "number",
            "value": limite_state,
            "onChange": lambda e: set_limite_state(e["target"]["value"])
        })),
        html.td(
            html.button({"onClick": lambda *_: on_update(cat_id, nome_state, float(limite_state))}, "Salvar"),
            html.button({"onClick": lambda *_: on_delete(cat_id)}, "Remover")
        )
    )

@component
def EditarCategorias():
    categorias, set_categorias = use_state([])
    msg, set_msg = use_state("")
    novo_nome, set_novo_nome = use_state("")
    novo_limite, set_novo_limite = use_state("")

    def carregar_categorias():
        set_categorias(get_categorias())

    @use_effect
    def on_mount():
        carregar_categorias()
        return

    def atualizar_categoria(cat_id, nome, limite):
        update_categoria(cat_id, nome, limite)
        set_msg(f"✅ Categoria {nome} atualizada!")
        carregar_categorias()

    def remover_categoria(cat_id):
        delete_categoria(cat_id)
        set_msg("🗑️ Categoria removida.")
        carregar_categorias()
    
    def salvar_categoria(event=None):
        if not novo_nome or not novo_limite:
            set_msg("⚠️ Preencha nome e limite.")
            return
        try:
            from db import add_categoria
            add_categoria(novo_nome, float(novo_limite))
            set_msg(f"✅ Categoria '{novo_nome}' adicionada.")
            set_novo_nome("")
            set_novo_limite("")
            carregar_categorias()
        except Exception as e:
            set_msg(f"❌ Erro ao adicionar categoria: {e}")

    return html.div(
        html.h2("Editar Categorias"),
        html.p(msg),

        html.h3("Adicionar nova categoria"),
        html.div(
            html.input({
                "type": "text",
                "placeholder": "Nome da categoria",
                "value": novo_nome,
                "onChange": lambda e: set_novo_nome(e["target"]["value"])
            }),
            html.input({
                "type": "number",
                "placeholder": "Limite",
                "value": novo_limite,
                "onChange": lambda e: set_novo_limite(e["target"]["value"])
            }),
            html.button({"onClick": salvar_categoria}, "Salvar Categoria")
        ),

        html.table(
            {"border": "1", "cellPadding": "5"},
            html.thead(
                html.tr(
                    html.th("Nome"),
                    html.th("Limite"),
                    html.th("Ações")
                )
            ),
            html.tbody(
                [LinhaCategoria(cat, atualizar_categoria, remover_categoria) for cat in categorias]
            )
        )
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
            return EditarCategorias()
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
