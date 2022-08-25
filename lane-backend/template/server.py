from flask import Flask, jsonify
app = Flask(__name__)


@app.route('/ok', methods=['GET'])
def ok():
    return jsonify({'message': 'it works.'})


if __name__ == "__main__":
    app.run()
