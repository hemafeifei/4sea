# -*- coding: utf-8 -*
import dash
import dash_core_components as dcc
import dash_html_components as html

from server import app
import plotly.graph_objs as go
from datetime import datetime, timedelta
import pandas as pd

enddate = datetime.now() - timedelta(days=1, hours=10)
# tomorrow = str(pd.to_datetime(str(enddate)[:10], format='%Y-%m-%d') + timedelta(days=1))
data_path = '../../database/football/'
his_path = data_path + 'his_data/'
odds_path = data_path + 'odds_data/'


def get_match_all(date, lang):
    his_nsc = pd.read_csv(his_path + 'nsc_his_' + str(date)[:10] + '.txt')
    # his_nsc_en = pd.read_csv(his_path + 'en_his_' + str(date)[:10]  + '.txt')
    # his_nsc_all = pd.concat([his_nsc, his_nsc_en], ignore_index=True)
    his_nsc_all = his_nsc
    return his_nsc_all.loc[his_nsc_all.lang == str(lang)].reset_index(drop=True)


def get_odds_eu(date, ref):
    df_eu = pd.read_csv(odds_path + str(date)[:10] + '/' + str(ref) + '_eu.txt', index_col=False)
    return df_eu[['home', 'draw', 'away', 'dt']]


def get_odds_asian(date, ref):
    df_asia = pd.read_csv(odds_path + str(date)[:10] + '/' + str(ref) + '_asia.txt', index_col=False)
    return df_asia[['home', 'pankou', 'away', 'dt']]


layout = html.Div([

    html.Div([
        html.P("Football", className='title is-3'),
        html.Div([
            html.A("今日赛事", href='/football', className='tag subtitle is-7'),
            html.A("历史回查", href='/football/his', className='tag is-primary subtitle is-7'),
            html.A("赛果预测", href='/football/ml', className='tag subtitle is-7'),
            html.A("Labs", href='/football/mllabs', className='tag subtitle is-7'),



            # html.A(" 外汇 ", ),
        ], className='row'),

    ], className='hero'),

    # html.Br(),
    html.Div([
        html.Div([
            html.Div([
                html.Label('选择日期: ', className='title is-7'),
                html.Br(),
                dcc.DatePickerSingle(
                    id='my-date-picker-single',
                    min_date_allowed=enddate - timedelta(days=7),
                    max_date_allowed=enddate,
                    display_format='YYYY-MM-DD',
                    initial_visible_month=enddate,
                    date=enddate),

                html.Div([
                    dcc.Dropdown(
                        id='match-type-checklist_his',
                        multi=True),
                ]),
                html.Hr()
            ], className='column is-one-third', style={'font-size': '12px', "textAlign": 'left'}),

            html.Div([
                html.Label('language', style={'font-size': '12px'}),
                dcc.RadioItems(
                    id='lang-select',
                    options=[
                        # {'label': 'EN', 'value': 'en'},
                        {'label': '中文', 'value': 'zh_cn'},
                        # {'label': '繁体', 'value': 'td_cn'},

                    ],
                    value='zh_cn', labelStyle={'font-size': '13px'}
                ),
            ], className='column is-two-thirds', style={'font-size': '13px', "textAlign": 'right'}),
            # html.Div(id='his-table'
            #          , className='column is-two-thirds'),

        ], className='columns'),
        # html.Br([]),
        html.Div([
            html.Div([
                # html.Label('Match Day: {} to {} UTC+08:00'.format(today[:10], tomorrow[:10])),
                html.Br(),
                html.Label("选择赛事：", className='title is-7'),
                dcc.RadioItems(id='href-dropdown_his',
                               labelStyle={'display': 'inline-block',
                                           'font-size': 13,
                                           'text-align': 'vertical',
                                           'margin-right': 20}

                               ), ], className='column is-one-third', style={'height': '850px', 'overflowY': 'scroll'}),
            html.Div([
                html.Div([
                    dcc.Graph(id='selected-odds-eu_his'),
                ], ),
                html.Div([
                    dcc.Graph(id='selected-odds-asia_his', ),
                ], ),
            ], className='column is-two-thirds')

        ],
            className='columns'),
    ], className='section'),

])


@app.callback(
    dash.dependencies.Output('match-type-checklist_his', 'options'),
    [dash.dependencies.Input('my-date-picker-single', 'date'),
     dash.dependencies.Input('lang-select', 'value')])
def select_lang(date, selected_lang):
    match_all = get_match_all(str(date[:10]), selected_lang)
    mtype = list(match_all['mtype'].unique())
    return [{'label': mtype[i], 'value': mtype[i]} for i in range(len(mtype))]


@app.callback(
    dash.dependencies.Output('match-type-checklist_his', 'value'),
    [dash.dependencies.Input('match-type-checklist_his', 'options')])
def set_match(match_type_options):
    return [match_type_options[i]['value'] for i in range(len(match_type_options))]


@app.callback(
    dash.dependencies.Output('href-dropdown_his', 'options'),
    [dash.dependencies.Input('my-date-picker-single', 'date'),
     dash.dependencies.Input('lang-select', 'value'),
     dash.dependencies.Input('match-type-checklist_his', 'value')]
)
def set_href_options(date, selected_lang, selected_match_type):
    match_nsc_all = get_match_all(date[:10], selected_lang)
    effect_options = match_nsc_all.loc[(match_nsc_all['mtype'].isin(selected_match_type))].reset_index(drop=True)
    return [{"label": effect_options.loc[i, 'dt_utc08'][11:] + ' ' + effect_options.loc[i, 'mtype'] + ' ' + '(' +
                      effect_options.loc[i, 'result'] + ')' + ' ' + effect_options.loc[i, 'home'] + '-' +
                      effect_options.loc[i, 'away'],
             "value": effect_options.loc[i, 'href_nsc']} for i in range(len(effect_options))]


@app.callback(
    dash.dependencies.Output('href-dropdown_his', 'value'),
    [dash.dependencies.Input('href-dropdown_his', 'options')])
def set_href_value(available_options):
    return available_options[0]['value']


@app.callback(
    dash.dependencies.Output('selected-odds-eu_his', 'figure'),
    [dash.dependencies.Input('my-date-picker-single', 'date'),
     dash.dependencies.Input('href-dropdown_his', 'value')])
def set_selected_children(date, selected_href):
    df = get_odds_eu(date, selected_href)
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
    layout = dict(title='欧赔历史走势 - European Odds Trend',
                  # xaxis=dict(title='timeline'),
                  yaxis=dict(title='odds'))
    fig = dict(data=data, layout=layout)
    return fig


@app.callback(
    dash.dependencies.Output('selected-odds-asia_his', 'figure'),
    [dash.dependencies.Input('my-date-picker-single', 'date'),
     dash.dependencies.Input('href-dropdown_his', 'value')])
def set_selected_children(date, selected_href):
    df = get_odds_asian(date, selected_href)
    trace0 = go.Scatter(
        x=list(df['dt']),
        y=list(df['home']),
        name='home')
    trace1 = go.Scatter(
        x=list(df['dt']),
        y=list(df['away']),
        name='away')

    data = [trace0, trace1]
    layout = dict(title='亚盘历史走势 - Asian Handicap Trend',
                  xaxis=dict(title='timeline'),
                  yaxis=dict(title='odds'))
    fig = dict(data=data, layout=layout)
    return fig
