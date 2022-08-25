from flask import Flask, jsonify
from decorator import catch_exception
app = Flask(__name__)


@app.route('/ok', methods=['GET'])
@catch_exception
def ok():
    return jsonify({'message': 'it works.'})


if __name__ == "__main__":
    app.run()
