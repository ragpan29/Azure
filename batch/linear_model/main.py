import os
import datetime
import sys
import time
import json
import uuid

import azure.storage.blob as azureblob
import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batchauth
import azure.batch.models as batchmodels

from batch_controls import *

with open("./batch/batch_config.json",'r') as conf:
    config = json.load(conf)

# Update the Batch and Storage account credential strings below with the values
# unique to your accounts. These are used when constructing connection strings
# for the Batch and Storage client objects.

# Batch account credentials
_BATCH_ACCOUNT_NAME = config["_BATCH_ACCOUNT_NAME"]
_BATCH_ACCOUNT_KEY = config["_BATCH_ACCOUNT_KEY"]
_BATCH_ACCOUNT_URL = config["_BATCH_ACCOUNT_URL"]

# Storage account credentials
_STORAGE_ACCOUNT_NAME = config["_STORAGE_ACCOUNT_NAME"]
_APP_STORAGE_CONTAINER = config["_APP_STORAGE_CONTAINER"]
_INPUT_STORAGE_CONTAINER = config["_INPUT_STORAGE_CONTAINER"]
_OUTPUT_STORAGE_CONTAINER = config["_OUTPUT_STORAGE_CONTAINER"]
_STORAGE_ACCOUNT_KEY = config["_STORAGE_ACCOUNT_KEY"]

# Set up pool and app information
_POOL_ID = config["_POOL_ID"]
_JOB_ID = config["_JOB_ID"]

_APP_NAME = config["_APP_NAME"]
_APP_VERSION = config["_APP_VERSION"]
_APP_FILE = config["_APP_FILE"]

_VM_PUBLISHER = config["vm_publisher"].lower()
_VM_OFFER = config["vm_offer"].lower()
_VM_SKU = config["vm_sku"].lower()
_POOL_VM_SIZE = config["_POOL_VM_SIZE"]
_POOL_NODE_COUNT = config["_POOL_NODE_COUNT"]

_EXPECTED_MODEL_RUN_IN_MINUTES = config["_EXPECTED_MODEL_RUN_IN_MINUTES"]

_FILE_PATTERN = config["_FILE_PATTERN"]


if __name__ == '__main__':

    # Create the blob client, for use in obtaining references to
    # blob storage containers and uploading files to containers.
    blob_client = azureblob.BlockBlobService(
        account_name=_STORAGE_ACCOUNT_NAME,
        account_key=_STORAGE_ACCOUNT_KEY)

    credentials = batchauth.SharedKeyCredentials(_BATCH_ACCOUNT_NAME,_BATCH_ACCOUNT_KEY)
    batch_client = batch.BatchServiceClient(credentials,base_url=_BATCH_ACCOUNT_URL)
    
    # Create a pool based on configurate
    try:
        create_pool(batch_client, _POOL_ID, None,_VM_PUBLISHER,_VM_OFFER, _VM_SKU,_POOL_VM_SIZE,_POOL_NODE_COUNT)
    except batchmodels.BatchErrorException as err:
        if err.error.code != "PoolExists":
            raise
        else:
            print("Pool already exists.  Continuing with existing pool.")


    # Creating a Job
    job = batch.models.JobAddParameter(
        id = _JOB_ID,
        pool_info = batch.models.PoolInformation(pool_id=_POOL_ID)
    )
    
    try:
        batch_client.job.add(job)
    except batchmodels.BatchErrorException as err:
        if err.error.code != "JobExists":
            print(err)
            raise
        else:
            print("Job already exists.  Continuing with existing job name.")

    # List all the input files in the given container that start with the _FILE_PATTERN.
    # The listing of files includes the full path (e.g. /My/Path/To/File.txt rather than File.txt)
    # Convert those inputs to "Resource File" objects from the batch models package.
    input_files = [
        create_resource_file_from_blob(blob_client, _INPUT_STORAGE_CONTAINER, str(blob.name)) 
        for blob in blob_client.list_blobs(_INPUT_STORAGE_CONTAINER) 
        if str(blob.name).startswith(_FILE_PATTERN)
    ]

    print("There are {} files to be analyzed".format(len(input_files)))

    # Adding a Task
    # Referencing the AZ_BATCH_APP_PACKAGE path to get access to the application loaded via the portal.
    # Everything after the reference to the App file is custom to the app file itself.
    tasks = list()
    for idx, input_file in enumerate(input_files):
        command = ['python3 $AZ_BATCH_APP_PACKAGE{}/{} -i {} --storageaccount {} --storagecontainer {} --key {}'.format(
            app_rename_rules(_APP_NAME,_APP_VERSION),
            _APP_FILE,
            input_file.file_path,
            _STORAGE_ACCOUNT_NAME,
            _OUTPUT_STORAGE_CONTAINER,
            _STORAGE_ACCOUNT_KEY)]

        # Appending the tasks with a random identifier (uuid4).
        tasks.append(
            batch.models.TaskAddParameter(
                id = 'make_lm{}'.format(uuid.uuid4()),
                command_line = wrap_commands_in_shell('linux',command),
                resource_files=[input_file],
                # This part assumes you've uploaded an application package and have specified a default version
                application_package_references = [batchmodels.ApplicationPackageReference(_APP_NAME)]
            )
        )
    
    print("There are {} tasks created".format(len(tasks)))

    successfully_added_all_tasks = batch_client.task.add_collection(_JOB_ID, tasks)

    registered_tasks = batch_client.task.list(_JOB_ID)

    print("Starting to wait and pinging the service for job tracking")

    wait_for_tasks_to_complete(batch_client,
                               _JOB_ID,
                               datetime.timedelta(minutes=_EXPECTED_MODEL_RUN_IN_MINUTES)
                               )

    print("Success! All tasks reached the 'Completed' state within the specified timeout period.")