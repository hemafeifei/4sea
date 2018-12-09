from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from app import app
from apps import app_home, app_his, app_ml


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
         return app_home.layout
    elif pathname == '/ml_his':
         return app_his.layout
    elif pathname == '/ml':
         return app_ml.layout

    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)