import os
from enum import Enum


############################
# Cofiguration
############################


#########
# Enum
#########


class TABLE_TYPE(Enum):
    # use ~.value to use as string
    MEDIA = 'media001'
    FAV = 'fav001'
    USER = 'user001'
    COMMENT = 'comment001'


class KEY_TYPE(Enum):
    LANE_TYPE = 'lane_type'
    MEDIA_ID = 'media_id'
    USER_ID = 'user_id'
    CREATED_AT = 'created_at'
    USER_SUB = 'user_sub'
    FAV_ID = 'fav_id'
    COMMENT_ID = 'comment_id'


class ENV_TYPE(Enum):
    DEV = 1
    PROD = 2


# Application root directory
APP_ROOT = os.getcwd()+'/'

# Dynamodb Talbe name
DB_NAME = os.environ.get("DB_NAME")

# ENVIRONMENT(PROD or DEV)
ENVIRONMENT = ENV_TYPE.PROD

# S3
BUCKET_NAME = os.environ.get("BUCKET_NAME")
S3_USER_KEY = os.environ.get("S3_USER_KEY")
S3_MEDIA_KEY = os.environ.get("S3_MEDIA_KEY")

# Cloudfront
CF_HOST_NAME = os.environ.get("CF_HOST_NAME")

# Google
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_TOKEN_ENDPOINT = 'https://www.googleapis.com/oauth2/v4/token'
GOOGLE_CERT_ENDPOINT = 'https://www.googleapis.com/oauth2/v3/certs'

# URL PREFIX
URL_PREFIX = '/api/v1'

# testing
DUMMY_ERR_MSG = 'dummy err msg'
