resource "azurerm_public_ip" "lb_ip" {
  name                = var.public_ip_name
  location            = var.region
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                = "Standard"
}

resource "azurerm_lb" "lb" {
  name                = var.lb_name
  location            = var.region
  resource_group_name = var.resource_group_name
  sku                = "Standard"

  frontend_ip_configuration {
    name                 = "PublicIPAddress"
    public_ip_address_id = azurerm_public_ip.lb_ip.id
  }

  tags = {
    environment = var.environment
  }
}

resource "azurerm_lb_backend_address_pool" "backend_pool" {
  loadbalancer_id = azurerm_lb.lb.id
  name            = "BackEndAddressPool"
}

resource "azurerm_lb_probe" "probe" {
  loadbalancer_id = azurerm_lb.lb.id
  name            = "http-probe"
  protocol        = "Http"
  request_path    = "/"
  port            = 80
} 