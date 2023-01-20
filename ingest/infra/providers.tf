terraform {
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.55.0"
    }
  } 
  backend "s3" {
    bucket = "pipelines-terraform-bucket"
    key = "ingest/terraform.tfstate"
    region = "ap-southeast-2"
    dynamodb_table = "tf-state-lock"
  }
}

provider "snowflake" {
  account          = var.snowflake_account_param["account"]  
  region           = var.snowflake_account_param["region"]
  username         = var.snowflake_account_param["user"]
  role             = var.snowflake_account_param["role"]
  password         = var.snowflake_account_param["password"]
}

provider aws {
  region = var.aws_region
}