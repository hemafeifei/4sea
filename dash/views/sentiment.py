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
import os

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

csv_path = '../../database/senti/weibo/'
today = datetime.today()
control_dt = str(today - relativedelta(days=1))[:10]


def ge_table(dataframe):
    df = dataframe.copy()
    df = df.rename(columns={'rank': '排名',
                            'topic': '话题',
                            'heat': '热度',})
    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        sort_action="native",
        style_cell={'fontSize': 13, 'font-family': 'sans-serif'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            # 'textAlign': 'center',
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'rank'},
                'textAlign': 'left',
            },
        ])


layout = html.Div([
    html.Div([
        html.P("Sentiment", className='title is-3'),
        html.Div([
            html.A("热搜榜", href='/sentiment', className='tag is-primary subtitle is-7'),
            html.A("市场情绪", href='/sentiment/market', className='tag subtitle is-7'),
            # html.A("ETF追踪", href='/wealth/etf', className='tag is-primary subtitle is-7'),
        ], className='row'),
    ],className='hero'),



    html.Div([
        # html.P("Weibo", className='tag is-info title is-7'),
        html.Div([
            # Row 1
            html.Div([
                html.Br(),
                html.Div([
                    html.Label('选择日期: ', className='title is-7'),
                    html.Br(),
                    dcc.DatePickerSingle(
                        id='senti-date-picker-single',
                        min_date_allowed=today - timedelta(days=365),
                        max_date_allowed=control_dt,
                        display_format='YYYY-MM-DD',
                        initial_visible_month=control_dt,
                        date=control_dt),

                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.P("实时热搜请前往：", className='title is-7'),
                    html.A("Weibo", href='https://s.weibo.com/top/summary?cate=realtimehot',),

                ]),
            ], className='column is-one-quarter'),

            html.Div([
                html.P("Internal Error", id='weibo-updated', className='title is-5', style={'textAlign': 'center'}),
                html.Div(id='weibo-table-1')
            ], className='column is-half'),


        ], className='columns'),
        # html.Hr(),
        # Row 2
        html.Div([
            html.Label("* Source: Weibo", style={'textAlign': 'center'}),
        ], className='columns')

    ], className='container')

], className='hero')


@app.callback(
    [Output('weibo-updated', 'children'),
    Output('weibo-table-1', 'children')],
    [Input('senti-date-picker-single', 'date'), ]
)
def refresh_etf_data(dt):
    effect_dt = str(dt)[:10]
    file = os.path.join(csv_path, "{}.txt".format(effect_dt))
    if os.path.exists(file):
        rank_df = pd.read_csv(file, usecols=['rank', 'topic', 'heat'])
    else:
        rank_df = pd.DataFrame(columns=['rank', 'topic', 'heat'])
    return "微博热搜榜 of {}".format(effect_dt), ge_table(rank_df)
