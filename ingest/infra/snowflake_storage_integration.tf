// Storage integration that assumes the AWS role created
resource "snowflake_storage_integration" "integration" {
  name                      = upper("${var.project_code}_${var.region_code}_s3_load_int")
  comment                   = "Storage integration used to read files from S3 staging bucket"
  type                      = "EXTERNAL_STAGE"
  enabled                   = true
  storage_provider          = "S3"
  storage_aws_role_arn      = aws_iam_role.role_for_snowflake_load.arn
  storage_allowed_locations = [
    "s3://${local.bucket_name}/"
  ]    
}