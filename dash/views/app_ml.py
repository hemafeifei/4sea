# -*- coding: utf-8 -*
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash
import dash_table
import os
import _pickle as cPickle
from server import app
# import plotly.graph_objs as go
from datetime import datetime, timedelta
import pandas as pd


today = str(datetime.now() - timedelta(hours=11, days=0))
tomorrow = str(pd.to_datetime(today[:10], format='%Y-%m-%d') + timedelta(days=1))
cur_path = './'
config_path = 'config/'
data_path = '../../database/football/'
model_path = '../../model/'
match_path = data_path + 'match_data/'
match_nsc = pd.read_csv(match_path + today[:10] + '.txt')
# match_nsc_en = pd.read_csv(match_path + today[:10] + '_en.txt')
# match_nsc_all = pd.concat([match_nsc, match_nsc_en], ignore_index=True)
match_nsc_all = match_nsc

df_name = pd.read_csv((os.path.join(config_path, 'league_name.txt')), encoding='utf8')
ml_pred = pd.read_csv(os.path.join(config_path, 'ml_prediction_98_more.txt'))
scaler_file_1 = 'std_scaler_98_more.pickle'

# model 2: nosclaer v1.6
ml_pred_new = pd.read_csv(os.path.join(config_path, 'ml_prediction_98_more.txt'))
# scaler_file_2 = '/std_scaler_94_more.pickle'
model_file_2_1 = 'v1.6_lgb_98_more.pickle'
model_file_2_2 = 'v1.6_svm_98_more.pickle'
model_file_2_3 = 'v1.6_lr_98_more.pickle'

kelly_filter = pd.read_csv(os.path.join(config_path, 'ml_kelly_filter.txt'))

# model 3: svm_94_reduced
ml_pred_3 = pd.read_csv(os.path.join(config_path, 'ml_prediction_94_reduced.txt'))
scaler_file_3 = 'std_scaler_94_reduced.pickle'
model_file_3_1 = 'model_lgb_94_reduced.pickle'
model_file_3_2 = 'model_svm_94_reduced.pickle'

# model HKJC
model_file_6_1 = 'v1.7_lgb_98_more.pickle'
model_file_6_2 = 'v1.7_svm_98_more.pickle'
model_file_6_3 = 'v1.7_lr_98_more.pickle'

differ_path = data_path + 'differ_data/'
differ_file = differ_path + today[:10] + '.txt'
ml_path = data_path + 'ml_data/'
dummy_data = pd.read_csv(os.path.join(config_path, 'league_dummy.txt'))

now = datetime.today()

# added on 2019-08
trend_begin_file = differ_path + today[:10] + '_gl.txt'

if os.path.exists(trend_begin_file):
    trend_begin = pd.read_csv(trend_begin_file, index_col=False)
    trend_begin = trend_begin[['dt_utc08', 'league', 'home', 'away', 'trend', 'updated']]
    trend_begin = trend_begin.rename(columns={"dt_utc08": "time"})
    trend_begin['time'] = [i[5:] for i in trend_begin['time'].values]
else:
    trend_begin = pd.DataFrame(columns=['time', 'league', 'home', 'away', 'trend', 'updated'])

trend_latest_file = differ_path + today[:10] + '_gl_latest.txt'


def create_table(df):
    return html.Iframe(srcDoc=df.to_html())


def generate_table(dataframe, max_rows=20):
    return html.Table(
        # Header
        [html.Tr([html.Th(col, style={'text-align': 'center'}) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col], style={'text-align': 'center'}) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

def easy_table(dataframe):
    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in dataframe.columns],
        data=dataframe.to_dict('records'),
        sort_action="native",
        style_cell={'fontSize': 13, 'font-family': 'sans-serif'},
        style_data_conditional=[
            {
                'if': {'column_id': '指数'},
                'textAlign': 'left',
            },
            ])


def get_differ_data(file, time_differ=20):
    if os.path.exists(file):
        df_differ = pd.read_csv(differ_file, header=None, names=['Time', 'League', 'Home', 'Away', 'Trend', 'Updated',
                                                                 'href_nsc', 'Handicap', 'hw1', 'dw1', 'aw1', 'hw2',
                                                                 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1',
                                                                 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw', 'differ_dw',
                                                                 'differ_aw', 'kelly_sum'])
        df_differ = df_differ.drop_duplicates(subset=['Time', 'League', 'Home', 'Away', 'Trend', 'href_nsc'],
                                              keep='last')
        df_differ = df_differ[['Trend', 'href_nsc', 'Updated', 'Handicap', 'hw1', 'dw1', 'aw1', 'hw2', 'dw2', 'aw2',
                               'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw', 'differ_dw',
                               'differ_aw', 'kelly_sum']]

    else:
        df_differ = pd.DataFrame(
            columns=['Trend', 'href_nsc', 'Updated', 'Handicap', 'hw1', 'dw1', 'aw1', 'hw2', 'dw2', 'aw2',
                     'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw',
                     'kelly_sum'])
    return df_differ


def get_differ_gl10oal(gl_file):
    if os.path.exists(gl_file):
        df_differ = pd.read_csv(gl_file, header=None,
                                names=['Time', 'League', 'Home', 'Away', 'Trend', 'Updated', 'link', 'Handicap', 'hw1',
                                       'dw1', 'aw1',
                                       'hw2', 'dw2', 'aw2', 'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum'])
        df_differ = df_differ.drop_duplicates(subset=['Time', 'League', 'Home', 'Away', 'Trend', 'link'], keep='last')
        df_differ = df_differ[
            ['Time', 'League', 'Home', 'Away', 'Trend', 'Updated', 'Handicap', 'link', 'hw1', 'dw1', 'aw1', 'hw2',
             'dw2', 'aw2',
             'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum']]

    else:
        df_differ = pd.DataFrame(
            columns=['Time', 'League', 'Home', 'Away', 'Trend', 'Updated', 'Handicap', 'link', 'hw1', 'dw1', 'aw1',
                     'hw2', 'dw2', 'aw2',
                     'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum'])
    return df_differ


def calculate_proba(df_differ_filter, rules_data, scaler, model):
    if len(df_differ_filter) > 0:
        df_tmp = df_differ_filter.copy()
        # effective Trend
        tmp = df_tmp.merge(rules_data, on=['League', 'Handicap', 'Trend'], how='inner')
        if len(tmp) > 0:
            df_num = tmp[['hw1', 'dw1', 'aw1', 'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2',
                          'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw']]
            with open(model_path + scaler, 'rb') as f:
                std_scaler = cPickle.load(f)
            df_num_scaled = std_scaler.transform(df_num)

            df_dummy = pd.DataFrame(tmp['League']).merge(dummy_data, on='League', how='left')
            df_dummy = df_dummy.drop('League', axis=1).reset_index(drop=True)
            X_data = pd.concat([pd.DataFrame(df_num_scaled), df_dummy], axis=1)

            with open(model_path + model, 'rb') as f2:
                clf = cPickle.load(f2)
            y_pred = clf.predict(X_data)
            tmp['Probability'] = [round(i, 2) for i in y_pred]
            tmp = tmp[['href_nsc', 'Probability']]
        else:
            tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])
    else:
        tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])

    return tmp


def calculate_proba_ks(df_differ_filter, rules_data, scaler, model):
    if len(df_differ_filter) > 0:
        df_tmp = df_differ_filter.copy()
        # effective Trend
        tmp = df_tmp.merge(rules_data, on=['League', 'Handicap', 'Trend'], how='inner')
        if len(tmp) > 0:
            df_num = tmp[['hw1', 'dw1', 'aw1', 'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2',
                          'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum']]
            with open(model_path + scaler, 'rb') as f:
                std_scaler = cPickle.load(f)
            df_num_scaled = std_scaler.transform(df_num)

            df_dummy = pd.DataFrame(tmp['League']).merge(dummy_data, on='League', how='left')
            df_dummy = df_dummy.drop('League', axis=1).reset_index(drop=True)
            X_data = pd.concat([pd.DataFrame(df_num_scaled), df_dummy], axis=1)

            with open(model_path + model, 'rb') as f2:
                clf = cPickle.load(f2)
            y_pred = clf.predict(X_data)
            tmp['Probability'] = [round(i, 2) for i in y_pred]
            tmp = tmp[['href_nsc', 'Probability']]
        else:
            tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])
    else:
        tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])

    return tmp


def calculate_proba_ks_svm(df_differ_filter, rules_data, scaler, model):
    if len(df_differ_filter) > 0:
        df_tmp = df_differ_filter.copy()
        # effective Trend
        tmp = df_tmp.merge(rules_data, on=['League', 'Handicap', 'Trend'], how='inner')
        if len(tmp) > 0:
            df_num = tmp[['hw1', 'dw1', 'aw1', 'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2',
                          'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum']]
            with open(model_path + scaler, 'rb') as f:
                std_scaler = cPickle.load(f)
            df_num_scaled = std_scaler.transform(df_num)

            df_dummy = pd.DataFrame(tmp['League']).merge(dummy_data, on='League', how='left')
            df_dummy = df_dummy.drop('League', axis=1).reset_index(drop=True)
            X_data = pd.concat([pd.DataFrame(df_num_scaled), df_dummy], axis=1)

            with open(model_path + model, 'rb') as f2:
                clf = cPickle.load(f2)
            y_pred_proba = clf.predict_proba(X_data)[:, 1]
            tmp['Probability'] = [round(i, 2) for i in list(y_pred_proba)]
            tmp = tmp[['href_nsc', 'Probability']]
        else:
            tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])
    else:
        tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])

    return tmp

# edited on 2019-05-18, delete stack method, added noscaler methods
def calculate_proba_ks_noscaler(df_differ_filter, rules_data, model):
    if len(df_differ_filter) > 0:
        df_tmp = df_differ_filter.copy()
        # effective Trend
        tmp = df_tmp.merge(rules_data, on=['League', 'Handicap', 'Trend'], how='inner')
        if len(tmp) > 0:
            df_num = tmp[['hw1', 'dw1', 'aw1', 'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2',
                          'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum']]
            df_dummy = pd.DataFrame(tmp['League']).merge(dummy_data, on='League', how='left')
            df_dummy = df_dummy.drop('League', axis=1).reset_index(drop=True)
            X_data = pd.concat([pd.DataFrame(df_num), df_dummy], axis=1)

            with open(model_path + model, 'rb') as f2:
                clf = cPickle.load(f2)
            y_pred = clf.predict(X_data)
            tmp['Probability'] = [round(i, 2) for i in y_pred]
            tmp = tmp[['href_nsc', 'Probability']]
        else:
            tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])
    else:
        tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])

    return tmp


def calculate_proba_ks_svm_noscaler(df_differ_filter, rules_data, model):
    if len(df_differ_filter) > 0:
        df_tmp = df_differ_filter.copy()
        # effective Trend
        tmp = df_tmp.merge(rules_data, on=['League', 'Handicap', 'Trend'], how='inner')
        if len(tmp) > 0:
            df_num = tmp[['hw1', 'dw1', 'aw1', 'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2',
                          'kly_a2', 'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum']]

            df_dummy = pd.DataFrame(tmp['League']).merge(dummy_data, on='League', how='left')
            df_dummy = df_dummy.drop('League', axis=1).reset_index(drop=True)
            X_data = pd.concat([pd.DataFrame(df_num), df_dummy], axis=1)

            with open(model_path + model, 'rb') as f2:
                clf = cPickle.load(f2)
            y_pred_proba = clf.predict_proba(X_data)[:, 1]
            tmp['Probability'] = [round(i, 2) for i in list(y_pred_proba)]
            tmp = tmp[['href_nsc', 'Probability']]
        else:
            tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])
    else:
        tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])

    return tmp


# edit on 2019-08-31
def _calculate_proba_ks_noscaler(df_differ_filter, rules_data, model):
    if len(df_differ_filter) > 0:
        df_tmp = df_differ_filter.copy()
        # effective Trend
        tmp = df_tmp.merge(rules_data, on=['League', 'Handicap', 'Trend'], how='inner')
        if len(tmp) > 0:
            df_num = tmp[['hw1', 'dw1', 'aw1', 'hw2', 'dw2', 'aw2', 'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum']]
            df_dummy = pd.DataFrame(tmp['League']).merge(dummy_data, on='League', how='left')
            df_dummy = df_dummy.drop('League', axis=1).reset_index(drop=True)
            X_data = pd.concat([pd.DataFrame(df_num), df_dummy], axis=1)

            with open(cur_path + model, 'rb') as f2:
                clf = cPickle.load(f2)
            y_pred = clf.predict(X_data)
            tmp['Probability'] = [round(i, 2) for i in y_pred]
            tmp = tmp[['link', 'Probability']]
        else:
            tmp = pd.DataFrame(columns=['link', 'Probability'])
    else:
        tmp = pd.DataFrame(columns=['link', 'Probability'])

    return tmp


def _calculate_proba_ks_svm_noscaler(df_differ_filter, rules_data, model):
    if len(df_differ_filter) > 0:
        df_tmp = df_differ_filter.copy()
        # effective Trend
        tmp = df_tmp.merge(rules_data, on=['League', 'Handicap', 'Trend'], how='inner')
        if len(tmp) > 0:
            df_num = tmp[['hw1', 'dw1', 'aw1', 'hw2', 'dw2', 'aw2', 'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum']]

            df_dummy = pd.DataFrame(tmp['League']).merge(dummy_data, on='League', how='left')
            df_dummy = df_dummy.drop('League', axis=1).reset_index(drop=True)
            X_data = pd.concat([pd.DataFrame(df_num), df_dummy], axis=1)

            with open(cur_path + model, 'rb') as f2:
                clf = cPickle.load(f2)
            y_pred_proba = clf.predict_proba(X_data)[:, 1]
            tmp['Probability'] = [round(i, 2) for i in list(y_pred_proba)]
            tmp = tmp[['link', 'Probability']]
        else:
            tmp = pd.DataFrame(columns=['link', 'Probability'])
    else:
        tmp = pd.DataFrame(columns=['link', 'Probability'])

    return tmp



layout = html.Div([
    # page_header,
    html.Div([
        html.P("Football", className='title is-3'),
        html.Div([
            html.A("今日赛事", href='/football', className='tag subtitle is-7'),
            html.A("历史回查", href='/football/his', className='tag subtitle is-7'),
            html.A("赛果预测", href='/football/ml', className='tag is-primary subtitle is-7'),
            html.A("Labs", href='/football/mllabs', className='tag subtitle is-7'),

            # html.A(" 外汇 ", ),
        ], className='row'),

    ], className='hero'),

    html.Div([
        html.Div([
            html.Div([
                html.Label('language', style={'display': 'inline-block', 'font-size': '12px'}),
                dcc.RadioItems(
                    id='lang-select',
                    options=[
                        # {'label': 'EN', 'value': 'en'},
                        {'label': '中文', 'value': 'zh_cn'},

                    ],
                    value='zh_cn', labelStyle={'display': 'inline-block', 'font-size': '13px'}
                ),
            ], className='column ', style={'font-size': '13px', "textAlign": 'right'}),

        ], className='row'),

        html.Div([
            html.Label("1X2 Prediction", className='title is-5', style={'textAlign': 'center'}),
            html.Br(),
            html.Label('比赛日: {} to {} UTC+08:00'.format(today[:10], tomorrow[:10]), style={'font-size': '12px'})
        ],className='column is-full'),
        html.Hr([]),

        html.Div([
            html.Div([
                html.H5("Observation1: Dynamic kelly model", className='title is-7'),
                # html.Label("Viel Spaß!", style={'font-size': '13px', }),
                html.H6("Without standardized transformation", style={'font-size': '13px', }),
            ], className='column is-one-quarter', style={"textAlign": 'left', }),

            html.Div([
                html.Div(children=[
                    html.H5(children='Prediction', style={"textAlign": 'center'}),
                    html.Div(id='table-container-3')
                ]),
            ],
                className='column is-three-quarters')
        ], className='columns'),
        html.Hr([]),
        html.Div([
            # html.Div([],className='column', style={'font-size': '0.2rem'}),

            html.Div([
                html.H5("Observation 2: Less is more model", className='title is-7'),
                # html.Label("This prediction is based on trend.", style={'font-size': '13px', }),
            ],  className='column is-one-quarter', style={'height': '200px', "textAlign": 'left', }),

            html.Div([
                html.Div(children=[
                    html.H5(children='Prediction', style={"textAlign": 'center'}),
                    html.Div(id='table-container-4')

                ]),

            ],
                className='column is-three-quarters')

        ], className='columns'),

        html.Hr([]),

        html.Div([
            # html.Div([],className='column', style={'font-size': '0.2rem'}),

            html.Div([
                html.H5("Observation 3: 香港马会", className='title is-7'),
                html.Label("This prediction is based on trend.", style={'font-size': '13px', }),
                html.Br([]),

            ],
                className='column is-one-quarter', style={'height': '200px', "textAlign": 'left', }),

            html.Div([
                html.Div(children=[
                    html.H5(children='Today\'s Prediction (Temp)', style={"textAlign": 'center'}),
                    html.H5(children='{} {}'.format(today[:11], (datetime.now() - timedelta(hours=11)).strftime('%A')),
                            style={"textAlign": 'center'}),
                    html.H6("初盘", style={'font-size': '13px', }),
                    html.Div(easy_table(trend_begin)),
                    html.Br(),
                    html.H6("即时(暂停更新)", style={'font-size': '13px', }),
                    # html.Div(id='table-container-6')
                ]),
            ],
                className='column is-three-quarters')

        ], className='columns'),

    ], className='container'),

])


# Tab  Kelly sum filter model
@app.callback(Output('table-container-3', 'children'),
              [Input('lang-select', 'value')])
def update_table(value):
    df = match_nsc_all.loc[match_nsc_all.lang == value]  # update with your own logic
    df_differ = get_differ_data(differ_file)
    dff = pd.merge(df_differ, df, on='href_nsc', how='left')

    # # origional filter with kelly
    # dff = dff.loc[dff.kelly_sum<1.94].reset_index(drop=True)

    # kelly sum filter with kelly
    dff = dff.rename(columns={'mtype': 'League', 'dt_utc08': 'Time', 'home': 'Home', 'away': "Away"})
    ks_filter = kelly_filter.loc[kelly_filter.lang == value].reset_index(drop=True)
    dff = dff.merge(ks_filter, on=['League', 'Handicap', 'Trend'], how='left').reset_index(drop=True)
    dff_ml = dff.loc[(dff.kelly_sum >= dff.kly_min) & (dff.kelly_sum < dff.kly_max)].reset_index(drop=True)

    df_proba = calculate_proba_ks_noscaler(dff_ml, ml_pred_new, model_file_2_1)
    df_proba_svm = calculate_proba_ks_svm_noscaler(dff_ml, ml_pred_new, model_file_2_2)
    df_proba_lr = calculate_proba_ks_svm_noscaler(dff_ml, ml_pred_new, model_file_2_3)

    # dff = dff[['href_nsc', 'League', 'Time', 'Home', 'Away', 'Handicap', 'Updated', 'Trend']]
    dff['Time'] = [i[5:] for i in dff['Time'].values]
    dff = dff.merge(ml_pred_new, on=['League', 'Handicap', 'Trend'], how='left') # left or inner, to show more or less

    if len(df_proba) > 0:

        df_proba = df_proba.rename(columns={'Probability': 'Proba_1'})
        df_proba_svm = df_proba_svm.rename(columns={'Probability': 'Proba_2'})
        df_proba_lr = df_proba_lr.rename(columns={'Probability': 'Proba_3'})

        dff = dff.merge(df_proba, on='href_nsc', how='left')
        dff = dff.merge(df_proba_svm, on='href_nsc', how='left')
        dff = dff.merge(df_proba_lr, on='href_nsc', how='left')
        # dff = dff.merge(df_proba_knn, on='href_nsc', how='left')
        dff = dff[['Time', 'League', 'Home', 'Away', 'Updated', 'Handicap', 'Trend', 'Prediction', 'Proba_1', 'Proba_2',
                   'Proba_3']]

    else:
        dff = pd.DataFrame(columns=['Time', 'League', 'Home', 'Away', 'Updated', 'Handicap', 'Trend', 'Prediction'])

    return easy_table(dff)


# Tab  Reduced
@app.callback(Output('table-container-4', 'children'),
              [Input('lang-select', 'value')])
def update_table(value):
    df = match_nsc_all.loc[match_nsc_all.lang == value]  # update with your own logic
    df_differ = get_differ_data(differ_file)
    dff = pd.merge(df_differ, df, on='href_nsc', how='left')
    # origional filter with kelly
    dff = dff.loc[dff.kelly_sum < 1.94].reset_index(drop=True)

    dff = dff.rename(columns={'mtype': 'League', 'dt_utc08': 'Time', 'home': 'Home', 'away': "Away"})
    df_proba = calculate_proba_ks(dff, ml_pred_3, scaler_file_3, model_file_3_1)
    df_proba_svm = calculate_proba_ks_svm(dff, ml_pred_3, scaler_file_3, model_file_3_2)

    # dff = dff[['href_nsc', 'League', 'Time', 'Home', 'Away', 'Handicap', 'Updated', 'Trend']]
    dff['Time'] = [i[11:] for i in dff['Time'].values]
    dff = dff.merge(ml_pred_3, on=['League', 'Handicap', 'Trend'], how='inner')

    if len(dff) > 0:

        if len(df_proba) > 0:

            df_proba = df_proba.rename(columns={'Probability': 'Proba_lgb'})
            df_proba_svm = df_proba_svm.rename(columns={'Probability': 'Proba_svm'})

            dff = dff.merge(df_proba, on='href_nsc', how='left')
            dff = dff.merge(df_proba_svm, on='href_nsc', how='left')
            # dff = dff.merge(df_proba_knn, on='href_nsc', how='left')
            dff = dff[
                ['Time', 'League', 'Home', 'Away', 'Updated', 'Handicap', 'Trend', 'Prediction', 'Proba_lgb', 'Proba_svm']]
        else:
            dff = dff

    else:
        dff = pd.DataFrame(columns=['Time', 'League', 'Home', 'Away', 'Updated', 'Handicap', 'Trend', 'Prediction'])

    return easy_table(dff)


# # Tab 6
# @app.callback(Output('table-container-6', 'children'),
#               [Input('lang-select', 'value')])
# def update_table(value):
#     df = match_nsc_all.loc[match_nsc_all.lang == value]  # update with your own logic
#     dff = get_differ_gl10oal(trend_latest_file)
#
#     ks_filter = kelly_filter.loc[kelly_filter.lang == 'en'].reset_index(drop=True)
#
#     dff = dff.merge(ks_filter, on=['League', 'Handicap', 'Trend'], how='left').reset_index(drop=True)
#     dff_ml = dff.loc[((dff.kelly_sum >= dff.kly_min) & (dff.kelly_sum < dff.kly_max))].reset_index(drop=True)
#
#     # df_proba = _calculate_proba_ks_noscaler(dff_ml, ml_pred_new, model_file_6_1)
#     # df_proba_svm = _calculate_proba_ks_svm_noscaler(dff_ml, ml_pred_new, model_file_6_2)
#     # df_proba_lr = _calculate_proba_ks_svm_noscaler(dff_ml, ml_pred_new, model_file_6_3)
#     #
#     # # dff = dff[['href_nsc', 'League', 'Time', 'Home', 'Away', 'Handicap', 'Updated', 'Trend']]
#     dff['Time'] = [i[11:] for i in dff['Time'].values]
#     dff = dff.merge(ml_pred_new, on=['League', 'Handicap', 'Trend'], how='left')
#     dff = dff[['link', 'League', 'Time', 'Home', 'Away', 'Handicap', 'Updated', 'Trend', 'Prediction']]
#     # #
#     # #
#     # if len(df_proba_lr) > 0:
#     #     df_proba = df_proba.rename(columns={'Probability': 'Proba_1'})
#     #     df_proba_svm = df_proba_svm.rename(columns={'Probability': 'Proba_2'})
#     #     df_proba_lr = df_proba_lr.rename(columns={'Probability': 'Proba_3'})
#     #
#     #     dff = dff.merge(df_proba, on='link', how='left')
#     #     dff = dff.merge(df_proba_svm, on='link', how='left')
#     #     dff = dff.merge(df_proba_lr, on='link', how='left')
#     #     dff = dff[['Time', 'League', 'Home', 'Away', 'Updated', 'Handicap', 'Trend', 'Prediction', 'Proba_1', 'Proba_2',
#     #                'Proba_3']]
#     #
#     # else:
#     #     dff = dff[['Time', 'League', 'Home', 'Away', 'Updated', 'Handicap', 'Trend']]
#
#     return easy_table(dff)
