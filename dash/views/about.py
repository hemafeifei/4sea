# -*- coding: utf-8 -*

from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
# import styles
from server import app

layout = html.Div([

    # html.Br(),

    html.Div([
        html.P("About US", className='title is-3'),
        html.Div([

            html.Div([
                html.Div(children=[
                    html.Div([
                        html.P("Latest", className='title is-5'),
                        html.P("You will never walk alone."),
                        html.P(" 2018/19 season, accuracy: 66% (95 matches, 63 correct)")
                    ], className='column'),

                    html.Div([
                        html.P("Milestone", className='title is-5'),
                        html.P("2018-07-24 new to born", className='subtitle is-7'),
                        html.P("2018-08-08 add result query", className='subtitle is-7'),
                        html.P("2018-12-10 add ML History query", className='subtitle is-7'),
                        html.P("2018-12-28 add Email message, add observation model", className='subtitle is-7'),
                        html.P("2019-01-19 stack Lightgbm, SVM and KNN models to reduce variance, but bad results", className='subtitle is-7'),
                        html.P("2019-05-18 replace Observation1 with a non-standardized features", className='subtitle is-7'),
                        html.P("2019-11-08 add Finance module, framework 2.0 online", className='subtitle is-7'),
                        html.P("2020-01-30 add Sentiment module", className='subtitle is-7 is-primary'),

                    ], className='column'),

                    html.Div([
                        html.P("Focus", className='title is-5'),
                        html.P("爬虫任务采集数据", className='subtitle is-7'),
                        html.P("交互式的数据可视化", className='subtitle is-7'),
                        html.P("基于机器学习与深度学习建立预测模型", className='subtitle is-7'),
                    ], className='column'),

                ])
                ,
                # html.Div(
                # html.Img(src='data:image/png;base64,{}'.format(encoded_image)),
                # ),

            ], className='column is-half'),


            html.Div([

                html.Div(children=[
                    html.P("Code and Technology", className='title is-5'),
                    dcc.Markdown('''
                    ### Dash
                    This Website was developed with Python Dash. Other apps running backstage are also writen in python.
                    The mainly used tools are:
                    * dash
                    * BeautifulSoup
                    * Flask


                    '''.replace('    ', '')),


                    dcc.Markdown('''
                    ```py
                    import dash_html_components as html
                    import dash_core_components as dcc
                    import dash

                    app = dash.Dash()
                    server = app.server
                    app.layout = html.Div([
                        html.Div([]),
                        html.Div([]),

                    ])
                    ```
                    '''.replace('  ', ''),


                                          # language='python'
                    ),

                    dcc.Markdown('''
                    ### Machine Learning
                    足球是圆的，一场比赛踢出任何结果都有可能，绝地翻盘、以弱胜强更是足球的魅力所在。
                    基于现阶段数据的来说，直接预测比赛结果是困难的, 为此我们还需采集大量数据，除了比赛结果，我们还将追踪主客进球数。

                    Football match result prediction is a 3-class classification problem.
                    You won't get any accurate result based on simple team and player info.
                    Our goal is to find matches with special odds trend first, then use machine learning to predict if
                    those trend will be consistent with the real result. Probability was introduced to measure the prediction.

                    Also we can use the visualization to find the rules between odds trend and result.
                    The mainly used tools are:
                    * sklearn
                    * Tensorflow

                    '''.replace('    ', '')),

                    dcc.Markdown('''
                    ```py
                    import tensorflow as tf
                    from sklearn.preprocessing import StandardScaler, Normalizer
                    import pandas as pd
                    import numpy as np

                    ...

                    loss = tf.losses.sparse_softmax_cross_entropy(labels=tf_y, logits=output)
                    accuracy = tf.metrics.accuracy(labels=tf.squeeze(tf_y),predictions=tf.argmax(output, axis=1),)[1]
                    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.01)
                    train_op = optimizer.minimize(loss)

                    ```
                    '''.replace('  ', ''),

                                          # language='python'
                                          ),


                ])
                ,


            ],
                className='column is-half'),
        ],className='columns'),




    ], className='section'),



])
