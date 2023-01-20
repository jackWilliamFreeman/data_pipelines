locals {
 account_id          = data.aws_caller_identity.current.account_id
 ecr_repository_name = "lambda-ingest-${var.environment}"
 ecr_image_tag       = "latest"
}

data aws_caller_identity current {}
 

data "aws_ecr_repository" "lambda_ingest_repo" {
  name = local.ecr_repository_name
}

data aws_ecr_image lambda_image {
 repository_name = local.ecr_repository_name
 image_tag       = local.ecr_image_tag
}

resource aws_lambda_function ingest_lambda {
  function_name = "ingest-schooldb-${var.environment}"
  role          = aws_iam_role.lambda_execution_role.arn
  image_uri = "${data.aws_ecr_repository.lambda_ingest_repo.repository_url}@${data.aws_ecr_image.lambda_image.id}"
  package_type = "Image"
  timeout = 600

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }
}