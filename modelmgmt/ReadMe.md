# Model Management

## Setup

* Install Docker on your machine
* Add a Machine Learning Experimentation Account
* Add the Model Management Account during the Experimentation Account setup.
* Install ML Workbench
* Add a project to your default workspace

## Training a Model

* Using the ML Workbench to train a model...
* Train an sklearn model and pickle it to an **./outputs** folder.
 * You can train the model on a DSVM via a (remote docker container)[https://docs.microsoft.com/en-us/azure/machine-learning/desktop-workbench/tutorial-classifying-iris-part-2#run-scripts-in-a-remote-docker-container].


    az ml computetarget attach remotedocker --name myvm --address <your-IP> --username <your-username> --password <your-password>
    az ml experiment prepare -c myvm

 * Modify the aml_config `myvm.runconfig` to `Framework: Python`
 * Submit the experiment with

    az ml experiment submit -c myvm model_train.py

## Deploying a Model

* In the ML Workbench command line or powershell window.
* Enable the Container Registry in your command line tool so that you can send commands to create a container registry.

    az provider register --namespace Microsoft.ContainerRegistry 
    az provider register -n Microsoft.MachineLearningCompute
    az provider show -n Microsoft.ContainerRegistry 

* Create an environment where the model will be deployed to.
 * For testing purposes, you can setup a local docker installation.
 * This will create two resource groups
 * One will be empty and one hold your Container Registry

    az ml env setup -n <new deployment environment name> --location <e.g. eastus2> -g <resource group name>

 * Once you're ready to deploy for real, you'd create a cluster environment using the `--cluster` switch.
  * This will create another resource group that contains your ACS VMs, NICs, VNET, Load Balance, Availability Set, App Insights, and Container Service.

    az ml env setup -n <new deployment environment name> --location <e.g. eastus2>  -g <resource group name> --cluster

* You'll also set the environment for deployment

    az ml env set -n <deployment environment name> -g <existing resource group name>

* Set the model management account so that the deployed model is associate to that account.

    az ml account modelmanagement set -n <youracctname> -g <yourresourcegroupname>

* Update the dependencies in the `aml_config/conda_dependencies.yml`
 * For example, adding Scikit-Learn

* Create the web service

    az ml service create realtime -f score.py --model-file model.pkl -s service_schema.json -n <model name> -r python -c aml_config\conda_dependencies.yml

* If something goes wrong, you can use this command to read the logs for any errors.

    az ml service logs realtime -i <model name>

* You can query your model by calling...
 * Using the dataframe data structure, you can pass mutlipe rows as separate 

    az ml service run realtime -i <model name> -d "{\"input_df\": [{\"column1\": value, \"columnN\": valueN},{\"column1\": valueX, \"columnN\": valueY}]}"

 * Using rest api calls

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