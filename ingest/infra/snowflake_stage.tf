// Stage for tweets prefix
resource "snowflake_stage" "stage_students" {
  name                = upper("${var.region_code}_school_db_ingest_${var.environment}")
  url                 = "s3://${local.bucket_name}/"
  database            = snowflake_database.db.name
  schema              = snowflake_schema.schema.name
  storage_integration = snowflake_storage_integration.integration.name
  file_format         = "FORMAT_NAME = ${snowflake_database.db.name}.${snowflake_schema.schema.name}.${snowflake_file_format.parquet_file_format.name}"
}

resource "snowflake_file_format" "parquet_file_format" {
  name        = upper("parquet_ff")
  database    = snowflake_database.db.name
  schema      = snowflake_schema.schema.name
  format_type = "PARQUET"
  compression = "SNAPPY"
}