import pyarrow as pa
import os

ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')

class ParquetWriter():

    def __init__(self, pa_table):
        self.pa_table = pa_table
