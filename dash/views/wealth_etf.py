# -*- coding: utf-8 -*
import warnings
# Dash configuration
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import dash_dangerously_set_inner_html
from server import app
# import chart_studio.plotly as py
import plotly.graph_objs as go

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os

csv_path = '../../database/finance/etf/'
fn = sorted(os.listdir(csv_path))[-2]
raw_df = pd.read_csv(os.path.join(csv_path, fn))

if len(raw_df) > 0:
    etf_type = list(raw_df['name'])
    eft_type_options = [{'label': etf_type[i], 'value': etf_type[i]} for i in range(len(etf_type))]
    kept_etf_type = ['上证50', '沪深300', '中证500','中证红利', '纳指100', '标普500', '恒生指数', '创业板', '德国DAX']
else:
    eft_type_options = None
    kept_etf_type = None


def ge_table(dataframe):
    df = dataframe.copy()
    df = df.rename(columns={'name': '指数',
                                          'pe_pct': 'pe百分位(%)',
                                          'pb_pct': 'pb百分位(%)',
                                          'dyr': '股息率',
                                          })
    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        sort_action="native",
        style_cell={'fontSize': 13, 'font-family': 'sans-serif'},
        style_data_conditional=[
            {
                'if': {'column_id': '指数'},
                'textAlign': 'left',
            },
        ])

layout = html.Div([
    html.Div([
        html.P("Finance", className='title is-3'),
        html.Div([
            html.A("全球指数", href='/wealth', className='tag is subtitle is-7'),
            html.A("沪深市场", href='/wealth/sec', className='tag subtitle is-7'),
            html.A("ETF追踪", href='/wealth/etf', className='tag is-primary subtitle is-7'),
            # html.A(" 外汇 ", ),
        ], className='row'),
    ],className='hero'),

    html.Div([
        html.Div([
            # Row 1
            html.Div([
                html.Br(),
                html.Br(),
                html.Br(),
                html.Label('选择指数: ', className='title is-7'),
                dcc.Dropdown(
                            id='etf-type-checklist',
                            options=eft_type_options,
                            # options=[eft_type_options[i]['value'] for i in range(len(eft_type_options))],
                            value=kept_etf_type,
                            multi=True
                                ),

            ], className='column is-one-third', style={'font-size': '12px', "textAlign": 'left',}),

            html.Div([
                html.H5("ETF指数估值表", className='title is-5', style={'textAlign': 'center'}),
                html.P("Internal Error", id='etf-updated', className='title is-7', style={'textAlign': 'left'}),
                html.Div(id='etf-table-1')

            ], className='column is-two-thirds')


        ], className='columns'),
        # html.Hr(),
        # Row 2
        html.Div([
            html.Label("* Source: Xueqiu", style={'textAlign': 'center'}),
        ], className='columns')

    ], className='container')

], className='hero')


@app.callback(
    [Output('etf-updated', 'children'),
    Output('etf-table-1', 'children')],
    [Input('etf-type-checklist', 'value'), ]
)
def refresh_etf_data(type):
    selected_df = raw_df.loc[raw_df.name.isin(type)].reset_index(drop=True)
    updated_dt = selected_df['dt'][0]
    selected_df = selected_df.drop(['code_xq', 'dt'], axis=1)
    return "Last updated on {}".format(updated_dt), ge_table(selected_df)