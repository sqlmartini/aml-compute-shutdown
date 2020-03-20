import os
import logging
import azure.functions as func

#Azure ML
import azureml.core
from azureml.core import Workspace
from azureml.core.compute import ComputeTarget
from azureml.core.authentication import ServicePrincipalAuthentication

def shutdownComputeInstances():

    #Get service principal details from app settings
    subscriptionID = os.environ["subscriptionID"]
    tenantID = os.environ["tenantID"]
    clientID = os.environ["clientID"]
    spSecret = os.environ["secret"]

    #Authenticate to AML workspace with service principal
    auth = ServicePrincipalAuthentication(
        tenant_id = tenantID,
        service_principal_id = clientID,
        service_principal_password = spSecret)

    ws = Workspace(subscription_id = subscriptionID,
                resource_group = "azureml",
                workspace_name = "azureml",
                auth = auth)

    #Loop through workspace compute, stop all compute instances
    computeList = ComputeTarget.list(ws)
    for compute in computeList:
        if compute.type == 'ComputeInstance':
            logging.info("stop compute instance")
            compute.stop()


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    shutdownComputeInstances()

    return func.HttpResponse(status_code=200)
