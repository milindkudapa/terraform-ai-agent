resource "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  address_space       = var.address_space
  location            = var.region
  resource_group_name = var.resource_group_name

  subnet {
    name           = "default"
    address_prefix = var.subnet_prefix
  }

  tags = {
    environment = var.environment
  }
}

resource "azurerm_subnet" "subnet" {
  name                 = var.subnet_name
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet_prefix]

  service_endpoints = ["Microsoft.Storage", "Microsoft.Sql"]
} 