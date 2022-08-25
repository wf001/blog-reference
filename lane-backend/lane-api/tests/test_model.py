from datetime import datetime, timedelta
from moto import mock_dynamodb2
import boto3
import pytest
import random
import string
from api.model import MediaTable, FavTable, UserTable, CommentTable
from api.util import Util, LaneInvalidFormat, _info
from config import DB_NAME, TABLE_TYPE, KEY_TYPE
from setup_dynamodb import DynamoDBSetup
from botocore.exceptions import ClientError


class TestMediaTable:

    @mock_dynamodb2
    @pytest.mark.parametrize('cur, bt, rg, expected_volume, is_included_LEK, start, end', [
        (
            Util().get_current_time(),
            None,
            10,
            10,
            True,
            '1609459219',
            '1609459210'
        ),
        (
            Util().get_current_time(),
            None,
            40,
            20,
            False,
            '1609459219',
            '1609459200'
        ),
        (
            '1609459200',
            None,
            10,
            0,
            False,
            None,
            None
        ),
        (
            '1609459210',
            None,
            5,
            5,
            True,
            '1609459209',
            '1609459205'
        ),
        (
            Util().get_current_time(),
            {
                'created_at': '1609459301',
                KEY_TYPE.LANE_TYPE.value: TABLE_TYPE.MEDIA.value
            },
            5,
            5,
            True,
            '1609459219',
            '1609459215'
        ),
        (
            Util().get_current_time(),
            {
                'created_at': '1609459201',
                KEY_TYPE.LANE_TYPE.value: TABLE_TYPE.MEDIA.value
            },
            5,
            1,
            False,
            '1609459200',
            None
        ),
        (
            Util().get_current_time(),
            {
                'created_at': '1609459210',
                KEY_TYPE.LANE_TYPE.value: TABLE_TYPE.MEDIA.value
            },
            5,
            5,
            True,
            '1609459209',
            '1609459205'
        ),
        (
            Util().get_current_time(),
            {
                'created_at': '1609459210',
                KEY_TYPE.LANE_TYPE.value: TABLE_TYPE.MEDIA.value
            },
            5,
            5,
            True,
            '1609459209',
            '1609459205'
        ),
        (
            Util().get_current_time(),
            {
                'created_at': '1609459205',
                KEY_TYPE.LANE_TYPE.value: TABLE_TYPE.MEDIA.value
            },
            5,
            5,
            False,
            '1609459204',
            '1609459200'
        ),
    ])
    def test_media_table_list_ok(
            self,
            cur,
            bt,
            rg,
            expected_volume,
            is_included_LEK,
            start,
            end
    ):
        db = DynamoDBSetup(DB_NAME, False)._create_table()
        # d = datetime(2021, 1, 1, 0, 0, 0)
        d = '1609459200'

        for i in range(20):
            data = {
                "lane_type": "media001",
                "user_id": "user_id001",
                "media_id": "media_id00"+str(i),
                "avator_url": "https://hogehoge.com/1",
                "image_url": "https://hogehoge.com/1",
                "media_text": "this is media text",
                "created_at": str(int(d)+i)
            }

            db._insert_data(data)

        actual = MediaTable(False).list(cur, bt, rg)
        assert len(actual['Items']) == expected_volume
        assert ('LastEvaluatedKey' in actual) is is_included_LEK
        assert type(actual['Items']) == list
        if start is not None:
            assert actual['Items'][0]['created_at'] == start
        if end is not None:
            assert actual['Items'][-1]['created_at'] == end

    @ mock_dynamodb2
    def test_media_table_list_ng(self, mocker):
        mock_list = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'query'
        )
        mock_list.side_effect = Exception
        cur = '1609372800'

        with pytest.raises(Exception):
            MediaTable(False).list(cur, None)

    @ mock_dynamodb2
    def test_media_table_get_ok(self):
        db = DynamoDBSetup(DB_NAME, False)._create_table()
        # d = datetime(2021, 1, 1, 0, 0, 0)
        d = '1609459200'

        for i in range(20):
            data = {
                "lane_type": "media001",
                "user_id": "user001",
                "media_id": "media00"+str(i),
                "avator_url": "https://hogehoge.com/1",
                "image_url": "https://hogehoge.com/1",
                "media_text": "this is media text",
                "created_at": str(int(d)+60*i)
            }

            db._insert_data(data)

        actual = MediaTable(False).get('media001')
        assert len(actual) == 1
        assert type(actual) == list
        assert actual[0]['media_id'] == 'media001'

    @ mock_dynamodb2
    def test_media_table_get_ng(self, mocker):
        mock_get = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'query'
        )
        mock_get.side_effect = Exception

        with pytest.raises(Exception):
            MediaTable(False).get('dummy-media')

    @ mock_dynamodb2
    def test_media_table_post_ok(self):
        DynamoDBSetup(DB_NAME, False)._create_table()
        # preparing
        # start = str(datetime(2020, 12, 31, 0, 0, 0))
        cur = '1609459201'
        before = MediaTable(False).list(cur, None)
        assert len(before['Items']) == 0

        # testing
        data = {
            "lane_type": "media001",
            "user_id": "user001",
            "media_id": "media001",
            "avator_url": "https://hogehoge.com/1",
            "image_url": "https://hogehoge.com/1",
            "media_text": "this is media text",
            "created_at": '1609459200'
        }

        actual = MediaTable(False).post(data)
        assert actual['message'] == 'ok'
        assert type(actual) == dict

        after = MediaTable(False).list(cur, None)
        assert len(after['Items']) == 1

    @ mock_dynamodb2
    def test_media_table_post_ng(self, mocker):
        mock_put_item = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'put_item'
        )
        mock_put_item.side_effect = Exception

        with pytest.raises(Exception):
            MediaTable(False).post({})

    @ mock_dynamodb2
    def test_media_table_delete_ok(self):
        DynamoDBSetup(DB_NAME, False)._create_table()
        target = 'media001'
        # preparing
        data = {
            "lane_type": target,
            "user_id": "user001",
            "media_id": "media001",
            "avator_url": "https://hogehoge.com/1",
            "image_url": "https://hogehoge.com/1",
            "media_text": "this is media text",
            "created_at": '1609459200',
        }

        MediaTable(False).post(data)
        before = MediaTable(False).get(target)
        assert len(before) == 1

        # testing

        actual = MediaTable(False).delete(target)
        assert type(actual) == dict
        assert actual['message'] == 'ok'

        after = MediaTable(False).get(target)
        assert len(after) == 0

    @ mock_dynamodb2
    def test_media_table_delete_ng_01(self, mocker):
        mock_del_item = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'delete_item'
        )
        mock_del_item.side_effect = Exception

        with pytest.raises(Exception):
            MediaTable(False).delete('media001')

    @ mock_dynamodb2
    def test_media_table_delete_ng_02(self, mocker):
        mock_get_item = mocker.patch.object(MediaTable, 'get')
        mock_get_item.side_effect = Exception
        mock_del_item = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'delete_item'
        )
        mock_del_item.return_value = {"message": "ok"}

        with pytest.raises(Exception):
            MediaTable(False).delete('media001')
            assert mock_del_item.call_count == 0


class TestFavTable:
    #    @mock_dynamodb2
    #    @pytest.mark.parametrize('cur, bt, rg, expected_volume, start, end', [
    #        (
    #            '1609459220',
    #            None,
    #            4,
    #            2,
    #            '1609459218',
    #            '1609459216'
    #        ),
    #                (
    #                    Util().get_current_time(),
    #                    {
    #                        'created_at': '1609459301',
    #                        KEY_TYPE.LANE_TYPE.value: TABLE_TYPE.FAV.value
    #                    },
    #                    4,
    #                    2,
    #                    '1609459218',
    #                    '1609459216'
    #                ),
    #    ])
    #    ######################
    #    # FIXME:Cant test here because of the difference of Actual Behavior and Mocked Behavior
    #    # Mocked -> Filter, next Lim
    #    # Actual -> Lim, next Filter
    #    ######################
    #    def test_fav_table_list_ok(
    #            self,
    #            cur,
    #            bt,
    #            rg,
    #            expected_volume,
    #            start,
    #            end
    #    ):
    #        db = DynamoDBSetup(DB_NAME, False)._create_table()
    #        # d = datetime(2021, 1, 1, 0, 0, 0)
    #        d = '1609459200'
    #        for i in range(0, 20, 2):
    #            data = {
    #                "lane_type": "fav001",
    #                "user_id": "user_id001",
    #                "media_id": Util().gen_identifier(),
    #                "avator_url": "https://hogehoge.com/1",
    #                "image_url": "https://hogehoge.com/1",
    #                "media_text": "this is media text",
    #                "created_at": str(int(d)+i),
    #                "fav_id": Util().gen_identifier(),
    #                "target_user_id": 'tgt_user'
    #            }
    #
    #            db._insert_data(data)
    #
    #            data = {
    #                "lane_type": "fav001",
    #                "user_id": "user_id002",
    #                "media_id": Util().gen_identifier(),
    #                "avator_url": "https://hogehoge.com/1",
    #                "image_url": "https://hogehoge.com/1",
    #                "media_text": "this is media text",
    #                "created_at": str(int(d) + i+1),
    #                "fav_id": Util().gen_identifier(),
    #                "target_user_id": 'tgt_user'
    #            }
    #
    #            db._insert_data(data)
    #
    #        FavTable(False).list('user_id002', cur, bt, rg)
    #        actual = FavTable(False).list('user_id001', cur, bt, rg)
    #        assert len(actual['Items']) == expected_volume
    #        assert type(actual['Items']) == list
    #        if start is not None:
    #            assert actual['Items'][0]['created_at'] == start
    #        if end is not None:
    #            assert actual['Items'][-1]['created_at'] == end

    @mock_dynamodb2
    def test_fav_table_list_ng(self, mocker):
        mock_list = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'query'
        )
        mock_list.side_effect = Exception
        # start = str(datetime(2020, 12, 31, 0, 0, 0))

        with pytest.raises(Exception):
            FavTable(False).list('user001')

    @mock_dynamodb2
    @pytest.mark.parametrize('fav_id, expected', [
        ('tgt_fav_id', 1),
        ('dummy_fav_id', 0),
    ])
    def test_fav_table_get_ok(self, fav_id, expected):
        db = DynamoDBSetup(DB_NAME, False)._create_table()
        d = '1609459200'

        data = {
            "lane_type": "fav001",
            "user_id": "user001",
            "media_id": Util().gen_identifier(),
            "avator_url": "https://hogehoge.com/1",
            "image_url": "https://hogehoge.com/1",
            "media_text": "this is media text",
            "created_at": str(int(d)-60),
            "fav_id": 'tgt_fav_id',
            "target_user_id": 'tgt_user'
        }
        db._insert_data(data)

        for i in range(10):
            data = {
                "lane_type": "fav001",
                "user_id": "user001",
                "media_id": Util().gen_identifier(),
                "avator_url": "https://hogehoge.com/1",
                "image_url": "https://hogehoge.com/1",
                "media_text": "this is media text",
                "created_at": str(int(d)+60*i),
                "fav_id": Util().gen_identifier(),
                "target_user_id": 'tgt_user'
            }

            db._insert_data(data)

        actual = FavTable(False).get(fav_id)
        assert len(actual) == expected
        assert type(actual) == list

    @mock_dynamodb2
    def test_fav_table_get_ng(self, mocker):
        mock_get = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'query'
        )
        mock_get.side_effect = Exception

        with pytest.raises(Exception):
            FavTable(False).get('fav_id')

    @ mock_dynamodb2
    def test_fav_table_post_ok(self):
        DynamoDBSetup(DB_NAME, False)._create_table()
        create_fav_id = 'fav001'
        before = FavTable(False).get(create_fav_id)
        assert len(before) == 0

        # testing
        data = {
            "lane_type": "fav001",
            "user_id": "user001",
            "media_id": "media001",
            "avator_url": "https://hogehoge.com/1",
            "image_url": "https://hogehoge.com/1",
            "media_text": "this is media text",
            "created_at": '1609459200',
            "fav_id": create_fav_id,
            "target_user_id": 'tgt_user'
        }

        actual = FavTable(False).post(data)
        assert actual['message'] == 'ok'
        assert type(actual) == dict

        after = FavTable(False).get(create_fav_id)
        assert len(after) == 1

    @ mock_dynamodb2
    def test_fav_table_post_ng(self, mocker):
        mock_put_item = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'put_item'
        )
        mock_put_item.side_effect = Exception

        with pytest.raises(Exception):
            FavTable(False).post({})

    @ mock_dynamodb2
    def test_fav_table_delete_ok(self):
        DynamoDBSetup(DB_NAME, False)._create_table()
        deleting_fav_id = 'deleting_fav_id'
        # preparing
        data = {
            "lane_type": 'fav001',
            "user_id": "user001",
            "media_id": "media001",
            "avator_url": "https://hogehoge.com/1",
            "image_url": "https://hogehoge.com/1",
            "media_text": "this is media text",
            "created_at": '1609459200',
            "fav_id": deleting_fav_id,
            "target_user_id": 'tgt_user'
        }

        FavTable(False).post(data)
        before = FavTable(False).get(deleting_fav_id)
        assert len(before) == 1

        # testing

        actual = FavTable(False).delete_by_id(deleting_fav_id)
        assert type(actual) == dict
        assert actual['message'] == 'ok'

        after = FavTable(False).get(deleting_fav_id)
        assert len(after) == 0

    @ mock_dynamodb2
    def test_fav_table_delete_ng_01(self, mocker):
        mock_del_item = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'delete_item'
        )
        mock_del_item.side_effect = Exception

        with pytest.raises(Exception):
            FavTable(False).delete_by_id('fav001')

    @ mock_dynamodb2
    def test_fav_table_delete_ng_02(self, mocker):
        mock_get_item = mocker.patch.object(FavTable, 'get')
        mock_get_item.side_effect = Exception
        mock_del_item = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'delete_item'
        )
        mock_del_item.return_value = {"message": "ok"}

        with pytest.raises(Exception):
            FavTable(False).delete_by_id('fav001')
            assert mock_del_item.call_count == 0


class TestUserTable:
    @ mock_dynamodb2
    def test_user_table_post_ok(self, mocker):
        DynamoDBSetup(DB_NAME, False)._create_table()
        created_user_id = 'user_id001'
        before = UserTable(False).get(created_user_id)
        assert len(before) == 0

        # testing
        data = {
            'lane_type': TABLE_TYPE.USER.value,
            'user_id': created_user_id,
            'user_sub': 'aaaaaaaaaaaaaaaa1111111111111111111',
            'refresh_token': 'aaaaaaaaaaaaaaaaAAAAAAA111111111123',
            'created_at': '1629639190'
        }

        actual = UserTable(False).post(data)
        assert actual['message'] == 'ok'
        assert type(actual) == dict

        after = UserTable(False).get(created_user_id)
        assert len(after) == 1

    @ mock_dynamodb2
    def test_user_table_post_same_time_ng(self, mocker):
        DynamoDBSetup(DB_NAME, False)._create_table()

        pre = UserTable(False).get('user_id001')
        assert len(pre) == 0
        created_at = '1629639190'

        # user 1 registing
        data = {
            'lane_type': TABLE_TYPE.USER.value,
            'user_id': 'user_id001',
            'user_sub': 'aaaaaaaaaaaaaaaa1111111111111111111',
            'refresh_token': 'aaaaaaaaaaaaaaaaAAAAAAA111111111123',
            'created_at': created_at
        }

        UserTable(False).post(data)
        after = UserTable(False).get('user_id001')
        assert len(after) == 1

        # user 2 register at same time as user 1
        data = {
            'lane_type': TABLE_TYPE.USER.value,
            'user_id': 'user_id002',
            'user_sub': 'baaaaaaaaaaaaaaa1111111111111111111',
            'refresh_token': 'aaaaaaaaaaaaaaaaAAAAAAA111111111123',
            'created_at': created_at
        }

        with pytest.raises(ClientError):
            UserTable(False).post(data)

    @ mock_dynamodb2
    def test_user_table_post_same_user_id(self, mocker):
        DynamoDBSetup(DB_NAME, False)._create_table()

        pre = UserTable(False).get('user_id001')
        assert len(pre) == 0

        # user registing
        data = {
            'lane_type': TABLE_TYPE.USER.value,
            'user_id': 'user_id001',
            'user_sub': 'aaaaaaaaaaaaaaaa1111111111111111111',
            'refresh_token': 'aaaaaaaaaaaaaaaaAAAAAAA111111111123',
            'created_at': '1629639190'
        }

        UserTable(False).post(data)
        after = UserTable(False).get('user_id001')
        assert len(after) == 1

        # regist again with same user_id as following user
        data = {
            'lane_type': TABLE_TYPE.USER.value,
            'user_id': 'user_id001',
            'user_sub': 'aaaaaaaaaaaaaaaa1111111111111111111',
            'refresh_token': 'aaaaaaaaaaaaaaaaAAAAAAA111111111123',
            'created_at': '1629639191'
        }

        mock_put_item = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'put_item'
        )

        with pytest.raises(LaneInvalidFormat):
            UserTable(False).post(data)

        assert mock_put_item.call_count == 0

    @ mock_dynamodb2
    def test_user_table_post_ng(self, mocker):
        mock_put_item = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'put_item'
        )
        mock_put_item.side_effect = Exception
        data = {
            'lane_type': TABLE_TYPE.USER.value,
            'user_id': 'user_id001',
            'user_sub': 'aaaaaaaaaaaaaaaa1111111111111111111',
            'refresh_token': 'aaaaaaaaaaaaaaaaAAAAAAA111111111123',
            'created_at': '1629639191'
        }

        with pytest.raises(Exception):
            UserTable(False).post(data)

    @ mock_dynamodb2
    # get error
    def test_user_table_post_ng2(self, mocker):
        mock_get_item = mocker.patch('api.model.UserTable.get')
        mock_get_item.side_effect = Exception
        mock_put_item = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'put_item'
        )

        data = {
            'lane_type': TABLE_TYPE.USER.value,
            'user_id': 'user_id001',
            'user_sub': 'aaaaaaaaaaaaaaaa1111111111111111111',
            'refresh_token': 'aaaaaaaaaaaaaaaaAAAAAAA111111111123',
            'created_at': '1629639191'
        }

        with pytest.raises(Exception):
            UserTable(False).post(data)
        assert mock_put_item.call_count == 0

    @ mock_dynamodb2
    @pytest.mark.parametrize('data, expected_avator, expected_description, expected_user_name', [
        (
            {
                'created_at': '1629639190',
                'avator_url': 'https: // hoge.com'
            },
            'https: // hoge.com',
            None,
            None
        ),
        (
            {
                'created_at': '1629639190',
                'description': 'updated'
            },
            None,
            'updated',
            None
        ),
        (
            {
                'created_at': '1629639190',
                'user_name': 'updated_name'
            },
            None,
            None,
            'updated_name'
        ),
        (
            {
                'created_at': '1629639190',
                'avator_url': 'https://hoge.com',
                'description': 'updated'
            },
            'https://hoge.com',
            'updated',
            None
        ),
        (
            {
                'created_at': '1629639190',
                'description': 'updated',
                'user_name': 'updated_name'
            },
            None,
            'updated',
            'updated_name'
        ),
        (
            {
                'created_at': '1629639190',
                'avator_url': 'https://hoge.com',
                'user_name': 'updated_name'
            },
            'https://hoge.com',
            None,
            'updated_name'
        ),
        (
            {
                'created_at': '1629639190',
                'avator_url': 'https://hoge.com',
                'description': 'updated',
                'user_name': 'updated_name'
            },
            'https://hoge.com',
            'updated',
            'updated_name'
        ),
        (
            {
                'created_at': '1629639190',
            },
            None,
            None,
            None
        ),
    ])
    def test_user_table_put_ok(
            self,
            mocker,
            data,
            expected_avator,
            expected_description,
            expected_user_name
    ):
        DynamoDBSetup(DB_NAME, False)._create_table()
        created_user_id = 'user_id001'
        before = UserTable(False).get(created_user_id)
        assert len(before) == 0
        user_created_at = '1629639190'
        user_sub = 'aaaaaaaaaaaaaaaa1111111111111111111'
        refresh_token = 'aaaaaaaaaaaaaaaaAAAAAAA111111111123'

        # preparing
        d = {
            'lane_type': TABLE_TYPE.USER.value,
            'user_id': created_user_id,
            'user_sub': user_sub,
            'refresh_token': refresh_token,
            'created_at': user_created_at
        }

        actual = UserTable(False).post(d)
        after = UserTable(False).get(created_user_id)
        assert len(after) == 1

        UserTable(False).put(data)
        actual = UserTable(False).get(created_user_id)[0]
        assert actual.get('avator_url') == expected_avator
        assert actual.get('description') == expected_description
        assert actual.get('user_name') == expected_user_name
        assert actual.get('user_sub') == user_sub
        assert actual.get('refresh_token') == refresh_token
        assert actual.get('created_at') == user_created_at

    @ mock_dynamodb2
    def test_user_table_put_ng(self, mocker):
        mock_put_item = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'update_item'
        )
        mock_put_item.side_effect = Exception

        data = {
            'created_at': '1629639190',
            'avator_url': 'https://hoge.com',
            'user_name': 'updated_name'
        }
        with pytest.raises(Exception):
            UserTable(False).put(data)
            UserTable(False).put(data)


class TestCommentTable:

    @mock_dynamodb2
    def test_comment_table_list_ok(
            self):
        db = DynamoDBSetup(DB_NAME, False)._create_table()
        # d = datetime(2021, 1, 1, 0, 0, 0)
        d = '1609459200'

        for i in range(10):

            data = {
                "media_id": 'media_id001',
                "created_at": str(int(d)+i),
                "avator_url": "https://hoge.jp/yuUAq",
                "lane_type": "comment001",
                "comment_id": Util().gen_identifier(),
                "user_id": Util().gen_identifier()
            }

            data = {
                "media_id": 'media_id001',
                "created_at": str(int(d)+10+i),
                "avator_url": "https://hoge.jp/yuUAq",
                "lane_type": "comment001",
                "comment_id": Util().gen_identifier(),
                "user_id": Util().gen_identifier()
            }

            db._insert_data(data)

        actual = CommentTable(False).list('media_id001', d)

        assert len(actual) == 10
        assert type(actual) == list

    @ mock_dynamodb2
    def test_comment_table_list_ng(self, mocker):
        mock_list = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'query'
        )
        mock_list.side_effect = Exception
        d = '1609372800'

        with pytest.raises(Exception):
            CommentTable(False).list('dummy_media_id001', d)

    @ mock_dynamodb2
    def test_comment_table_get_ok(self):
        db = DynamoDBSetup(DB_NAME, False)._create_table()
        # d = datetime(2021, 1, 1, 0, 0, 0)
        d = '1609459200'

        for i in range(20):
            data = {
                "media_id": Util().gen_identifier(),
                "created_at": str(int(d)+i),
                "avator_url": "https://hoge.jp/yuUAq",
                "lane_type": "comment001",
                "comment_id": 'comment_id00' + str(i),
                "user_id": Util().gen_identifier()
            }

            db._insert_data(data)

        actual = CommentTable(False).get('comment_id001')
        assert len(actual) == 1
        assert type(actual) == list
        assert actual[0]['comment_id'] == 'comment_id001'

    @ mock_dynamodb2
    def test_comment_table_get_ng(self, mocker):
        mock_get = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'query'
        )
        mock_get.side_effect = Exception

        with pytest.raises(Exception):
            CommentTable(False).get('dummy-media')

    @ mock_dynamodb2
    def test_comment_table_post_ok(self):
        DynamoDBSetup(DB_NAME, False)._create_table()
        # preparing
        # start = str(datetime(2020, 12, 31, 0, 0, 0))
        cur = '1609459201'
        before = CommentTable(False).get('comment_id001')
        assert len(before) == 0

        # testing
        data = {
            "media_id": Util().gen_identifier(),
            "created_at": '111111111111',
            "avator_url": "https://hoge.jp/yuUAq",
            "lane_type": "comment001",
            "comment_id": 'comment_id001',
            "user_id": Util().gen_identifier()
        }

        actual = MediaTable(False).post(data)
        assert actual['message'] == 'ok'
        assert type(actual) == dict

        after = CommentTable(False).get('comment_id001')
        assert len(after) == 1

    @ mock_dynamodb2
    def test_comment_table_post_ng(self, mocker):
        mock_put_item = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'put_item'
        )
        mock_put_item.side_effect = Exception

        with pytest.raises(Exception):
            CommentTable(False).post({})

    @ mock_dynamodb2
    def test_comment_table_delete_ok(self):
        DynamoDBSetup(DB_NAME, False)._create_table()
        target = 'comment_id001'
        # preparing
        data = {
            "media_id": Util().gen_identifier(),
            "created_at": '111111111111',
            "avator_url": "https://hoge.jp/yuUAq",
            "lane_type": "comment001",
            "comment_id": target,
            "user_id": Util().gen_identifier()
        }

        CommentTable(False).post(data)
        before = CommentTable(False).get(target)
        assert len(before) == 1

        # testing

        actual = CommentTable(False).delete(target)
        assert type(actual) == dict
        assert actual['message'] == 'ok'

        after = CommentTable(False).get(target)
        assert len(after) == 0

    @ mock_dynamodb2
    def test_comment_table_delete_ng_01(self, mocker):
        mock_del_item = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'delete_item'
        )
        mock_del_item.side_effect = Exception

        with pytest.raises(Exception):
            CommentTable(False).delete('comment_id001')

    @ mock_dynamodb2
    def test_media_table_delete_ng_02(self, mocker):
        mock_get_item = mocker.patch.object(CommentTable, 'get')
        mock_get_item.side_effect = Exception
        mock_del_item = mocker.patch.object(
            boto3.resource('dynamodb').Table(DB_NAME),
            'delete_item'
        )
        mock_del_item.return_value = {"message": "ok"}

        with pytest.raises(Exception):
            CommentTable(False).delete('comment001')
            assert mock_del_item.call_count == 0
