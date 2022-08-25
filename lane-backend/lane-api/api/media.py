from flask import jsonify, request, Blueprint
import boto3
from http import HTTPStatus
from botocore.exceptions import ClientError
from api.model import MediaTable
from api.config import URL_PREFIX, S3_MEDIA_KEY, KEY_TYPE, TABLE_TYPE, CF_HOST_NAME, BUCKET_NAME
from api.util import Util, catch_exception, authorize, _info
import json
import base64
import uuid
from botocore.client import Config


bp_media = Blueprint('bp_media', __name__)


@bp_media.route(URL_PREFIX+'/medias', methods=['GET'])
@catch_exception
def list():
    cur = request.args.get('cur', Util().get_current_time())

    border_time = request.args.get('bt', None)

    last_evaluated_key = None

    if border_time is not None:
        last_evaluated_key = {
            'created_at': border_time,
            KEY_TYPE.LANE_TYPE.value: TABLE_TYPE.MEDIA.value
        }

    res = MediaTable().list(cur, last_evaluated_key)

    lek = res['LastEvaluatedKey']['created_at'] \
        if 'LastEvaluatedKey' in res else -1

    return jsonify({
        'medias': res['Items'],
        'lek': lek,
        'cur': cur
    })


@bp_media.route(URL_PREFIX+'/medias/<user_id>', methods=['GET'])
@authorize
@catch_exception
def list_by_user_id(user_id):
    cur = request.args.get('cur', Util().get_current_time())

    border_time = request.args.get('bt', None)

    last_evaluated_key = None

    if border_time is not None:
        last_evaluated_key = {
            'created_at': border_time,
            KEY_TYPE.LANE_TYPE.value: TABLE_TYPE.FAV.value
        }

    try:
        res = MediaTable().list_by_user_id(user_id, cur, last_evaluated_key)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationException':
            return jsonify({'medias': [],
                            'cur': cur,
                            'lek': -1}), \
                HTTPStatus.OK

    lek = res['Items'][-1]['created_at'] \
        if len(res['Items']) > 0 else -1

    return jsonify({
        'medias': res['Items'],
        'lek': lek,
        'cur': cur
    })


@bp_media.route(URL_PREFIX+'/media/<media_id>', methods=['GET'])
@authorize
@catch_exception
def get(media_id):
    res = MediaTable().get(media_id)
    return jsonify({'media': res})


@bp_media.route(URL_PREFIX+'/media', methods=['POST'])
@authorize
@catch_exception
def post():
    data = request.form.to_dict()
    _info(data)

    file_name = data['file_name']
    data2 = {}
    data2['created_at'] = Util().get_current_time()
    data2['image_url'] = CF_HOST_NAME+file_name
    data2['avator_url'] = data['avator_url']
    data2['user_id'] = data['user_id']
    data2['media_id'] = Util().gen_identifier()
    data2['lane_type'] = 'media001'
    data2['media_text'] = data['media_text']

    res = MediaTable().post(data2)
    return jsonify(res)


@bp_media.route(URL_PREFIX+'/media_image', methods=['POST'])
@authorize
@catch_exception
def post_image():
    s3 = boto3.client('s3',  config=Config(signature_version='s3v4'))
    file_name = Util().gen_identifier() + '.jpeg'

    res = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={'Bucket': BUCKET_NAME, 'Key': S3_MEDIA_KEY+file_name},
        ExpiresIn=60,
        HttpMethod='PUT')
    return jsonify({'url': res})


@bp_media.route(URL_PREFIX+'/media/<media_id>', methods=['DELETE'])
@authorize
@catch_exception
def delete(media_id):
    res = MediaTable().delete(media_id)
    return jsonify(res)
