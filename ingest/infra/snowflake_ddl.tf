// Snowflake DDL
resource "snowflake_database" "db" {
  name    = upper("${var.region_code}_raw_db_${var.environment}")
  comment = "Database for Snowflake Ingestion Pipeline (SIP) project"  
}

resource "snowflake_schema" "schema" {    
  database = snowflake_database.db.name
  name     = "TEST"
  comment  = "Schema from TEST source system"

  is_transient        = false
  is_managed          = false
}

resource "snowflake_table" "table" {   
  database            = snowflake_database.db.name
  schema              = snowflake_schema.schema.name
  name                = "STUDENTS_RAW"
  comment             = "raw student data"

  column {
    name     = "PARQUET_RAW"
    type     = "VARIANT" 
  }

  column {
    name     = "RECORD_CREATED_TS"
    type     = "TIMESTAMP_LTZ" 
  }

  column {
    name     = "FILE_NAME"
    type     = "VARCHAR(16000)" 
  }
}