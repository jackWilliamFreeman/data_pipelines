from library.parquetwriter.parquetwriter import ParquetWriter
from library.sources.rdbms import RDBMSSource
from library.watermarks import watermarks
from dotenv import load_dotenv
import json
import logging
import datetime
import boto3
import os

# for development .env files
load_dotenv()
logging.getLogger().setLevel(logging.INFO)
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')


def _get_config_for_source(environment, source_name):
    try:
        dynamodb = boto3.resource('dynamodb')
        table_name = f'ingest_config_{environment}'
        table = dynamodb.Table(table_name)
        key = {'pk': source_name, 'sk': 'configuration'}
        config = table.get_item(
            TableName=table_name,
            Key=key
        )
        return config['Item']
    except Exception as e:
        print(f'Error raised getting config: {e}')


def lambda_handler(event, context):
    source_name = event.get('source_name')
    print(f'starting ingest for {source_name}')
    logging.info(f'source name is {source_name}')

    config = _get_config_for_source(ENVIRONMENT, source_name)
    if config.get('has_watermark'):
        watermark = watermarks.Watermark(source_name)
    else:
        watermark = None

    # get records in chunks from db
    database_source = RDBMSSource(source_name, config, watermark)
    logging.info(f'connected to database success')
    reader = database_source.get_data_in_chunks()
    logging.info('got reader success')

    # write to s3
    writer = ParquetWriter(source_name)
    writer.write_generator_parquet_to_s3(reader)

    # update the watermark when finished
    if watermark.watermark_updated:
        watermark.update_watermark()

    return {
        'statusCode': 200,
        'body': json.dumps(f'ingest completed for {source_name}')
    }


if __name__ == '__main__':
    lambda_handler({'source_name': 'students'}, None)
