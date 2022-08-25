from http import HTTPStatus
from flask import jsonify


def catch_exception(f):

    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except Exception as e:
            return jsonify({'error_message': str(e)}),\
                HTTPStatus.BAD_REQUEST

    wrapped.__name__ = f.__name__
    return wrapped
