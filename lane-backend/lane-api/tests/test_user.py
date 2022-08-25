from unittest import mock
import json
from http import HTTPStatus
from config import DUMMY_ERR_MSG, APP_ROOT
import pytest
import base64
import jwt
from util import LaneInvalidGrantException
from werkzeug.datastructures import ImmutableMultiDict


with mock.patch('api.util.authorize', lambda function: function):
    import server

client = server.app.test_client()
dummy_user_response_dict = {
    'lane_type': 'user001',
    'user_id': "111111111111111",
    'user_sub': "aaaaaaaaaaa11111111111",
    'refresh_token': "11111111AAAAAAAAAAaaaaaaaaaa",
    'created_at': "1577836200",
    'description': "this is user_text",
}


class ResponseMock():
    def __init__(self, data):
        self.text = data


class TestUser:

    @pytest.mark.parametrize('res', [
        ([]),
        ([{'user_id': 'dummy_user_id'}])
    ])
    def test_get_ok(self, mocker, res):
        user_model_get_mock = mocker.patch('api.model.UserTable.get')
        user_model_get_mock.return_value = res

        actual = client.get('/api/v1/user/dummy_user_id')
        assert actual.status_code == HTTPStatus.OK
        assert user_model_get_mock.call_count == 1
        assert type(actual.data) == bytes

    def test_get_ng(self, mocker):
        user_model_get_mock = mocker.patch('api.model.UserTable.get')
        user_model_get_mock.side_effect = Exception(DUMMY_ERR_MSG)

        res = client.get('/api/v1/user/dummy_user_id')
        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert json.loads(res.data)['error_message'] == DUMMY_ERR_MSG
        assert user_model_get_mock.call_count == 1
        assert type(res.data) == bytes

    def test_post_ok(self, mocker):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')
        validate_id_token_mock.return_value = {'sub': '111111111'}

        requests_post_mock = mocker.patch('requests.post')
        res = ResponseMock(
            json.dumps({
                'id_token': 'dummy_id_token',
                'refresh_token': 'dummy_refresh_token'
            })
        )
        requests_post_mock.return_value = res

        user_model_post_mock = mocker.patch('api.model.UserTable.post')

        data = {
            'user_id': 'dummy',
            'serverAuthCode': 'dummy',
            'idToken': 'dummy',
        }

        res = client.post('/api/v1/user', data=data)

        assert res.status_code == HTTPStatus.OK
        assert json.loads(res.data)['id_token'] == 'dummy_id_token'
        assert validate_id_token_mock.call_count == 1
        assert requests_post_mock.call_count == 1
        assert user_model_post_mock.call_count == 1
        assert type(res.data) == bytes

    @pytest.mark.parametrize('err, expected', [
        (jwt.ExpiredSignatureError, HTTPStatus.BAD_REQUEST),
        (StopIteration, HTTPStatus.BAD_REQUEST),
        (Exception, HTTPStatus.INTERNAL_SERVER_ERROR)
    ])
    def test_post_validate_ng(self, mocker, err, expected):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')
        validate_id_token_mock.side_effect = err

        requests_post_mock = mocker.patch('requests.post')
        res = ResponseMock(
            json.dumps({
                'id_token': 'dummy_id_token',
                'refresh_token': 'dummy_refresh_token'
            })
        )
        requests_post_mock.return_value = res

        user_model_post_mock = mocker.patch('api.model.UserTable.post')

        data = {
            'user_id': 'dummy',
            'serverAuthCode': 'dummy',
            'idToken': 'dummy',
        }

        res = client.post('/api/v1/user', data=data)

        assert res.status_code == expected
        assert validate_id_token_mock.call_count == 1
        assert requests_post_mock.call_count == 0
        assert user_model_post_mock.call_count == 0
        assert type(res.data) == bytes

    def test_post_requests_ng1(self, mocker):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')
        validate_id_token_mock.return_value = {'sub': '111111111'}

        requests_post_mock = mocker.patch('requests.post')
        requests_post_mock.return_value = ResponseMock(
            data=json.dumps({'error': 'dummy'})
        )

        user_model_post_mock = mocker.patch('api.model.UserTable.post')

        data = {
            'user_id': 'dummy',
            'serverAuthCode': 'dummy',
            'idToken': 'dummy',
        }

        res = client.post('/api/v1/user', data=data)

        assert res.status_code == HTTPStatus.BAD_REQUEST
        assert validate_id_token_mock.call_count == 1
        assert requests_post_mock.call_count == 1
        assert user_model_post_mock.call_count == 0
        assert type(res.data) == bytes

    def test_post_requests_ng2(self, mocker):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')
        validate_id_token_mock.return_value = {'sub': '111111111'}

        requests_post_mock = mocker.patch('requests.post')
        requests_post_mock.side_effect = Exception(DUMMY_ERR_MSG)

        user_model_post_mock = mocker.patch('api.model.UserTable.post')

        data = {
            'user_id': 'dummy',
            'serverAuthCode': 'dummy',
            'idToken': 'dummy',
        }

        res = client.post('/api/v1/user', data=data)

        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert validate_id_token_mock.call_count == 1
        assert requests_post_mock.call_count == 1
        assert user_model_post_mock.call_count == 0
        assert type(res.data) == bytes

    def test_post_model_post_ng(self, mocker):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')
        validate_id_token_mock.return_value = {'sub': '111111111'}

        requests_post_mock = mocker.patch('requests.post')
        res = ResponseMock(
            json.dumps({
                'id_token': 'dummy_id_token',
                'refresh_token': 'dummy_refresh_token'
            })
        )
        requests_post_mock.return_value = res

        user_model_post_mock = mocker.patch('api.model.UserTable.post')
        user_model_post_mock.side_effect = Exception(DUMMY_ERR_MSG)

        data = {
            'user_id': 'dummy',
            'serverAuthCode': 'dummy',
            'idToken': 'dummy',
        }

        res = client.post('/api/v1/user', data=data)

        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert validate_id_token_mock.call_count == 1
        assert requests_post_mock.call_count == 1
        assert user_model_post_mock.call_count == 1
        assert type(res.data) == bytes

    def test_put_ok(self, mocker):
        user_model_put_mock = mocker.patch('api.model.UserTable.put')
        user_model_put_mock.return_value = {'meesage', 'ok'}
        data = {
            'created_at': '1577836200',
            'description': 'updated',
            'avator_url': 'https://s3.aws.amazon.com/hogehoge'
        }
        res = client.put('/api/v1/user', data=data)
        assert res.status_code == HTTPStatus.OK
        assert user_model_put_mock.call_count == 1
        assert type(res.data) == bytes

    def test_put_ng(self, mocker):
        user_model_put_mock = mocker.patch('api.model.UserTable.put')
        user_model_put_mock.side_effect = Exception
        data = {
            'created_at': '1577836200',
            'description': 'updated',
            'avator_url': 'https://s3.aws.amazon.com/hogehoge'
        }
        res = client.put('/api/v1/user', data=data)
        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert user_model_put_mock.call_count == 1
        assert type(res.data) == bytes

    def test_update_no_refresh(self, mocker):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')

        data = {
            'idToken': 'dummy',
        }
        res = client.post('/api/v1/user/update', data=data)
        assert validate_id_token_mock.call_count == 1
        assert res.status_code == HTTPStatus.OK
        assert type(res.data) == bytes

    def test_update_refresh_ok(self, mocker):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')

        validate_id_token_mock.side_effect = jwt.ExpiredSignatureError
        get_sub_mock = mocker.patch(
            'api.util.Util.get_user_sub_without_verification')
        get_sub_mock.return_value = {'sub': 'dummy'}
        model_get_user_by_sub_mock = mocker.patch(
            'api.model.UserTable.get_sub')
        model_get_user_by_sub_mock.return_value = [{
            'refresh_token': 'dummy'
        }]

        requests_post_mock = mocker.patch('requests.post')
        res = ResponseMock(
            json.dumps({
                'id_token': 'refreshed_id_token',
            })
        )
        requests_post_mock.return_value = res

        data = {
            'idToken': 'expired_dummy',
        }
        res = client.post('/api/v1/user/update', data=data)
        assert validate_id_token_mock.call_count == 1
        assert get_sub_mock.call_count == 1
        assert model_get_user_by_sub_mock.call_count == 1
        assert requests_post_mock.call_count == 1
        assert res.status_code == HTTPStatus.OK
        assert json.loads(res.data)['id_token'] == 'refreshed_id_token'
        assert type(res.data) == bytes

    # granted id token validation error
    def test_update_refresh_ng1(self, mocker):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')

        validate_id_token_mock.side_effect = Exception
        get_sub_mock = mocker.patch(
            'api.util.Util.get_user_sub_without_verification')
        get_sub_mock.return_value = {'sub': 'dummy'}
        model_get_user_by_sub_mock = mocker.patch(
            'api.model.UserTable.get_sub')
        model_get_user_by_sub_mock.return_value = [{
            'refresh_token': 'dummy'
        }]

        requests_post_mock = mocker.patch('requests.post')
        res = ResponseMock(
            json.dumps({
                'id_token': 'refreshed_id_token',
            })
        )
        requests_post_mock.return_value = res

        data = {
            'idToken': 'invalid_dummy',
        }
        res = client.post('/api/v1/user/update', data=data)
        assert validate_id_token_mock.call_count == 1
        assert get_sub_mock.call_count == 0
        assert model_get_user_by_sub_mock.call_count == 0
        assert requests_post_mock.call_count == 0
        assert res.status_code == HTTPStatus.BAD_REQUEST
        assert type(res.data) == bytes

    # id token decode error
    def test_update_refresh_ng2(self, mocker):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')
        validate_id_token_mock.side_effect = jwt.ExpiredSignatureError

        get_sub_mock = mocker.patch(
            'api.util.Util.get_user_sub_without_verification')
        get_sub_mock.side_effect = Exception

        model_get_user_by_sub_mock = mocker.patch(
            'api.model.UserTable.get_sub')
        model_get_user_by_sub_mock.return_value = [{
            'refresh_token': 'dummy'
        }]

        requests_post_mock = mocker.patch('requests.post')
        res = ResponseMock(
            json.dumps({
                'id_token': 'refreshed_id_token',
            })
        )
        requests_post_mock.return_value = res

        data = {
            'idToken': 'expired_dummy',
        }
        res = client.post('/api/v1/user/update', data=data)
        assert validate_id_token_mock.call_count == 1
        assert get_sub_mock.call_count == 1
        assert model_get_user_by_sub_mock.call_count == 0
        assert requests_post_mock.call_count == 0
        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert type(res.data) == bytes

    # user doesnt exist
    def test_update_refresh_ng3(self, mocker):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')

        validate_id_token_mock.side_effect = jwt.ExpiredSignatureError
        get_sub_mock = mocker.patch(
            'api.util.Util.get_user_sub_without_verification')
        get_sub_mock.return_value = {'sub': 'dummy'}
        model_get_user_by_sub_mock = mocker.patch(
            'api.model.UserTable.get_sub')
        model_get_user_by_sub_mock.return_value = []

        requests_post_mock = mocker.patch('requests.post')
        res = ResponseMock(
            json.dumps({
                'id_token': 'refreshed_id_token',
            })
        )
        requests_post_mock.return_value = res

        data = {
            'idToken': 'expired_dummy',
        }
        res = client.post('/api/v1/user/update', data=data)
        assert validate_id_token_mock.call_count == 1
        assert get_sub_mock.call_count == 1
        assert model_get_user_by_sub_mock.call_count == 1
        assert requests_post_mock.call_count == 0
        assert res.status_code == HTTPStatus.NOT_FOUND
        assert type(res.data) == bytes

    # boto3 api error
    def test_update_refresh_ng4(self, mocker):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')

        validate_id_token_mock.side_effect = jwt.ExpiredSignatureError
        get_sub_mock = mocker.patch(
            'api.util.Util.get_user_sub_without_verification')
        get_sub_mock.return_value = {'sub': 'dummy'}
        model_get_user_by_sub_mock = mocker.patch(
            'api.model.UserTable.get_sub')
        model_get_user_by_sub_mock.side_effect = Exception

        requests_post_mock = mocker.patch('requests.post')
        res = ResponseMock(
            json.dumps({
                'id_token': 'refreshed_id_token',
            })
        )
        requests_post_mock.return_value = res

        data = {
            'idToken': 'expired_dummy',
        }
        res = client.post('/api/v1/user/update', data=data)
        assert validate_id_token_mock.call_count == 1
        assert get_sub_mock.call_count == 1
        assert model_get_user_by_sub_mock.call_count == 1
        assert requests_post_mock.call_count == 0
        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert type(res.data) == bytes

    # google token refresh api error
    def test_update_refresh_ng5(self, mocker):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')

        validate_id_token_mock.side_effect = jwt.ExpiredSignatureError
        get_sub_mock = mocker.patch(
            'api.util.Util.get_user_sub_without_verification')
        get_sub_mock.return_value = {'sub': 'dummy'}
        model_get_user_by_sub_mock = mocker.patch(
            'api.model.UserTable.get_sub')
        model_get_user_by_sub_mock.return_value = [{
            'refresh_token': 'dummy'
        }]

        requests_post_mock = mocker.patch('requests.post')
        res = ResponseMock(
            json.dumps({
                'error': 'dummy',
            })
        )
        requests_post_mock.return_value = res

        data = {
            'idToken': 'expired_dummy',
        }
        res = client.post('/api/v1/user/update', data=data)
        assert validate_id_token_mock.call_count == 1
        assert get_sub_mock.call_count == 1
        assert model_get_user_by_sub_mock.call_count == 1
        assert requests_post_mock.call_count == 1
        assert res.status_code == HTTPStatus.BAD_REQUEST
        assert type(res.data) == bytes

    def test_login_ok(self, mocker):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')
        validate_id_token_mock.return_value = {'sub': 'dummy sub'}

        model_get_user_sub_mock = mocker.patch('api.model.UserTable.get_sub')
        model_get_user_sub_mock.return_value = [{
            'user_id': 'aaa'
        }]
        data = {
            'idToken': 'dummy',
        }
        res = client.post('/api/v1/user/login', data=data)
        assert res.status_code == HTTPStatus.OK
        assert json.loads(res.data)['message'] == 'ok'
        assert validate_id_token_mock.call_count == 1
        assert model_get_user_sub_mock.call_count == 1
        assert type(res.data) == bytes

    @pytest.mark.parametrize('err, status_code', [
        (StopIteration, HTTPStatus.BAD_REQUEST),
        (jwt.ExpiredSignatureError, HTTPStatus.BAD_REQUEST),
        (Exception, HTTPStatus.INTERNAL_SERVER_ERROR)
    ])
    def test_login_validate_ng(self, mocker, err, status_code):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')
        validate_id_token_mock.side_effect = err

        model_get_user_sub_mock = mocker.patch('api.model.UserTable.get_sub')
        model_get_user_sub_mock.return_value = {
            'user_id': 'aaa'
        }
        data = {
            'idToken': 'dummy',
        }
        res = client.post('/api/v1/user/login', data=data)
        assert res.status_code == status_code
        assert validate_id_token_mock.call_count == 1
        assert model_get_user_sub_mock.call_count == 0
        assert type(res.data) == bytes

    def test_login_user_not_exist_ng(self, mocker):
        validate_id_token_mock = mocker.patch(
            'api.util.Util.validate_id_token')
        validate_id_token_mock.return_value = {'sub': 'dummy sub'}

        model_get_user_sub_mock = mocker.patch('api.model.UserTable.get_sub')
        model_get_user_sub_mock.return_value = []
        data = {
            'idToken': 'dummy',
        }
        res = client.post('/api/v1/user/login', data=data)
        assert res.status_code == HTTPStatus.NOT_FOUND
        assert validate_id_token_mock.call_count == 1
        assert model_get_user_sub_mock.call_count == 1
        assert type(res.data) == bytes
