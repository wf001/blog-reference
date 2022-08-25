import pytest
from flask import jsonify, Flask
from unittest import mock
from decorator import auth, call_api
from http import HTTPStatus
import json

app = Flask(__name__)


class TestDecorator:
    def test_auth_ok(self, mocker):
        inner_func = mock.Mock()
        with app.app_context():
            inner_func.return_value = jsonify({'message': 'ok'})
            call_api_mock = mocker.patch('decorator.call_api')
            call_api_mock.return_value = 'call_api_ret'

            wrapper = auth(inner_func)
            actual = wrapper()
            assert inner_func.called
            assert json.loads(actual.data)['message'] == 'ok'

    def test_auth_ng(self, mocker):
        inner_func = mock.Mock()
        inner_func.return_value = 'inner_func_ret'
        call_api_mock = mocker.patch('decorator.call_api')
        call_api_mock.side_effect = Exception("dummy error")

        wrapper = auth(inner_func)
        with app.app_context():
            actual = wrapper()
            assert inner_func.called == False
            assert actual[1] == HTTPStatus.UNAUTHORIZED
            assert json.loads(actual[0].data)['error_message'] == \
                'Authorization failed :dummy error'
