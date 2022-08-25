from flask import jsonify, request, Blueprint
from api.model import MediaTable, FavTable
from api.config import URL_PREFIX, S3_MEDIA_KEY, KEY_TYPE, TABLE_TYPE
from api.util import Util, catch_exception, authorize, _info
import json
import base64
import uuid


bp_fav = Blueprint('bp_fav', __name__, url_prefix=URL_PREFIX)


@bp_fav.route('/fav/ok', methods=['GET'])
def ok():
    return jsonify({'message': 'ok'})


@bp_fav.route('/favs/<user_id>', methods=['GET'])
@catch_exception
def list(user_id):
    cur = request.args.get('cur', Util().get_current_time())

    border_time = request.args.get('bt', None)

    last_evaluated_key = None

    if border_time is not None:
        last_evaluated_key = {
            'created_at': border_time,
            KEY_TYPE.LANE_TYPE.value: TABLE_TYPE.FAV.value
        }

    res = FavTable().list(user_id, cur, last_evaluated_key)

    lek = res['Items'][-1]['created_at'] \
        if len(res['Items']) > 0 else -1

    return jsonify({
        'medias': res['Items'],
        'lek': lek,
        'cur': cur
    })


@bp_fav.route('/fav/<fav_id>', methods=['GET'])
@catch_exception
def get(fav_id):
    res = FavTable().get(fav_id)
    return jsonify({'fav': res})


@bp_fav.route('/fav/<user_id>/<media_id>', methods=['GET'])
@catch_exception
def get_by_media_id(user_id, media_id):
    res = FavTable().get_by_media_id(user_id, media_id)
    return jsonify({'fav': res})


@bp_fav.route('/fav', methods=['POST'])
@catch_exception
def post():
    data = request.form.to_dict()
    data['created_at'] = Util().get_current_time()
    data['fav_id'] = Util().gen_identifier()
    _info(data)

    res = FavTable().post(data)
    return jsonify(res)


@bp_fav.route('/fav/<fav_id>', methods=['DELETE'])
@catch_exception
def delete(fav_id):
    res = FavTable().delete_by_id(fav_id)
    return jsonify(res)
