import dash
import dash_bootstrap_components as dbc
import json

from dash import html, dcc, Input, Output, State, callback_context
from .piece import Piece


dash.register_page(__name__, path="/define-piece", name="ピースの定義ページ", title="ピースの定義ページ")

layout = html.Div(
    [
        dcc.Store(id="piece-grid-state", data=[]),
        dbc.Row(
            [
                # 左カラム: ピース定義
                dbc.Col(
                    html.Div(
                        style={"fontFamily": "Inter, sans-serif", "textAlign": "center", "padding": "20px"},
                        children=[
                            html.H1("ピースの定義", style={"color": "#333", "marginBottom": "30px"}),
                            html.Div(
                                [
                                    html.P("行数と列数を入力してグリッドを生成し、セルをクリックしてピース形状を決めてください。"),
                                    html.P("色付きセルがミノのある部分です。"),
                                ],
                                style={"fontSize": "1.1em", "color": "#555"},
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Input(id="piece-rows-input", type="number", placeholder="行数", min=1, max=10, value=3),
                                        width=3,
                                    ),
                                    dbc.Col(
                                        dbc.Input(id="piece-cols-input", type="number", placeholder="列数", min=1, max=10, value=3),
                                        width=3,
                                    ),
                                    dbc.Col(
                                        dbc.Button("グリッドを生成", id="generate-piece-button", color="primary", n_clicks=0),
                                        width="auto",
                                    ),
                                ],
                                justify="center",
                                className="mb-4 mt-3",
                                style={"gap": "10px"},
                            ),
                            html.Div(id="piece-grid", style={"display": "inline-block", "marginBottom": "20px"}),
                            html.Br(),
                            dbc.Button(
                                "追加",
                                color="success",
                                id="add-piece-button",
                                n_clicks=0,
                                style={"padding": "12px 25px", "marginTop": "10px", "marginBottom": "20px"},
                            ),
                            html.Div(id="piece-validation-message", style={"color": "red", "marginTop": "10px"}),
                        ],
                    ),
                    md=6,
                ),
                # 右カラム: 定義済みピース一覧
                dbc.Col(
                    html.Div(
                        [
                            html.H1("定義したピースの一覧"),
                            html.Div(children=[], id="piece-display-area-sub", style={"textAlign": "center"}),
                        ]
                    ),
                    md=6,
                ),
            ]
        ),
    ]
)


def _render_piece_grid(grid, color="#4A90D9"):
    """grid (2D list of 0 or 1) をクリック可能な Div グリッドとしてレンダリングする"""
    rows = []
    for r, row in enumerate(grid):
        cells = []
        for c, val in enumerate(row):
            is_filled = val == 1
            cells.append(
                html.Div(
                    id={"type": "piece-cell", "index": f"{r}-{c}"},
                    n_clicks=0,
                    style={
                        "width": "40px",
                        "height": "40px",
                        "backgroundColor": color if is_filled else "#fff",
                        "border": "1px solid #aaa",
                        "cursor": "pointer",
                        "boxSizing": "border-box",
                    },
                )
            )
        rows.append(html.Div(children=cells, style={"display": "flex"}))
    return html.Div(children=rows)


def _render_piece_list(pieces):
    """保存済みピースのリストを表示用 Div として返す"""
    piece_display = []
    for piece in pieces:
        grid = json.loads(piece[0])
        color = piece[1]
        rows = []
        for row in grid:
            cells = []
            for cell_value in row:
                cell_color = color if cell_value == 1 else "white"
                cells.append(
                    html.Div(
                        style={
                            "width": "30px",
                            "height": "30px",
                            "backgroundColor": cell_color,
                            "border": "1px solid #eee",
                        }
                    )
                )
            rows.append(html.Div(style={"display": "flex", "justifyContent": "center"}, children=cells))
        piece_display.append(
            html.Div(style={"display": "flex", "flexDirection": "column", "margin": "10px"}, children=rows)
        )
    return html.Div(children=piece_display, style={"display": "flex", "flexWrap": "wrap", "justifyContent": "center"})


@dash.callback(
    Output("piece-grid", "children"),
    Output("piece-grid-state", "data"),
    Input("generate-piece-button", "n_clicks"),
    State("piece-rows-input", "value"),
    State("piece-cols-input", "value"),
    prevent_initial_call=True,
)
def generate_piece_grid(_n_clicks, rows, cols):
    if not rows or not cols or rows <= 0 or cols <= 0:
        return dash.no_update, dash.no_update
    grid = [[0] * int(cols) for _ in range(int(rows))]
    return _render_piece_grid(grid), grid


@dash.callback(
    Output("piece-grid", "children", allow_duplicate=True),
    Output("piece-grid-state", "data", allow_duplicate=True),
    Input({"type": "piece-cell", "index": dash.ALL}, "n_clicks"),
    State("piece-grid-state", "data"),
    prevent_initial_call=True,
)
def toggle_piece_cell(_n_clicks_list, grid):
    ctx = callback_context
    if not ctx.triggered or not grid:
        return dash.no_update, dash.no_update

    triggered_id_str = ctx.triggered[0]["prop_id"].split(".")[0]
    triggered_id = json.loads(triggered_id_str)
    if triggered_id["type"] != "piece-cell":
        return dash.no_update, dash.no_update

    r_str, c_str = triggered_id["index"].split("-")
    r, c = int(r_str), int(c_str)

    grid[r][c] = 0 if grid[r][c] == 1 else 1

    return _render_piece_grid(grid), grid


@dash.callback(
    Output("piece-display-area-sub", "children"),
    Output("piece-validation-message", "children"),
    Output("shared-data", "data", allow_duplicate=True),
    Input("add-piece-button", "n_clicks"),
    State("piece-grid-state", "data"),
    State("shared-data", "data"),
    prevent_initial_call=True,
)
def add_piece(_n_clicks, grid, store):
    pieces = [tuple(p) for p in store["ピース"]]

    if not grid:
        if not pieces:
            return html.Div("表示するピースがありません。"), "", store
        return _render_piece_list(pieces), "", store

    # 1が一つもない場合はエラー
    flat = [v for row in grid for v in row]
    if all(v == 0 for v in flat):
        return _render_piece_list(pieces), "エラー: ミノが選択されていません。", store

    piece = Piece([[str(v) for v in row] for row in grid])
    dumped = piece.dump()
    if dumped not in pieces:
        pieces.append(dumped)
    store["ピース"] = list(pieces)

    return _render_piece_list(pieces), "", store
