from sqlalchemy import create_engine
from datetime import datetime
import logging
import boto3
import json
import pyarrow as pa
import os

from library.watermarks import watermarks


def _get_env():
    environment = os.getenv('ENVIRONMENT')
    if not environment:
        raise Exception('could not get env variable for environment')
    return environment


def _set_engine(url, database, password, user):
    """abstract method that sets the mysql engine from class constructor"""
    try:
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{url}/{database}", echo=False)
    except Exception as e:
        print(f'Issue creating engine in class: {e}')
        raise
    return engine


def _get_parameters_for_source(env_name, source_name):
    """This accepts an argument of environment and target, this calls ssm parameter store to get credentials and
    details etc """
    try:
        ssm = boto3.client('ssm')
        param_name = f'/pipeline/{env_name}/ingest/{source_name}'
        parameter = ssm.get_parameter(Name=param_name, WithDecryption=True)
        parameter_dict = json.loads(parameter['Parameter']['Value'])

        url = parameter_dict.get("URL", 'NOT FOUND')
        database = parameter_dict.get('DATABASE', 'NOT FOUND')
        password = parameter_dict.get('PASSWORD', 'NOT FOUND')
        username = parameter_dict.get('USERNAME', 'NOT FOUND')

        if 'NOT FOUND' in [url, database, password, username]:
            raise Exception(f'Could not get the correct required params from {param_name}, required: URL, DATABASE, '
                            f'USER and PASSWORD')
        return url, database, password, username

    except Exception as e:
        print(f'Error calling to ssm parameter at location /pipeline/{env_name}/ingest/{source_name} with error: {e}')
        raise


def _get_config_for_source(environment, source_name):
    dynamodb = boto3.resource('dynamodb')
    table_name = f'ingest_config_{environment}'
    table = dynamodb.Table(table_name)

    key = {'pk': source_name, 'sk': 'configuration'}
    config = table.get_item(
        TableName=table_name,
        Key=key
    )
    return config['Item']


class RDBMSSource:
    """class for containing RDBMS logic for connecting and querying sources for RDBMS"""

    def __init__(self, source_name, sql_strain='mysql'):
        self.source_name = source_name
        self.environment = _get_env()
        url, database, password, user = _get_parameters_for_source(self.environment, source_name)
        self.engine = _set_engine(url, database, password, user)
        # todo further config calls
        self.ingest_config = _get_config_for_source(self.environment, self.source_name)
        self.watermark = watermarks.Watermark(self.source_name)
        self.query = self.format_query()
        self.batch_size = 200
        if sql_strain != 'mysql':
            raise NotImplementedError('Only support MySql for now sorry.')

    # mapping for types from describe cursors to python and pyarrow types
    _type_map = {
        3: [int, pa.int64()],
        4: [float, pa.float64()],
        5: [float, pa.float64()],
        6: None,
        12: [datetime, pa.timestamp('ms')],
        253: [str, pa.string()],
    }

    def get_data_in_chunks(self):
        """
        Reads data from a table and breaks the read into defined chunks, returns a tuple of: a dict of columns types
        and a chunk of rows
        """
        if not self.engine:
            raise Exception("you need to first set this classes engine")
        with self.engine.connect() as connection:
            try:
                with connection.connection.cursor() as result_cursor:

                    result_cursor.execute(self.query)
                    cursor_desc = result_cursor.description

                    column_schema = {column[0]: self._type_map.get(column[1]) for column in cursor_desc}
                    logging.info(f'schema is : {column_schema}')
                    result_cursor.arraysize = 10000

                    while True:
                        chunk = result_cursor.fetchmany(self.batch_size)
                        if not chunk:
                            break
                        yield column_schema, chunk

            except Exception as e:
                print(f"error executing query - exception raised {e}")
                raise
            finally:
                connection.close()

    def format_query(self):
        if not self.ingest_config:
            raise Exception('Config is required to format the query')
        base_query = f'select * from {self.source_name}'
        if self.ingest_config.get('has_watermark'):
            watermark_cols = self.ingest_config.get('watermark_columns')
            base_query = base_query + ' where ('
            for i, watermark_col in enumerate(watermark_cols):
                if i > 0:
                    or_text = ' or '
                else:
                    or_text = ''
                criteria_text = "{watermark_column} >= '{watermark_value}'".format(
                    watermark_column=watermark_col,
                    watermark_value=self.watermark.current_watermark
                )
                base_query = base_query + or_text + criteria_text
            base_query = base_query + ')'
        return base_query
