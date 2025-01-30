resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.region
  account_tier             = var.account_tier
  account_replication_type = var.replication_type

  enable_https_traffic_only = true
  min_tls_version          = "TLS1_2"

  blob_properties {
    versioning_enabled = true
    
    container_delete_retention_policy {
      days = 7
    }
  }

  tags = {
    environment = var.environment
  }
}

resource "azurerm_storage_container" "container" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
} 