from datetime import datetime, timedelta
import logging
import inspect
import sys
import requests
import jwt
from jwt.algorithms import RSAAlgorithm
from functools import wraps
from flask import jsonify, request
from http import HTTPStatus
from logging import getLogger, StreamHandler, Formatter, DEBUG
from api.config import ENVIRONMENT, ENV_TYPE, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_TOKEN_ENDPOINT, GOOGLE_CERT_ENDPOINT
import traceback
import boto3
from botocore.exceptions import ClientError
import time
import hashlib
import uuid
from api.config import BUCKET_NAME
import base64
import json

# TODO: add verifing process.

#########
# Logger
#########


class FormatterJSON(logging.Formatter):
    def format(self, record):
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        j = {
            'logLevel': record.levelname,
            'extra_data': record.__dict__.get('extra_data', {}),
            'aws_request_id': getattr(record, 'aws_request_id', '00000000-0000-0000-0000-000000000000'),
            'message': record.getMessage(),
            'module': record.module,
            'filename': record.filename,
            'funcName': record.funcName,
            'levelno': record.levelno,
            'lineno': record.lineno,
            'traceback': {},
            'timestamp': '%(asctime)s.%(msecs)dZ' % dict(asctime=record.asctime, msecs=record.msecs),
            'event': record.__dict__.get('event', {}),
        }
        if record.exc_info:
            exception_data = traceback.format_exc().splitlines()
            j['traceback'] = exception_data

        return json.dumps(j, ensure_ascii=False)


logger = logging.getLogger()
logger.setLevel('INFO')

formatter = FormatterJSON(
    '[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(levelno)s\t%(message)s\n',
    '%Y-%m-%dT%H:%M:%S'
)
# Replace the LambdaLoggerHandler formatter :
if len(logger.handlers) > 0:
    logger.handlers[0].setFormatter(formatter)


def _info(data):
    i = inspect.stack()[1]
    print('\nINFO #######',
          i.filename.split('/')[-1]+'('+str(i.lineno)+')::'+i.function+"\n",
          data)

#########
# Decorator
#########


def authorize(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            data = request.headers.get('Authorization')
            _, id_token = data.split()
            Util().validate_id_token(id_token)
        except jwt.InvalidIssuerError:
            Util().validate_id_token(id_token, 'accounts.google.com')
        except Exception as e:
            return jsonify(
                {'error_message': "Authorization failed :" + str(e)
                 }), HTTPStatus.UNAUTHORIZED
        return f(*args, **kwargs)

    return wrapper


def catch_exception(f):

    def wrapped(*args, **kwargs):
        try:
            logger.info('', extra=dict({
                'extra_data': {
                    'METHOD': request.method,
                    'PATH': request.path
                }
            }
            ))
            return f(*args, **kwargs)

        except LaneInvalidGrantException as e:
            logging.exception(e)
            return jsonify({'error_message': str(e)}),\
                HTTPStatus.BAD_REQUEST
        except jwt.ExpiredSignatureError as e:
            logging.exception(e)
            return jsonify({'error_message': str(e)}),\
                HTTPStatus.BAD_REQUEST
        except LaneTokenNotFoundException as e:
            logging.exception(e)
            return jsonify({'error_message': str(e)}),\
                HTTPStatus.BAD_REQUEST

        except ValueError as e:
            logging.exception(e)
            return jsonify({'error_message': str('Invalid request format.')}),\
                HTTPStatus.NOT_FOUND

        except LaneResourceNotFoundException as e:
            logging.exception(e)
            return jsonify({'error_message': str(e)}),\
                HTTPStatus.NOT_FOUND
        except ClientError as e:
            logging.exception(e)
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return jsonify({'error_message': str(e.response['Error']['Code'])}),\
                    HTTPStatus.BAD_REQUEST
            elif e.response['Error']['Code'] == 'ValidationException':
                return jsonify({'message': str(e.response['Error']['Code'])}),\
                    HTTPStatus.OK
            elif e.response['Error']['Code'] == 'AccessDenied':
                return jsonify({'message': str(e.response['Error']['Code'])}),\
                    HTTPStatus.FORBIDDEN
            else:
                return jsonify({'message': 'unexpected server error'}),\
                    HTTPStatus.INTERNAL_SERVER_ERROR
        except LaneInvalidFormat as e:
            logging.exception(e)
            return jsonify({'error_message': str(e)}),\
                HTTPStatus.BAD_REQUEST

        except Exception as e:
            logging.exception(e)
            return jsonify({'error_message': str(e)}),\
                HTTPStatus.INTERNAL_SERVER_ERROR
    wrapped.__name__ = f.__name__
    return wrapped

#########
# Utility function
#########


class Util:

    # TODO: mul 1000, return millisec
    def get_current_time(self):
        return str(int(time.time()))

    def upload_to_s3(self, file_obj, key):
        s3 = boto3.resource('s3').Object(BUCKET_NAME, key)
        return s3.put(Body=file_obj)

    def gen_identifier(self):
        return str(uuid.uuid4())[19:].replace('-', '')

    def hash_user_sub(self, sub):
        return hashlib.sha256(sub.encode()).hexdigest()

    def validate_id_token(self, id_token, issuer=None):
        JWKS_URI = GOOGLE_CERT_ENDPOINT
        GOOGLE_ISSUER = 'https://accounts.google.com'
        if issuer is not None:
            GOOGLE_ISSUER = issuer

        CLIENT_ID = GOOGLE_CLIENT_ID

        header = jwt.get_unverified_header(id_token)

        res = requests.get(JWKS_URI)
        jwk_set = json.loads(res.text)
        jwk = next(filter(lambda k: k['kid'] ==
                          header['kid'], jwk_set['keys']))

        public_key = RSAAlgorithm.from_jwk(json.dumps(jwk))

        claims = jwt.decode(id_token,
                            public_key,
                            issuer=GOOGLE_ISSUER,
                            audience=CLIENT_ID,
                            algorithms=["RS256"])
        return claims

    def get_user_sub_without_verification(self, id_token):
        return jwt.decode(id_token, options={"verify_signature": False})


class LaneResourceNotFoundException(Exception):
    pass


class LaneInvalidGrantException(Exception):
    pass


class LaneTokenNotFoundException(Exception):
    pass


class LaneInvalidFormat(Exception):
    pass
