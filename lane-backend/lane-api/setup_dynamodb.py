import boto3
import random
import string
import datetime
import time
import yaml
from api.config import APP_ROOT, ENVIRONMENT, DB_NAME, ENV_TYPE, CF_HOST_NAME
from api.util import Util


def str_time_prop(start, end, format, prop):

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def random_date(start, prop):
    return str(start + prop)


def randomname(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))


class DynamoDBSetup:
    def __init__(self, db_name, use_ddb_local=True):
        self.users = []
        self.medias = []
        self.DATASET_VOLUME = 40
        self.USER_VOLUME = 6

        self.db_name = db_name
        self.dynamo = None
        if not use_ddb_local or ENVIRONMENT == ENV_TYPE.PROD:
            self.dynamo = boto3.resource(
                'dynamodb',
                region_name='ap-northeast-1'
            )
            print("use ACTUAL DDB or mock DDB.")
        else:
            self.dynamo = boto3.resource(
                'dynamodb',
                endpoint_url='http://dynamodb:8000'
            )
            print("use LOCAL DDB.")
        self.table = self.dynamo.Table(self.db_name)

    def _insert_data(self, data):

        return self.table.put_item(
            Item=data
        )

    def _create_table(self):
        ddb_def_yaml = APP_ROOT + "ddb_table_definition.yaml"
        with open(ddb_def_yaml, 'r', encoding='utf-8') as fp:
            table_config = yaml.safe_load(fp)['Table']

        self.dynamo.create_table(
            TableName=self.db_name,
            AttributeDefinitions=table_config['AttributeDefinitions'],
            KeySchema=table_config['KeySchema'],
            ProvisionedThroughput=table_config['ProvisionedThroughput'],
            LocalSecondaryIndexes=table_config['LocalSecondaryIndexes']
        )
        return self

    def seed_media(self):

        for i in range(self.DATASET_VOLUME):
            user_id = self.users[random.randint(0, self.USER_VOLUME-1)]
            media_id = Util().gen_identifier()
            self.medias.append(f'm{media_id}')
            image_url_path = randomname(5)
            avator_url = randomname(5)
            media_text = randomname(10)
            # 2020/1/1 00:00:00 +0:00
            start = 1577836800
            date = str(int(start)+100*i)

            response = self._insert_data(
                {
                    "lane_type": "media001",
                    "user_id": user_id,
                    "media_id": f'm{media_id}',
                    "avator_url": f'https://{CF_HOST_NAME}/lane-user001/test_img_small.png',
                    "image_url": f'https://{CF_HOST_NAME}/lane-media001/Screenshot+from+2020-12-31+17-48-39.png',
                    "media_text": media_text,
                    "created_at": date
                }
            )
            print(response)

    def seed_fav(self):
        for i in range(self.DATASET_VOLUME):
            user_id = self.users[random.randint(0, self.USER_VOLUME-1)]
            target_user_id = self.users[random.randint(0, self.USER_VOLUME-1)]
            media_id = self.medias[random.randint(0, self.DATASET_VOLUME-1)]
            fav_id = Util().gen_identifier()
            image_url_path = randomname(5)
            avator_url = randomname(5)
            media_text = randomname(10)
            # 2020/1/1 00:00:00 +0:00
            start = 1577836800
            date = str(int(start)+100*i)

            response = self._insert_data(
                {
                    "lane_type": "fav001",
                    "user_id": user_id,
                    "target_user_id": target_user_id,
                    "media_id": media_id,
                    "avator_url": f'{CF_HOST_NAME}{avator_url}',
                    "fav_id": f'f{fav_id}',
                    "image_url": f'{CF_HOST_NAME}{image_url_path}',
                    "media_text": media_text,
                    "created_at": date
                }
            )
            print(response)

    def seed_user(self):
        for i in range(self.USER_VOLUME):
            self.users.append(randomname(10))

        for i in range(self.USER_VOLUME):
            user_id = self.users[i]
            description = randomname(10)
            user_name = randomname(7)
            user_sub = Util().hash_user_sub(str(i))
            avator_url = randomname(5)
            # 2020/1/1 00:00:00 +0:00
            start = 1577836800
            date = random_date(start, random.randint(1, 31622399))

            response = self._insert_data(
                {
                    "lane_type": "user001",
                    "user_id": user_id,
                    "description": description,
                    "avator_url": f'{CF_HOST_NAME}{avator_url}',
                    "user_sub": user_sub,
                    "user_name": f'un_{user_name}',
                    "created_at": date
                }
            )
            print(response)

    def seed_comment(self):
        for i in range(self.DATASET_VOLUME*5):
            user_id = self.users[random.randint(0, self.USER_VOLUME-1)]
            media_id = self.medias[random.randint(0, self.DATASET_VOLUME-1)]
            avator_url = randomname(5)
            comment_text = randomname(20)
            comment_id = Util().gen_identifier()
            # 2020/1/1 00:00:00 +0:00
            start = 1579836800
            date = str(int(start)+100*i)

            response = self._insert_data(
                {
                    "lane_type": "comment001",
                    "media_id": media_id,
                    "user_id": user_id,
                    "avator_url": f'{CF_HOST_NAME}{avator_url}',
                    "comment_id": f'c{comment_id}',
                    "created_at": date,
                    "comment_text": comment_text
                }
            )
            print(response)


if __name__ == '__main__':
    if ENVIRONMENT == ENV_TYPE.PROD:
        # seeding to Real DDB
        DDB = DynamoDBSetup(DB_NAME, False)._create_table()
    else:
        # seeding to DDB Local
        DDB = DynamoDBSetup(DB_NAME)._create_table()
    time.sleep(1)
    DDB.seed_user()
    DDB.seed_media()
    DDB.seed_fav()
    DDB.seed_comment()
