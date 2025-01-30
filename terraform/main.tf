terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.region

  tags = {
    environment = var.environment
  }
}

# Variables
variable "resource_group_name" {
  type        = string
  description = "Name of the resource group"
}

variable "region" {
  type        = string
  description = "Azure region to deploy resources"
}

variable "environment" {
  type        = string
  description = "Environment (dev, staging, prod)"
  default     = "dev"
}

# Output the resource group ID
output "resource_group_id" {
  value = azurerm_resource_group.rg.id
} 