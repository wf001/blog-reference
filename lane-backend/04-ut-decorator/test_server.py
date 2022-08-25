from unittest import mock
import json

with mock.patch('decorator.auth', lambda function: function):
    import server

client = server.app.test_client()


class TestServer:
    def test_ok(self, mocker):
        actual = client.get('/ok')
        assert json.loads(actual.data)['message'] == 'it works.'
