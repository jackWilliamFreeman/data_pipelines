import sources.rdbms as rdbms
import pyarrow as pa
from pyarrow import parquet as pq
import uuid
import s3fs

#these come from lambda invoke
TARGET = 'students'


database_source = rdbms.RDBMSSource(TARGET)
reader = database_source.get_data_in_chunks()

root_path = f's3://schooldb/ingest_data/{TARGET}/'
batch_id = str(uuid.uuid4())
final_path = root_path+batch_id+'/'
basename_template = f"{TARGET}-{{internal_increment:04d}}-{{{{i}}}}.parquet"

for i,table in enumerate(database_source.get_pa_table_from_reader(reader)):
    writer = pa.BufferOutputStream()
    pq.write_to_dataset(
        table=table, 
        root_path=final_path,
        filesystem=s3fs.S3FileSystem(),
        basename_template=basename_template.format(internal_increment=i)
    )
    print('printed')