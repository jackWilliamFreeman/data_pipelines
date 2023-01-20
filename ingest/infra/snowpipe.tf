resource "snowflake_pipe" "pipe_students" {
  database          = snowflake_table.table.database
  schema            = snowflake_table.table.schema
  name              = upper("${var.region_code}_students_pipe")
  comment           = "A pipe to ingest the incoming students."

  copy_statement    = <<EOT
    COPY INTO ${snowflake_table.table.database}.${snowflake_table.table.schema}.${snowflake_table.table.name} 
        FROM (
        SELECT 
        $1, 
        CURRENT_TIMESTAMP(), 
        METADATA$FILENAME 
        FROM @${snowflake_table.table.database}.${snowflake_table.table.schema}.${snowflake_stage.stage_students.name} t
        )
    EOT

  auto_ingest       = true
}