from unittest import mock
import json
from http import HTTPStatus
from config import DUMMY_ERR_MSG, APP_ROOT
import pytest
import base64


with mock.patch('api.util.authorize', lambda function: function):
    import server

client = server.app.test_client()
dummy_fav_response_dict = {
    'avator_url': "http://hogehoge.com/1",
    'created_at': "1577836200",
    'image_url': "http://hogehoge.com/2",
    'lane_type': "fav001",
    'media_id': "media_id001",
    'media_text': "this is media_text",
    'user_id': "user_id001",
    'fav_id': "fav_id001",
    'target_user_id': 'target_user_id001'
}
dummy_fav_post_data_dict = {
    'avator_url': "http://hogehoge.com/1",
    'image_url': "http://hogehoge.com/2",
    'lane_type': "fav001",
    'media_id': "media_id001",
    'media_text': "this is media_text",
    'user_id': "user_id001",
    'fav_id': "fav_id001",
    'target_user_id': 'target_user_id001'
}


class TestFav:

    def test_list_ok(self, mocker):
        fav_model_list_mock = mocker.patch('api.model.FavTable.list')
        fav_model_list_mock.return_value = {
            'Items': [dummy_fav_response_dict]*10}

        res = client.get('/api/v1/favs/dummy_user_id')
        assert res.status_code == HTTPStatus.OK
        assert fav_model_list_mock.call_count == 1
        assert len(json.loads(res.data)['medias']) == 10
        assert type(res.data) == bytes

    def test_list_ng(self, mocker):
        fav_model_list_mock = mocker.patch('api.model.FavTable.list')
        fav_model_list_mock.side_effect = Exception(DUMMY_ERR_MSG)

        res = client.get('/api/v1/favs/dummy_user_id')

        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert fav_model_list_mock.call_count == 1
        assert json.loads(res.data)['error_message'] == DUMMY_ERR_MSG

    def test_get_ok(self, mocker):
        fav_model_get_mock = mocker.patch('api.model.FavTable.get')
        fav_model_get_mock.return_value = [dummy_fav_response_dict]

        res = client.get('/api/v1/fav/dummy_fav_id')
        assert res.status_code == HTTPStatus.OK
        assert fav_model_get_mock.call_count == 1
        assert len(json.loads(res.data)['fav']) == 1
        assert type(res.data) == bytes

    def test_get_ng(self, mocker):
        fav_model_get_mock = mocker.patch('api.model.FavTable.get')
        fav_model_get_mock.side_effect = Exception(DUMMY_ERR_MSG)

        res = client.get('/api/v1/fav/dummy_user_id')

        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert fav_model_get_mock.call_count == 1
        assert json.loads(res.data)['error_message'] == DUMMY_ERR_MSG

    def test_post_ok(self, mocker):

        fav_model_post_mock = mocker.patch('api.model.FavTable.post')
        fav_model_post_mock.return_value = {'message': 'ok'}

        res = client.post("/api/v1/fav", data=dummy_fav_post_data_dict)

        assert res.status_code == HTTPStatus.OK
        assert fav_model_post_mock.call_count == 1
        assert json.loads(res.data)['message'] == 'ok'
        assert type(res.data) == bytes

    def test_post_500(self, mocker):

        fav_model_post_mock = mocker.patch('api.model.FavTable.post')
        fav_model_post_mock.side_effect = Exception(DUMMY_ERR_MSG)

        res = client.post("/api/v1/fav", data=dummy_fav_post_data_dict)

        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert fav_model_post_mock.call_count == 1
        assert json.loads(res.data)['error_message'] == DUMMY_ERR_MSG
        assert type(res.data) == bytes

    def test_delete_ok(self, mocker):
        fav_model_delete_mock = mocker.patch(
            'api.model.FavTable.delete_by_id')
        fav_model_delete_mock.return_value = {'message': 'ok'}

        res = client.delete("/api/v1/fav/somefav")

        assert res.status_code == HTTPStatus.OK
        assert fav_model_delete_mock.call_count == 1
        assert json.loads(res.data)['message'] == 'ok'
        assert type(res.data) == bytes

    def test_delete_500(self, mocker):
        fav_model_delete_mock = mocker.patch(
            'api.model.FavTable.delete_by_id')
        fav_model_delete_mock.side_effect = Exception(DUMMY_ERR_MSG)

        res = client.delete("/api/v1/fav/somefav")

        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert fav_model_delete_mock.call_count == 1
        assert json.loads(res.data)['error_message'] == DUMMY_ERR_MSG
        assert type(res.data) == bytes
