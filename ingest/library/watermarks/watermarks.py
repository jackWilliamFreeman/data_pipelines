import boto3
import os


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
        self._get_watermark()

    def _get_watermark(self):
        try:
            response = self.dynamo_table.get_item(
                TableName=self.table_name,
                Key={'pk': self.source, 'sk': 'watermark'}
            )
            watermark_text = response['Item']
            self.current_watermark = watermark_text.get('current_watermark')
            self.previous_watermark = watermark_text.get('previous_watermark')
        except Exception as e:
            print(f'error getting watermark from DynamoDb with error: {e}')
            raise
