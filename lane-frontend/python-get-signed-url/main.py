from flask import Flask, jsonify
import boto3
from botocore.client import Config
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['POST'])
def get_signed_url():
    s3 = boto3.client('s3', config=Config(signature_version='s3v4'))

    res = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={'Bucket': 'my-bucket', 'Key': 'test.jpeg'},
        ExpiresIn=60,
        HttpMethod='PUT')
    return jsonify({'url': res})


if __name__ == '__main__':
    app.run(port='80', host="0.0.0.0")
