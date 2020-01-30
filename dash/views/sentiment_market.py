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
        style_data_conditional=[
            {
                'if': {'column_id': 'rank'},
                'textAlign': 'left',
            },
        ])

csv_path = '../../database/senti/jisilu/'
today = datetime.today()
control_dt = str(today - relativedelta(days=1))[:10]

parm_dict = {'reply': '回帖数',
             'viewers': '浏览数',
             'title': '主题数'}
raw_df = pd.concat([pd.read_csv(os.path.join(csv_path, f), index_col=False) for f in os.listdir(csv_path)],
                   axis=0, ignore_index=True)
raw_df = raw_df[['topic', 'title', 'reply', 'viewers', 'updated']]
raw_df['date'] = [i[:10] for i in list(raw_df['updated'])]

rank_df = raw_df.drop_duplicates(subset=['topic', 'title'], keep='first')
rank_df = rank_df.drop(['date'], axis=1).sort_values('reply', ascending=False).head(10)
raw_grouped = raw_df.groupby('date')['title', 'reply', 'viewers'].agg({'title': 'count',
                                                                       'reply': 'sum',
                                                                       'viewers':'sum'}).reset_index()

layout = html.Div([
    html.Div([
        html.P("Sentiment", className='title is-3'),
        html.Div([
            html.A("热搜榜", href='/sentiment', className='tag subtitle is-7'),
            html.A("市场情绪", href='/sentiment/market', className='tag is-primary subtitle is-7'),
            # html.A("ETF追踪", href='/wealth/etf', className='tag is-primary subtitle is-7'),
        ], className='row'),
    ],className='hero'),

    html.Div([
        html.Br(),
        html.P("投资论坛热度", className='title is-5'),
        html.Div([
            # Row 1

            html.Div([
                html.Label('Checkboxes'),
                dcc.Checklist(
                    id='senti-checklist-multi',
                    # multi=True,
                    labelStyle={'display': 'inline-block',
                                'font-size': 13,
                                'text-align': 'vertical',
                                'margin-right': 50},
                    options=[
                        {'label': '活跃话题数', 'value': 'title'},
                        {'label': '话题回帖数', 'value': 'reply'},
                        {'label': '话题浏览数', 'value': 'viewers'},

                    ],
                    value=['title']
                ),
            ], className='column is-one-fifth'),

            html.Div([
                html.P("活跃度走势", className='title is-7', style={'textAlign': 'center'}),
                dcc.Graph(id='jisilu-trend'),
                # dcc.Graph(id='price-trend'),

                html.Hr(),
                html.P("热门话题 Top 10", className='title is-7', style={'textAlign': 'center'}),
                html.P(ge_table(rank_df) ,id='table-jisilu',),

            ], className='column is-four-fifths'),


        ], className='columns'),
        # html.Hr(),
        # Row 2
        html.Div([
            html.Label("* Source: ******", style={'textAlign': 'center'}),
        ], className='columns')

    ], className='container')

], className='hero')


@app.callback(
    dash.dependencies.Output('jisilu-trend', 'figure'),
    [dash.dependencies.Input('senti-checklist-multi', 'value'), ])
def render_content(cols):
    sel_cols = ['date']
    sel_cols.extend(cols)
    df_trend = raw_grouped[sel_cols]
    df_trend['date'] = pd.to_datetime(df_trend['date'])
    # for col in df_trend.columns:
    #     if col in ['txn_sec_top100', 'txn_sec_msci_top100', 'txn_etf_top50']:
    #         df_trend[col] = (df_trend[col] / 1e4).astype(int)

    traces = []
    for col in df_trend.columns:
        if col != 'date':
            trace = go.Scatter(x=list(df_trend['date']),
                               y=list(df_trend[col]),
                               name=parm_dict[col])
            traces.append(trace)

    _data = traces
    _layout = dict(
        xaxis=dict(title='Date'),
        yaxis=dict(title='# of matter'))
    fig = dict(data=_data, layout=_layout)

    return fig
