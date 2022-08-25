# -*- coding: utf-8 -*-
import boto3
from boto3.dynamodb.conditions import Key
from api.config import DB_NAME, ENVIRONMENT, ENV_TYPE, TABLE_TYPE, KEY_TYPE
import sys
from api.util import _info, LaneInvalidFormat
from pprint import pprint


class BaseTable():
    def __init__(self, use_ddb_local=True):
        dynamo = None
        if not use_ddb_local or ENVIRONMENT == ENV_TYPE.PROD:
            dynamo = boto3.resource('dynamodb')
        else:
            dynamo = boto3.resource(
                'dynamodb',
                endpoint_url='http://dynamodb:8000'
            )
        self.table = dynamo.Table(DB_NAME)


class MediaTable(BaseTable):

    def __init__(self, use_ddb_local=True):
        super().__init__(use_ddb_local)

    def list(self, cur, last_evaluated_key=None, range=10):

        cnd1 = Key(KEY_TYPE.LANE_TYPE.value).eq(TABLE_TYPE.MEDIA.value)
        cnd2 = Key(KEY_TYPE.CREATED_AT.value).lt(cur)

        response = None

        if(last_evaluated_key is not None):
            response = self.table.query(
                KeyConditionExpression=cnd1 & cnd2,
                ScanIndexForward=False,
                Limit=range,
                ExclusiveStartKey=last_evaluated_key
            )
        else:
            response = self.table.query(
                KeyConditionExpression=cnd1 & cnd2,
                ScanIndexForward=False,
                Limit=range,
            )
        return response

    def list_by_user_id(self, user_id, cur, last_evaluated_key=None, range=1000):

        cnd1 = Key(KEY_TYPE.LANE_TYPE.value).eq(TABLE_TYPE.MEDIA.value)
        cnd2 = Key(KEY_TYPE.CREATED_AT.value).lt(cur)
        cnd3 = Key(KEY_TYPE.USER_ID.value).eq(user_id)

        response = None

        # TODO: Cant scale out, fix in future
        if(last_evaluated_key is not None):
            response = self.table.query(
                KeyConditionExpression=cnd1 & cnd2,
                ScanIndexForward=False,
                FilterExpression=cnd3,
                Limit=range,
                ExclusiveStartKey=last_evaluated_key
            )
        else:
            response = self.table.query(
                KeyConditionExpression=cnd1 & cnd2,
                ScanIndexForward=False,
                FilterExpression=cnd3,
                Limit=range,
            )
        return response

    def get(self, media_id):
        cnd1 = Key(KEY_TYPE.LANE_TYPE.value).eq(TABLE_TYPE.MEDIA.value)
        cnd2 = Key(KEY_TYPE.MEDIA_ID.value).eq(media_id)

        response = self.table.query(
            IndexName=KEY_TYPE.MEDIA_ID.value,
            KeyConditionExpression=cnd1 & cnd2
        )
        return response['Items']

    def post(self, data):
        self.table.put_item(Item=data)
        return {'message': 'ok'}

    def delete(self, media_id):
        media = self.get(media_id)[0]

        cnd1 = {
            KEY_TYPE.LANE_TYPE.value: TABLE_TYPE.MEDIA.value,
            KEY_TYPE.CREATED_AT.value: media['created_at']
        }
        cnd2 = Key(KEY_TYPE.MEDIA_ID.value).eq(media_id)

        self.table.delete_item(
            Key=cnd1,
            ConditionExpression=cnd2
        )
        return {'message': 'ok'}


class UserTable(BaseTable):

    def __init__(self, use_ddb_local=True):
        super().__init__(use_ddb_local)

    def get(self, user_id):
        cnd1 = Key(KEY_TYPE.LANE_TYPE.value).eq(TABLE_TYPE.USER.value)
        cnd2 = Key(KEY_TYPE.USER_ID.value).eq(user_id)

        response = self.table.query(
            IndexName=KEY_TYPE.USER_ID.value,
            KeyConditionExpression=cnd1 & cnd2
        )
        return response['Items']

    def post(self, data):
        does_user_exist = len(self.get_sub(data['user_sub']))
        _info(does_user_exist)
        if(does_user_exist):
            raise LaneInvalidFormat

        self.table.put_item(
            Item=data,
            ConditionExpression='attribute_not_exists(created_at)'
        )
        return {'message': 'ok'}

    def put(self, data):

        description = data.get('description')
        avator_url = data.get('avator_url')
        user_name = data.get('user_name')
        created_at = data['created_at']

        self.table.update_item(
            Key={
                KEY_TYPE.LANE_TYPE.value: TABLE_TYPE.USER.value,
                KEY_TYPE.CREATED_AT.value: created_at
            },
            UpdateExpression="set \
                    description= :desc, \
                    avator_url= :avator_url, \
                    user_name= :user_name",
            ExpressionAttributeValues={
                ':desc': description,
                ':avator_url': avator_url,
                ':user_name': user_name
            }
        )
        return {'message': 'ok'}

    def get_sub(self, user_sub):
        cnd1 = Key(KEY_TYPE.LANE_TYPE.value).eq(TABLE_TYPE.USER.value)
        cnd2 = Key(KEY_TYPE.USER_SUB.value).eq(user_sub)

        response = self.table.query(
            IndexName=KEY_TYPE.USER_SUB.value,
            KeyConditionExpression=cnd1 & cnd2
        )
        return response['Items']


class FavTable(BaseTable):
    def __init__(self, use_ddb_local=True):
        super().__init__(use_ddb_local)

    def list(self, user_id, cur, last_evaluated_key=None, range=1000):

        cnd1 = Key(KEY_TYPE.LANE_TYPE.value).eq(TABLE_TYPE.FAV.value)
        cnd2 = Key(KEY_TYPE.CREATED_AT.value).lt(cur)
        cnd3 = Key(KEY_TYPE.USER_ID.value).eq(user_id)

        response = None

        # TODO: Cant scale out, fix in future
        if(last_evaluated_key is not None):
            response = self.table.query(
                KeyConditionExpression=cnd1 & cnd2,
                ScanIndexForward=False,
                FilterExpression=cnd3,
                Limit=range,
                ExclusiveStartKey=last_evaluated_key
            )
        else:
            response = self.table.query(
                KeyConditionExpression=cnd1 & cnd2,
                ScanIndexForward=False,
                FilterExpression=cnd3,
                Limit=range,
            )
        return response

    def get(self, fav_id):
        cnd1 = Key(KEY_TYPE.LANE_TYPE.value).eq(TABLE_TYPE.FAV.value)
        cnd2 = Key(KEY_TYPE.FAV_ID.value).eq(fav_id)

        response = self.table.query(
            IndexName=KEY_TYPE.FAV_ID.value,
            KeyConditionExpression=cnd1 & cnd2
        )
        return response['Items']

    def get_by_media_id(self, user_id, media_id):
        cnd1 = Key(KEY_TYPE.LANE_TYPE.value).eq(TABLE_TYPE.FAV.value)
        cnd2 = Key(KEY_TYPE.USER_ID.value).eq(user_id)
        cnd3 = Key(KEY_TYPE.MEDIA_ID.value).eq(media_id)

        response = self.table.query(
            IndexName=KEY_TYPE.USER_ID.value,
            KeyConditionExpression=cnd1 & cnd2,
            FilterExpression=cnd3,
        )
        return response['Items']

    def post(self, data):
        self.table.put_item(Item=data)
        return {'message': 'ok', 'fav_id':data['fav_id']}

    def delete_by_id(self, fav_id):
        fav = self.get(fav_id)[0]

        cnd1 = {
            KEY_TYPE.LANE_TYPE.value: TABLE_TYPE.FAV.value,
            KEY_TYPE.CREATED_AT.value: fav['created_at']
        }
        cnd2 = Key(KEY_TYPE.FAV_ID.value).eq(fav_id)

        self.table.delete_item(
            Key=cnd1,
            ConditionExpression=cnd2
        )
        return {'message': 'ok'}


class CommentTable(BaseTable):
    def __init__(self, use_ddb_local=True):
        super().__init__(use_ddb_local)

    def list(self, media_id, created_at):
        cnd1 = Key(KEY_TYPE.LANE_TYPE.value).eq(TABLE_TYPE.COMMENT.value)
        cnd2 = Key(KEY_TYPE.CREATED_AT.value).gt(created_at)
        cnd3 = Key(KEY_TYPE.MEDIA_ID.value).eq(media_id)

        response = self.table.query(
            KeyConditionExpression=cnd1 & cnd2,
            ScanIndexForward=False,
            FilterExpression=cnd3
        )
        return response['Items']

    def get(self, comment_id):
        cnd1 = Key(KEY_TYPE.LANE_TYPE.value).eq(TABLE_TYPE.COMMENT.value)
        cnd2 = Key(KEY_TYPE.COMMENT_ID.value).eq(comment_id)

        response = self.table.query(
            IndexName=KEY_TYPE.COMMENT_ID.value,
            KeyConditionExpression=cnd1 & cnd2
        )
        return response['Items']

    def post(self, data):
        self.table.put_item(Item=data)
        return {'message': 'ok'}

    def delete(self, comment_id):
        comment = self.get(comment_id)[0]

        cnd1 = {
            KEY_TYPE.LANE_TYPE.value: TABLE_TYPE.COMMENT.value,
            KEY_TYPE.CREATED_AT.value: comment['created_at']
        }
        cnd2 = Key(KEY_TYPE.COMMENT_ID.value).eq(comment_id)

        self.table.delete_item(
            Key=cnd1,
            ConditionExpression=cnd2
        )
        return {'message': 'ok'}
