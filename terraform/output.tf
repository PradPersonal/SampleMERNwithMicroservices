output "repository_url" {
  value       = aws_ecr_repository.app.repository_url
  description = "URL of the created ECR repository"
}

output "repository_id" {
  value       = aws_ecr_repository.app.id
  description = "ECR repository id"
}

output "registry_id" {
  value       = aws_ecr_repository.app.registry_id
  description = "ECR registry id"
}
