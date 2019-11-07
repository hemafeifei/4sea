import warnings
# Dash configuration
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import dash_dangerously_set_inner_html
from server import app

# FI_IMAGE = 'https://cdn.earlytorise.com/wp-content/uploads/2018/02/stockmarket.jpg'
# FT_IMAGE = 'http://www.freelunch.co.in/wp-content/uploads/2018/07/machine-learning-in-sports-730x410.png'
# SEC_IMAGE = 'https://www.hsbc.com.hk/content/dam/hsbc/hk/images/investments/16-9/stocks-trading-graph-21364.jpg/jcr:content/renditions/cq5dam.web.300.1000.jpeg'
# TMP_IMAGE = 'https://catanacapital.com/wp-content/uploads/2019/03/Mathematical_Concept-780x438.jpg'
# TMP_IMAGE2 = 'http://img5.imgtn.bdimg.com/it/u=1950189138,323868647&fm=26&gp=0.jpg'
# ABT_IMAGE = 'https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcTLanMv0-Ovx-Zlftqdi5lV_oYJ9OYuNmiG3hbVKny5JLWuWgVP'

FI_IMAGE = 'https://i.loli.net/2019/11/04/7mPCGdKe2XJfEoA.jpg '
FT_IMAGE = 'https://i.loli.net/2019/11/04/p3A2nbrKfyLD1qX.jpg'
SENTI_IMAGE = 'https://i.loli.net/2019/11/04/6Use9w3fCvHt2p4.jpg'
TOOL_IMAGE = 'https://i.loli.net/2019/11/04/cIaQFDqgz1t9Erx.jpg'
LRN_IMAGE = 'https://i.loli.net/2019/11/04/aGXUzA1yfdNqIZT.jpg'
ABT_IMAGE = 'https://i.loli.net/2019/11/04/px1XfJ4WNQuTPKk.jpg'

layout = html.Div([
    html.Div([
        html.Div(className='flow-1'),
        html.Div(className='flow-2'),
        html.Div(className='flow-3'),
    ], className='flow'),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Img(src=FI_IMAGE),
                    ], className='card-image'),
                    html.Div([
                        html.A("Finance", className="title is-3 no-padding", href='/wealth',
                               style={'color': 'turquoise'}),

                        html.Div([
                            html.A(" 全球指数 ",  href='/wealth', className='tag'),
                            "|",
                            html.A(" 沪深市场 ", href='/wealth/sec', className='tag'),
                            "|",
                            html.A(" ETF追踪 ", className='tag'),
                            # "|",
                            # html.A(" 外汇 ", ),
                        ], className='row'),
                        html.Hr(),
                        html.H5("The Beast stumbled in the dark for it could no longer see the path. It started to "
                                "fracture and weaken, trying to reshape itself into the form of metal. Even the witches "
                                "would no longer lay eyes upon it, for it had become hideous and twisted.",
                                className='content')
                    ], className='card-content')
                ], className='card large round')
            ], className='column is-one-third'),
            html.Div([
                html.Div([
                    html.Div([
                        html.Img(src=FT_IMAGE)
                    ], className='card-image'),
                    html.Div([
                        html.A("Football", className="title is-3 no-padding", href='/customer',
                               style={'color': 'turquoise'}),
                        html.Div([
                            html.A(" 今日赛事 ", href='/football', className='tag'),
                            "|",
                            html.A(" 历史回查 ", href='/football/his', className='tag'),
                            "|",
                            html.A(" 赛果预测 ", href='/football/ml',  className='tag'),

                        ], className='row'),
                        html.Hr(),
                        html.H5("The Beast stumbled in the dark for it could no longer see the path. It started to "
                                "fracture and weaken, trying to reshape itself into the form of metal. Even the witches "
                                "would no longer lay eyes upon it, for it had become hideous and twisted.",
                                className='content')
                    ], className='card-content')
                ], className='card large round')
            ], className='column is-one-third'),
            html.Div([
                html.Div([
                    html.Div([
                        html.Img(src=SENTI_IMAGE)
                    ], className='card-image'),
                    html.Div([
                        html.A("Sentiment", className="title is-3 no-padding", href='/sentiment',
                               style={'color': 'turquoise'}),
                        html.Div([
                            html.A(" 热搜榜 ", href='/sentiment', className='tag'),
                            "|",
                            html.A(" 市场情绪 ", href='/sentiment/market', className='tag'),

                        ], className='row'),
                        html.Hr(),
                        html.H5("The Beast stumbled in the dark for it could no longer see the path. It started to "
                                "fracture and weaken, trying to reshape itself into the form of metal. Even the witches "
                                "would no longer lay eyes upon it, for it had become hideous and twisted.",
                                className='content')
                    ], className='card-content')
                ], className='card large round')
            ], className='column is-one-third'),
            html.Div([
                html.Div([
                    html.Div([
                        html.Img(src=TOOL_IMAGE)
                    ], className='card-image'),
                    html.Div([
                        html.A("Tools", className="title is-3 ", style={'color': 'turquoise'}),
                        html.Hr(),
                        html.H5("The Beast stumbled in the dark for it could no longer see the path. It started to "
                                "fracture and weaken, trying to reshape itself into the form of metal. Even the witches "
                                "would no longer lay eyes upon it, for it had become hideous and twisted.",
                                className='content')
                    ], className='card-content')
                ], className='card large round')
            ], className='column is-one-third'),
            html.Div([
                html.Div([
                    html.Div([
                        html.Img(src=LRN_IMAGE)
                    ], className='card-image'),
                    html.Div([
                        html.A("Learning", className="title is-3", style={'color': 'turquoise'}),
                        html.Hr(),
                        html.H5("The Beast stumbled in the dark for it could no longer see the path. It started to "
                                "fracture and weaken, trying to reshape itself into the form of metal. Even the witches "
                                "would no longer lay eyes upon it, for it had become hideous and twisted.",
                                className='content')
                    ], className='card-content')
                ], className='card large round')
            ], className='column is-one-third'),
            html.Div([
                html.Div([
                    html.Div([
                        html.Img(src=ABT_IMAGE)
                    ], className='card-image'),
                    html.Div([
                        html.A("About", className="title is-3", style={'color': 'turquoise'}),
                        html.Hr(),
                        html.H5("The Beast stumbled in the dark for it could no longer see the path. It started to "
                                "fracture and weaken, trying to reshape itself into the form of metal. Even the witches "
                                "would no longer lay eyes upon it, for it had become hideous and twisted.",
                                className='content')
                    ], className='card-content')
                ], className='card large round')
            ], className='column is-one-third'),
        ], className='row columns is-multiline')
    ], className='section'),
], className='container')
