from flask import jsonify, request, Blueprint
from api.model import CommentTable
from api.config import URL_PREFIX, S3_MEDIA_KEY
from api.util import Util, catch_exception, authorize
import json
import base64
import uuid


bp_comment = Blueprint('bp_comment', __name__, url_prefix=URL_PREFIX)


@bp_comment.route('/comment/ok', methods=['GET'])
def ok():
    return jsonify({'message': 'ok'})


@bp_comment.route('/comments/<media_id>/<created_at>', methods=['GET'])
@authorize
@catch_exception
def list(media_id, created_at):
    res = CommentTable().list(media_id, created_at)
    return jsonify({'comments': res})


@bp_comment.route('/comment/<comment_id>', methods=['GET'])
@authorize
@catch_exception
def get(comment_id):
    res = CommentTable().get(comment_id)
    return jsonify({'comment': res})


@bp_comment.route('/comment', methods=['POST'])
@authorize
@catch_exception
def post():
    data = request.form.to_dict()
    data['created_at'] = Util().get_current_time()
    data['comment_id'] = Util().gen_identifier()

    res = CommentTable().post(data)
    return jsonify(res)


@bp_comment.route('/comment/<comment_id>', methods=['DELETE'])
@authorize
@catch_exception
def delete(comment_id):
    res = CommentTable().delete(comment_id)
    return jsonify(res)
