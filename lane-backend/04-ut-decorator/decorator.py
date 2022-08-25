from flask import request, jsonify
from functools import wraps


def auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            raise Exception()
        except Exception:
            return jsonify({'message': 'ng'})
        return f(*args, **kwargs)

    return wrapper
