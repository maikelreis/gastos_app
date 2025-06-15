from reactpy import component, html, run, use_state, use_effect
from reactpy.backend.fastapi import configure
from fastapi import FastAPI
from db import get_categorias, add_despesa, get_despesas
from db import update_categoria, delete_categoria
from datetime import datetime, date
from collections import defaultdict
import plotly.graph_objs as go
import uvicorn

app_fastapi = FastAPI()

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
        html.button({"onClick": lambda *_: on_select("semana")}, "Gastos da Semana")
    )

@component
def GastosDaSemana():
    despesas, set_despesas = use_state([])
    total, set_total = use_state(0.0)

    @use_effect
    def carregar():
        dados = get_despesas()
        set_despesas(dados)
        set_total(sum([d[2] for d in dados]))
        return

    def filtrar_por_semana(despesas):
        hoje = datetime.today()
        semana_atual = hoje.isocalendar()[1]
        return [d for d in despesas if date.fromisoformat(d[3]).isocalendar()[1] == semana_atual]

    return html.div(
        html.h2("🗓️ Gastos da Semana"),
        html.table(
            {"border": "1", "cellPadding": "5"},
            html.thead(
                html.tr(
                    html.th("Categoria"),
                    html.th("Valor"),
                    html.th("Data")
                )
            ),
            html.tbody([
                html.tr(
                    html.td(cat),
                    html.td(f"R$ {valor:.2f}"),
                    html.td(data)
                )
                for _, cat, valor, data in filtrar_por_semana(despesas)
            ])
        ),
        html.h3(f"Total Geral: R$ {total:.2f}")
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
def RelatorioGastos():
    despesas, set_despesas = use_state([])
    categorias, set_categorias = use_state([])
    mes_selecionado, set_mes_selecionado = use_state(date.today().month)

    @use_effect
    def on_mount():
        set_despesas(get_despesas())
        set_categorias(get_categorias())
        return

    def filtrar_por_mes(despesas, mes):
        return [d for d in despesas if date.fromisoformat(d[3]).month == mes]

    def gerar_relatorio():
        despesas_filtradas = filtrar_por_mes(despesas, mes_selecionado)

        # Mapeando por nome da categoria
        categorias_dict = {
            cat[1]: cat[2]  # "Alimentação": 1000.0
            for cat in categorias
        }

        total_por_categoria = defaultdict(float)

        for _, cat_nome, valor, _ in despesas_filtradas:
            total_por_categoria[cat_nome] += valor

        linhas = []
        total_gastos = 0.0
        total_limites = 0.0

        for cat_nome, gasto in total_por_categoria.items():
            limite = categorias_dict.get(cat_nome, 0.0)
            diferenca = limite - gasto
            total_gastos += gasto
            total_limites += limite

            linhas.append(html.tr(
                html.td(cat_nome),
                html.td(f"R$ {gasto:.2f}"),
                html.td(f"R$ {limite:.2f}"),
                html.td(f"R$ {diferenca:.2f}")
            ))

        return html.div(
            html.h3("Relatório de Gastos por Categoria"),
            html.div(
                html.label("Selecionar Mês: "),
                html.select(
                    {
                        "value": str(mes_selecionado),
                        "onChange": lambda e: set_mes_selecionado(int(e["target"]["value"]))
                    },
                    *[html.option({"value": str(i)}, date(2025, i, 1).strftime("%B")) for i in range(1, 13)]
                )
            ),
            html.table(
                {"border": "1", "cellPadding": "5", "style": {"marginTop": "15px"}},
                html.thead(
                    html.tr(
                        html.th("Categoria"),
                        html.th("Gasto Total"),
                        html.th("Limite"),
                        html.th("Diferença")
                    )
                ),
                html.tbody(linhas)
            ),
            html.div(
                html.p(f"💰 Total de Gastos: R$ {total_gastos:.2f}"),
                html.p(f"📈 Total de Limites: R$ {total_limites:.2f}"),
                html.p(f"💡 Saldo Disponível: R$ {total_limites - total_gastos:.2f}")
            )
        )

    return gerar_relatorio()

@component
def Dashboard():
    despesas, set_despesas = use_state([])

    @use_effect
    def on_mount():
        set_despesas(get_despesas())
        return

    def gerar_plot(fig):
        plot_html = fig.to_html(include_plotlyjs='cdn', full_html=False)
        return html.iframe({
            "srcDoc": plot_html,
            "width": "100%",
            "height": "500px",
            "style": {"border": "none"}
        })

    def filtrar_despesas_por_periodo(despesas, filtro):
        hoje = datetime.today()
        resultado = []

        for desp in despesas:
            _, categoria, valor, data_str = desp
            data = date.fromisoformat(data_str)
            if filtro(data, hoje):
                resultado.append((categoria, valor, data))
        return resultado

    def total_por_categoria(despesas_filtradas):
        totais = defaultdict(float)
        for categoria, valor, _ in despesas_filtradas:
            totais[categoria] += valor
        return totais

    hoje = datetime.today()

    # --- Semana Atual ---
    semana_atual = hoje.isocalendar()[1]
    semana_passada = semana_atual - 1
    dados_semana = filtrar_despesas_por_periodo(despesas, lambda d, h: d.isocalendar()[1] == semana_atual and d.year == h.year)
    totais_semana = total_por_categoria(dados_semana)

    # --- Semana Passada ---
    dados_semana_passada = filtrar_despesas_por_periodo(despesas, lambda d, h: d.isocalendar()[1] == semana_passada and d.year == h.year)
    totais_semana_passada = total_por_categoria(dados_semana_passada)

    # --- Mês Atual ---
    dados_mes = filtrar_despesas_por_periodo(despesas, lambda d, h: d.month == h.month and d.year == h.year)
    totais_mes = total_por_categoria(dados_mes)

    # --- Mês Passado ---
    mes_passado = hoje.month - 1 if hoje.month > 1 else 12
    ano_ref = hoje.year if hoje.month > 1 else hoje.year - 1
    dados_mes_passado = filtrar_despesas_por_periodo(despesas, lambda d, h: d.month == mes_passado and d.year == ano_ref)
    totais_mes_passado = total_por_categoria(dados_mes_passado)

    # --- Ano Atual ---
    dados_ano = filtrar_despesas_por_periodo(despesas, lambda d, h: d.year == h.year)
    totais_ano = total_por_categoria(dados_ano)

    return html.div(
        html.h2("📊 Dashboard"),

        html.h3("1. Gastos por Categoria - Semana Atual (Pizza)"),
        gerar_plot(go.Figure(data=[go.Pie(
            labels=list(totais_semana.keys()),
            values=list(totais_semana.values())
        )])),

        html.h3("2. Comparativo: Semana Atual x Semana Passada"),
        gerar_plot(go.Figure(data=[
            go.Bar(name='Semana Atual', x=list(totais_semana.keys()), y=list(totais_semana.values())),
            go.Bar(name='Semana Passada', x=list(totais_semana_passada.keys()), y=[totais_semana_passada.get(k, 0) for k in totais_semana.keys()])
        ]).update_layout(barmode='group')),

        html.h3("3. Comparativo: Mês Atual x Mês Passado"),
        gerar_plot(go.Figure(data=[
            go.Bar(name='Mês Atual', x=list(totais_mes.keys()), y=list(totais_mes.values())),
            go.Bar(name='Mês Passado', x=list(totais_mes_passado.keys()), y=[totais_mes_passado.get(k, 0) for k in totais_mes.keys()])
        ]).update_layout(barmode='group')),

        html.h3("4. Total por Categoria no Ano"),
        gerar_plot(go.Figure(data=[
            go.Bar(x=list(totais_ano.keys()), y=list(totais_ano.values()))
        ]))
    )

@component
def App():
    page, set_page = use_state("adicionar")

    def render_page():
        if page == "dashboard":
            return Dashboard()
        elif page == "adicionar":
            return AdicionarGasto()
        elif page == "editar":
            return EditarCategorias()
        elif page == "relatorios":
            return RelatorioGastos()
        elif page == "semana":
            return GastosDaSemana()
        return html.h2("Página não encontrada")

    return html.div(
        html.h1("Controle de Gastos"),
        html.p("Bem-vindo ao seu parceiro de controle financeiro!"),
        Menu(set_page),
        render_page()
    )

configure(app_fastapi, App)

if __name__ == "__main__":
    uvicorn.run(app_fastapi, host="127.0.0.1", port=10000)
