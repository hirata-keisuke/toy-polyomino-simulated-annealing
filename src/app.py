import argparse
import dash
import dash_bootstrap_components as dbc

from dash import Dash, html, dcc

app = Dash("ポリオミノ配置探索", use_pages=True, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
links = dict(sorted([(k,v) for k, v in dash.page_registry.items()], key=lambda x: x[0].split(".")[1]))

sidebar = html.Div(
    [
        html.Div("ページメニュー"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(html.Div(page["name"], className="ms-2"), href=page["path"], active="exact")
                for page in links.values()
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        "background-color": "#f8f9fa",
        "zIndex": 1
    }
)

app.layout = html.Div([
    dcc.Store(id='shared-data', data={"ボード": None, "ピース": [], "ピース枚数": [], "結果": None, "結果文字": "", "resule_summary": ""}, storage_type="session"),
    sidebar,
    html.Div(
        [dash.page_container],
        style={
            "margin-left": "16rem",
            "padding": "2rem 1rem",
            "background-color": "#AFDFE4",
            "min-height": "100vh",
            "box-sizing": "border-box"
        }
    )
])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ポリオミノ配置探索アプリ")
    parser.add_argument("--debug", type=bool, default=False, help="デバッグモードフラグ")
    args = parser.parse_args()
    
    app.run(debug=args.debug)

