from flask import jsonify, request, Blueprint
import requests
import json
import jwt
from api.model import UserTable
from api.config import (URL_PREFIX, GOOGLE_CLIENT_ID,
                        GOOGLE_CLIENT_SECRET, GOOGLE_TOKEN_ENDPOINT,
                        TABLE_TYPE, S3_USER_KEY, S3_MEDIA_KEY, CF_HOST_NAME)
from api.util import (Util, catch_exception, LaneInvalidGrantException,
                      LaneResourceNotFoundException, _info, authorize, logger)
import base64

bp_user = Blueprint('bp_user', __name__, url_prefix=URL_PREFIX+'/user')


@bp_user.route('/user/ok', methods=['GET'])
def ok():
    return jsonify({'message': 'ok, it works'})


@bp_user.route('/<user_id>', methods=['GET'])
@catch_exception
def get(user_id):
    user_exists = True if len(UserTable().get(user_id)) > 0 else False
    return jsonify({'user_exists': user_exists}), 200


@bp_user.route('/info', methods=['GET'])
@authorize
@catch_exception
def get_info():
    data = request.headers.get('Authorization')
    _, id_token = data.split()

    sub = Util().get_user_sub_without_verification(id_token)['sub']
    hashed_user_sub = Util().hash_user_sub(sub)
    res = UserTable().get_sub(hashed_user_sub)
    return jsonify({'user': res}), 200


@bp_user.route('', methods=['POST'])
@catch_exception
def post():
    data = request.form.to_dict()
    code = data['serverAuthCode']
    init_id_token = data['idToken']
    user_id = data['user_id']
    ua = request.headers.get('User-Agent')
    try:
        if 'Android' not in ua:
            res = Util().validate_id_token(init_id_token, 'accounts.google.com')
        else:
            res = Util().validate_id_token(init_id_token)

    except StopIteration as e:
        raise LaneInvalidGrantException(str(e))

    user_sub = res['sub']
    hashed_user_sub = Util().hash_user_sub(user_sub)

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': 'http://localhost:8081/callback',
        'grant_type': 'authorization_code',
        'access_type': 'offline',
    }

    res = requests.post(GOOGLE_TOKEN_ENDPOINT, data=data, headers=headers)
    if('error' in json.loads(res.text)):
        raise LaneInvalidGrantException(json.loads(res.text)['error'])

    new_id_token = json.loads(res.text)['id_token']
    refresh_token = json.loads(res.text)['refresh_token']

    data = {
        'lane_type': TABLE_TYPE.USER.value,
        'user_id': user_id,
        'user_sub': hashed_user_sub,
        'refresh_token': refresh_token,
        'created_at': Util().get_current_time(),
        'avator_url': CF_HOST_NAME+S3_USER_KEY+hashed_user_sub+'.jpeg'
    }

    res = UserTable().post(data)

    return jsonify({'id_token': new_id_token,
                    'avator_url': data['avator_url']
                    })


@bp_user.route('', methods=['PUT'])
@authorize
@catch_exception
def put():
    data = request.form.to_dict()
    file_name = data['avator_url'].split('/')[-1]
    print(file_name)
    if 'upfile' in data:
        decoded_image = base64.b64decode(data['upfile'])
        Util().upload_to_s3(decoded_image, S3_USER_KEY+file_name)

    data['lane_type'] = 'user001'
    UserTable().put(data)
    return jsonify({'message': 'ok'})


@bp_user.route('/update', methods=['POST'])
@catch_exception
def update_token():
    data = request.form
    id_token = data['idToken']

    try:
        Util().validate_id_token(id_token)
        return jsonify({'id_token': ''}), 200
    except jwt.InvalidIssuerError:
        Util().validate_id_token(id_token, 'accounts.google.com')
        return jsonify({'id_token': ''}), 200
    except jwt.ExpiredSignatureError:
        sub = Util().get_user_sub_without_verification(id_token)['sub']
        hashed_user_sub = Util().hash_user_sub(sub)

        res = UserTable().get_sub(hashed_user_sub)
        if(len(res) == 0):
            raise LaneResourceNotFoundException

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        refresh_token = res[0]['refresh_token']
        data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        res = requests.post(GOOGLE_TOKEN_ENDPOINT, data=data, headers=headers)
        if('error' in json.loads(res.text)):
            raise LaneInvalidGrantException(json.loads(res.text)['error'])

        return jsonify({'id_token': json.loads(res.text)['id_token']})
    except Exception:
        raise LaneInvalidGrantException


@bp_user.route('/login', methods=['POST'])
@catch_exception
def login():
    data = request.form
    id_token = data['idToken']
    ua = request.headers.get('User-Agent')

    try:
        if 'Android' not in ua:
            res = Util().validate_id_token(id_token, 'accounts.google.com')
        else:
            res = Util().validate_id_token(id_token)

    except StopIteration as e:
        raise LaneInvalidGrantException(str(e))

    sub = res['sub']

    hashed_user_sub = Util().hash_user_sub(sub)

    res = UserTable().get_sub(hashed_user_sub)

    if(len(res) == 0):
        raise LaneResourceNotFoundException

    return jsonify({'message': 'ok'})
