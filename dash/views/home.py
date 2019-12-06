#!/usr/bin/env python3
# -*- coding: utf-8 -*
import dash_html_components as html

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
                            html.A(" 全球指数 ", href='/wealth', className='tag'),
                            "|",
                            html.A(" 沪深市场 ", href='/wealth/sec', className='tag'),
                            "|",
                            html.A(" ETF追踪 ", className='tag'),
                            # "|",
                            # html.A(" 外汇 ", ),
                        ], className='row'),
                        html.Hr(),
                        html.H5("巴菲特建议普通人购买的SP500指数，在过去40年期间，年化收益可达7.5%左右。在中国融入全球化近20年后的今天，"
                                "证券市场显然是值得关注的地方。当然中国很多好的企业在境外上市，因此投资中国证券市场需要关注全球市场。"
                                "如果你还懂一点量化策略，可以预期收益10%-15%",
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
                        html.A("Football", className="title is-3 no-padding", href='/football',
                               style={'color': 'turquoise'}),
                        html.Div([
                            html.A(" 今日赛事 ", href='/football', className='tag'),
                            "|",
                            html.A(" 历史回查 ", href='/football/his', className='tag'),
                            "|",
                            html.A(" 赛果预测 ", href='/football/ml', className='tag'),

                        ], className='row'),
                        html.Hr(),
                        html.H5("足球的魅力无与伦比，一切皆有可能，但比赛的结果并非完全不可预测。"
                                "我们持续追踪10个赛季的五大联赛，发现有一部分比赛是有明显的赔率波动趋势。根据这一趋势，使用机器学习"
                                "进行建模并预测，持续增加的数据让我们的模型不断进步，上赛季预测准确率超过67%。",
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
                        html.H5("追踪舆论热点与财经温度。追踪财经市场与情绪相关的Sentiment分析。"
                                "从微博、谷歌反馈的数据来看：中国人都在追娱乐新闻，德国人都在关注球赛，美国人在搜 Taylor Swift。"
                                "自这届美国总统上任，舆论认为世界进入了逆全球化阶段，其实这些年各个地区都是各玩各的吧....",
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
                        html.H5("基金定投、财富规划、保险计算等实用工具。",
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
                        html.A("Labs", className="title is-3", style={'color': 'turquoise'}),
                        html.Hr(),
                        html.H5("趣味实验室。一切新奇的想法都可以进行测试，比如已经蓄势待发近N年的：地图炮、转会市场网...",
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
                        html.A("About", className="title is-3", href='/about', style={'color': 'turquoise'}),
                        html.Hr(),
                        html.H5("关于我们。"
                                "你不是一个人在战斗。"
                                "Good Luck! Viel Spaß!",
                                className='content')
                    ], className='card-content')
                ], className='card large round')
            ], className='column is-one-third'),
        ], className='row columns is-multiline')
    ], className='section'),
], className='container', )
