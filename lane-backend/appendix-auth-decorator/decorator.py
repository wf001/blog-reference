from flask import jsonify
from functools import wraps
from http import HTTPStatus


def auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            call_api()
        except Exception as e:
            return jsonify(
                {'error_message': "Authorization failed :" + str(e)
                 }), HTTPStatus.UNAUTHORIZED
        return f(*args, **kwargs)

    return wrapper


def call_api():
    return 'it works'
