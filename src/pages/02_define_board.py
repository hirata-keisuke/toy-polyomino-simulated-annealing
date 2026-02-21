import dash
import dash_bootstrap_components as dbc
import json

from dash import html, dcc, Input, Output, State, callback_context


dash.register_page(__name__, path="/define-board", name="ボードの定義ページ", title="ボードの定義ページ")

layout = html.Div(
    style={"fontFamily": "Inter, sans-serif", "textAlign": "center", "padding": "20px"},
    children=[
        dcc.Store(id="board-grid-state", data=[]),
        html.H1("ボード形状の定義", style={"color": "#333", "marginBottom": "30px"}),
        html.Div(
            [
                html.P("行数と列数を入力してグリッドを生成し、セルをクリックして形状を決めてください。"),
                html.P("白いセルは配置可能、黒いセルは配置不可を表します。"),
            ],
            style={"fontSize": "1.1em", "color": "#555"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(id="board-rows-input", type="number", placeholder="行数", min=1, max=20, value=5),
                    width=2,
                ),
                dbc.Col(
                    dbc.Input(id="board-cols-input", type="number", placeholder="列数", min=1, max=20, value=5),
                    width=2,
                ),
                dbc.Col(
                    dbc.Button("グリッドを生成", id="generate-board-button", color="primary", n_clicks=0),
                    width="auto",
                ),
            ],
            justify="center",
            className="mb-4 mt-3",
            style={"gap": "10px"},
        ),
        html.Div(id="board-grid", style={"display": "inline-block", "marginBottom": "20px"}),
        html.Br(),
        dbc.Button(
            "設定してホームに戻る",
            id="set-board-button",
            color="success",
            n_clicks=0,
            style={"padding": "12px 25px", "marginTop": "10px", "marginBottom": "20px"},
        ),
        html.Div(id="validation-message", style={"color": "red", "marginTop": "10px"}),
        dcc.Location(id="redirect-to-home", refresh=True),
    ],
)


def _render_grid(grid):
    """grid (2D list of 0 or None) を Div のグリッドとしてレンダリングする"""
    rows = []
    for r, row in enumerate(grid):
        cells = []
        for c, val in enumerate(row):
            is_blocked = val is None
            cells.append(
                html.Div(
                    id={"type": "board-cell", "index": f"{r}-{c}"},
                    n_clicks=0,
                    style={
                        "width": "40px",
                        "height": "40px",
                        "backgroundColor": "#222" if is_blocked else "#fff",
                        "border": "1px solid #aaa",
                        "cursor": "pointer",
                        "boxSizing": "border-box",
                    },
                )
            )
        rows.append(html.Div(children=cells, style={"display": "flex"}))
    return html.Div(children=rows)


@dash.callback(
    Output("board-grid", "children"),
    Output("board-grid-state", "data"),
    Input("generate-board-button", "n_clicks"),
    State("board-rows-input", "value"),
    State("board-cols-input", "value"),
    prevent_initial_call=True,
)
def generate_grid(_n_clicks, rows, cols):
    if not rows or not cols or rows <= 0 or cols <= 0:
        return dash.no_update, dash.no_update
    grid = [[0] * int(cols) for _ in range(int(rows))]
    return _render_grid(grid), grid


@dash.callback(
    Output("board-grid", "children", allow_duplicate=True),
    Output("board-grid-state", "data", allow_duplicate=True),
    Input({"type": "board-cell", "index": dash.ALL}, "n_clicks"),
    State("board-grid-state", "data"),
    prevent_initial_call=True,
)
def toggle_cell(_n_clicks_list, grid):
    ctx = callback_context
    if not ctx.triggered or not grid:
        return dash.no_update, dash.no_update

    triggered_id_str = ctx.triggered[0]["prop_id"].split(".")[0]
    triggered_id = json.loads(triggered_id_str)
    if triggered_id["type"] != "board-cell":
        return dash.no_update, dash.no_update

    r_str, c_str = triggered_id["index"].split("-")
    r, c = int(r_str), int(c_str)

    current_val = grid[r][c]
    grid[r][c] = None if current_val == 0 else 0

    return _render_grid(grid), grid


@dash.callback(
    Output("validation-message", "children"),
    Output("redirect-to-home", "pathname"),
    Output("shared-data", "data", allow_duplicate=True),
    Input("set-board-button", "n_clicks"),
    State("board-grid-state", "data"),
    State("shared-data", "data"),
    prevent_initial_call=True,
)
def save_board(n_clicks, grid, store):
    if n_clicks == 0:
        return dash.no_update, dash.no_update, store
    if not grid:
        return "エラー: グリッドが生成されていません。", dash.no_update, store

    store["ボード"] = json.dumps(grid)
    return "", "/", store
