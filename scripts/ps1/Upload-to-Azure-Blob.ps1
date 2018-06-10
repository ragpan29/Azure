# Upload data to Azure Blob Storage
# https://docs.microsoft.com/en-gb/azure/hdinsight/hdinsight-upload-data
# Log in to the Azure
Login-AzureRmAccount

$resourceGroupName = "<AzureResourceGroupName>"
$storageAccountName = "<StorageAccountName>"
$containerName = "<ContainerName>"

$fileName ="<LocalFileName>"
$blobName = "<BlobName>"

# Get the storage account key
$storageAccountKey = (Get-AzureRmStorageAccountKey -ResourceGroupName $resourceGroupName -Name $storageAccountName)[0].Value
# Create the storage context object
$destContext = New-AzureStorageContext -StorageAccountName $storageAccountName -StorageAccountKey $storageaccountkey

# Copy the file from local workstation to the Blob container
# Use -Force to force overwrite and avoid being prompted
Set-AzureStorageBlobContent -File $fileName -Container $containerName -Blob $blobName -context $destContext -Force