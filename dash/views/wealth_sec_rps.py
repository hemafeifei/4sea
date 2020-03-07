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

csv_path = '../../database/finance/sec/'

df_stock = pd.read_csv(os.path.join(csv_path, 'rps_stock_info.csv'), dtype={'code':str})
df_price = pd.read_csv(os.path.join(csv_path, 'rps_stock_price.csv'), index_col='date')
df_return = pd.read_csv(os.path.join(csv_path, 'rps_stock_return.txt'), index_col='date')
df_return_med = pd.read_csv(os.path.join(csv_path, 'rps_stock_chg_median.txt'), index_col='date')

# 根据某一时刻的收益率计算所有股票的RPS
def get_rps(ret_row):
    df = pd.DataFrame(ret_row.sort_values(ascending=False))
    df['rank'] = range(1, len(df) + 1)
    df['rps'] = (1 - df['rank'] / len(df)) * 100
    return df


def concate_rps(ret_df, top_n_week=12, top_n_rank=1000):
    '''
    :param ret_df:  stock_return
    :param top_n_week: rolling windlows, axis=0, e.g. in the past 10 weeks
    :param top_n_stock: top ranking stocks, axis=1, e.g the top 20 of the RPS ranking
    :return:
    '''

    date_idx = ret_df.index
    dict_rps = {}
    for i in range(len(ret_df))[:30]:
        rps = get_rps(ret_df.iloc[i])
        dict_rps[date_idx[i]] = pd.DataFrame(rps.values, columns=['increase', 'rank', 'rps'], index=rps.index)
    sorted_date = sorted(date_idx[:top_n_week])

    df_trend = pd.DataFrame({dt: list(dict_rps[dt].index[:top_n_rank]) for dt in sorted_date})
    return dict_rps, df_trend


dict_rps, trend_rps = concate_rps(df_return) # dict_rps is a dictionary of date: datafroma
dict_code_name = dict(zip(df_stock['code'], df_stock['name']))
dict_name_code = dict(zip(df_stock['name'], df_stock['code']))

def query_stock_rps(rps_dict, name):
    date_index = sorted(rps_dict.keys())
    rps_lst = []
    for dt in date_index:
        rps = rps_dict[dt].loc[name, 'rps']
        rps_lst.append(rps)
    stock_rps = pd.DataFrame({'rps': rps_lst}, index=date_index)
    return stock_rps

def ge_table(dataframe):
    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in dataframe.columns],
        data=dataframe.to_dict('records'),
        sort_action="native",
        style_cell={'fontSize': 11, 'font-family': 'sans-serif'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'column_id': '指数'},
                'textAlign': 'left',
            },

        ])


def ge_figure(series, idx, y_axis_title):
    trace0 = go.Scatter(
        x=list(series.index),
        y=[round(float(i),2) for i in list(series.values)],
        name=idx)

    data = [trace0]
    layout = dict(
        # title='Trend of {}'.format(idx),
        xaxis=dict(title='timeline'),
        yaxis=dict(title=y_axis_title))
    fig = dict(data=data, layout=layout)
    return fig


def ge_figure_datetime(df):
    data = []
    for col in df.columns:
        if col != 'date':
            trace = go.Scatter(
                x=list(df.index),
                y=[round(float(i),2) for i in list(df[col].values)],
                name=col)
            data.append(trace)

    layout = dict(
        # title='Trend of {}'.format(idx),
        xaxis=dict(title='timeline'),
        yaxis=dict(title='increase'),
        legend=dict(x=-.1, y=1.2))
    fig = dict(data=data, layout=layout)
    return fig



layout = html.Div([
    html.Div([
        html.P("Finance", className='title is-3'),
        html.Div([
            html.A("全球指数", href='/wealth', className='tag subtitle is-7'),
            html.A("沪深市场", href='/wealth/sec', className='tag subtitle is-7'),
            html.A("ETF追踪", href='/wealth/etf', className='tag subtitle is-7'),
            html.A("RPS研究", href='/wealth/sec_rps', className='tag is-primary subtitle is-7'),
        ], className='row'),
    ], className='hero'),

    html.Div([
        html.Div([
        ], className='columns'),

        html.P("RPS", className='title is-5'),
        html.P("Ranking", className='tag is-info title is-7'),
        html.Div([
            html.Div([
            ], className='column is-one-fifth'),
            html.Div([

                html.H5("RPS Ranking Top 15", className='title is-5', style={"textAlign": 'center'}),
                html.P("Update to {}".format(df_return_med.index.max()), className='title is-7'),
                html.Div(id='rps-table-1', children=ge_table(trend_rps[:15])),
            ], className='column is-four-fifths'),
        ], className='columns'),

        html.P("RPS选股", className='tag is-info title is-7'),
        html.Div([
            html.Div([
                html.Label('Please Select', className='title is-7'),

                html.P("RPS before 1 week >=:"),
                dcc.Input(id="input_range_1", type="number", placeholder="input with range", value=90,
                          min=80, max=100, step=2, className='input is-info'),

                html.P("RPS before 2 weeks <=:"),
                dcc.Input(id="input_range_2", type="number", placeholder="input with range", value=80,
                          min=50, max=100, step=5, className='input is-info'),
                html.P("RPS before 3 weeks <=:"),
                dcc.Input(id="input_range_3", type="number", placeholder="input with range", value=70,
                          min=50, max=100, step=5, className='input is-info'),


                html.Br(),
                html.Br(),
                # html.P(id='query-check'),
                html.Label('Please Select', className='title is-7'),
                dcc.Dropdown(
                    id='rps-href-dropdown',
                    #     options=option_type,
                    #     values=[option_type[i]['value'] for i in range(len(option_type))],
                    multi=False
                ),
                html.Button('Reset', id='query-button', className="button is-light", style={'height': '30px'}),

            ], className='column is-one-fifth', style={'font-size': '12px'}),
            html.Div([
                html.Br(),
                html.Br(),
                html.P("After filtering you can find :", className='title is-7'),
                html.P(id='query-check', className='heading'),

                html.Br(),
                html.H5(id='rps-table-2', className='title is-5', style={"textAlign": 'center'}),

                dcc.Graph(id='rps-figure-1', style={'height': '400px'}),
                dcc.Graph(id='rps-figure-2', style={'height': '400px'}),

                html.P("Note: ", className='heading'),
                html.P("""
                RPS英文全称 Relative Price Strength Rating，即股价相对强度，该指标是欧奈尔CANSLIM选股法则中的趋势分析，
                具有很强的实战指导意义。RPS指标是指在一段时间内，个股涨幅在全部股票涨幅排名中的位次值。比如A股共有3500只股票，
                若某只股票的120日涨幅在所有股票中排名第350位，则该股票的RPS值为：(1-350/3500)*100=90。
                """, style={'font-size': '11px'}),
                html.Br(),
                html.P("""
                RPS的值代表该股的120日涨幅超过其他90%的股票的涨幅。通过该指标可以反映个股股价走势在同期市场中的表现相对强弱。
                RPS的值介于0-100之间，在过去的一年中，所有股票的涨幅排行中，前1%的股票的RPS值为99至100，前2%的股票的RPS值为98至99，
                以此类推。RPS时间周期可以自己根据需要进行调整，常用的有60日（3个月）、120日（半年）和250日（一年）等。
                """, style={'font-size': '11px'}),
            ], className='column four-fifths')
        ], className='columns'),

        html.Hr(),
        html.P("趋势追踪", className='title is-5'),
        html.P("全市场回报", className='tag is-info title is-7'),
        html.Div([
            # html.Div([
            #     html.P("收益率中位数", className='title is-7'),
            # ], className='column is-one-fifth'),

            html.Div([
                html.P("Note：全市场收益率中位数 by 过去60d, 120d, 250d", className='heading'),
                dcc.Graph(figure=ge_figure_datetime(df_return_med)),
                # dcc.Graph(id='price-trend'),
            ], className='column'),

        ], className='columns'),
    ], className='container')
], className='container')


@app.callback(
    [Output('query-check', 'children'),
     Output('rps-href-dropdown', 'options'),
     ],
    [Input('input_range_1', 'value'),
    Input('input_range_2', 'value'),
    Input('input_range_3', 'value'),
    Input('query-button', 'n_clicks'),
     ])
def query_stock_rps(input1, input2, input3, n_clicks):

    sel_week_1 = dict_rps[sorted(dict_rps.keys())[-1]]
    stock_week_1 = sel_week_1.loc[sel_week_1.rps >= input1].index
    sel_week_2 = dict_rps[sorted(dict_rps.keys())[-2]]
    stock_week_2 = sel_week_2.loc[sel_week_2.rps <= input2].index
    sel_week_3 = dict_rps[sorted(dict_rps.keys())[-3]]
    stock_week_3 = sel_week_3.loc[sel_week_3.rps <= input3].index

    sel_stocks = [i for i in stock_week_1 if i in stock_week_2 and i in stock_week_3]

    if len(sel_stocks) < 1:
        sel_stocks = ['平安银行']

    check = '''
            {}
    '''.format(sel_stocks)
    stock_options = [{'label': sel_stocks[i], 'value': sel_stocks[i]} for i in range(len(sel_stocks))]
    return check, stock_options


@app.callback(
    Output('rps-href-dropdown', 'value'),
    [Input('rps-href-dropdown', 'options')])
def rps_href_value(available_options):
    return available_options[0]['value']


@app.callback(
    [Output('rps-table-2', 'children'),
     # Output('rps-table-3', 'children'),
     Output('rps-figure-1', 'figure'),
     Output('rps-figure-2', 'figure'),
     ],
    [Input('rps-href-dropdown', 'value')])
def rps_plot(stock_name):
    sec_name = stock_name
    code = dict_name_code[sec_name]
    date_index = sorted(dict_rps.keys())
    rps_lst = []
    for dt in date_index:
        rps = dict_rps[dt].loc[sec_name, 'rps']
        rps_lst.append(rps)
    stock_rps = pd.DataFrame({'rps': rps_lst}, index=date_index)
    fig1 = ge_figure(stock_rps, sec_name, "RPS")
    stock_price = df_price.loc[stock_rps.index, sec_name]
    fig2 = ge_figure(stock_price, sec_name, "Price")
    return "RPS vs Price {} - {}".format(sec_name, code), fig1, fig2

