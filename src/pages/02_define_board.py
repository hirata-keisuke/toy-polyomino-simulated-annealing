import dash
import dash_bootstrap_components as dbc
import json

from dash import html, dcc, Input, Output, State, callback_context


dash.register_page(__name__, path="/define-board", name="ボードの定義ページ", title="ボードの定義ページ")

layout = html.Div(style={"fontFamily": "Inter, sans-serif", "textAlign": "center", "padding": "20px"}, children=[
    html.H1("ボード形状の定義", style={"color": "#333", "marginBottom": "30px"}),
    html.Div([
        html.P("各テキストボックスにボードの行データを「0」と「None」のカンマ区切りで入力してください。"),
        html.P("「0」はミノを配置可能なセルを表し、「None」はミノを配置不可能なセルを表します。")
    ], style={"fontSize": "1.1em", "color": "#555"}),
    dbc.Button(
        "行を追加", id="add-board-row-button", color="primary", n_clicks=0,
        style={"padding": "12px 25px", "marginTop": "30px", "marginBottom": "20px"}
    ),
    html.Div(id="textbox-container-board", children=[], style={"display": "flex", "flexDirection": "column", "alignItems": "center"}),
    dbc.Button(
        "設定してホームに戻る", id="set-board-button", color="success", n_clicks=0,
        style={"padding": "12px 25px", "marginTop": "30px", "marginBottom": "20px"}
    ),
    html.Div(id="validation-message", style={"color": "red", "marginTop": "10px"}),
    dcc.Location(id="redirect-to-home", refresh=True)
])

@dash.callback(
    Output("textbox-container-board", "children"),
    Input("add-board-row-button", "n_clicks"),
    State("textbox-container-board", "children"),
    prevent_initial_call=True
)
def add_textbox(n_clicks, existing_children):
    new_row_id = f"row-{n_clicks}"
    new_textbox_id = f"textbox-{n_clicks}"

    new_row = html.Div([
        dbc.Input(
            id={"type": "board-input", "index": new_textbox_id},
            type="text", placeholder=f"(例: 0,None,0)",
        ),
        dbc.Button(
            "削除", id={"type": "remove-row-button", "index": new_row_id}, color="danger", n_clicks=0, 
            style={"margin": "5px", "fontSize": "0.9em", "width": "5em"}
        )
    ], id=new_row_id, style={"display": "flex", "alignItems": "center"})
    existing_children.append(new_row)
    return existing_children

@dash.callback(
    Output("textbox-container-board", "children", allow_duplicate=True),
    Input({"type": "remove-row-button", "index": dash.ALL}, "n_clicks"),
    State("textbox-container-board", "children"),
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
    Output("validation-message", "children"), Output("redirect-to-home", "pathname"),
    Output("shared-data", "data", allow_duplicate=True),
    Input("set-board-button", "n_clicks"),
    State("shared-data", "data"), State({"type": "board-input", "index": dash.ALL}, "value"),
    prevent_initial_call=True
)
def set_board_and_redirect(n_clicks, store, board_input_values):
    if n_clicks is None or n_clicks == 0:
        return dash.no_update, dash.no_update, store

    if not board_input_values:
        return "エラー: ボードの行がありません。", dash.no_update, store

    board = []
    col_count = -1
    for _, row_str in enumerate(board_input_values):
        if row_str is None:
            return f"エラー: 値を入力してください。", dash.no_update, store

        elements = [e.strip() for e in row_str.split(",")]
        current_row = []
        for elem in elements:
            if elem == "0":
                current_row.append(0)
            elif elem == "None":
                current_row.append(None)
            else:
                return f"エラー: 無効な値が含まれています。0 または None を使用してください。", dash.no_update, store

        if col_count == -1:
            col_count = len(current_row)
        elif len(current_row) != col_count:
            return f"エラー: 行の列数が一致していません。", dash.no_update, store
        
        board.append(current_row)
    board_json = json.dumps(board)
    store["ボード"] = board_json

    return "", "/", store

