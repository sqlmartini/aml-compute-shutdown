# **Intro**

This is an example project to automate the shutting down of Azure ML Compute Instances using Azure Functions.  Useful from a cost savings perspective to ensure that compute is shut down outside of normal working hours.  

As of 3/27/2020 the AML Python SDK is the only way to manage Compute Instances as the AML CLI is not currently supported.

Services Used:
- **Azure Machine Learning**:  workspace that contains the Compute Instance used for ML development and model training
- **Azure Function App**:  contains serverless functions for shutting down AML Compute Instances
- **Azure Key Vault**:  stores secrets to be utilized by functions
- **Azure Blob Storage**:  storage account used by Azure Functions and AML
- **Azure App Insights**:  required by AML and helpful for troubleshooting functions

# **Pre-reqs**

- **Azure Powershell** - https://docs.microsoft.com/en-us/powershell/azure/install-az-ps?view=azps-2.8.0
- **Azure Functions project using VS Code** - https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-vs-code?pivots=programming-language-python

# **Steps**

## 1.  Create AAD Service Principal

The Azure functions will authenticate to the AML workspace using an AAD service principal.  The powershell commands below will create a new service principal and print out the object ID, client ID, and secret.  Store these values as they will be needed in later steps.  Be sure to replace "ServicePrinicpalNameHere" with the name you want to use.  

```powershell
$sp = New-AzADServicePrincipal -DisplayName ServicePrincipalNameHere
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sp.Secret)
$UnsecureSecret = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

"secret: " + $UnsecureSecret
"object ID: " + $sp.Id
"client ID: " + $sp.ApplicationId
```

## 2.  Modify the ARM Template Parameters

Open and modify the Template/parameters.json file.

- **resourceNamePrefix**:  prefix to be used in naming the Azure resources deployed in the template.  Make it all lowercase and don't include hyphens or underscores as storage account resource don't allow it.
- **SP-objectID**:  object ID of the service principal created in the previous step
- **SP-clientID**:  client ID of the service principal created in the previous step
- **SP-secret**:  secret of the service principal created in the previous step


```powershell
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "resourceNamePrefix": {
            "value": ""
        },
        "SP-objectID": {
            "value": ""
        },        
        "SP-clientID": {
            "value": ""
        },
        "SP-secret": {
            "value": ""
        }
    }
}
```

## 3.  Deploy the ARM Template

Run the following powershell commands to connect authenticate to Azure, create a resource group for the deployment, and deploy the template.  Modify the resource group and region as needed.

```powershell
Connect-AzAccount
New-AzResourceGroup -Name sqlmartini -Location "eastus2"
New-AzResourceGroupDeployment -ResourceGroupName sqlmartini -TemplateFile template.json -TemplateParameterFile parameters.json
```

## 4.  Deploy Azure Functions

Publish the Azure Functions project to the Azure Function App created from the ARM template using VS Code.  

**Reference:**  https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-vs-code?pivots=programming-language-python#publish-the-project-to-azure

There are two Azure functions in the solution that execute the same code, but use different triggers.
- **amlComputeShutdown-Timer**:  triggered by a timer.  Configured for 10pm UTC.
- **amlComputeShutdown-HTTP**:  triggered by an HTTP request.

The functions use the AML Python SDK to authenticate to the AML workspace using the created service principal.  Azure Key Vault references are used in the Function App application settings to reference the secrets needed to authenticate with the service principal.  After authentication, the function loops through all Compute Instances in the AML workspace and shuts them down.

**Key Vault reference docs:**  https://docs.microsoft.com/en-us/azure/app-service/app-service-key-vault-references

## 5.  Test amlComputeShutdown-HTTP Function using Postman

From VS Code in the Azure: Functions area in the side bar, expand the new function app under your subscription. Expand Functions, right-click (Windows) or Ctrl + click (MacOS) on amlComputeShutdown-Timer, and then choose Copy function URL.  

Paste this URL into a new Postman GET request and hit send.  

Navigate to https://azureml.com and verify that the Compute Instance created in the ARM template is in a "Stopping" or "Stopped" state. Voila!
