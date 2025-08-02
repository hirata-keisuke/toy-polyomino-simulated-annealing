import dash
import json
import dash_bootstrap_components as dbc
from dash import html, Input, Output, State

dash.register_page(__name__, path="/", name="表示画面", title="表示画面")

board_display = dbc.Col(
    html.Div(
        children = [
            html.H1("現在のボード"),
            dbc.Button(
                "ボードをリセット", color="warning", id="reset-board", n_clicks=0,
                style={"display": "flex", "justifyContent": "center", "alignItems": "center"}
            ),
            html.Div(
                children=[], id="board-display-area-home", 
                style={"display": "flex", "justifyContent": "center", "alignItems": "center", "minHeight": "200px"}
            )
        ], style={"alignItems": "center"}))

piece_display = dbc.Col(
    html.Div(
        children = [
            html.H1("定義したピースの一覧"),
            dbc.Button(
                "ピースをリセット", color="warning", id="reset-piece", n_clicks=0,
                style={"display": "flex", "justifyContent": "center", "alignItems": "center"}
            ),
            html.Div(
                children=[], id="piece-display-area-home",
                style={"display": "flex", "justifyContent": "center", "alignItems": "center", "minHeight": "200px"}
            )
        ]), md=6)

layout = html.Div([dbc.Row([board_display, piece_display])], style={"color": "#333"})


@dash.callback(
    Output("shared-data", "data", allow_duplicate=True),
    Input("reset-board", "n_clicks"),
    State("shared-data", "data"),
    prevent_initial_call=True
)
def reset_board(n_clicks, store):
    if n_clicks > 0:
        store["ボード"] = None
    return store

@dash.callback(
    Output("shared-data", "data", allow_duplicate=True),
    Input("reset-piece", "n_clicks"),
    State("shared-data", "data"),
    prevent_initial_call=True
)
def reset_piece(n_clicks, store):
    if n_clicks > 0:
        store["ピース"] = []
    return store

@dash.callback(
    Output("board-display-area-home", "children"),
    Input("shared-data", "data"),
)
def update_board_display(store):
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
    Output("piece-display-area-home", "children"),
    Input("shared-data", "data"),
)
def update_piece_display(store):
    if len(store["ピース"]) == 0:
        return html.P("まだピースは定義されていません。", style={"color": "#777"})

    pieces = [tuple(p) for p in store["ピース"]]
    piece_display = []
    for piece in pieces:
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
            cells.append(html.Br())
            rows.append(html.Div(style={"display": "flex", "justifyContent": "center"}, children=cells))
        piece_display.append(
            html.Div(style={"display": "flex", "flex-direction": "column", "margin": "10px"}, children=rows))

    return html.Div(children=piece_display)
