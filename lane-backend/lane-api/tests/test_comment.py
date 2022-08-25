from unittest import mock
import json
from http import HTTPStatus
from config import DUMMY_ERR_MSG, APP_ROOT
import pytest
import base64


with mock.patch('api.util.authorize', lambda function: function):
    import server

client = server.app.test_client()
dummy_comment_dict = {
    'avator_url': "http://hogehoge.com/1",
    'created_at': "1577836200",
    'lane_type': "comment001",
    'media_id': "media_id001",
    'user_id': "user_id001",
    'comment_id': 'comment_id_001',
    'comment_text': 'this is comment'
}


class TestComment:

    def test_list_ok(self, mocker):
        comment_model_list_mock = mocker.patch('api.model.CommentTable.list')
        comment_model_list_mock.return_value = [dummy_comment_dict]*10

        res = client.get('/api/v1/comments/dummy_media_id/1111111111')
        assert res.status_code == HTTPStatus.OK
        assert comment_model_list_mock.call_count == 1
        assert len(json.loads(res.data)['comments']) == 10
        assert type(res.data) == bytes

    def test_list_ng(self, mocker):
        comment_model_list_mock = mocker.patch('api.model.CommentTable.list')
        comment_model_list_mock.side_effect = Exception(DUMMY_ERR_MSG)

        res = client.get('/api/v1/comments/dummy_media_id/111111111111')

        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert comment_model_list_mock.call_count == 1
        assert json.loads(res.data)['error_message'] == DUMMY_ERR_MSG

    def test_get_ok(self, mocker):
        comment_model_get_mock = mocker.patch('api.model.CommentTable.get')
        comment_model_get_mock.return_value = [dummy_comment_dict]

        res = client.get('/api/v1/comment/dummy_comment_id')
        assert res.status_code == HTTPStatus.OK
        assert comment_model_get_mock.call_count == 1
        assert len(json.loads(res.data)['comment']) == 1
        assert type(res.data) == bytes

    def test_get_ng(self, mocker):
        comment_model_get_mock = mocker.patch('api.model.CommentTable.get')
        comment_model_get_mock.side_effect = Exception(DUMMY_ERR_MSG)

        res = client.get('/api/v1/comment/dummy_comment_id')

        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert comment_model_get_mock.call_count == 1
        assert json.loads(res.data)['error_message'] == DUMMY_ERR_MSG

    def test_post_ok(self, mocker):

        comment_model_post_mock = mocker.patch('api.model.CommentTable.post')
        comment_model_post_mock.return_value = {'message': 'ok'}

        res = client.post("/api/v1/comment", data=dummy_comment_dict)

        assert res.status_code == HTTPStatus.OK
        assert comment_model_post_mock.call_count == 1
        assert json.loads(res.data)['message'] == 'ok'
        assert type(res.data) == bytes

    def test_post_500(self, mocker):

        comment_model_post_mock = mocker.patch('api.model.CommentTable.post')
        comment_model_post_mock.side_effect = Exception(DUMMY_ERR_MSG)

        res = client.post('/api/v1/comment', data=dummy_comment_dict)

        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert comment_model_post_mock.call_count == 1
        assert json.loads(res.data)['error_message'] == DUMMY_ERR_MSG
        assert type(res.data) == bytes

    def test_delete_ok(self, mocker):
        comment_model_delete_mock = mocker.patch(
            'api.model.CommentTable.delete')
        comment_model_delete_mock.return_value = {'message': 'ok'}

        res = client.delete("/api/v1/comment/somefav")

        assert res.status_code == HTTPStatus.OK
        assert comment_model_delete_mock.call_count == 1
        assert json.loads(res.data)['message'] == 'ok'
        assert type(res.data) == bytes

    def test_delete_500(self, mocker):
        comment_model_delete_mock = mocker.patch(
            'api.model.CommentTable.delete')
        comment_model_delete_mock.side_effect = Exception(DUMMY_ERR_MSG)

        res = client.delete("/api/v1/comment/somefav")

        assert res.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert comment_model_delete_mock.call_count == 1
        assert json.loads(res.data)['error_message'] == DUMMY_ERR_MSG
        assert type(res.data) == bytes
