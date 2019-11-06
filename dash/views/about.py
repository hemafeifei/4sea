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

                    dcc.Markdown('''
                    ## Latest
                    __You will never walk alone.__

                    2018/19 season, accuracy: 66% (95 matches, 63 correct)


                    ## Focus
                    * Data Visualization
                    * Use machine Learning to predict result
                    * data driven development

                    ## Milestone
                    * __2018-07-24__  new to born
                    * __2018-08-08__  add result query
                    * __2018-12-10__  add ML History query
                    * __2018-12-28__  add Email message, add observation model
                    * __2019-01-19__  stack Lightgbm, SVM and KNN models to reduce variance, but bad results
                    * __2019-05-18__  replace Observation1 with a non-standardized features


                    ## 关于本站
                    本站主要专注于数据驱动下的比赛分析。
                    * 使用爬虫收集数据
                    * 交互式的数据可视化
                    * 基于机器学习与深度学习来预测比赛结果与进球
                    '''),


                ])
                ,
                # html.Div(
                # html.Img(src='data:image/png;base64,{}'.format(encoded_image)),
                # ),

            ], className='column is-half'),


            html.Div([
                html.Div(children=[

                    dcc.Markdown('''
                    # Code and Technology
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
