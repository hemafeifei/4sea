from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash_table_experiments as dash_table
import plotly.figure_factory as ff
import dash
import os

from app import app
import plotly.graph_objs as go
from datetime import datetime, timedelta
import pandas as pd

today = str(datetime.now() -timedelta(hours=9))
tomorrow = str(pd.to_datetime(today[:10], format='%Y-%m-%d') + timedelta(days=1))
my_path ='/Users/weizheng/PycharmProjects/Learning_flask/spyre/data/'
match_nsc = pd.read_csv(my_path+ today[:10] + '.txt')
match_nsc_en = pd.read_csv(my_path+ today[:10] + '_en.txt')
match_nsc_all = pd.concat([match_nsc, match_nsc_en], ignore_index=True)

differ_path = '/Users/weizheng/PycharmProjects/Learning_flask/spyre/differ_data/'
differ_file = differ_path + today[:10] + '.txt'
sched_path = '/Users/weizheng/PycharmProjects/football/01-jingcai/match_schedule.csv'
sched_data = pd.read_csv(sched_path)



def create_table(df):
    return html.Iframe(srcDoc=df.to_html())

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

def get_differ_data(file):
    if os.path.exists(file):
        df_differ = pd.read_csv(differ_file, header=None, names = ['Time', 'League', 'Home', 'Away', 'Prediction', 'Updated', 'href_nsc', 'Handicap', 'kly_h1',
                                                     'kly_d1', 'kly_a1', 'kly_h2','kly_d2', 'kly_a2'])
        df_differ = df_differ.drop_duplicates(subset=['Time', 'League', 'Home', 'Away', 'Prediction', 'href_nsc'], keep='last')
        df_differ = df_differ[['Prediction', 'href_nsc', 'Updated', 'Handicap']]

    else:
        df_differ = pd.DataFrame(columns=['Prediction', 'href_nsc', 'Updated', 'Handicap'])
    return df_differ


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
                ], className='column'),
                html.Div([
                    html.H4(children="四海 | \nfoursea"
                            , style={'textAlign': 'right',
                                     'color': '#F8F9FA', 'font-size': '24px', 'font': 'Bebas Neue'}),
                ], className='column'),
            ], className="row"),



        ]),
        className="gs-header gs-text-header padded"  # 'no-print'
    )



layout = html.Div([
    my_header,

    # html.Br(),
    html.Div([
        html.Div([dcc.Link(html.H5(html.Strong('Home')), href='/'), ],
                 className='column', style={'font-size': '14px', "textAlign": 'center'}),
        html.Div([dcc.Link(html.H5(html.Strong('Result')), href='/history'), ],
                 className='column', style={'font-size': '14px', "textAlign": 'center'}),
        html.Div([dcc.Link(html.H5(html.Strong('Machine Learning')), href='/ml'), ],
                 className='column ', style={'font-size': '14px', "textAlign": 'center', }),
        html.Div([dcc.Link(html.H5(html.Strong('About us')), href='/about'), ],
                 className='column ', style={'font-size': '14px', "textAlign": 'center', }),
    ], className='row', style={'backgroundColor': '#2C3859'}),
    html.Div([
        html.Div([html.H6('今日赛事')],
                 className='column', style={'color': '#ADB9CA', "textAlign": 'center'}),
        html.Div([html.H6('历史查询')],
                 className='column', style={'color': '#ADB9CA', "textAlign": 'center'}),
        html.Div([html.H6('赛事预测')],
                 className='column', style={'color': '#ADB9CA', "textAlign": 'center'}),
        html.Div([html.H6('关于我们')],
                 className='column', style={'color': '#ADB9CA', "textAlign": 'center'}),
    ], className='row', style={'backgroundColor': '#2C3859'})
    ,

    html.Br(),

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
            ], className='column-offset-5 column column-100', style={'font-size': '13px', "textAlign": 'right'}),

        ], className='row'),

        html.H3("1X2 Prediction"),

        html.Div([
            html.Div([
                html.Label("This prediction is based on odds trend.", style={'font-size': '13px',}),
                html.Label("预测胜平负.", style={'font-size': '13px',}),
                html.H6("Please check the Prediction column  of right side table."),
                html.H6("H = Home 胜"),
                html.H6("D = Draw 平"),
                html.H6("A = Away 负"),

            ], className='column column-40'),
            html.Div([
                html.Div(children=[
                    html.H5(children='Today\'s Prediction', style={ "textAlign": 'center'}),
                    html.Div(id='table-container', style={ "textAlign": 'center'}),
                    # generate_table(df_differ)
                ])
            ], className='column column-60')

        ], className='row'),
        html.Br([]),
        html.H3("Score Prediction (in testing)"),
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
                ], className='column column-50', style={'font-size': '12px', "textAlign": 'left'}),
                html.Br([]),
                html.Div([
                    html.Label("Choose Round", style={'font-size': '11px'}),

                    dcc.Dropdown(
                        id='round-dropdown',

                        multi=False),
                ], className='column column-50', style={'font-size': '12px', "textAlign": 'left'}),



            ],
                className='column column-40', style={'height': '600px', "textAlign": 'left', }),

            html.Div([
                html.Div(children=[
                    html.H5(children='Match Schedule', style={ "textAlign": 'center'}),
                    html.Div(id='datatable')
                ]),






            ],
                className='column column-60')

        ], className='row'),
    ], className='container'),
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
    dff = dff[['Time', 'League', 'Home', 'Away','Prediction', 'Handicap', 'Updated']]
    dff['Time'] = [i[5:] for i in dff['Time'].values]
    return generate_table(dff)


@app.callback(
    dash.dependencies.Output('round-dropdown', 'options'),
    [dash.dependencies.Input('league-dropdown', 'value')])
def get_round_option(league):
    df = sched_data.loc[sched_data['league'] == str(league)].reset_index(drop=True)
    round_list = list(df['Round'].unique())
    return [{'label': round_list[i], 'value': round_list[i]} for i in range(len(round_list))]

@app.callback(
    dash.dependencies.Output('round-dropdown', 'value'),
    [dash.dependencies.Input('round-dropdown', 'options')])
def get_round_value(options):
    return options[0]['value']

@app.callback(Output('datatable', 'children'),
              [Input('round-dropdown', 'value')])
def update_datatable(user_selection):
    """
    For user selections, return the relevant table
    """
    data = sched_data.loc[sched_data.Round==user_selection].reset_index(drop=True)
    new_table_schedule = generate_table(dataframe=data.drop('league', axis=1))
    return new_table_schedule