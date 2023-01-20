resource "random_pet" "pet_name" {
  length =2
}

resource "random_string" "random" {
  length = 6
  special = false
  upper = false
}

locals {
  prefix       = "${var.project_code}-${var.region_code}"
  bucket_name = "raw-data-pipelines-${var.environment}"
  default_tags = {
    Project   = upper(var.project_code)
    ManagedBy = var.managed_by
  }  
}
