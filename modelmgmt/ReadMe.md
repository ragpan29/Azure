# Model Management

## Setup

* Install Docker on your machine
* Add a Machine Learning Experimentation Account
* Add the Model Management Account during the Experimentation Account setup.
* Install [ML Workbench](https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-installation#install-and-log-in-to-workbench)
* Add a project to your default workspace in the workbench.

## Training a Model

* Using the ML Workbench to train a model...
* Train an sklearn model and pickle it to an **./outputs** folder.
 * [OPTIONAL] You can train the model on a DSVM via a [remote docker container](https://docs.microsoft.com/en-us/azure/machine-learning/desktop-workbench/tutorial-classifying-iris-part-2#run-scripts-in-a-remote-docker-container).



       az ml computetarget attach remotedocker --name myvm --address <your-IP> --username <your-username> --password <your-password>
       az ml experiment prepare -c myvm


 * Modify the aml_config `myvm.runconfig` to `Framework: Python`
 * Submit the experiment with

       az ml experiment submit -c myvm model_train.py

## Deploying a Model

* In the ML Workbench command line or powershell window.
* Enable the Container Registry and Machine Learning Compute in your command line tool so that you can send commands to create a container registry.

      az provider register --namespace Microsoft.ContainerRegistry 
      az provider register -n Microsoft.MachineLearningCompute
      az provider show -n Microsoft.ContainerRegistry 

### Local Environment Setup

Before you deploy to your Container Service, you can deploy it a local Docker instance.

On the command line, you'll need to...
* Setup an environment (keep it local by not using the `--cluster` switch).
* Set the environment.
* Set the model management account.

       az ml env setup -n <new deployment environment name> --location <e.g. eastus2> -g <resource group name>
       az ml env set -n <deployment environment name> -g <existing resource group name>
       az ml account modelmanagement set -n <youracctname> -g <yourresourcegroupname>

* Update the dependencies in the `aml_config/conda_dependencies.yml`
 * For example, adding Scikit-Learn

### Local Model Deployment

* Create the docker manifest and image.  While in local mode, it will pull the image down to your local docker.
 * Note that this script, in non-cluster mode, will create a manifest and image but not a service.
 * The service is only visible in the portal when the terminal is set to a cluster environment.

       az ml service create realtime -f score.py --model-file model.pkl -s service_schema.json -n <model name> -r python -c aml_config\conda_dependencies.yml

* If something goes wrong, you can use this command to read the logs for any errors.

      az ml service logs realtime -i <model name>

* You can query your model by calling...
 * Using the dataframe data structure, you can pass mutlipe rows as separate 

       az ml service run realtime -i <model name> -d "{\"input_df\": [{\"column1\": value, \"columnN\": valueN},{\"column1\": valueX, \"columnN\": valueY}]}"

* If there was an error with pulling the service to your local docker, you can try creating the service again.
 * Run `az ml image list` to list the available image ids.
 * Run the `az ml service create` command to trigger the service to be created / downloaded.

       az ml image list
       az ml service create realtime --image-id <image ID> -n <model service name>

### Cluster Environment Setup

* Once you're ready to deploy for real, you'd create a cluster environment using the `--cluster` switch.
* This will create another resource group that contains your ACS VMs, NICs, VNET, Load Balance, Availability Set, App Insights, and Container Service.

        az ml env setup -n <new Cloud deployment env name> --location <e.g. eastus2>  -g <resource group name> --cluster
        az ml env set -n <Cloud deployment env name> -g <existing resource group name>

### Cloud Model Deployment

* You've already done the work of creating the image, so you need only to get the model image you want to deploy.

      az ml image list
      az ml service create realtime --image-id <image ID> -n <model service name>

 * When the model is deployed, you can use rest api calls.  This example script can be used to call the URL using a key.  Both are provided in the portal or the key can be found via calling `az ml service list realtime` to get the service id and then calling `az ml service keys realtime -i <service id>`.

       import requests
       import json
       import argparse

       if __name__ == "__main__":
           parser = argparse.ArgumentParser()
           parser.add_argument("-u","--url", required=True)
           parser.add_argument("-k","--key", required=True)
           args = parser.parse_args()

           # This is an example dataframe defined in a dictionary and turned into a json string
           data = {"input_df": [{"x1": 10, "x2": 3}]}
           body = str.encode(json.dumps(data))

           headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ args.key)}

           resp = requests.post(args.url, body, headers=headers)
           print(json.loads(resp.json()))

* Alternatively, you can call the `az ml service run realtime` on the command line with the model id.

      az ml service run realtime -i <model id> -d "{\"input_df\": [{\"column\": value}]}"