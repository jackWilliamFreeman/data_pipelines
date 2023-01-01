import pyarrow as pa
from pyarrow import parquet as pq
import uuid
import s3fs


def _get_pa_table_from_reader(reader_generator):
    """pass in a generator from source reader object, needs to output a column dict and a chunk of data from a
    cursor """
    for columns, chunk in reader_generator:
        col_data_arrays = []
        for i, key in enumerate(columns):
            pa_column_type = columns[key][1]
            if not pa_column_type:
                raise Exception(f'Could not get pyarrow data type for column {key}')
            col_data = [row[i] for row in chunk]
            col_data_arrays.append(pa.array(col_data, type=pa_column_type))
        col_names = [key for key in columns]
        table = pa.Table.from_arrays(col_data_arrays, col_names)
        yield table


class ParquetWriter:

    def __init__(self, source_name):
        self.source_name = source_name
        self.root_path = f's3://schooldb/ingest_data/{self.source_name}/'

    def write_generator_parquet_to_s3(self, generator):
        batch_id = str(uuid.uuid4())
        final_path = self.root_path + batch_id + '/'
        basename_template = f"{self.source_name}-{{internal_increment:04d}}-{{{{i}}}}.parquet"

        try:
            for i, table in enumerate(_get_pa_table_from_reader(generator)):
                pq.write_to_dataset(
                    table=table,
                    root_path=final_path,
                    filesystem=s3fs.S3FileSystem(),
                    basename_template=basename_template.format(internal_increment=i)
                )
                print(f'printed file number : {basename_template.format(internal_increment=i)}')
        except Exception as e:
            print(f'Error writing to S3: {e}')
            raise
