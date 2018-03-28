from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello 4Sea!"


if __name__ == '__main__':
    app.run()