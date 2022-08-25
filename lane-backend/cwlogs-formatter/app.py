from flask import Flask, jsonify
from util import catch_exception

app = Flask(__name__)


@app.route("/")
@catch_exception
def ok():
    return jsonify(message='ok!')


@app.route("/ng")
@catch_exception
def ng():
    raise Exception
    return jsonify(message='ng')


if __name__ == '__main__':
    app.run()
