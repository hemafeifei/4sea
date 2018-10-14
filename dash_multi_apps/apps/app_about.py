from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
# import styles
from app import app

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
                html.Div(children=[

                    dcc.Markdown('''
                    ### Latest
                    Machine Leaning will be online in October.
                    
                   
                    ### Focus
                    * Data Visualization
                    * Machine Learning to predict result
                    * data driven development
                    
                    ### Milestone
                    * __2018-07-24__  new to born
                    * __2018-08-08__  add result query
                    
                    ### 关于本站
                    本站将主要专注于数据驱动下的比赛分析。
                    * 使用爬虫收集数据
                    * 交互式的数据可视化
                    * 基于机器学习与深度学习来预测比赛结果与进球
                    '''.replace('    ', '')),

                ])
                ,

            ],
                className='column column-50'),


            html.Div([
                html.Div(children=[

                    dcc.Markdown('''
                    # Code and Technology
                    ### Dash
                    This Website was developed with Python Dash. Other apps run backstage are also writen in python.
                    The mainly used tools are:
                    * dash
                    * BeautifulSoup
                    * Flask
    
                    
                    '''.replace('    ', '')),


                    dcc.SyntaxHighlighter('''
                    import dash_html_components as html
                    import dash_core_components as dcc
                    import dash
                    
                    app = dash.Dash()
                    server = app.server
                    app.layout = html.Div([ 
                        html.Div([]),
                        html.Div([]),
                        
                    ])
                    
                    '''.replace('  ', ''),


                                          language='python'
                    ),

                    dcc.Markdown('''
                    ### Machine Learning
                    足球是圆的，一场比赛踢出任何结果都有可能，绝地翻盘、以弱胜强更是足球的魅力所在。
                    基于现阶段数据的来说，直接预测比赛结果是困难的, 为此我们还需采集大量数据，除了比赛结果，我们还将追踪主客进球数。
                    
                    Football match result prediction is a 3-class classification problem. 
                    You won't get any accuracy result based on simple team and player info.
                    Our goal is to predict the goals of a match firstly. 
                    Also we can use the visualization to find the rules between odds trend and result.
                    The mainly used tools are:
                    * sklearn
                    * Tensorflow

                    '''.replace('    ', '')),

                    dcc.SyntaxHighlighter('''
                    import tensorflow as tf
                    from sklearn.preprocessing import StandardScaler, Normalizer
                    import pandas as pd
                    import numpy as np
                    
                    ...
                                     
                    loss = tf.losses.sparse_softmax_cross_entropy(labels=tf_y, logits=output)
                    accuracy = tf.metrics.accuracy(labels=tf.squeeze(tf_y),predictions=tf.argmax(output, axis=1),)[1]
                    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.01)
                    train_op = optimizer.minimize(loss)
   

                    '''.replace('  ', ''),

                                          language='python'
                                          ),


                ])
                ,


            ],
                className='column column-50'),
        ],className='row'),




    ], className='container'),

    html.H6(children="Contact & Copyright: 4sea.club@gmail.com",
            style={'textAlign': 'center', 'backgroundColor': '#2C3859',
                   'color': '#ADB9CA', 'font-size': '16px'}),



])
