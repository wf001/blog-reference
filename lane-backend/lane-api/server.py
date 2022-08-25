from flask import Flask, jsonify, request
import traceback
import json
import requests
from os.path import join, dirname
from dotenv import load_dotenv
from api.config import ENVIRONMENT, ENV_TYPE, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_TOKEN_ENDPOINT, GOOGLE_CERT_ENDPOINT
import jwt
from jwt.algorithms import RSAAlgorithm
from api.util import catch_exception

from api import media, user, fav, comment
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(media.bp_media)
app.register_blueprint(user.bp_user)
app.register_blueprint(fav.bp_fav)
app.register_blueprint(comment.bp_comment)

CORS(app)


@app.route('/ok', methods=['GET'])
@catch_exception
def ok():
    return jsonify({'message': 'updated, it works'})


if __name__ == "__main__":
    load_dotenv(verbose=True)
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    if(ENVIRONMENT == ENV_TYPE.PROD):
        app.run(debug=True, host="0.0.0.0", port="80")
    else:
        app.run(debug=False)
