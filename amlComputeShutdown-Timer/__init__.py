import os
import datetime
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
    resourceGroupName = os.environ["resourceGroupName"]
    amlWorkspaceName = os.environ["amlWorkspaceName"]    

    #Authenticate to AML workspace with service principal
    auth = ServicePrincipalAuthentication(
        tenant_id = tenantID,
        service_principal_id = clientID,
        service_principal_password = spSecret)

    ws = Workspace(subscription_id = subscriptionID,
                resource_group = resourceGroupName,
                workspace_name = amlWorkspaceName,
                auth = auth)

    #Loop through workspace compute, stop all compute instances
    computeList = ComputeTarget.list(ws)
    for compute in computeList:
        #Filter compute to only compute instances
        if compute.type == 'ComputeInstance':
            logging.info("stop compute instance")
            compute.stop()


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')
        shutdownComputeInstances()

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

