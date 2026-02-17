terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "kubernetes" {
  config_path = var.kubeconfig_path
}

provider "helm" {
  kubernetes {
    config_path = var.kubeconfig_path
  }
}

# Variables
variable "cluster_name" {
  description = "Name of the Kubernetes cluster"
  type        = string
  default     = "cloudcostguard"
}

variable "namespace" {
  description = "Kubernetes namespace for CloudCostGuard"
  type        = string
  default     = "cloudcostguard"
}

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

variable "prometheus_url" {
  description = "Prometheus server URL"
  type        = string
  default     = "http://prometheus:9090"
}

variable "kubeconfig_path" {
  description = "Path to kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}

variable "create_namespace" {
  description = "Whether to create the namespace"
  type        = bool
  default     = true
}

variable "backend_replicas" {
  description = "Number of backend replicas"
  type        = number
  default     = 1
}

variable "frontend_replicas" {
  description = "Number of frontend replicas"
  type        = number
  default     = 1
}

variable "enable_postgresql" {
  description = "Whether to deploy PostgreSQL"
  type        = bool
  default     = true
}

variable "enable_redis" {
  description = "Whether to deploy Redis"
  type        = bool
  default     = true
}

variable "postgresql_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
  default     = "cloudcostguard"
}

# Create namespace if requested
resource "kubernetes_namespace" "cloudcostguard" {
  count = var.create_namespace ? 1 : 0
  
  metadata {
    name = var.namespace
    labels = {
      name = var.namespace
      app  = "cloudcostguard"
    }
  }
}

# Deploy CloudCostGuard using Helm
resource "helm_release" "cloudcostguard" {
  name       = "cloudcostguard"
  repository = "https://charts.cloudcostguard.io"
  chart      = "cloudcostguard"
  version    = "1.0.0"
  namespace  = var.create_namespace ? kubernetes_namespace.cloudcostguard[0].metadata[0].name : var.namespace
  
  set {
    name  = "azure.subscriptionId"
    value = var.azure_subscription_id
  }
  
  set {
    name  = "azure.clientId"
    value = var.azure_client_id
  }
  
  set {
    name  = "azure.clientSecret"
    value = var.azure_client_secret
  }
  
  set {
    name  = "azure.tenantId"
    value = var.azure_tenant_id
  }
  
  set {
    name  = "prometheus.url"
    value = var.prometheus_url
  }
  
  set {
    name  = "backend.replicaCount"
    value = var.backend_replicas
  }
  
  set {
    name  = "frontend.replicaCount"
    value = var.frontend_replicas
  }
  
  set {
    name  = "postgresql.enabled"
    value = var.enable_postgresql
  }
  
  set {
    name  = "redis.enabled"
    value = var.enable_redis
  }
  
  set {
    name  = "postgresql.auth.postgresPassword"
    value = var.postgresql_password
  }
  
  depends_on = [
    kubernetes_namespace.cloudcostguard
  ]
}

# Service Monitor for Prometheus (if Prometheus is deployed in the same cluster)
resource "kubernetes_manifest" "service_monitor" {
  count = var.enable_postgresql ? 1 : 0
  
  manifest = {
    apiVersion = "monitoring.coreos.com/v1"
    kind       = "ServiceMonitor"
    metadata = {
      name      = "cloudcostguard"
      namespace = var.create_namespace ? kubernetes_namespace.cloudcostguard[0].metadata[0].name : var.namespace
      labels = {
        app = "cloudcostguard"
      }
    }
    spec = {
      selector = {
        matchLabels = {
          app = "cloudcostguard"
        }
      }
      endpoints = [
        {
          port = "http"
          path = "/metrics"
        }
      ]
    }
  }
}

# Outputs
output "namespace" {
  description = "Kubernetes namespace where CloudCostGuard is deployed"
  value       = var.create_namespace ? kubernetes_namespace.cloudcostguard[0].metadata[0].name : var.namespace
}

output "backend_service" {
  description = "Backend service name"
  value       = helm_release.cloudcostguard.name == "cloudcostguard" ? "${helm_release.cloudcostguard.name}-backend" : null
}

output "frontend_service" {
  description = "Frontend service name"
  value       = helm_release.cloudcostguard.name == "cloudcostguard" ? "${helm_release.cloudcostguard.name}-frontend" : null
}

output "helm_release" {
  description = "Helm release information"
  value       = helm_release.cloudcostguard
}
