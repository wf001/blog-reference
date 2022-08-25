from flask import Flask, jsonify, request
from util import _info
app = Flask(__name__)


@app.route('/ok', methods=['GET'])
def ok():
    _info('here!')
    return jsonify({'message': 'it works.'})


if __name__ == "__main__":
    app.run()
