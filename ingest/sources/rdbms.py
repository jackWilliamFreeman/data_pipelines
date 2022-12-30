from sqlalchemy import create_engine
from datetime import datetime
import boto3
import json
import pyarrow as pa
import os

ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')

def _set_engine(url, database, password, user):
    '''abstract method that sets the mysql engine from class constructor'''
    try:
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{url}/{database}",echo = False)
    except Exception as e:
        print(f'Issue creating engine in class: {e}')
        raise
    return engine

def get_parameters_for_source(ENVIRONMENT, source_name):
    '''This accepts an argument of environment and target, this calls ssm paramter store to get credentials and details etc'''
    try:
        session = boto3.Session()
        ssm = boto3.client('ssm')
        param_name = f'/pipeline/{ENVIRONMENT}/ingest/{source_name}'
        parameter = ssm.get_parameter(Name=param_name, WithDecryption=True)
        parameter_dict = json.loads(parameter['Parameter']['Value'])

        url = parameter_dict.get("URL",'NOT FOUND')
        database = parameter_dict.get('DATABASE','NOT FOUND')
        password = parameter_dict.get('PASSWORD','NOT FOUND')
        username = parameter_dict.get('USERNAME','NOT FOUND')

        if 'NOT FOUND' in [url, database, password, username]:
            raise Exception(f'Could not get the correct required params from {param_name}, required: URL, DATABASE, USER and PASSWORD')
        return (url, database, password, username)

    except Exception as e:
        print(f'Error calling to ssm paramter at location /pipeline/{ENVIRONMENT}/ingest/{source_name} with error: {e}')
        raise

class RDBMSSource():
    '''class for containings RDBMS logic for connecting and querying sources for RDBMS'''
    def __init__(self, source_name, sql_strain='mysql'):
        self.query = 'select * from students'
        url, database, password, user = get_parameters_for_source(ENVIRONMENT, source_name)
        self.engine = _set_engine(url, database, password, user)
        #todo further config calls
        self.batch_size = 200
        if sql_strain != 'mysql':
            raise NotImplementedError('Only support MySql for now sorry.')

        #mapping for types from describe cursors to python and pyarrow types
    _type_map = {
        3:[int, pa.int64()],
        4:[float, pa.float64()],
        5:[float, pa.float64()],
        6:None,
        12:[datetime,pa.timestamp('ms')],
        253:[str,pa.string()],
    }

    def get_data_in_chunks(self):
        '''
        Reads data from a table and breaks the read into defined chunks, returns a tuple of: a dict of columns types and a chunk of rows
        '''
        if not self.engine:
            raise Exception("you need to first set this classes engine")
        with self.engine.connect() as connection:
            try:
                with connection.connection.cursor() as result_cursor:

                    result_cursor.execute(self.query)
                    cursor_desc = result_cursor.description

                    column_schema = {column[0]:self._type_map.get(column[1]) for column in cursor_desc}
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

    def get_pa_table_from_reader(self,reader_generator):
        '''pass in a generator from source reader object, needs to output a column dict and a chunk of data from a cursor'''
        for columns,chunk in reader_generator:
            col_data_arrays = []
            for i,key in enumerate(columns):
                pa_column_type  = columns[key][1]
                if not pa_column_type:
                    raise Exception(f'Could not get pyarrow data type for column {key}')
                col_data = [row[i] for row in chunk]
                col_data_arrays.append(pa.array(col_data, type=pa_column_type))
            col_names = [key for key in columns]
            table = pa.Table.from_arrays(col_data_arrays, col_names)
            yield table
