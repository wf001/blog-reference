from util import Util
import freezegun
import pytest
from moto import mock_s3
import base64
from api.config import APP_ROOT, BUCKET_NAME
import boto3
import json


DUMMY_DATETIME_01 = '2020-01-01 00:00:00'
# -> 1577836800 +0:00


class TestUtil:

    @mock_s3
    def test_upload_to_s3_ok(self):
        with open(APP_ROOT+'api/test_img_small.png', "rb") as image_file:
            data = base64.b64encode(image_file.read())
        boto3.client('s3').create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={
                'LocationConstraint': 'ap-northeast-1'}
        )

        Util().upload_to_s3(
            data,
            'test_file_001'
        )
        s3 = boto3.client('s3', region_name='ap-northeast-1')
        actual = s3.list_objects_v2(
            Bucket=BUCKET_NAME,
        )
        assert 'test_file_001' == actual['Contents'][0]['Key']
