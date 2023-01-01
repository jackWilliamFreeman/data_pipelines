from library.parquetwriter.parquetwriter import ParquetWriter
from library.sources.rdbms import RDBMSSource
from dotenv import load_dotenv
import json

# for development .env files
load_dotenv()


def lambda_handler(event, context):
    # TODO implement
    source_name = event.get('source_name')

    database_source = RDBMSSource(source_name)
    reader = database_source.get_data_in_chunks()

    writer = ParquetWriter(source_name)
    writer.write_generator_parquet_to_s3(reader)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


if __name__ == '__main__':
    lambda_handler('students', None)
