import dash
import dash_bootstrap_components as dbc
import json
import numpy as np

from dash import html, Input, Output, State, callback_context
from .piece import Piece

dash.register_page(__name__, path="/define-piece", name="ピースの定義ページ", title="ピースの定義ページ")

difine_piece_section = dbc.Col(
    html.Div(
        style={"fontFamily": "Inter, sans-serif", "textAlign": "center", "padding": "20px"}, 
        children=[
            html.H1("ピースの定義", style={"color": "#333", "marginBottom": "30px"}, id="piece-define-page-title"),
            html.Div([
                html.P("各テキストボックスにピースの行データを「0」と「1」のカンマ区切りで入力してください。"),
                html.P("「0」はピース上でミノが無い部分、「1」はミノがある部分を表します。")
            ], style={"fontSize": "1.1em", "color": "#555"}),
            dbc.Button(
                "行を追加", id="add-piece-row-button", n_clicks=0,
                style={"padding": "12px 25px", "marginTop": "30px", "marginBottom": "20px"}
            ),
            html.Div(id="textbox-container-piece", children=[], style={"display": "flex", "flexDirection": "column", "alignItems": "center"}),
            dbc.Button(
                "追加", color="success", id="add-piece-button", n_clicks=0,
                style={"padding": "12px 25px", "marginTop": "30px", "marginBottom": "20px"}
            )
        ]
    ), md=6)

display_pieces_section = dbc.Col(
    html.Div([
        html.H1("定義したピースの一覧"),
        html.Div(children=[], id="piece-display-area-sub", style={"textAlign": "center"})
    ]),
    md=6
)

layout = html.Div([dbc.Row([difine_piece_section, display_pieces_section])])


@dash.callback(
    Output("textbox-container-piece", "children"),
    Input("add-piece-row-button", "n_clicks"),
    State("textbox-container-piece", "children"),
    prevent_initial_call=True
)
def add_textbox(n_clicks, existing_children):
    new_row_id = f"row-{n_clicks}"
    new_textbox_id = f"textbox-{n_clicks}"

    new_row = html.Div([
        dbc.Input(
            id={"type": "board-input", "index": new_textbox_id},
            type="text", placeholder=f"(例: 0,1,1)",
        ),
        dbc.Button(
            "削除", id={"type": "remove-row-button", "index": new_row_id}, color="danger", n_clicks=0, 
            style={"margin": "5px", "fontSize": "0.9em", "width": "5em"}
        )
    ], id=new_row_id, style={"display": "flex", "alignItems": "center"})
    existing_children.append(new_row)
    return existing_children

@dash.callback(
    Output("textbox-container-piece", "children", allow_duplicate=True),
    Input({"type": "remove-row-button", "index": dash.ALL}, "n_clicks"),
    State("textbox-container-piece", "children"),
    prevent_initial_call=True
)
def remove_textbox(n_clicks_list, existing_children):
    ctx = callback_context
    if not ctx.triggered:
        return existing_children

    triggered_id = ctx.triggered[0]["prop_id"]
    button_id_str = triggered_id.split(".")[0]
    button_id = json.loads(button_id_str)
    
    if button_id["type"] == "remove-row-button" and ctx.triggered[0]["value"] > 0:
        row_to_remove_id = button_id["index"]
        new_children = [child for child in existing_children if child["props"]["id"] != row_to_remove_id]
        return new_children

    return dash.no_update

@dash.callback(
    Output("piece-display-area-sub", "children"), Output("shared-data", "data", allow_duplicate=True),
    Input("add-piece-button", "n_clicks"),
    State("textbox-container-piece", "children"), State("shared-data", "data"),
    prevent_initial_call=True
)
def add_piece(n_clicks, piece_definition_components, store):
    piece_definition_data = [
        c["props"]["children"][0]["props"]["value"].split(",") for c in piece_definition_components
        if c["props"]["children"][0]["props"].get("value") is not None
    ]
    
    if len(piece_definition_data) == 0 and len(store["ピース"]) == 0:
        return html.Div("表示するピースがありません。", style={"textAlign": "center", "marginTop": "20px"}), store
    
    try:
        np.array(piece_definition_data)
    except:
        return html.Div("形状が間違っています。全ての行の個数を同じにしてください。", style={"textAlign": "center", "marginTop": "20px"}), store
    
    pieces = [tuple(p) for p in store["ピース"]]
    if len(piece_definition_data) != 0:
        for row in piece_definition_data:
            for cell in row:
                if cell not in ("0", "1"):
                    return html.Div("無効な文字が使用されています。", style={"textAlign": "center", "marginTop": "20px"}), store

        piece = Piece(piece_definition_data)
        dumped_piece = piece.dump()
        if dumped_piece not in pieces:
            pieces.append(dumped_piece)
        store["ピース"] = list(pieces)

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
            html.Div(style={"display": "flex", "flex-direction": "column", "margin": "10px"}, 
                     children=rows))
    return html.Div(children=piece_display), store