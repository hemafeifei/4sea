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
# today = datetime.today()
# control_dt = str(today - relativedelta(days=1))[:10]
df_smry = pd.read_csv(os.path.join(csv_path, 'sec_txn_summary.txt'), index_col=False)
txn_dt = df_smry['date'].max()
df_top = pd.read_csv(os.path.join(csv_path, 'sec_txn_top100_' + txn_dt + '.txt'), index_col=False)
df_top_msci = pd.read_csv(os.path.join(csv_path, 'sec_txn_msci_top100_' + txn_dt + '.txt'), index_col=False)

parm_dict = {'txn_amt_all': '全市成交',
             'txn_amt_hs300': '沪深300',
             'txn_amt_zz500': '中证500',
             'txn_sec_top100': '全市场成交-Top100',
             'txn_sec_msci_top100': 'MSCI成交-Top100',
             'txn_etf_top50': '场内ETF成交-Top50'}


def easy_table(df):
    dataframe = df.copy()
    if 'txn_amt' in dataframe.columns:
        dataframe['txn_amt'] = dataframe['txn_amt'].astype(float)
        dataframe['txn_amt'] = round((dataframe['txn_amt'] / 1e4), 1)
    dataframe = dataframe.rename(columns={'code': '代码',
                                          'name': '名称',
                                          'close': '收盘',
                                          'change': '涨跌',
                                          'txn_vol': '成交量',
                                          'pe': 'PE',
                                          'txn_amt': '成交额（亿）'})
    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in dataframe.columns],
        data=dataframe.to_dict('records'),
        sort_action="native",
        style_cell={'fontSize': 13, 'font-family': 'sans-serif'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'code'},
                'textAlign': 'left',
            },
        ])


def get_html(df):
    total_amt = df.iloc[-1, 10]
    txn_hs300 = df.iloc[-1, 7]
    txn_zz500 = df.iloc[-1, 8]
    txn_top50 = df.iloc[-1, 11] / 1e4
    txn_top100 = df.iloc[-1, 12] / 1e4
    txn_msci_top50 = df.iloc[-1, 13] / 1e4
    txn_msci_top100 = df.iloc[-1, 14] / 1e4
    pct_hs300 = txn_hs300 * 100 / total_amt
    pct_zz500 = txn_zz500 * 100 / total_amt
    pct_top50 = txn_top50 * 100 / total_amt
    pct_top100 = txn_top100 * 100 / total_amt
    pct_msci_top50 = txn_msci_top50 * 100 / total_amt
    pct_msci_top100 = txn_msci_top100 * 100 / total_amt

    return dash_dangerously_set_inner_html.DangerouslySetInnerHTML('''
<nav class="level">
  <div class="level-item has-text-centered">
    <div>
      <p class="heading">沪深A股</p>
      <p class="title is-3">{}亿</p>
      <p class="title is-5">100%</p>
    </div>
  </div>
  <div class="level-item has-text-centered">
    <div>
      <p class="heading">沪深300</p>
      <p class="title is-3">{}亿</p>
      <p class="title is-5">{:.1f}%</p>
    </div>
  </div>
    <div class="level-item has-text-centered">
    <div>
      <p class="heading">中证500</p>
      <p class="title is-3">{}亿</p>
      <p class="title is-5">{:.1f}%</p>
    </div>
  </div>
    <div class="level-item has-text-centered">
    <div>
      <p class="heading">Top50成交</p>
      <p class="title is-3">{:.0f}亿</p>
      <p class="title is-5">{:.1f}%</p>
    </div>
  </div>
    <div class="level-item has-text-centered">
    <div>
      <p class="heading">Top100成交</p>
      <p class="title is-3">{:.0f}亿</p>
      <p class="title is-5">{:.1f}%</p>
    </div>
  </div>
    <div class="level-item has-text-centered">
    <div>
      <p class="heading">MSCI-Top50成交</p>
      <p class="title is-3">{:.0f}亿</p>
      <p class="title is-5">{:.1f}%</p>
    </div>
  </div>
    </div>
    <div class="level-item has-text-centered">
    <div>
      <p class="heading">MSCI-Top100成交</p>
      <p class="title is-3">{:.0f}亿</p>
      <p class="title is-5">{:.1f}%</p>
    </div>
  </div>
</nav>

'''.format(total_amt, txn_hs300, pct_hs300, txn_zz500, pct_zz500, txn_top50, pct_top50, txn_top100, pct_top100,
           txn_msci_top50, pct_msci_top50, txn_msci_top100, pct_msci_top100))


level_layout = get_html(df_smry)

layout = html.Div([
    html.Div([
        html.P("Finance", className='title is-3'),
        html.Div([
            html.A("全球指数", href='/wealth', className='tag subtitle is-7'),
            html.A("沪深市场", href='/wealth/sec', className='tag is-primary subtitle is-7'),
            html.A("ETF追踪", href='/wealth/etf', className='tag subtitle is-7'),
            html.A("RPS研究", href='/wealth/sec_rps', className='tag subtitle is-7'),
            # html.A(" 外汇 ", ),
        ], className='row'),
    ], className='hero'),

    html.Div([
        html.P("{} 交易日".format(df_smry['date'].values[-1]), className='title is-7'),
        level_layout,
        html.Hr(),
        # Row 2
        html.Div([
        ], className='columns'),

        html.P("MSCI成分", className='title is-5'),
        html.P("相同性", className='tag is-info title is-7'),

        html.Div([
            html.Div([
                html.Label('Dropdown'),
                dcc.Dropdown(
                    id='dropdown-sec',
                    options=[
                        {'label': '10', 'value': 10},
                        {'label': '30', 'value': 30},
                        {'label': '50', 'value': 50}
                    ],
                    value=30
                ),
            ], className='column is-one-fifth'),

            html.Div([
                html.P(id='smry-1', className='title is-7'),
                html.Div(id='table-1'),
            ], className='column is-half'),
            html.Div([

                html.P("全市场成交额-Top10", className='title is-7'),
                html.Div(easy_table(df_top.drop(['pe', 'views', 'close', 'change'], axis=1)[:10])),
                # html.A("more", href='http://summary.jrj.com.cn/scfl/index.shtml?q=cn|s|sa&c=m&n=hqa&o=tm,d&p=1050'),

                html.Br(),
                html.Br(),
                html.P("MSCI成交额-Top5", className='title is-7'),
                html.Div(easy_table(df_top_msci.drop(['pe', 'views', 'close', 'change'], axis=1)[:5])),
                # html.A("more", href='http://summary.jrj.com.cn/scfl/msci.shtml?q=cn|s|msci&c=m&n=hqa&o=tm,d&p=1050'),
            ], className='column is-one-quarter'),
        ], className='columns'),

        html.P("相异性", className='tag is-info title is-7'),
        html.Div([
            html.Div([
                html.Label('Dropdown'),
                dcc.Dropdown(
                    id='dropdown-sec-2',
                    options=[
                        {'label': '10', 'value': 10},
                        {'label': '30', 'value': 30},
                        {'label': '50', 'value': 50},
                        {'label': '100', 'value': 100}
                    ],
                    value=30
                ),
            ], className='column is-one-fifth'),
            html.Div([
                html.P(id='smry-2', className='title is-7'),
                html.Div(id='table-2'),
            ], className='column is-half')
        ], className='columns'),
        html.Hr(),
        html.P("趋势追踪", className='title is-5'),
        html.P("市场偏好", className='tag is-info title is-7'),
        html.Div([
            html.Div([
                html.Label('Checkboxes'),
                dcc.Checklist(
                    id='checklist-multi',
                    # multi=True,
                    labelStyle={'display': 'inline-block',
                                'font-size': 13,
                                'text-align': 'vertical',
                                'margin-right': 50},
                    options=[
                        {'label': '沪深300', 'value': 'txn_amt_hs300'},
                        {'label': '中证500', 'value': 'txn_amt_zz500'},
                        {'label': '全市场成交-Top100', 'value': 'txn_sec_top100'},
                        {'label': 'MSCI成交-Top100', 'value': 'txn_sec_msci_top100'},
                        {'label': '场内ETF成交-Top50', 'value': 'txn_etf_top50'},
                    ],
                    value=['txn_amt_hs300', 'txn_amt_zz500', 'txn_etf_top50']
                ),
            ], className='column is-one-fifth'),
            html.Div([
                html.P("成交额走势", className='title is-7'),
                html.P("注意：在市场狂热阶段, ETF成交额会持续走高, 因为基金公司方的收益与成交挂钩。", className='heading'),
                dcc.Graph(id='txn-trend'),
                # dcc.Graph(id='price-trend'),
            ], className='column is-four-fifths'),
            html.Div([], className='column is-two-fifths'),

        ], className='columns'),
    ], className='container')
], className='container')


@app.callback(
    [dash.dependencies.Output('smry-1', 'children'),
     dash.dependencies.Output('table-1', 'children')],
    [dash.dependencies.Input('dropdown-sec', 'value'), ])
def refresh_data(num):
    df_sec = df_top[:num].loc[df_top.code.isin(df_top_msci.code)]
    df_sec = df_sec.drop('views', axis=1)
    m = len(df_sec)
    pe = round(df_sec.loc[df_sec.pe > 1]['pe'].median(), 2)
    return "市场交易Top{}股票，而且也在MSCI成分中的一共{}支, 它们的PE中位数(移出异常值)为{}".format(num, m, pe), easy_table(df_sec)


@app.callback(
    [dash.dependencies.Output('smry-2', 'children'),
     dash.dependencies.Output('table-2', 'children')],
    [dash.dependencies.Input('dropdown-sec-2', 'value'), ])
def refresh_data(num):
    df_sec = df_top[:num].loc[~df_top.code.isin(df_top_msci.code)]
    df_sec = df_sec.drop('views', axis=1)
    m = len(df_sec)
    pe = round(df_sec.loc[df_sec.pe > 1]['pe'].median(), 2)
    return "市场交易Top{}股票，而且不在MSCI成分中的一共{}支, 它们的PE中位数(移出异常值)为{}".format(num, m, pe), easy_table(df_sec)


def ge_figure(df, idx):
    trace0 = go.Scatter(x=list(df['Date']),
                        y=list(df['Close']),
                        name=idx)
    _data = [trace0]
    _layout = dict(xaxis=dict(title='timeline'),
                   yaxis=dict(title='price'))
    fig = dict(data=_data, layout=_layout)
    return fig


@app.callback(
    [dash.dependencies.Output('table-3-left', 'children'),
     dash.dependencies.Output('txn-trend', 'figure'), ],
    [dash.dependencies.Input('checklist-multi', 'value'), ])
def render_content(cols):
    sel_cols = ['date', 'txn_amt_all']
    sel_cols.extend(cols)
    df_trend = df_smry[sel_cols]
    df_trend['date'] = pd.to_datetime(df_trend['date'])
    for col in df_trend.columns:
        if col in ['txn_sec_top100', 'txn_sec_msci_top100', 'txn_etf_top50']:
            df_trend[col] = (df_trend[col] / 1e4).astype(int)

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
        yaxis=dict(title='成交额（亿）'))
    fig = dict(data=_data, layout=_layout)

    return easy_table(df_trend), fig
