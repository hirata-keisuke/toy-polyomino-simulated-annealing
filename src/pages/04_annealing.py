import dash
import json
import dash_bootstrap_components as dbc

from dash import html, Input, Output, State, dcc
from .solver import solve

dash.register_page(__name__, path="/annealing", name="シミュレーションアニーリング法", title="シミュレーションアニーリング法")

board_display = dbc.Col(
    html.Div(
        children = [
            html.H1("現在のボード"),
            html.Div(
                children=[], id="board-display-area-annealing", 
                style={"display": "flex", "justifyContent": "center", "alignItems": "center", "minHeight": "200px"}
            )
        ], style={"alignItems": "center"}), md=6)

piece_display = dbc.Col(
    html.Div(
        children = [
            html.H1("定義したピースの一覧"),
            html.Div(
                children=[], id="piece-display-area-annealing",
                style={"display": "flex", "justifyContent": "center", "alignItems": "center", "minHeight": "200px"}
            )
        ]), md=6)

run_button_row = dbc.Col([
    dbc.Row(dbc.Input(id="num_reads", type="number", placeholder=f"探索の回数", style={"margin": "5px"})),
    dbc.Row(dbc.Button("実行", id="run-solver", color="primary", n_clicks=0))],
    width={"size": 6, "offset": 3}, className="text-center mt-4"
)



layout = html.Div(
    [
        dbc.Row([board_display, piece_display]), dbc.Row(run_button_row), 
        dcc.Loading(dcc.Location(id="redirect-to-result", refresh=True), type="circle")
    ], 
    style={"color": "#333", "justifyContent": "center"})

@dash.callback(
    Output("board-display-area-annealing", "children"),
    Input("shared-data", "data"),
)
def show_board_display(store):
    if store["ボード"] is None:
        return html.P("まだボードは定義されていません。", style={"color": "#777"})
    board_data_json = store["ボード"]
    try:
        board = json.loads(board_data_json)
    except json.JSONDecodeError:
        return html.P("ボードデータの解析に失敗しました。", style={"color": "red"})

    if not isinstance(board, list) or not all(isinstance(row, list) for row in board):
        return html.P("無効なボードデータ形式です。", style={"color": "red"})

    rows = []
    for row in board:
        cells = []
        for cell_value in row:
            cell_color = "white" if cell_value == 0 else "black"
            cell_style = {
                "width": "30px", 
                "height": "30px",
                "backgroundColor": cell_color,
                "border": "1px solid #eee",
                "display": "flex",
                "color": "#333" if cell_color == "white" else "#eee"
            }
            cells.append(html.Div(style=cell_style))
        rows.append(html.Div(style={"display": "flex"}, children=cells))

    return html.Div(children=rows)

@dash.callback(
    Output("piece-display-area-annealing", "children"),
    Input("shared-data", "data"),
)
def show_piece_display(store):
    if len(store["ピース"]) == 0:
        return html.P("まだピースは定義されていません。", style={"color": "#777"})

    pieces = [tuple(p) for p in store["ピース"]]
    piece_display = []
    for piece_id, piece in enumerate(pieces):
        rows = []
        grid = json.loads(piece[0])
        color = piece[1]
        for row in grid:
            cells = []
            for cell_value in row:
                if cell_value == 1:
                    cell_color = color
                else:
                    cell_color = "white"
                cell_style = {
                    "width": "30px", 
                    "height": "30px",
                    "backgroundColor": cell_color,
                    "border": "1px solid #eee",
                    "display": "flex",
                    "color": "#333" if cell_color == "white" else "#eee"
                }
                cells.append(html.Div(style=cell_style))
            rows.append(html.Div(style={"display": "flex", "justifyContent": "center"}, children=cells))
        rows.append(
            dbc.Input(
                id={"type": "piece-num", "index": piece_id}, value=1,
                type="number", placeholder=f"使えるピースの数", style={"margin": "5px"}
            )
        )
        piece_display.append(
            html.Div(style={"display": "flex", "flex-direction": "column", "margin": "10px"}, 
                     children=rows))

    return html.Div(children=piece_display)

@dash.callback(
    Output("redirect-to-result", "pathname"), Output("shared-data", "data", allow_duplicate=True),
    Input("run-solver", "n_clicks"),
    State("shared-data", "data"), State({"type": "piece-num", "index": dash.ALL}, "value"), State("num_reads", "value"),
    prevent_initial_call=True
)
def run_solver(n_clicks, store, piece_nums, num_reads):
    if n_clicks == 0 or num_reads is None or num_reads <= 0:
        return "/annealing", store
    board = json.loads(store["ボード"])
    piece_data = store["ピース"]
    pieces = [json.loads(d[0]) for d in piece_data]
    piece_ids = [i+1 for i in range(len(piece_data))]
    reason, result, summary = solve(board, pieces, piece_ids, piece_nums, num_reads)
    store["result_summary"] = summary

    store["結果"] = json.dumps(result)
    store["結果文字"] = reason
    return "/show-result", store
