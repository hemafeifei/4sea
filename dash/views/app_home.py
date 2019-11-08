# -*- coding: utf-8 -*
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash
import os

from server import app
import plotly.graph_objs as go
from datetime import datetime, timedelta
import pandas as pd

today = str(datetime.now() - timedelta(hours=11, days=0))  # for fixing
tomorrow = str(pd.to_datetime(today[:10], format='%Y-%m-%d') + timedelta(days=1))
match_path = '../../database/football/match_data/'
odds_path = '../../database/football/odds_data/'
today_odds_path = odds_path + today[:10]

match_nsc = pd.read_csv(match_path + today[:10] + '.txt')
match_nsc_en = pd.read_csv(match_path + today[:10] + '_en.txt')
match_nsc_all = pd.concat([match_nsc, match_nsc_en], ignore_index=True)

if os.path.exists(match_path + today[:10] + '_en.txt'):
    match_nsc_all = pd.concat([match_nsc, match_nsc_en], ignore_index=True)
else:
    today = pd.to_datetime('2019-10-06', format='%Y-%m-%d')
    match_nsc = pd.read_csv(match_path + today[:10] + '.txt')
    match_nsc_en = pd.read_csv(match_path + today[:10] + '_en.txt')
    match_nsc_all = pd.concat([match_nsc, match_nsc_en], ignore_index=True)
    tomorrow = str(pd.to_datetime(today[:10], format='%Y-%m-%d') + timedelta(days=1))


def get_match_type(lang):
    return list(match_nsc_all.loc[match_nsc_all.lang == str(lang)]['mtype'].unique())


def get_odds_eu(ref):
    df_eu = pd.read_csv(today_odds_path + '/' + str(ref) + '_eu.txt', index_col=False)
    return df_eu[['home', 'draw', 'away', 'dt']]


def get_odds_asian(ref):
    df_asia = pd.read_csv(today_odds_path + '/' + str(ref) + '_asia.txt', index_col=False)
    return df_asia[['home', 'pankou', 'away', 'dt']]



layout = html.Div([

    # page_header,
    html.Div([
            html.P("Football", className='title is-3'),
            html.Div([
                html.A("今日赛事", href='/football', className='tag is-primary subtitle is-7'),
                html.A("历史回查", href='/football/his', className='tag subtitle is-7'),
                html.A("赛果预测", href='/football/ml', className='tag subtitle is-7'),
                html.A("Labs", href='/football/mllabs', className='tag subtitle is-7'),

                # html.A(" 外汇 ", ),
            ], className='row'),

        ], className='hero'),

    html.Div([

        html.Div([

            html.Div([
                html.Label('比赛日: {} to {} UTC+08:00'.format(today[:10], tomorrow[:10]),
                           style={'font-size': '12px'}),
                # html.Label("选择联赛：",className='title is-7'),
                dcc.Dropdown(
                    id='match-type-checklist',
                    #     options=option_type,
                    #     values=[option_type[i]['value'] for i in range(len(option_type))],
                    multi=True
                ),
            ], className='column is-one-third', style={'font-size': '12px',
                                                       "textAlign": 'left',
                                                       }),

            html.Div([
                html.Label('language', style={'display': 'inline-block', 'font-size': '12px'}),
                dcc.RadioItems(
                    id='lang-select',
                    options=[
                        # {'label': 'EN', 'value': 'en'},
                        {'label': '中文', 'value': 'zh_cn'},
                    ],
                    value='zh_cn', labelStyle={'display': 'inline-block', 'font-size': '13px'},
                    # className='char-btn'
                ),
            ], className='column is-two-thirds', style={'font-size': '13px', "textAlign": 'right'}),

        ], className='columns'),

        html.Div([
            # html.Div([],className='column', style={'font-size': '0.2rem'}),

            html.Div([
                html.Hr(),
                html.Label("选择赛事：",className='title is-7'),
                dcc.RadioItems(id='href-dropdown',
                               labelStyle={'display': 'inline-block',
                                            'font-size':13,
                                           'text-align': 'vertical',
                                           'margin-right': 30}),

            ], className='column is-one-third', style={'height': '850px', 'overflowY': 'scroll', 'font-size': '14px'}),

            html.Div([
                html.H5(id='selected-match', className='title is-5', style={"textAlign": 'center'}),
                html.Div([
                    dcc.Graph(id='selected-odds-eu'),], ),
                html.Div([
                    dcc.Graph(id='selected-odds-asia',),], ),
            ], className='column is-two-thirds')

        ], className='columns'),
    ], className='container'),

], className='hero')


@app.callback(
    dash.dependencies.Output('match-type-checklist', 'options'),
    [dash.dependencies.Input('lang-select', 'value')])
def select_lang(selected_lang):
    match = match_nsc_all.loc[match_nsc_all['lang'] == selected_lang].reset_index(drop=True)
    mtype = list(match['mtype'].unique())
    return [{'label': mtype[i], 'value': mtype[i]} for i in range(len(mtype))]


@app.callback(
    dash.dependencies.Output('match-type-checklist', 'value'),
    [dash.dependencies.Input('match-type-checklist', 'options')])
def set_match(match_type_options):
    return [match_type_options[i]['value'] for i in range(len(match_type_options))]


@app.callback(
    dash.dependencies.Output('href-dropdown', 'options'),
    [dash.dependencies.Input('lang-select', 'value'),
     dash.dependencies.Input('match-type-checklist', 'value')]
)
def set_href_options(selected_lang, selected_match_type):
    match = match_nsc_all.loc[match_nsc_all['lang'] == selected_lang].reset_index(drop=True)
    effect_options = match.loc[(match['mtype'].isin(selected_match_type))].reset_index(drop=True)
    return [{"label": effect_options.loc[i, 'dt_utc08'][11:] + ' ' + effect_options.loc[i, 'mtype'] + ' ' +
                      effect_options.loc[i, 'home'] + '-' + effect_options.loc[i, 'away'],
             "value": effect_options.loc[i, 'href_nsc']} for i in range(len(effect_options))]


@app.callback(
    dash.dependencies.Output('href-dropdown', 'value'),
    [dash.dependencies.Input('href-dropdown', 'options')])
def set_href_value(available_options):
    return available_options[0]['value']


@app.callback(
    [dash.dependencies.Output('selected-match', 'children'),
    dash.dependencies.Output('selected-odds-eu', 'figure'),],
    [dash.dependencies.Input('href-dropdown', 'value')])
def set_selected_children(selected_href):
    match = match_nsc.loc[match_nsc['href_nsc']==selected_href]['home'] + '-' + \
            match_nsc.loc[match_nsc['href_nsc']==selected_href]['away']

    df = get_odds_eu(selected_href)
    trace0 = go.Scatter(
        x=list(df['dt']),
        y=list(df['home']),
        name='home')
    trace1 = go.Scatter(
        x=list(df['dt']),
        y=list(df['away']),
        name='away')
    trace2 = go.Scatter(
        x=list(df['dt']),
        y=list(df['draw']),
        name='draw')
    data = [trace0, trace1, trace2]
    layout = dict(title='欧赔临场走势 - European Odds Trend',
                  # xaxis=dict(title='timeline'),
                  yaxis=dict(title='odds'))
    fig = dict(data=data, layout=layout)
    return match, fig


@app.callback(
    dash.dependencies.Output('selected-odds-asia', 'figure'),
    [dash.dependencies.Input('href-dropdown', 'value')])
def set_selected_children(selected_href):
    df = get_odds_asian(selected_href)
    trace0 = go.Scatter(
        x=list(df['dt']),
        y=list(df['home']),
        name='home')
    trace1 = go.Scatter(
        x=list(df['dt']),
        y=list(df['away']),
        name='away')

    data = [trace0, trace1]
    layout = dict(title='亚盘临场走势 - Asian Handicap Trend',
                  xaxis=dict(title='timeline'),
                  yaxis=dict(title='odds'))
    fig = dict(data=data, layout=layout)
    return fig
