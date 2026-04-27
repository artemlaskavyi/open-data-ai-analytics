variable "resource_group_location" {
  type        = string
  default     = "polandcentral"
  description = "Location of the resource group."
}

variable "resource_group_name_prefix" {
  type        = string
  default     = "rg-open-data"
  description = "Prefix of the resource group name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "vm_size" {
  type        = string
  default     = "Standard_D2s_v3"
  description = "Size of the virtual machine."
}

variable "admin_username" {
  type        = string
  default     = "azureuser"
  description = "Admin username for the VM."
}
