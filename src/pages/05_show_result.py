import dash
import json

from dash import html, Input, Output, dash_table

dash.register_page(__name__, path="/show-result", name="結果の表示", title="結果の表示")

layout = html.Div(style={"fontFamily": "Inter, sans-serif", "textAlign": "center", "padding": "20px"}, children=[
    html.H1("探索された配置", style={"color": "#333", "marginBottom": "30px"}),
    html.Div(
        children=[], id="result-display-area",
        style={"display": "flex", "justifyContent": "center", "alignItems": "center", "minHeight": "200px"}
    )
])


@dash.callback(
    Output("result-display-area", "children"),
    Input("shared-data", "data")
)
def show_board_display(store):
    if store["結果"] is None:
        return html.P("まだ、探索されていません。", style={"color": "#777"})
    board_data_json = store["結果"]
    try:
        board = json.loads(board_data_json)
    except json.JSONDecodeError:
        return html.P("ボードデータの解析に失敗しました。", style={"color": "red"})

    if not isinstance(board, list) or not all(isinstance(row, list) for row in board):
        return html.P("無効なボードデータ形式です。", style={"color": "red"})

    pieces = [tuple(p) for p in store["ピース"]]
    colors = {i+1: p[1] for i, p in enumerate(pieces)}
    rows = []
    for row in board:
        cells = []
        for cell_value in row:
            cell_color = "white" if cell_value == 0 else "black" if cell_value is None else colors[int(cell_value.split("-")[0])]
            cell_style = {
                "width": "50px", 
                "height": "50px",
                "backgroundColor": cell_color,
                "border": "1px solid #eee" if cell_color == "white" else "1px solid #fff" if cell_color=="black" else "1px solid #000",
                "display": "flex",
                "color": "#333" if cell_color == "white" else "#eee" if cell_color=="black" else "#000"
            }
            cells.append(html.Div(f"{cell_value}", style=cell_style))
        rows.append(html.Div(style={"display": "flex"}, children=cells))

    summary = json.loads(store["result_summary"])
    return html.Div([
        html.Div(children=rows), html.P(store["結果文字"]),
        dash_table.DataTable(
            [{"種別": k, "回数": v} for k, v in summary.items()],
            [{"name": "種別", "id": "種別"}, {"name": "回数", "id": "回数"}])
    ])
