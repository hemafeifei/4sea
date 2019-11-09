# -*- coding: utf-8 -*

from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash
import dash_table
import os
import _pickle as cPickle
import pickle

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
his_path = data_path + 'his_data/'
match_nsc = pd.read_csv(match_path + today[:10] + '.txt')
# match_nsc_en = pd.read_csv(match_path + today[:10] + '_en.txt')
# match_nsc_all = pd.concat([match_nsc, match_nsc_en], ignore_index=True)
match_nsc_all = match_nsc
df_name = pd.read_csv((os.path.join(config_path, 'league_name.txt')), encoding='utf8')

# model 2: nosclaer v1.6
ml_pred_new = pd.read_csv(os.path.join(config_path, 'ml_prediction_98_more.txt'))
# scaler_file_2 = '/std_scaler_94_more.pickle'
model_file_2_1 = 'v1.6_lgb_98_more.pickle'
model_file_2_2 = 'v1.6_svm_98_more.pickle'
model_file_2_3 = 'v1.6_lr_98_more.pickle'

kelly_filter = pd.read_csv(os.path.join(config_path, 'ml_kelly_filter.txt'))
differ_path = data_path + 'differ_data/'
differ_file = differ_path + today[:10] + '.txt'
ml_path = data_path + 'ml_data/'
dummy_data = pd.read_csv(os.path.join(config_path, 'league_dummy.txt'))

now = datetime.today()
idx = (now.weekday() + 1) % 7
sat = now - timedelta(7 + idx - 6)
enddate = datetime.now() - timedelta(days=1, hours=10)


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
                # clf = pickle.load(f2)

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
                # clf = pickle.load(f2)
            y_pred_proba = clf.predict_proba(X_data)[:, 1]
            tmp['Probability'] = [round(i, 2) for i in list(y_pred_proba)]
            tmp = tmp[['href_nsc', 'Probability']]
        else:
            tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])
    else:
        tmp = pd.DataFrame(columns=['href_nsc', 'Probability'])

    return tmp


def get_match_his(date, lang):
    his_nsc = pd.read_csv(his_path + 'nsc_his_' + str(date)[:10] + '.txt')
    # his_nsc_en = pd.read_csv(his_path + 'en_his_' + str(date)[:10] + '.txt')
    # his_nsc_all = pd.concat([his_nsc, his_nsc_en], ignore_index=True)
    his_nsc_all = his_nsc
    return his_nsc_all.loc[his_nsc_all.lang == str(lang)].reset_index(drop=True)


def get_differ_his(date):
    differ_his_file = differ_path + str(date)[:10] + '.txt'

    if os.path.exists(differ_his_file):
        df_differ = pd.read_csv(differ_his_file, header=None,
                                names=['Time', 'League', 'Home', 'Away', 'Trend', 'Updated', 'href_nsc', 'Handicap',
                                       'hw1', 'dw1', 'aw1',
                                       'hw2', 'dw2', 'aw2', 'kly_h1', 'kly_d1', 'kly_a1', 'kly_h2', 'kly_d2', 'kly_a2',
                                       'differ_hw', 'differ_dw', 'differ_aw', 'kelly_sum'])
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


layout = html.Div([
    # page_header,
    html.Div([
        html.P("Football", className='title is-3'),
        html.Div([
            html.A("今日赛事", href='/football', className='tag subtitle is-7'),
            html.A("历史回查", href='/football/his', className='tag subtitle is-7'),
            html.A("赛果预测", href='/football/ml', className='tag subtitle is-7'),
            html.A("Labs", href='/football/mllabs', className='tag is-primary subtitle is-7'),
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

        html.Label("Prediction History", className='title is-5', style={'textAlign': 'center'}),
        html.Hr(),
        html.Div([
            html.Div([
                html.Label('选择日期: ', className='title is-7'),
                html.Br(),
                dcc.DatePickerSingle(
                    id='my-date-picker-single',
                    min_date_allowed=enddate - timedelta(days=85),
                    max_date_allowed=enddate,
                    display_format='YYYY-MM-DD',
                    initial_visible_month=enddate,
                    date=sat),

            ], className='column is-one-quarter'),
            html.Div([
                html.Div(children=[
                    html.H5(children='History Prediction', style={"textAlign": 'center'}),
                    html.Div(id='table-container-2'),
                    # generate_table(df_differ)
                ])
            ], className='column is-three-quarters')

        ], className='columns'),


    ], className='container'),

])


# Tab 2 - History
@app.callback(
    dash.dependencies.Output('table-container-2', 'children'),
    [dash.dependencies.Input('my-date-picker-single', 'date'),
     dash.dependencies.Input('lang-select', 'value')])
def select_lang(date, value):
    match_his = get_match_his(str(date), value)
    differ_his = get_differ_his(date)
    dff = pd.merge(differ_his, match_his, on='href_nsc', how='left')

    # kelly sum filter with kelly
    dff = dff.rename(columns={'mtype': 'League', 'dt_utc08': 'Time', 'home': 'Home', 'away': "Away"})
    ks_filter = kelly_filter.loc[kelly_filter.lang == value].reset_index(drop=True)
    dff = dff.merge(ks_filter.drop(['options', 'lang'], axis=1), on=['League', 'Handicap', 'Trend'], how='left').reset_index(drop=True)
    dff_ml = dff.loc[(dff.kelly_sum >= dff.kly_min) & (dff.kelly_sum < dff.kly_max)].reset_index(drop=True)

    df_proba = calculate_proba_ks_noscaler(dff_ml, ml_pred_new, model_file_2_1)

    # dff = dff[['href_nsc', 'League', 'Time', 'Home', 'result', 'Away', 'Handicap', 'Updated', 'Trend']]
    dff['Time'] = [i[5:] for i in dff['Time'].values]

    if len(df_proba) > 0:
        df_proba = df_proba.rename(columns={'Probability': 'Proba_lgb'})
        df_proba_svm = calculate_proba_ks_svm_noscaler(dff_ml, ml_pred_new, model_file_2_2)
        df_proba_svm = df_proba_svm.rename(columns={'Probability': 'Proba_svm'})
        df_proba_lr = calculate_proba_ks_svm_noscaler(dff_ml, ml_pred_new, model_file_2_3)
        df_proba_lr = df_proba_lr.rename(columns={'Probability': 'Proba_lr'})

        dff = dff.merge(df_proba, on='href_nsc', how='left')
        dff = dff.merge(df_proba_svm, on='href_nsc', how='left')
        dff = dff.merge(df_proba_lr, on='href_nsc', how='left')
        dff = dff.merge(ml_pred_new, on=['League', 'Handicap', 'Trend'], how='left')
        dff = dff[
            ['Time', 'League', 'Home', 'result', 'Away', 'Updated', 'Handicap', 'Trend', 'Prediction', 'Proba_lgb',
             'Proba_svm', 'Proba_lr']]
    else:
        dff = dff[['Time', 'League', 'Home', 'result', 'Away', 'Updated', 'Handicap', 'Trend']]

    # dff['Updated'] = [str(i)[11:16] for i in dff['Updated'].values]
    return easy_table(dff)







