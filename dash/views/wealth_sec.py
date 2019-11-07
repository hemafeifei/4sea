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
            # html.A(" 外汇 ", ),
        ], className='row'),
    ], className='hero'),

    html.Div([
        html.P("{} 交易日".format(df_smry['date'].values[-1]), className='title is-7'),
        level_layout,
        html.Hr(),
        # Row 2
        html.Div([

        ], className='columns')

    ], className='container')

], className='container')
