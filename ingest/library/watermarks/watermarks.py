import boto3
import os
from datetime import datetime


def _get_dynamo_table():
    env = _get_env()
    try:
        dynamodb = boto3.resource('dynamodb')
        table_name = f'ingest_config_{env}'
        table = dynamodb.Table(table_name)
    except Exception as e:
        print(f'Could not get dynamo db table: {table_name} with error: {e}')
        raise
    return table, table_name


def _get_env():
    env = os.getenv("ENVIRONMENT")
    if not env:
        raise Exception('could not get env from ENVIRONMENT env variable')
    return env


class Watermark:

    def __init__(self, source):
        self.source = source
        table_details = _get_dynamo_table()
        self.dynamo_table = table_details[0]
        self.table_name = table_details[1]
        self.current_watermark = None
        self.previous_watermark = None
        self.watermark_updated = False
        self.current_working_watermark = None
        self._get_watermark()

    def _get_watermark(self):
        try:
            response = self.dynamo_table.get_item(
                TableName=self.table_name,
                Key={'pk': self.source, 'sk': 'watermark'}
            )
            watermark_text = response['Item']
            try:
                self.current_watermark = datetime.strptime(watermark_text.get('current_watermark'), '%Y-%m-%d %H:%M:%S')
                self.previous_watermark = datetime.strptime(watermark_text.get('previous_watermark'), '%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print(f'could not set watermarks with error potentially caused by string format issues in dynamodb: {e}')
            self.current_working_watermark = self.current_watermark
        except Exception as e:
            print(f'error getting watermark from DynamoDb with error: {e}')
            raise

    def update_watermark(self):
        try:
            self.dynamo_table.put_item(
                TableName=self.table_name,
                Item={
                    'pk': self.source,
                    'sk': 'watermark',
                    'current_watermark': str(self.current_working_watermark),
                    'previous_watermark': str(self.current_watermark)
                }
            )
        except Exception as e:
            print(f'error setting watermark from DynamoDb with error: {e}')
            raise
