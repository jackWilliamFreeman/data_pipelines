resource "aws_s3_bucket" "raw_data_bucket" {
  bucket = local.bucket_name
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "stage_bucket_load_access_block" {
  bucket = aws_s3_bucket.raw_data_bucket.id

  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.raw_data_bucket.id

  queue {
    queue_arn     = snowflake_pipe.pipe_students.notification_channel
    events        = ["s3:ObjectCreated:*"]
  }
}