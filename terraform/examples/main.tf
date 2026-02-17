# Example usage of CloudCostGuard Terraform module

terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

# Deploy CloudCostGuard to Kubernetes cluster
module "cloudcostguard" {
  source = "../../modules/cloudcostguard-agent"
  
  # Azure Configuration
  azure_subscription_id = var.azure_subscription_id
  azure_client_id     = var.azure_client_id
  azure_client_secret = var.azure_client_secret
  azure_tenant_id     = var.azure_tenant_id
  
  # Kubernetes Configuration
  cluster_name        = "production"
  namespace          = "cloudcostguard"
  kubeconfig_path    = "~/.kube/config"
  create_namespace    = true
  
  # Application Configuration
  backend_replicas   = 2
  frontend_replicas  = 2
  
  # Database Configuration
  enable_postgresql  = true
  postgresql_password = var.postgresql_password
  
  # Monitoring Configuration
  enable_redis     = true
  prometheus_url   = "http://prometheus.monitoring.svc.cluster.local:9090"
}

# Variables
variable "azure_subscription_id" {
  description = "Azure subscription ID"
  type        = string
  sensitive   = true
}

variable "azure_client_id" {
  description = "Azure service principal client ID"
  type        = string
  sensitive   = true
}

variable "azure_client_secret" {
  description = "Azure service principal client secret"
  type        = string
  sensitive   = true
}

variable "azure_tenant_id" {
  description = "Azure tenant ID"
  type        = string
  sensitive   = true
}

variable "postgresql_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
  default     = "secure-password-change-me"
}

# Outputs
output "cloudcostguard_namespace" {
  description = "CloudCostGuard namespace"
  value       = module.cloudcostguard.namespace
}

output "cloudcostguard_backend_service" {
  description = "Backend service name"
  value       = module.cloudcostguard.backend_service
}

output "cloudcostguard_frontend_service" {
  description = "Frontend service name"
  value       = module.cloudcostguard.frontend_service
}
