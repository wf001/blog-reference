from flask import Flask, jsonify
from decorator import auth
app = Flask(__name__)


@app.route('/ok', methods=['GET'])
@auth
def ok():
    return jsonify({'message': 'it works.'})


if __name__ == "__main__":
    app.run()
