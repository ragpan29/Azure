# Azure Data Catalog

## Authentication
Azure Data Catalog uses Active Directory Authentication when accessing the REST API.

You'll need to...
* Register your native (not a web app / api) application in Active Directory ([Instructions](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-v1-add-azure-ad-app))
* Under settings, click Required Permissions ([Instructions](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-v1-update-azure-ad-app#add-application-credentials-or-permissions-to-access-web-apis) - Step 5 )
* Add delegated permissions for Data Catalog to your app.


## Example Quickstarts:

* [Import / Export tool (C#)](https://azure.microsoft.com/en-us/resources/samples/data-catalog-dotnet-import-export/)


