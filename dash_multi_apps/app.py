import dash

app = dash.Dash()
server = app.server
app.config.supress_callback_exceptions = True

external_css = [
                "https://rawgit.com/outboxcraft/beauter/master/beauter.min.css",
                # "https://cdn.rawgit.com/necolas/normalize.css/master/normalize.css",
                # "https://cdn.rawgit.com/milligram/milligram/master/dist/milligram.min.css",
                # "https://fonts.googleapis.com/css?family=Roboto:300,300italic,700,700italic",
                # "https://cdn.rawgit.com/plotly/dash-app-stylesheets/5047eb29e4afe01b45b27b1d2f7deda2a942311a/goldman-sachs-report.css",
                'https://codepen.io/plotly/pen/YEYMBZ.css',
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]

for css in external_css:
    app.css.append_css({"external_url": css})