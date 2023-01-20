data "aws_iam_policy_document" "lambda_ingest_policies" {

  statement {
    actions   = [
       "s3:GetAccountPublicAccessBlock",
        "s3:GetBucketAcl",
        "s3:GetBucketLocation",
        "s3:GetBucketPolicyStatus",
        "s3:GetBucketPublicAccessBlock",
        "s3:ListAccessPoints",
        "s3:ListAllMyBuckets"
    ]
    resources = [aws_s3_bucket.raw_data_bucket.arn]
    effect = "Allow"
  }
  statement {
    actions   = ["s3:*"]
    resources = ["${aws_s3_bucket.raw_data_bucket.arn}/*"]
    effect = "Allow"
  }
  statement {
            effect = "Allow"
            actions = ["logs:*"]
            resources = ["*"]
  }
  statement {
            effect = "Allow"
            actions = [
                "ssm:Describe*",
                "ssm:Get*",
                "ssm:List*"
            ]
            resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = ["dynamodb:*"]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = ["rds:Describe*"]
    resources = ["*"]
  }
}

resource "aws_iam_role" "lambda_execution_role" {
  name = "ingest-pipeline-lambda-execution-role"
  path =  "/service-role/"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })

  inline_policy {
    name = "${random_pet.pet_name.id}-policy"
    policy = data.aws_iam_policy_document.lambda_ingest_policies.json
  }

  tags = {
    purpose = "dev ingest pipeline"
  }
}