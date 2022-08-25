import sys
import os
import boto3
import yaml
from api.config import APP_ROOT

sys.path.append(os.path.abspath(os.path.dirname(
    os.path.abspath(__file__)) + "/../api/"))

sys.path.append(os.path.abspath(os.path.dirname(
    os.path.abspath(__file__)) + "/../"))


class DynamoDBSetup:
    def __init__(self, db_name):
        self.db_name = db_name

    def _insert_data(self, data):
        table = self.dynamo.Table(self.db_name)

        table.put_item(
            Item=data
        )

    def _create_table(self):
        ddb_def_yaml = APP_ROOT + "ddb_table_definition.yaml"
        with open(ddb_def_yaml, 'r', encoding='utf-8') as fp:
            table_config = yaml.safe_load(fp)['Table']

        self.dynamo = boto3.resource('dynamodb')
        self.dynamo.create_table(
            TableName=self.db_name,
            AttributeDefinitions=table_config['AttributeDefinitions'],
            KeySchema=table_config['KeySchema'],
            ProvisionedThroughput=table_config['ProvisionedThroughput'],
            LocalSecondaryIndexes=table_config['LocalSecondaryIndexes']
        )
        return self
