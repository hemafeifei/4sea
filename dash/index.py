#!/usr/bin/env python3
# -*- coding: utf-8 -*


# index page
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_dangerously_set_inner_html

from server import app, server
from flask_login import logout_user, current_user
from views import home, login, login_fd, logout, success, about
from views import wealth, wealth_sec, wealth_etf
from views import   app_home, app_ml, app_mllab, app_his

MY_LOGO = 'https://i.loli.net/2019/11/04/yEUzIGS2YLTtWCV.png'

header = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.A(html.Img(src=MY_LOGO, alt='Logo', style={'height': '3.25rem'}),
                       className='navbar-item', href='http://www.win4sea.com/', ),
                html.A("4Sea", className='title is-6', href='/', style={'color': 'turquoise'})
            ], className='navbar-item'),
            html.Div([
                html.Br(),
                html.Br(),
                html.Br(),
            ], className='navbar-burger is-active')

        ], className='navbar-brand'),
        html.Div([
            html.Div([
                html.A("Home", className='navbar-item', href='/'),
                html.A("Finance", className='navbar-item ', href='/wealth'),
                html.A("Football", className='navbar-item ', href='/football'),
                html.A("Sentiment", className='navbar-item disabled'),
                html.Div([
                    html.A('More', className='navbar-link', style={'vertical-align': 'middle'}),
                    html.Div([
                        html.A("Tools", className='navbar-item'),
                        html.A("ML Labs", className='navbar-item'),
                        html.A("About", className='navbar-item', href='/about'),

                        html.Hr(className='navbar-divider'),
                        html.A("Report an issue", className='navbar-item')
                    ], className='navbar-dropdown')
                ], className='navbar-item has-dropdown is-hoverable')

            ], className='navbar-start'),
            html.Div([
                html.Div([
                    html.H5("User", id='user-name', className='title is-6'),
                ], className='navbar-item'),

                html.A(html.Button("Sign up", className='button is-dark'), className='navbar-item'),

                html.Div([
                    html.A("My Account", className='navbar-link', style={'vertical-align': 'middle'}),
                    html.Div([
                        html.A("Log in", className='navbar-item', href='/login'),
                        html.A("Log out", className='navbar-item', href='/logout')
                    ], className='navbar-dropdown')
                ], className='navbar-item has-dropdown is-hoverable'),

            ], className='navbar-end'),

        ], className='navbar-menu'),

    ], className='container'),

], className='navbar has-shadow  is-dark')

footer_layout = dash_dangerously_set_inner_html.DangerouslySetInnerHTML('''
<section class="hero">
  <footer class="footer">
    <div class="container">
      <div class="content has-text-centered">    
        <p>
          <strong>Represent</strong> by 4Sea Tech.
          <span class="icon is-small">
            <i class="fa fa-copyright"></i>
          </span>2019</a>
        </p>
        <p>
          <a class="icon has-text-primary" href="http://www.4sea.site/" target="_blank">
            <i class="fa fa-globe"></i>
          </a>
          <a class="icon has-text-primary" href="https://alm-github.systems.uk.hsbc/RBWM-Analytics" target="_blank">
            <i class="fa fa-github"></i>
          </a>
          <a class="icon has-text-primary" href="mailto:4sea.club@gmail.com" target="_blank">
            <i class="fa fa-envelope"></i>
          </a>
        </p>
      </div>
    </div>
  </footer>
</section>

''')

app.layout = html.Div(
    [
        header,

        html.Div([
            html.Div(
                html.Div(id='page-content', className='section'),
            ),
        ], className='container'),
        dcc.Location(id='url', refresh=False),

        # footer
        footer_layout
    ],
)


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return home.layout
    # Finance channel
    elif pathname == '/wealth':
        return wealth.layout
    elif pathname == '/wealth/sec':
        return wealth_sec.layout
    elif pathname == '/wealth/etf':
        return wealth_etf.layout

    # Football channel
    elif pathname == '/football':
        return app_home.layout
    elif pathname == '/football/his':
        return app_his.layout
    elif pathname == '/football/ml':
        return app_ml.layout
    elif pathname == '/football/mllabs':
        return app_mllab.layout

    # About
    elif pathname == '/about':
        return about.layout

    # Management
    elif pathname == '/login':
        if current_user.is_authenticated:
            return success.layout
        else:
            return login.layout
    # elif pathname == '/success':
    #     if current_user.is_authenticated:
    #         return success.layout
    #     else:
    #         return login_fd.layout
    # # elif pathname == '/success/details':
    # #     if current_user.is_authenticated:
    # #         return details.layout
    # #     else:
    # #         return login_fd.layout
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return logout.layout
        else:
            return logout.layout
    else:
        return '404 - 施工中'


@app.callback(
    Output('user-name', 'children'),
    [Input('page-content', 'children')])
def cur_user(input1):
    if current_user.is_authenticated:
        return html.Div('Welcome, ' + current_user.username)
        # 'User authenticated' return username in get_id()
    else:
        return ''


@app.callback(
    Output('logout', 'children'),
    [Input('page-content', 'children')])
def user_logout(input1):
    if current_user.is_authenticated:
        return html.A('Logout', href='/logout')
    else:
        return ''


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=55001, debug=True)
