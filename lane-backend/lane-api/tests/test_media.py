from unittest import mock
import json
from http import HTTPStatus
from config import DUMMY_ERR_MSG, APP_ROOT
from util import Util
import pytest
import base64
import freezegun
import time


with mock.patch('api.util.authorize', lambda function: function):
    import server

client = server.app.test_client()
dummy_media_response_dict = {
    'avator_url': "http://hogehoge.com/1",
    'created_at': "1577836200",
    'image_url': "http://hogehoge.com/2",
    'lane_type': "media001",
    'media_id': "media_id001",
    'media_text': "this is media_text",
    'user_id': "user_id001",
}
dummy_media_post_data_dict = {
    'avator_url': "http://hogehoge.com/1",
    'lane_type': "media001",
    'media_id': "media_id001",
    'media_text': "this is media_text",
    'user_id': "user_id001",
    'file_name':"dummy_file_name"
}


class TestMedia:

    @freezegun.freeze_time('2020-01-01 12:34:56')
    @pytest.mark.parametrize('cur, bt', [
        (None, None),
        ('234567890', '123456789'),
    ])
    # argument when media::list() calling
    def test_list_ok_1(self, mocker, cur, bt):
        lek_created_at = '987654321'

        media_model_list_mock = mocker.patch('api.model.MediaTable.list')
        media_model_list_mock.return_value = {
            'Items': [
                {'media_id': '1'},
            ],
            'LastEvaluatedKey': {
                'created_at': lek_created_at,
                'lane_type': 'media001'
            }
        }
        url = '/api/v1/medias'
        if(cur is not None):
            url += '?cur='+cur

        if(bt is not None):
            url += '&bt='+bt

        res = client.get(url)

        assert res.status_code == HTTPStatus.OK
        assert media_model_list_mock.call_count == 1
        if cur is None:
            assert media_model_list_mock.call_args[0][0] == \
                Util().get_current_time()
        else:
            assert media_model_list_mock.call_args[0][0] == cur

        if bt is None:
            assert media_model_list_mock.call_args[0][1] is None 
        else:
            assert media_model_list_mock.call_args[0][1] ==\
                {'created_at': bt, 'lane_type': 'media001'}

        assert type(res.data) == bytes

    @freezegun.freeze_time('2020-01-01 12:34:56')
    @pytest.mark.parametrize('ret, expected_lek', [
        (
            {
                'Items': [
                    {'media_id': '1'},
                ],
                'LastEvaluatedKey': {
                    'created_at': '1',
                    'lane_type': 'media001'
                }
            },
            '1'
        ),
        (
            {
                'Items': [
                    {'media_id': '1'},
                ],
            },
            -1
        ),
    ])
    # return value
    def test_list_ok_2(self, mocker, ret, expected_lek):

        media_model_list_mock = mocker.patch('api.model.MediaTable.list')
        media_model_list_mock.return_value = ret
        url = '/api/v1/medias?cur=1&bt=1'
        res = client.get(url)

        assert res.status_code == HTTPStatus.OK
        assert media_model_list_mock.call_count == 1
        assert json.loads(res.data)['lek'] == expected_lek
        assert type(res.data) == bytes

    def test_get_ok(self, mocker):
        media_model_get_mock = mocker.patch('api.model.MediaTable.get')
        media_model_get_mock.return_value = dummy_media_response_dict
        target_media_id = "media_id001"
        res = client.get("/api/v1/media/media_id001")

        assert res.status_code == HTTPStatus.OK
        assert media_model_get_mock.call_count == 1
        assert media_model_get_mock.call_args[0][0] == target_media_id
        assert len(json.loads(res.data)) == 1
        assert type(res.data) == bytes

    def test_get_500(self, mocker):
        media_model_get_mock = mocker.patch('api.model.MediaTable.get')
        media_model_get_mock.side_effect = Exception(DUMMY_ERR_MSG)

        res = client.get("/api/v1/media/somemedia")

        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert media_model_get_mock.call_count == 1
        assert json.loads(res.data)['error_message'] == DUMMY_ERR_MSG
        assert type(res.data) == bytes

    def test_post_ok(self, mocker):
        dummy_dict = dummy_media_post_data_dict

        media_model_post_mock = mocker.patch('api.model.MediaTable.post')
        media_model_post_mock.return_value = {'message': 'ok'}

        res = client.post("/api/v1/media", data=dummy_dict)

        assert res.status_code == HTTPStatus.OK
        assert media_model_post_mock.call_count == 1
        assert json.loads(res.data)['message'] == 'ok'
        assert type(res.data) == bytes

    def test_post_500(self, mocker):
        with open(APP_ROOT+'api/test_img_small.png', "rb") as image_file:
            data = base64.b64encode(image_file.read())
        dummy_media_post_data_dict["upfile"] = data.decode('utf-8')
        dummy_dict = dummy_media_post_data_dict

        media_model_post_mock = mocker.patch('api.model.MediaTable.post')
        media_model_post_mock.side_effect = Exception(DUMMY_ERR_MSG)

        res = client.post("/api/v1/media", data=dummy_dict)

        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert media_model_post_mock.call_count == 1
        assert json.loads(res.data)['error_message'] == DUMMY_ERR_MSG
        assert type(res.data) == bytes

    def test_delete_ok(self, mocker):
        media_model_delete_mock = mocker.patch(
            'api.model.MediaTable.delete')
        media_model_delete_mock.return_value = {'message': 'ok'}

        res = client.delete("/api/v1/media/somemedia")

        assert res.status_code == HTTPStatus.OK
        assert media_model_delete_mock.call_count == 1
        assert json.loads(res.data)['message'] == 'ok'
        assert type(res.data) == bytes

    def test_delete_500(self, mocker):
        media_model_delete_mock = mocker.patch(
            'api.model.MediaTable.delete')
        media_model_delete_mock.side_effect = Exception(DUMMY_ERR_MSG)

        res = client.delete("/api/v1/media/somemedia")

        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert media_model_delete_mock.call_count == 1
        assert json.loads(res.data)['error_message'] == DUMMY_ERR_MSG
        assert type(res.data) == bytes
