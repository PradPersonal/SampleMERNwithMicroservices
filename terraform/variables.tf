variable "aws_region" {
  type        = string
  default     = "ca-central-1"
  description = "AWS region to deploy resources to"
}

variable "repository_name" {
  type        = string
  default     = "sample-mern-repo"
  description = "Name of the ECR repository"
}

variable "tags" {
  type = map(string)
  default = {
    Environment = "dev"
    Project     = "SampleMERNwithMicroservices"
  }
  description = "Tags to apply to created resources"
}
