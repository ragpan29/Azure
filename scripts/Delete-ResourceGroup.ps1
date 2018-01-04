# Delete a resource group and all contents in it
# Holds the powershell script until complete
# https://docs.microsoft.com/en-us/azure/azure-resource-manager/powershell-azure-resource-manager

# Use -Force option to prevent prompting
Remove-AzureRmResourceGroup -Name "ResourceGroupName"