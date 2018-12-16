from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
# import numpy as np
# import dash_table_experiments as dash_table
# import plotly.figure_factory as ff
import dash
import os
import _pickle as cPickle

from app import app
# import plotly.graph_objs as go
from datetime import datetime, timedelta
import pandas as pd

today = str(datetime.now() -timedelta(hours=11))
tomorrow = str(pd.to_datetime(today[:10], format='%Y-%m-%d') + timedelta(days=1))
cur_path = '/home/centos/football/4sea'
data_path = '/home/centos/football/data'
model_path = '/home/centos/football/model'
match_path = data_path + '/match_data/'
match_nsc = pd.read_csv(match_path+ today[:10] + '.txt')
match_nsc_en = pd.read_csv(match_path+ today[:10] + '_en.txt')
match_nsc_all = pd.concat([match_nsc, match_nsc_en], ignore_index=True)
ml_pred = pd.read_csv(cur_path + '/ml_prediction.txt')

differ_path = data_path + '/differ_data/'
differ_file = differ_path + today[:10] + '.txt'
ml_path = data_path + '/ml_data/'

dummy_data = pd.read_csv(cur_path + '/league_dummy.txt')
now = datetime.today()
idx = (now.weekday() + 1) % 7
sat = now - timedelta(7+idx-6)
enddate = datetime.now() -timedelta(days=1 ,hours=10)
his_path = data_path + '/his_data/'


def create_table(df):
    return html.Iframe(srcDoc=df.to_html())

def generate_table(dataframe, max_rows=15):
    return html.Table(
        # Header
        [html.Tr([html.Th(col, style={'text-align': 'center'}) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col], style={'text-align': 'center'}) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

def get_differ_data(file, time_differ=20):
    if os.path.exists(file):
        df_differ = pd.read_csv(differ_file, header=None, names = ['Time', 'League', 'Home', 'Away', 'Trend', 'Updated', 'href_nsc', 'Handicap', 'hw1', 'dw1', 'aw1',
        'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw'])
        df_differ = df_differ.drop_duplicates(subset=['Time', 'League', 'Home', 'Away', 'Trend', 'href_nsc'], keep='last')
        df_differ = df_differ[['Trend', 'href_nsc', 'Updated', 'Handicap']]

    else:
        df_differ = pd.DataFrame(columns=['Trend', 'href_nsc', 'Updated', 'Handicap'])
    return df_differ

def calculate_proba(file):
    if os.path.exists(file):
        df_tmp = pd.read_csv(file, header=None, names = ['Time', 'League', 'Home', 'Away', 'Trend', 'Updated', 'href_nsc', 'Handicap', 'hw1', 'dw1', 'aw1',
        'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw'])
        df_tmp = df_tmp.drop_duplicates(subset=['Time', 'League', 'Home', 'Away', 'Trend', 'href_nsc'], keep='last')

        tmp = df_tmp.merge(ml_pred, on=['League', 'Handicap', 'Trend'], how='inner')
        if len(tmp) > 0:
            df_num = tmp[['hw1', 'dw1', 'aw1', 'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw']]
            with open(model_path + '/std_scaler_94.pickle', 'rb') as f:
                std_scaler = cPickle.load(f)
            df_num_scaled = std_scaler.transform(df_num)

            df_dummy = pd.DataFrame(tmp['League']).merge(dummy_data, on='League', how='left')
            df_dummy = df_dummy.drop('League', axis=1)
            X_data = pd.concat([pd.DataFrame(df_num_scaled), df_dummy], axis=1)

            with open(model_path + '/model_lgb_94.pickle', 'rb') as f2:
                clf = cPickle.load(f2)
            y_pred = clf.predict(X_data)
            tmp['Probability'] = [round(i, 2) for i in y_pred]
            tmp = tmp[['href_nsc', 'Probability']]
        else:
            tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])
    else:
        tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])

    return tmp


def get_match_his(date, lang):
    his_nsc = pd.read_csv(his_path + 'nsc_his_' + str(date)[:10] + '.txt')
    his_nsc_en = pd.read_csv(his_path + 'en_his_' + str(date)[:10]  + '.txt')
    his_nsc_all = pd.concat([his_nsc, his_nsc_en], ignore_index=True)
    return his_nsc_all.loc[his_nsc_all.lang==str(lang)].reset_index(drop=True)


def get_differ_his(date):
    differ_his_file = differ_path + str(date)[:10] + '.txt'

    if os.path.exists(differ_his_file):
        df_differ = pd.read_csv(differ_his_file, header=None, names = ['Time', 'League', 'Home', 'Away', 'Trend', 'Updated', 'href_nsc', 'Handicap', 'hw1', 'dw1', 'aw1',
        'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw'])
        df_differ = df_differ.drop_duplicates(subset=['Time', 'League', 'Home', 'Away', 'Trend', 'href_nsc'], keep='last')
        df_differ = df_differ[['Trend', 'href_nsc', 'Updated', 'Handicap']]

    else:
        df_differ = pd.DataFrame(columns=['Trend', 'href_nsc', 'Updated', 'Handicap'])

    df_proba = calculate_proba(differ_his_file)
    return df_differ, df_proba


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
                 className='col m4 ', style={'font-size': '14px', "textAlign": 'center', 'color': '#ADB9CA'}),
    ], className='row', style={'backgroundColor': '#2C3859', }),
    # html.Br(),

    html.Div([
        html.Div([
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
            ], className='col m12', style={'font-size': '13px', "textAlign": 'right'}),

        ], className='row'),

        html.H4("1X2 Prediction"),

        html.Div([
            html.Div([
                html.Label("This prediction is based on odds trend.", style={'font-size': '13px',}),
                html.Label("预测胜平负,赛前1小时内根据赔率变化不断更新预测结果.", style={'font-size': '13px',}),
                html.H6("Please check the Prediction column  of right side table."),
                html.H6("H = Home 胜"),
                html.H6("D = Draw 平"),
                html.H6("A = Away 负"),
                html.H6("Deep = 深盘(亚盘)"),
                # html.H6("Shallow = 浅盘(亚盘)"),
                html.H6("Balanced = 平衡盘(亚盘)"),

            ], className='col m4'),
            html.Div([
                html.Div(children=[
                    html.H5(children='Today\'s Prediction', style={ "textAlign": 'center'}),
                    html.Div(id='table-container'),
                    # generate_table(df_differ)
                ])
            ], className='col m8')

        ], className='row'),

        html.Br([]),
        html.Br([]),
        html.H5("Prediction History"),

        html.Div([
            html.Div([
                html.Label('Choose History Date: ', style={'font-size': '11px'}),
                dcc.DatePickerSingle(
                    id='my-date-picker-single',
                    min_date_allowed=enddate - timedelta(days=21),
                    max_date_allowed=enddate,
                    display_format='YYYY-MM-DD',
                    initial_visible_month=enddate,
                    date=sat),

            ], className='col m4'),
            html.Div([
                html.Div(children=[
                    html.H5(children='History Prediction', style={"textAlign": 'center'}),
                    html.Div(id='table-container-2'),
                    # generate_table(df_differ)
                ])
            ], className='col m8')

        ], className='row'),


        html.Br([]),
        html.H5("Score Prediction (in testing)"),
        html.Div([
            # html.Div([],className='column', style={'font-size': '0.2rem'}),

            html.Div([
                html.Label("This prediction is based on team and player info.", style={'font-size': '13px',}),
                html.Label("预测主客进球数.", style={'font-size': '13px'}),
                html.H6("We will use at least 4-6 rounds of the match statistics to train the model, it is coming in October."),
                html.Br([]),

                html.Div([
                    html.Label("Choose League", style={'font-size': '11px'}),
                    dcc.Dropdown(
                        id='league-dropdown',
                        options=[
                            {'label': 'ENG PR', 'value': 'ENG PR'},
                            {'label': 'GER D1', 'value': 'GER D1'},


                        ],
                        value= 'ENG PR',

                        multi=False),
                ], className='col m6', style={'font-size': '12px', "textAlign": 'left'}),
                # html.Br([]),
                html.Div([
                    html.Label("Choose Round", style={'font-size': '11px'}),

                    dcc.Dropdown(
                        id='round-dropdown',

                        multi=False),
                ], className='col m6', style={'font-size': '12px', "textAlign": 'left'}),



            ],
                className='col m4', style={'height': '600px', "textAlign": 'left', }),

            html.Div([
                html.Div(children=[
                    html.H5(children='Match Schedule', style={ "textAlign": 'center'}),
                    html.Div(id='datatable')
                ]),






            ],
                className='col m8')

        ], className='row'),
    ], className='row'),
    html.H6(children="Contact & Copyright: 4sea.club@gmail.com",
            style={'textAlign': 'center', 'backgroundColor': '#2C3859',
                   'color': '#ADB9CA', 'font-size': '16px'}),



])


@app.callback(Output('table-container', 'children'),
              [Input('lang-select', 'value')])
def update_table(value):
    df = match_nsc_all.loc[match_nsc_all.lang==value]# update with your own logic
    df_differ = get_differ_data(differ_file)
    dff = pd.merge(df_differ, df, on='href_nsc', how='left')

    dff = dff.rename(columns={'mtype':'League', 'dt_utc08':'Time', 'home':'Home', 'away':"Away"})
    dff = dff[['href_nsc', 'League', 'Time', 'Home', 'Away','Handicap', 'Updated', 'Trend']]
    dff['Time'] = [i[5:] for i in dff['Time'].values]
    dff = dff.merge(ml_pred, on=['League', 'Handicap', 'Trend'], how='left')

    df_proba = calculate_proba(differ_file)
    if len(df_proba) > 0:
        dff = dff.merge(df_proba, on='href_nsc', how='left')

        # dff = dff.rename(columns={'href_nsc': 'ID'})
        dff = dff[['Time', 'League', 'Home', 'Away', 'Updated','Handicap', 'Trend', 'Prediction', 'Probability']]
    else:

        dff = dff[['Time', 'League', 'Home', 'Away', 'Updated','Handicap', 'Trend', 'Prediction']]

    # dff['Updated'] = [str(i)[11:16] for i in dff['Updated'].values]
    return generate_table(dff.tail(15))


@app.callback(
    dash.dependencies.Output('table-container-2', 'children'),
    [dash.dependencies.Input('my-date-picker-single', 'date'),
     dash.dependencies.Input('lang-select', 'value')])
def select_lang(date, value):
    match_his = get_match_his(str(date), value)
    differ_his, df_proba = get_differ_his(date)

    dff = pd.merge(differ_his, match_his, on='href_nsc', how='left')
    dff = dff.rename(columns={'mtype': 'League', 'dt_utc08': 'Time', 'home': 'Home', 'away': "Away"})
    dff = dff[['href_nsc', 'League', 'Time', 'Home', 'result', 'Away', 'Handicap', 'Updated', 'Trend']]
    dff['Time'] = [i[5:] for i in dff['Time'].values]
    dff = dff.merge(ml_pred, on=['League', 'Handicap', 'Trend'], how='left')

    if len(df_proba) > 0:
        dff = dff.merge(df_proba, on='href_nsc', how='left')

        # dff = dff.rename(columns={'href_nsc': 'ID'})
        dff = dff[['Time', 'League', 'Home', 'result', 'Away', 'Updated','Handicap', 'Trend', 'Prediction', 'Probability']]
    else:

        dff = dff[['Time', 'League', 'Home', 'result', 'Away', 'Updated','Handicap', 'Trend', 'Prediction']]

    # dff['Updated'] = [str(i)[11:16] for i in dff['Updated'].values]
    return generate_table(dff)


