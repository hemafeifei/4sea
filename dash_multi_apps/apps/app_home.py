from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash
import os

from app import app
import plotly.graph_objs as go
from datetime import datetime, timedelta
import pandas as pd

today = str(datetime.now() -timedelta(hours=9))
tomorrow = str(pd.to_datetime(today[:10], format='%Y-%m-%d') + timedelta(days=1))
match_path ='/home/centos/football/data/match_data/'
odds_path = '/home/centos/football/data/odds_data/'
today_odds_path = odds_path+ today[:10]

match_nsc = pd.read_csv(match_path+ today[:10] + '.txt')
match_nsc_en = pd.read_csv(match_path+ today[:10] + '_en.txt')
match_nsc_all = pd.concat([match_nsc, match_nsc_en], ignore_index=True)


if os.path.exists(match_path + today[:10] + '_en.txt'):
    match_nsc_all = pd.concat([match_nsc, match_nsc_en], ignore_index=True)
else:
    today = pd.to_datetime('2018-12-10', format='%Y-%m-%d')
    match_nsc = pd.read_csv(match_path+ today[:10] + '.txt')
    match_nsc_en = pd.read_csv(match_path+ today[:10] + '_en.txt')
    match_nsc_all = pd.concat([match_nsc, match_nsc_en], ignore_index=True)
    tomorrow = str(pd.to_datetime(today[:10], format='%Y-%m-%d') + timedelta(days=1))


def get_match_type(lang):
    return list(match_nsc_all.loc[match_nsc_all.lang==str(lang)]['mtype'].unique())

def get_odds_eu(ref):
    df_eu = pd.read_csv(today_odds_path + '/' + str(ref) + '_eu.txt', index_col=False)
    return  df_eu[['home','draw','away','dt']]

def get_odds_asian(ref):
    df_asia = pd.read_csv(today_odds_path + '/' + str(ref) + '_asia.txt', index_col=False)
    return df_asia[['home', 'pankou' ,'away', 'dt']]


my_header = html.Div(
        style={
            'height': '80px',
            'backgroundColor': '#563D7B'
        },
        children=html.Div([
            html.Div([
                html.Div([
                    html.H4(children=" 顶级赛事赔率观测 |\nFootball match odds monitor"
                            , style={'textAlign': 'left',
                                     'color': '#F8F9FA', 'font-size': '24px', 'font': 'Bebas Neue'}),
                ], className='col m6'),
                html.Div([
                    html.H4(children="四海 | \nfoursea"
                            , style={'textAlign': 'right',
                                     'color': '#F8F9FA', 'font-size': '24px', 'font': 'Bebas Neue'}),
                ], className='col m6'),
            ], className="row"),

        ]),
        className="row gs-header gs-text-header"  # 'no-print'
    )


layout = html.Div([
    my_header,

    # html.Br(),
    html.Div([
        html.Br(style={'backgroundColor': '#2C3859', }),
        html.Div([dcc.Link(html.H5(html.Strong('Home')), href='/'), html.H6('今日赛事')],
                 className='col m4', style={'font-size': '14px', "textAlign": 'center', 'color': '#ADB9CA'}),
        html.Div([dcc.Link(html.H5(html.Strong('Result')), href='/history'), html.H6('历史查询')],
                 className='col m4', style={'font-size': '14px', "textAlign": 'center', 'color': '#ADB9CA'}),
        html.Div([dcc.Link(html.H5(html.Strong('Machine Learning')), href='/ml'), html.H6('赛事预测')],
                 className='col m4', style={'font-size': '14px', "textAlign": 'center', 'color': '#ADB9CA'}),
    ], className='row', style={'backgroundColor': '#2C3859', }),

    html.Div([




        html.Div([

            html.Div([
                html.Label('Match Day: {} to {} UTC+08:00'.format(today[:10], tomorrow[:10]), style={'font-size': '11px'}),
                dcc.Dropdown(
                    id='match-type-checklist',
                    #     options=option_type,
                    #     values=[option_type[i]['value'] for i in range(len(option_type))],
                    # labelStyle={'display': 'inline-block', 'font-size': '10px'},
                    multi=True
                ),
            ], className='col m4', style={'font-size': '11px', "textAlign": 'left',}),


            html.Div([
                html.Label('language', style={'display': 'inline-block', 'font-size': '12px'}),
                dcc.RadioItems(
                    id='lang-select',
                    options=[
                        {'label': 'EN', 'value': 'en'},
                        {'label': '中文', 'value': 'zh_cn'},

                    ],
                    value='en', labelStyle={'display': 'inline-block', 'font-size': '13px'}
                ),
            ], className='col m8', style={'font-size': '13px', "textAlign": 'right'}),

        ], className='row'),
        # html.Br([]),
        html.Div([
            # html.Div([],className='column', style={'font-size': '0.2rem'}),

            html.Div([

                html.Br(),

                html.Br(),
                dcc.RadioItems(id='href-dropdown',
                               labelStyle={'font-size': '13px'}

                               ),

                # html.Hr(),

            ],
                className='col m4', style={'height': '850px', 'overflowY': 'scroll'}),

            html.Div([
                html.Div([
                    dcc.Graph(
                        id='selected-odds-eu'

                    ),
                ], ),
                html.Div([
                    dcc.Graph(
                        id='selected-odds-asia',
                    ),
                ], ),

            ],
                className='col m8')

        ], className='row'),
    ], className='row'),
    html.H6(children="Contact & Copyright: 4sea.club@gmail.com",
            style={'textAlign': 'center', 'backgroundColor': '#2C3859',
                   'color': '#ADB9CA', 'font-size': '16px'}),



])


@app.callback(
    dash.dependencies.Output('match-type-checklist', 'options'),
    [dash.dependencies.Input('lang-select', 'value')])
def select_lang(selected_lang):
    match = match_nsc_all.loc[match_nsc_all['lang']==selected_lang].reset_index(drop=True)
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
    match = match_nsc_all.loc[match_nsc_all['lang']==selected_lang].reset_index(drop=True)
    effect_options = match.loc[(match['mtype'].isin(selected_match_type))].reset_index(drop=True)
    return [{"label": effect_options.loc[i, 'dt_utc08'][11:] + ' '+ effect_options.loc[i, 'mtype'] + ' ' + effect_options.loc[i, 'home'] + '-' + effect_options.loc[i, 'away'],
             "value": effect_options.loc[i, 'href_nsc']} for i in range(len(effect_options))]

@app.callback(
    dash.dependencies.Output('href-dropdown', 'value'),
    [dash.dependencies.Input('href-dropdown', 'options')])
def set_href_value(available_options):
    return available_options[0]['value']


@app.callback(
    dash.dependencies.Output('selected-odds-eu', 'figure'),
    [dash.dependencies.Input('href-dropdown', 'value')])
def set_selected_children(selected_href):
    df = get_odds_eu(selected_href)
    trace0 = go.Scatter(
        x = list(df['dt']),
        y = list(df['home']),
        name = 'home')
    trace1 = go.Scatter(
        x = list(df['dt']),
        y = list(df['away']),
        name = 'away')
    trace2 = go.Scatter(
        x = list(df['dt']),
        y = list(df['draw']),
        name = 'draw')
    data = [trace0, trace1, trace2]
    layout = dict(title='欧赔临场走势 - European Odds Trend',
                  # xaxis=dict(title='timeline'),
                  yaxis=dict(title='odds'))
    fig = dict(data=data, layout=layout)
    return fig

@app.callback(
    dash.dependencies.Output('selected-odds-asia', 'figure'),
    [dash.dependencies.Input('href-dropdown', 'value')])
def set_selected_children(selected_href):
    df = get_odds_asian(selected_href)
    trace0 = go.Scatter(
        x = list(df['dt']),
        y = list(df['home']),
        name = 'home')
    trace1 = go.Scatter(
        x = list(df['dt']),
        y = list(df['away']),
        name = 'away')

    data = [trace0, trace1]
    layout = dict(title='亚盘临场走势 - Asian Handicap Trend',
                  xaxis=dict(title='timeline'),
                  yaxis=dict(title='odds'))
    fig = dict(data=data, layout=layout)
    return fig