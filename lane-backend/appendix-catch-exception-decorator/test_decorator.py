import pytest
from flask import jsonify, Flask
from unittest import mock
from decorator import catch_exception
from http import HTTPStatus
import json

app = Flask(__name__)


class TestDecorator:
    def test_catch_exception_ok(self, mocker):
        inner_func = mock.Mock()
        with app.app_context():
            inner_func.return_value = jsonify({'message': 'ok'})
            inner_func.__name__ = 'dummy'

            wrapper = catch_exception(inner_func)
            actual = wrapper()
            assert inner_func.called
            assert json.loads(actual.data)['message'] == 'ok'

    def test_catch_exception_ng(self, mocker):
        inner_func = mock.Mock()
        inner_func.side_effect = Exception('dummy error')
        inner_func.__name__ = 'dummy'

        wrapper = catch_exception(inner_func)
        with app.app_context():
            actual = wrapper()
            assert inner_func.called
            assert actual[1] == HTTPStatus.BAD_REQUEST
            assert json.loads(actual[0].data)['error_message'] == 'dummy error'
