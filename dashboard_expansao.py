import os
import dash
from dash import dcc, html, dash_table, Input, Output, State, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc

# ==========================
# 1. CONFIGURAÇÃO DE ARMAZENAMENTO
# ==========================
DATA_DIR = "data"
CSV_FILE = os.path.join(DATA_DIR, "metas.csv")

# Cria pasta data se não existir
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Dados iniciais (com base nos seus documentos)
initial_data = [
    # Fase 1 - Monte Verde e Bandeirantes
    {"Fase": "Fase 1", "Cidade": "Monte Verde", "Tipo": "Motorista", "Meta": 4, "Realizado": 0, "Unidade": "motoristas", "Periodo": "01/08 - 14/08"},
    {"Fase": "Fase 1", "Cidade": "Nova Bandeirantes", "Tipo": "Motorista", "Meta": 6, "Realizado": 0, "Unidade": "motoristas", "Periodo": "01/08 - 14/08"},
    {"Fase": "Fase 1", "Cidade": "Monte Verde", "Tipo": "Corrida", "Meta": 20, "Realizado": 0, "Unidade": "corridas", "Periodo": "16/08 - 14/09"},
    {"Fase": "Fase 1", "Cidade": "Nova Bandeirantes", "Tipo": "Corrida", "Meta": 30, "Realizado": 0, "Unidade": "corridas", "Periodo": "16/08 - 14/09"},

    # Fase 2 - Alta Floresta e Paranaíta
    {"Fase": "Fase 2", "Cidade": "Alta Floresta", "Tipo": "Motorista", "Meta": 8, "Realizado": 0, "Unidade": "motoristas", "Periodo": "15/09 - 29/09"},
    {"Fase": "Fase 2", "Cidade": "Paranaíta", "Tipo": "Motorista", "Meta": 4, "Realizado": 0, "Unidade": "motoristas", "Periodo": "15/09 - 29/09"},
    {"Fase": "Fase 2", "Cidade": "Alta Floresta", "Tipo": "Corrida", "Meta": 20, "Realizado": 0, "Unidade": "corridas", "Periodo": "30/09 - 29/10"},
    {"Fase": "Fase 2", "Cidade": "Paranaíta", "Tipo": "Corrida", "Meta": 30, "Realizado": 0, "Unidade": "corridas", "Periodo": "30/09 - 29/10"},

    # Fase 3 - Colíder, Nova Canaã, Carlinda
    {"Fase": "Fase 3", "Cidade": "Colíder", "Tipo": "Motorista", "Meta": 6, "Realizado": 0, "Unidade": "motoristas", "Periodo": "01/11 - 15/11"},
    {"Fase": "Fase 3", "Cidade": "Nova Canaã do Norte", "Tipo": "Motorista", "Meta": 5, "Realizado": 0, "Unidade": "motoristas", "Periodo": "01/11 - 15/11"},
    {"Fase": "Fase 3", "Cidade": "Carlinda", "Tipo": "Motorista", "Meta": 4, "Realizado": 0, "Unidade": "motoristas", "Periodo": "01/11 - 15/11"},
    {"Fase": "Fase 3", "Cidade": "Colíder", "Tipo": "Corrida", "Meta": 50, "Realizado": 0, "Unidade": "corridas", "Periodo": "16/11 - 15/12"},
    {"Fase": "Fase 3", "Cidade": "Nova Canaã do Norte", "Tipo": "Corrida", "Meta": 30, "Realizado": 0, "Unidade": "corridas", "Periodo": "16/11 - 15/12"},
    {"Fase": "Fase 3", "Cidade": "Carlinda", "Tipo": "Corrida", "Meta": 30, "Realizado": 0, "Unidade": "corridas", "Periodo": "16/11 - 15/12"},
]

# Carrega ou cria CSV
if not os.path.exists(CSV_FILE):
    df_initial = pd.DataFrame(initial_data)
    df_initial.to_csv(CSV_FILE, index=False)
else:
    df_initial = pd.read_csv(CSV_FILE)

# ==========================
# 2. INICIALIZA O APP
# ==========================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])
server = app.server  # Necessário para deploy online

# ==========================
# 3. LAYOUT
# ==========================
app.layout = html.Div([
    dbc.Container([
        html.H1("🚀 Dashboard de Expansão Municipal", className="text-center my-4 text-primary"),

        # Botões
        dbc.Row([
            dbc.Col([
                dbc.Button("➕ Adicionar Meta", id="open-add-modal", color="success", className="me-2"),
                dbc.Button("💾 Salvar Tudo", id="save-data", color="primary"),
                html.Span(id="save-status", style={"color": "green", "margin-left": "10px"})
            ], width=12, className="mb-4 text-center")
        ]),

        # Filtros
        dbc.Row([
            dbc.Col(dcc.Dropdown(id="filtro-fase", placeholder="Todas as fases", multi=True), width=4),
            dbc.Col(dcc.Dropdown(id="filtro-cidade", placeholder="Todas as cidades", multi=True), width=4),
            dbc.Col(dcc.Dropdown(id="filtro-tipo", placeholder="Todos os tipos", multi=True), width=4),
        ], className="mb-4"),

        # KPIs
        html.Div(id="kpi-container", className="mb-4"),

        # Gráficos
        dbc.Row([
            dbc.Col(dcc.Graph(id="grafico-progresso"), width=12),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(id="grafico-financeiro"), width=6),
            dbc.Col(dcc.Graph(id="grafico-demografia"), width=6),
        ], className="mb-4"),

        # Tabela Editável
        html.H4("📋 Metas - Edição Direta", className="mt-4"),
        dash_table.DataTable(
            id='tabela-metas',
            columns=[
                {"name": "Fase", "id": "Fase", "editable": True, "presentation": "dropdown"},
                {"name": "Cidade", "id": "Cidade", "editable": True, "presentation": "dropdown"},
                {"name": "Tipo", "id": "Tipo", "editable": True, "presentation": "dropdown"},
                {"name": "Meta", "id": "Meta", "editable": True, "type": "numeric"},
                {"name": "Realizado", "id": "Realizado", "editable": True, "type": "numeric"},
                {"name": "Unidade", "id": "Unidade", "editable": False},
                {"name": "Periodo", "id": "Periodo", "editable": True},
            ],
            data=df_initial.to_dict('records'),
            editable=True,
            row_deletable=True,
            filter_action="custom",
            sort_action="native",
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "8px"},
            style_header={"backgroundColor": "#f0f0f0", "fontWeight": "bold"}
        ),

        # Modal para adicionar
        dbc.Modal([
            dbc.ModalHeader("Adicionar Nova Meta"),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Fase"),
                            dcc.Dropdown(
                                id="modal-fase",
                                options=[{"label": f"Fase {i}", "value": f"Fase {i}"} for i in [1, 2, 3]],
                                value="Fase 1"
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Cidade"),
                            dcc.Dropdown(
                                id="modal-cidade",
                                options=[
                                    {"label": "Monte Verde", "value": "Monte Verde"},
                                    {"label": "Nova Bandeirantes", "value": "Nova Bandeirantes"},
                                    {"label": "Alta Floresta", "value": "Alta Floresta"},
                                    {"label": "Paranaíta", "value": "Paranaíta"},
                                    {"label": "Colíder", "value": "Colíder"},
                                    {"label": "Nova Canaã do Norte", "value": "Nova Canaã do Norte"},
                                    {"label": "Carlinda", "value": "Carlinda"},
                                ],
                                value="Monte Verde"
                            )
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Tipo"),
                            dcc.Dropdown(
                                id="modal-tipo",
                                options=[
                                    {"label": "Motorista", "value": "Motorista"},
                                    {"label": "Corrida", "value": "Corrida"},
                                ],
                                value="Motorista"
                            )
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Meta"),
                            dbc.Input(id="modal-meta", type="number", value=10)
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Realizado"),
                            dbc.Input(id="modal-realizado", type="number", value=0)
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Período"),
                            dbc.Input(id="modal-periodo", type="text", value="01/xx - 15/xx")
                        ], width=6),
                    ]),
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="close-add-modal", className="me-2"),
                dbc.Button("Adicionar", id="add-row", color="success"),
            ]),
        ], id="add-modal", is_open=False),

    ], fluid=True)
], style={"backgroundColor": "#f8f9fa", "minHeight": "100vh", "padding": "20px"})

# ==========================
# 4. CALLBACKS
# ==========================

# Atualiza opções dos filtros
@app.callback(
    [Output("filtro-fase", "options"),
     Output("filtro-cidade", "options"),
     Output("filtro-tipo", "options")],
    Input("tabela-metas", "data")
)
def update_filters_options(rows):
    df = pd.DataFrame(rows)
    return (
        [{"label": i, "value": i} for i in df["Fase"].unique()],
        [{"label": i, "value": i} for i in df["Cidade"].unique()],
        [{"label": i, "value": i} for i in df["Tipo"].unique()],
    )

# Abre/fecha modal
@app.callback(
    Output("add-modal", "is_open"),
    [Input("open-add-modal", "n_clicks"), Input("close-add-modal", "n_clicks")],
    [State("add-modal", "is_open")]
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Adiciona linha ou salva
@app.callback(
    Output("tabela-metas", "data"),
    [Input("add-row", "n_clicks"), Input("save-data", "n_clicks")],
    [State("tabela-metas", "data"),
     State("modal-fase", "value"),
     State("modal-cidade", "value"),
     State("modal-tipo", "value"),
     State("modal-meta", "value"),
     State("modal-realizado", "value"),
     State("modal-periodo", "value")]
)
def add_or_save_row(n_add, n_save, rows, fase, cidade, tipo, meta, realizado, periodo):
    ctx = dash.callback_context
    if not ctx.triggered:
        return rows

    prop_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if prop_id == "add-row":
        new_row = {
            "Fase": fase,
            "Cidade": cidade,
            "Tipo": tipo,
            "Meta": meta,
            "Realizado": realizado,
            "Unidade": "motoristas" if tipo == "Motorista" else "corridas",
            "Periodo": periodo
        }
        rows.append(new_row)
        return rows

    elif prop_id == "save-data":
        df = pd.DataFrame(rows)
        df.to_csv(CSV_FILE, index=False)
        return rows

    return rows

# Atualiza KPIs e gráficos
@app.callback(
    [Output("kpi-container", "children"),
     Output("grafico-progresso", "figure"),
     Output("grafico-financeiro", "figure"),
     Output("grafico-demografia", "figure")],
    [Input("tabela-metas", "data"),
     Input("filtro-fase", "value"),
     Input("filtro-cidade", "value"),
     Input("filtro-tipo", "value")]
)
def update_dashboard(rows, fases, cidades, tipos):
    df = pd.DataFrame(rows)
    df["Progresso (%)"] = (df["Realizado"] / df["Meta"]) * 100
    df["Progresso (%)"] = df["Progresso (%)"].round(2).fillna(0)

    # Filtra
    if fases:
        df = df[df["Fase"].isin(fases)]
    if cidades:
        df = df[df["Cidade"].isin(cidades)]
    if tipos:
        df = df[df["Tipo"].isin(tipos)]

    # KPIs
    motoristas_meta = df[df["Tipo"] == "Motorista"]["Meta"].sum() or 1
    motoristas_real = df[df["Tipo"] == "Motorista"]["Realizado"].sum()
    corridas_meta = df[df["Tipo"] == "Corrida"]["Meta"].sum() or 1
    corridas_real = df[df["Tipo"] == "Corrida"]["Realizado"].sum()

    kpi_cards = dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Motoristas", className="card-title"),
                    html.H3(f"{motoristas_real}/{motoristas_meta}", className="text-success"),
                    html.P(f"{motoristas_real / motoristas_meta * 100:.1f}%")
                ])
            ]), width=3),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Corridas", className="card-title"),
                    html.H3(f"{corridas_real}/{corridas_meta}", className="text-info"),
                    html.P(f"{corridas_real / corridas_meta * 100:.1f}%")
                ])
            ]), width=3),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Cidades", className="card-title"),
                    html.H3(len(df["Cidade"].unique()), className="text-warning"),
                    html.P("ativas")
                ])
            ]), width=3),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Metas", className="card-title"),
                    html.H3(len(df), className="text-secondary"),
                    html.P("registradas")
                ])
            ]), width=3),
    ])

    # Gráfico de progresso
    fig_progresso = px.bar(
        df,
        x="Cidade",
        y="Progresso (%)",
        color="Tipo",
        barmode="group",
        title="Progresso por Cidade",
        range_y=[0, 100],
        text="Progresso (%)",
        color_discrete_map={"Motorista": "#28a745", "Corrida": "#007bff"}
    )
    fig_progresso.update_traces(texttemplate='%{text:.1f}%', textposition='outside')

    # Dados financeiros (do documento)
    df_fin = pd.DataFrame([
        {"Fase": "Fase 1", "Pago": 2240, "Previsto": 1820},
        {"Fase": "Fase 2", "Pago": 3500, "Previsto": 3200},
        {"Fase": "Fase 3", "Pago": 4830, "Previsto": 4200},
    ])
    fig_fin = px.bar(df_fin, x="Fase", y=["Pago", "Previsto"], title="Orçamento por Fase (R$)",
                     barmode="stack", color_discrete_map={"Pago": "#28a745", "Previsto": "#ffc107"})

    # Demografia: metas 1º mês
    metas_1mes = {
        "Monte Verde": 19, "Nova Bandeirantes": 31, "Alta Floresta": 137,
        "Paranaíta": 25, "Colíder": 70, "Nova Canaã do Norte": 25, "Carlinda": 20
    }
    df_corr = df[df["Tipo"] == "Corrida"].copy()
    df_corr["Meta1Mes"] = df_corr["Cidade"].map(metas_1mes).fillna(0)

    fig_demog = go.Figure()
    fig_demog.add_bar(x=df_corr["Cidade"], y=df_corr["Meta1Mes"], name="Meta 1º Mês (Projeção)")
    fig_demog.add_bar(x=df_corr["Cidade"], y=df_corr["Meta"], name="Meta Estabelecida")
    fig_demog.update_layout(title="Meta 1º Mês: Projeção vs Planejada", barmode="group")

    return kpi_cards, fig_progresso, fig_fin, fig_demog

# ==========================
# 5. EXECUÇÃO
# ==========================
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
