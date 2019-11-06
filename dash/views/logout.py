# Dash configuration
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from server import app

# Create app layout
layout = html.Div(children=[
    dcc.Location(id='url_logout', refresh=True),
    html.Div(
        className="container",
        children=[
            html.Div(
                html.Div(
                    className="container",
                    children=[
                        html.Div(
                            className="column is-12",
                            children=[
                                html.Br(),
                                html.Div('You have logged out - Please login to view the pages'),
                            ]
                        ),
                        html.Div(
                            className="column is-12",
                            # children=html.A(html.Button('LogOut'), href='/')
                            children=[
                                html.Br(),
                                html.Button(id='back-button', children='Go back', n_clicks=0)
                            ]
                        )
                    ], style={"textAlign": 'center'}
                )
            )
        ]
    )
])


# Create callbacks
@app.callback(Output('url_logout', 'pathname'),
              [Input('back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/'
