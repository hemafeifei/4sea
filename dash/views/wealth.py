# -*- coding: utf-8 -*import warnings# Dash configurationimport dashimport dash_tableimport dash_core_components as dccimport dash_html_components as htmlfrom dash.dependencies import Input, Output, Stateimport pandas as pdimport dash_dangerously_set_inner_htmlfrom server import app# import chart_studio.plotly as pyimport plotly.graph_objs as gofrom datetime import datetime, timedeltafrom dateutil.relativedelta import relativedeltacsv_path = '../../database/finance/idx/'today = datetime.today()control_dt = str(today - relativedelta(days=1))[:10]def clean_data(file_path, image_dt):    df = pd.read_csv(file_path, usecols=['date', 'close'])    df['Date'] = pd.to_datetime(df['date'])    df = df.loc[df['Date'] <= image_dt].reset_index(drop=True)    df['Close'] = df['close'].astype(float)    df = df.sort_values('Date').reset_index(drop=True)    return df[['Date', 'Close']]def subset_data(df, image_dt, period):    df_effect = df.loc[df['Date'] <= image_dt]    date_effct = df_effect['Date'].max()    if period in ['1m', '3m', '6m', '1y', '3y', '5y']:        date_before = date_effct - relativedelta(months=dict_vars['timeline'][period])        df_subset = df_effect.loc[df_effect['Date'] >= date_before].reset_index(drop=True)        return df_subset    elif period == 'ytd':        date_before = str(date_effct)[:4] + '-01-01'        df_subset = df_effect.loc[df_effect['Date'] >= date_before].reset_index(drop=True)        return df_subsetdef calculate_differ(df, image_dt, idx_name):    effect_df = df.loc[df['Date'] <= image_dt].reset_index(drop=True)    effect_dt = effect_df['Date'].max()    effect_price = effect_df.iloc[-1, 1]    last_price = effect_df.iloc[-2, 1]    change = round((effect_price - last_price), 2)    date_before_1m = effect_dt - relativedelta(months=1)    date_before_3m = effect_dt - relativedelta(months=3)    date_before_6m = effect_dt - relativedelta(months=6)    date_year_start = str(effect_dt)[:4] + '-01-01'    date_before_1y = effect_dt - relativedelta(years=1)    date_before_3y = effect_dt - relativedelta(years=3)    date_before_5y = effect_dt - relativedelta(years=5)    differ_52w_h = effect_df.loc[effect_df['Date'] >= date_before_1y]['Close'].max()    differ_52w_l = effect_df.loc[effect_df['Date'] >= date_before_1y]['Close'].min()    def calculate_pct_chg(differ_dt):        differ_df = df.loc[df['Date'] >= differ_dt].reset_index(drop=True)        return ((differ_df.iloc[-1, 1] - differ_df.iloc[0, 1]) / differ_df.iloc[0, 1]) * 100  # return %    differ_1m = round(calculate_pct_chg(date_before_1m), 2)    differ_3m = round(calculate_pct_chg(date_before_3m), 2)    differ_6m = round(calculate_pct_chg(date_before_6m), 2)    differ_ytd = round(calculate_pct_chg(date_year_start), 2)    differ_1y = round(calculate_pct_chg(date_before_1y), 2)    differ_3y = round(calculate_pct_chg(date_before_3y), 2)    differ_5y = round(calculate_pct_chg(date_before_5y), 2)    return [idx_name, effect_price, change, differ_52w_h, differ_52w_l, differ_1m, differ_3m, differ_6m, differ_ytd,            differ_1y, differ_3y, differ_5y]def calculate_w_date_image(image_dt):    idx_sp500 = clean_data(csv_path + 'idx_sp500_his.txt', image_dt)    idx_sh_com = clean_data(csv_path + 'idx_shanghai_his.txt', image_dt)    idx_dax30 = clean_data(csv_path + 'idx_dax30_his.txt', image_dt)    idx_hsi = clean_data(csv_path + 'idx_hsi_his.txt', image_dt)    # idx_ftse = clean_data(csv_path + 'FTSE 100 Historical Data.csv', image_dt)    idx_gold = clean_data(csv_path + 'idx_gold_his.txt', image_dt)    price_sp500 = calculate_differ(idx_sp500, image_dt, 'SP500')    price_sh_com = calculate_differ(idx_sh_com, image_dt, '上证综指')    price_dax30 = calculate_differ(idx_dax30, image_dt, 'DAX30')    price_hsi = calculate_differ(idx_hsi, image_dt, '恒生指数')    # price_htse = calculate_differ(idx_ftse, image_dt, 'FTSE100')    price_gold = calculate_differ(idx_gold, image_dt, 'GOLD')    return pd.DataFrame([price_sp500, price_sh_com, price_dax30, price_hsi,                         # price_htse,                         price_gold],                        columns=['Name', 'Price', 'Change', '52w_h', '52w_l', '1M', '3M', '6M', 'YTD', '1Y', '3Y',                                 '5Y'])def ge_table(dataframe):    dataframe = dataframe.rename(columns={'Name': '指数',                                          'Price': '收盘',                                          'Change': '涨跌',                                          '52w_h': '52周 高',                                          '52w_l': '52周 低',                                          '1M': '1月(%)',                                          '3M': '3月(%)',                                          '6M': '6月(%)',                                          # 'YTD': '今年以来',                                          '1Y': '1年(%)',                                          '3Y': '3年(%)',                                          '5Y': '5年(%)',                                          })    return dash_table.DataTable(        id='table',        columns=[{"name": i, "id": i} for i in dataframe.columns],        data=dataframe.to_dict('records'),        sort_action="native",        style_cell={'fontSize': 13, 'font-family': 'sans-serif'},        style_header={            'backgroundColor': 'rgb(230, 230, 230)',            'fontWeight': 'bold'},        style_data_conditional=[            {                'if': {'column_id': '指数'},                'textAlign': 'left',            },            {                'if': {'column_id': 'Change',                       'filter_query': '{Change} < 0'                       },                'backgroundColor': '#3D9970',                'color': 'white',            },            {                'if': {'column_id': 'Change',                       'filter_query': '{Change} > 0'                       },                'backgroundColor': 'red',                'color': 'white',            },            {                'if': {'column_id': '1月(%)',                       'filter_query': '{1月(%)} < 0'                       },                'backgroundColor': '#3D9970',                'color': 'white',            },            {                'if': {'column_id': '1月(%)',                       'filter_query': '{1月(%)} > 0'                       },                'backgroundColor': 'red',                'color': 'white',            },            {                'if': {'column_id': '3月(%)',                       'filter_query': '{3月(%)} < 0'                       },                'backgroundColor': '#3D9970',                'color': 'white',            },            {                'if': {'column_id': '3月(%)',                       'filter_query': '{3月(%)} > 0'                       },                'backgroundColor': 'red',                'color': 'white',            },            {                'if': {'column_id': '6月(%)',                       'filter_query': '{6月(%)} < 0'                       },                'backgroundColor': '#3D9970',                'color': 'white',            },            {                'if': {'column_id': '6月(%)',                       'filter_query': '{6月(%)} > 0'                       },                'backgroundColor': 'red',                'color': 'white',            },            {                'if': {'column_id': 'YTD',                       'filter_query': '{YTD} < 0'                       },                'backgroundColor': '#3D9970',                'color': 'white',            },            {                'if': {'column_id': 'YTD',                       'filter_query': '{YTD} > 0'                       },                'backgroundColor': 'red',                'color': 'white',            },            {                'if': {'column_id': '1年(%)',                       'filter_query': '{1年(%)} < 0'                       },                'backgroundColor': '#3D9970',                'color': 'white',            },            {                'if': {'column_id': '1年(%)',                       'filter_query': '{1年(%)} > 0'                       },                'backgroundColor': 'red',                'color': 'white',            },            {                'if': {'column_id': '3年(%)',                       'filter_query': '{3年(%)} < 0'                       },                'backgroundColor': '#3D9970',                'color': 'white',            },            {                'if': {'column_id': '3年(%)',                       'filter_query': '{3年(%)} > 0'                       },                'backgroundColor': 'red',                'color': 'white',            },            {                'if': {'column_id': '5年(%)',                       'filter_query': '{5年(%)} < 0'                       },                'backgroundColor': '#3D9970',                'color': 'white',            },            {                'if': {'column_id': '5年(%)',                       'filter_query': '{5年(%)} > 0'                       },                'backgroundColor': 'red',                'color': 'white',            },        ])def ge_summary_profit(dataframe):    # for col in ['1M', '3M', '6M', 'YTD', '1Y', '3Y', '5Y']:    return [(dataframe.loc[dataframe[col].idxmax(), 'Name'], dataframe.loc[dataframe[col].idxmax(), col]) for col            in ['6M', 'YTD', '1Y', '3Y', '5Y']]def ge_summary_l(dataframe):    # for col in ['1M', '3M', '6M', 'YTD', '1Y', '3Y', '5Y']:    result = [(dataframe.loc[dataframe[col].idxmax(), 'Name'], dataframe.loc[dataframe[col].idxmax(), col]) for col              in ['1Y', '3Y', '5Y']]    return resultdef ge_summary_r(dataframe):    df = dataframe.copy()    df['cur_to_52h'] = df['Price'] / df['52w_h'] * 100    return df[['Name', 'cur_to_52h']]def generate_table(dataframe, max_rows=15):    return html.Table(        # Header        # [html.Tr([html.Th(col, style={'text-align': 'center'}) for col in dataframe.columns])] +        # Body        [html.Tr([            html.Td(dataframe.iloc[i][col], style={'text-align': 'left'}) for col in dataframe.columns        ]) for i in range(min(len(dataframe), max_rows))]    )def ge_figure(df, idx):    trace0 = go.Scatter(        x=list(df['Date']),        y=list(df['Close']),        name=idx)    data = [trace0]    layout = dict(        # title='Trend of {}'.format(idx),        xaxis=dict(title='timeline'),        yaxis=dict(title='price'))    fig = dict(data=data, layout=layout)    return figenddate = pd.to_datetime(control_dt)raw_sp500 = clean_data(csv_path + 'idx_sp500_his.txt', enddate)raw_sh_com = clean_data(csv_path + 'idx_shanghai_his.txt', enddate)raw_dax30 = clean_data(csv_path + 'idx_dax30_his.txt', enddate)raw_hsi = clean_data(csv_path + 'idx_hsi_his.txt', enddate)# raw_ftse = clean_data(csv_path + 'FTSE 100 Historical Data.csv', enddate)raw_gold = clean_data(csv_path + 'idx_gold_his.txt', enddate)dict_vars = {'timeline': {'1m': 1,                          '3m': 3,                          '6m': 6,                          '1y': 12,                          '3y': 36,                          '5y': 60},             'index_name': {'sp500': 'SP500',                            'sh_com': '上证综指',                            'hsi': '恒生指数',                            'dax30': 'DAX30',                            'gold': 'GOLD'}             }tabs_styles = {    'height': '1240px'}tab_style = {    # 'borderBottom': '1px solid #d6d6d6',    'padding': '40px',    'fontWeight': 'bold'}tab_selected_style = {    'borderTop': '1px solid turquoise',    'borderBottom': '1px solid turquoise',    'backgroundColor': 'turquoise',    'color': 'white',    'padding': '40px'}layout = html.Div([    html.Div([        html.P("Finance", className='title is-3'),        html.Div([            html.A("全球指数", href='/wealth', className='tag is-primary subtitle is-7'),            html.A("沪深市场", href='/wealth/sec', className='tag subtitle is-7'),            html.A("ETF追踪", href='/wealth/etf', className='tag subtitle is-7'),            html.A("RPS研究", href='/wealth/sec_rps', className='tag subtitle is-7'),            # html.A(" 外汇 ", ),        ], className='row'),    ],className='hero'),    html.Div([        html.Div([            # Row 1            html.Div([                html.Br(),                html.Br(),                html.Br(),                html.Div([                    html.Label('选择日期: ', className='title is-7'),                    html.Br(),                    dcc.DatePickerSingle(                        id='my-date-picker-single',                        min_date_allowed=enddate - timedelta(days=900),                        max_date_allowed=enddate,                        display_format='YYYY-MM-DD',                        initial_visible_month=enddate,                        date=enddate),                ]),                html.Br(),                html.Button("Submit", id='refresh-button', className='button is-info'),            ], className='column is-one-quarter'),            html.Div([                html.H5("全球市场-概览", className='title is-5', style={'textAlign': 'center'}),                html.H6(id='date-summary', style={'textAlign': 'left', 'fontSize': 14}),                # html.Br(),                html.Div([                    html.Div([                        html.Div([                            html.Label("收益", className='title is-6'),                            html.H5(id='tile1-1'),                            html.H5(id='tile1-2'),                            html.H5(id='tile1-3'),                        ], className='tile notification is-parent is-success is-vertical is-5',                            style={'fontSize': 13}),                        html.Div([                            html.Label("风险", className='title is-6'),                            html.H5(id='tile2-1'),                            html.H5(id='tile2-2'),                            html.H5(id='tile2-3'),                            html.H5(id='tile2-4'),                            html.H5(id='tile2-5'),                        ], className='tile notification is-parent is-warning is-vertical is-4',                            style={'fontSize': 13}),                    ], className='tile is-parent is-12'),                ], className='tile is-ancestor'),                html.Div(id='table-container-1')            ], className='column is-three-quarters'),        ], className='columns'),        html.Hr(),        # Row 2        html.Div([            html.Div([                html.Div([                    html.Label("选择指数: ", className='title is-7'),                    dcc.Dropdown(                        id='dropdown-idx',                        options=[                            {'label': 'SP500', 'value': 'sp500'},                            {'label': '上证综指', 'value': 'sh_com'},                            {'label': '恒生指数', 'value': 'hsi'},                            {'label': 'DAX30', 'value': 'dax30'},                            # {'label': 'FTSE', 'value': 'ftse'},                            {'label': 'GOLD', 'value': 'gold'},                        ],                        value='sp500'                    ),                ]),            ], className='column is-one-quarter'),            html.Div([                html.Div([                    html.H5(id='date-summary2', className='title is-5', style={'textAlign': 'center'}),                    # html.H5(id='date-summary2', className='title is-4', style={'textAlign':'center'}),                    dcc.Tabs(id='tabs-period',                             value='1m', children=[                            dcc.Tab(label='1M', value='1m', ),                            dcc.Tab(label='3M', value='3m', ),                            dcc.Tab(label='6M', value='6m'),                            dcc.Tab(label='YTD', value='ytd'),                            dcc.Tab(label='1 Year', value='1y'),                            dcc.Tab(label='3 Years', value='3y'),                            dcc.Tab(label='5 Years', value='5y'),                        ]),                ]),                dcc.Graph(id='idx-trend'),            ], className='column is-three-quarters', )        ], className='columns'),        html.Div([            html.Label("* Source: Bloomberg", style={'textAlign': 'center'}),            html.Div(id='idx-table'),        ], className='columns')    ], className='container')], className='hero')@app.callback(    [dash.dependencies.Output('date-summary', 'children'),     dash.dependencies.Output('tile1-1', 'children'),     dash.dependencies.Output('tile1-2', 'children'),     dash.dependencies.Output('tile1-3', 'children'),     dash.dependencies.Output('tile2-1', 'children'),     dash.dependencies.Output('tile2-2', 'children'),     dash.dependencies.Output('tile2-3', 'children'),     dash.dependencies.Output('tile2-4', 'children'),     dash.dependencies.Output('tile2-5', 'children'),     dash.dependencies.Output('table-container-1', 'children'), ],    [dash.dependencies.Input('my-date-picker-single', 'date'),     dash.dependencies.Input('refresh-button', 'n_clicks')])def refresh_data(date, n_clicks):    if n_clicks is None or n_clicks == 0:        df_sel = calculate_w_date_image(enddate)        date = str(date)[:10]        smry_left = ge_summary_l(df_sel)        smry_right = ge_summary_r(df_sel)        return "至{}".format(date), "近1年，全球市场表现最好的是{}, 收益为{}%。".format(smry_left[0][0], smry_left[0][1]), \               "近3年，全球市场表现最好的是{}, 收益为{}%。".format(smry_left[1][0], smry_left[1][1]), \               "近5年，全球市场表现最好的是{}, 收益为{}%。".format(smry_left[2][0], smry_left[2][1]), \               "{}   收盘价相当于近一年高位的{:.1f}%".format(smry_right.iloc[0, 0], smry_right.iloc[0, 1]), \               "{} 收盘价相当于近一年高位的{:.1f}%".format(smry_right.iloc[1, 0], smry_right.iloc[1, 1]), \               "{}   收盘价相当于近一年高位的{:.1f}%".format(smry_right.iloc[2, 0], smry_right.iloc[2, 1]), \               "{} 收盘价相当于近一年高位的{:.1f}%".format(smry_right.iloc[3, 0], smry_right.iloc[3, 1]), \               "{}    收盘价相当于近一年高位的{:.1f}%".format(smry_right.iloc[4, 0], smry_right.iloc[4, 1]), \               ge_table(df_sel)    elif n_clicks > 0:        df_sel = calculate_w_date_image(date)        date = str(date)[:10]        smry_left = ge_summary_l(df_sel)        smry_right = ge_summary_r(df_sel)        return "至{}".format(date), "近1年，全球市场表现最好的是{}, 收益为{}%。".format(smry_left[0][0], smry_left[0][1]), \               "近3年，全球市场表现最好的是{}, 收益为{}%。".format(smry_left[1][0], smry_left[1][1]), \               "近5年，全球市场表现最好的是{}, 收益为{}%。".format(smry_left[2][0], smry_left[2][1]), \               "{}   收盘价相当于近一年高位的{:.1f}%".format(smry_right.iloc[0, 0], smry_right.iloc[0, 1]), \               "{} 收盘价相当于近一年高位的{:.1f}%".format(smry_right.iloc[1, 0], smry_right.iloc[1, 1]), \               "{}   收盘价相当于近一年高位的{:.1f}%".format(smry_right.iloc[2, 0], smry_right.iloc[2, 1]), \               "{} 收盘价相当于近一年高位的{:.1f}%".format(smry_right.iloc[3, 0], smry_right.iloc[3, 1]), \               "{}    收盘价相当于近一年高位的{:.1f}%".format(smry_right.iloc[4, 0], smry_right.iloc[4, 1]), \               ge_table(df_sel)@app.callback(    dash.dependencies.Output('date-summary2', 'children'),    [dash.dependencies.Input('dropdown-idx', 'value'), ])def refresh_data(idx):    return "{}-日线走势".format(dict_vars['index_name'][idx])@app.callback(    dash.dependencies.Output('idx-trend', 'figure'),    [dash.dependencies.Input('my-date-picker-single', 'date'),     dash.dependencies.Input('dropdown-idx', 'value'),     dash.dependencies.Input('tabs-period', 'value')])def render_content(date, idx, period):    if idx == 'sp500':        df_subset = subset_data(raw_sp500, date, period)        fig = ge_figure(df_subset, idx)        return fig    elif idx == 'sh_com':        df_subset = subset_data(raw_sh_com, date, period)        fig = ge_figure(df_subset, idx)        return fig    elif idx == 'hsi':        df_subset = subset_data(raw_hsi, date, period)        fig = ge_figure(df_subset, idx)        return fig    elif idx == 'dax30':        df_subset = subset_data(raw_dax30, date, period)        fig = ge_figure(df_subset, idx)        return fig    # elif idx == 'ftse':    #     df_subset = subset_data(raw_ftse, date, period)    #     fig = ge_figure(df_subset, idx)    #     return fig    elif idx == 'gold':        df_subset = subset_data(raw_gold, date, period)        fig = ge_figure(df_subset, idx)        return fig