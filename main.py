from reactpy import component, html, run, use_state
from reactpy.backend.fastapi import configure
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@component
def Home():
    return html.div(
        html.h1("Controle de Gastos"),
        html.p("Bem-vindo ao seu parceiro de controle financeiro!")
    )

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
        html.button({"on_click": lambda: on_select("dashboard")}, "Dashboard"),
        html.button({"on_click": lambda: on_select("adicionar")}, "Adicionar Gasto"),
        html.button({"on_click": lambda: on_select("editar")}, "Editar Categorias"),
        html.button({"on_click": lambda: on_select("relatorios")}, "Relatórios"),
    )

@component
def App():
    page, set_page = use_state("dashboard")

    def render_page():
        if page == "dashboard":
            return html.h2("Dashboard - Em construção")
        elif page == "adicionar":
            return html.h2("Adicionar Gasto - Em construção")
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
