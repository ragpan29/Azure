# Training a Spark Model on Databricks and Deploying with Machine Learning Model Management

## Setting up your environment

1. Create a resource group to store these new resources for this project.
1. Create a **Blob Storage account** in your resource group.
1. Create a blob container that will house the data and model results.
1. Download and install the **[ML Workbench](https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-installation#install-and-log-in-to-workbench)**.
1. Create a **Machine Learning Experimentation Account** in your resource group.
1. During that process, create a **Machine Learning Model Management** resource.
1. Download the [NSF Research Award Abstracts 1990-2003 Data Set](https://archive.ics.uci.edu/ml/datasets/NSF+Research+Award+Abstracts+1990-2003)
   * At the very least, download the Part1 zip file.
   * Unzip the files.
   * Upload the uncompressed files to your blob storage container.
1. Create a **Databricks Workspace**.
1. Create a small Databricks cluster running at least the **4.0 Databricks Runtime**.
   * This cluster will only be used *once* to [mount the blob storage account](https://docs.azuredatabricks.net/spark/latest/data-sources/azure/azure-storage.html#mount-azure-blob-storage-containers-with-dbfs) to the workspace.
1. Create your training cluster running a **Spark version less than 2.3.0**.
   * We need Spark less than 2.3.0 because the Linear Regression algorithm added a new parameter in 2.3.0 ([epsilon](https://spark.apache.org/docs/latest/api/python/pyspark.ml.html#pyspark.ml.regression.LinearRegression.setEpsilon)).
   * This appears to break some backward compatibility with older Spark runtimes.
1. Create a Library in Databricks that installs the `azure-ml-api-sdk` PyPi package on your **training cluster**.


## Setting up Model Management

In order to use Model Management, you need to use the Command Prompt and the `az ml cli` in the ML Workbench.

1. Open the ML Workbench.
1. Create a new project in your workspace.
1. File >> Open Command Prompt
1. Run the following commands to enable you to send instructions to services we will use.

    az provider register --namespace Microsoft.ContainerRegistry 
    az provider register -n Microsoft.MachineLearningCompute

## Creating a cluster for deployments

This section describes how to deploy an Azure Container Registry which will house our machine learning web services.

In the ML Workbench command prompt for your project, run the following commands.  The cluster creation can take around 20 minutes.

    az ml account modelmanagement set -n <model mgmt acct name created already> -g <original resource group name>
    az ml env setup -n <deployment environment name> --location <e.g. eastus2> -g <new resource group name> --cluster
    az ml env set -n <deployment environment name> -g <new resource group name>

## Training your model

The `train_on_dbr.py` script can be uploaded to your Databricks workspace as a notebook.  Inside, it contains a call to mount your blob storage account to your workspace.  Secondly, it trains a linear regression model on one section of the training data you have stored in the storage account.

Because **mounting only works on Databricks Runtime 4.0+** be sure to first run that one cell on a 4.0+ cluster.

After mounting, you can attach the notebook to your training cluster that is running with Spark less than 2.3.0.  Then train your model and it will save the pipeline to your blob storage account under `models/predict_abstracts.model`.

## Downloading your model to local filesystem

In order to deploy the model, you'll need it on your local harddrive in your ML Workbench project folder.  One of the challenges is that Databricsk / Spark writes out each folder as a zero byte file.  Windows doesn't like that.  A few workaround are...

* Download the predict_abstracts.model "folder" via the Azure Storage Explorer tool.  Verify that all files are there manually.
* Run the `download_blobs.py` file in this project and specify the credentials and storage path.

  * I had the best luck with running this script on a DSVM and then making a tarball with `tar xvf models/predict_abstracts.model`.
  * Then uploading / downloading the tarball from blob to my windows machine.

For the latter, you'll need to `pip install azure-storage-blob` to use `from azure.storage.blob`.

## Deploying your model

Using this one line command, you will create a manifest, image, and web service in your set model management account.  This command must also be ran in the ML workbench command prompt.  Please note that the `score.py`, `predict_abstracts.model`, and `service_schema.json` must all be at the top level of the project folder for the command to work properly.  Secondly, the folder `aml_config` must also be at the root of the project folder.

    az ml service create realtime -f score.py --model-file predict_abstracts.model -s service_schema.json -n <model name> -r spark-py -c aml_config\conda_dependencies.yml
    
When the service creation completes successfully, you'll see an `az ml` command to test your model based on the example you provided in `generate_schema_on_dbr.py`.  In addition, you can make REST API calls.  See `api_call_example.py`.  The URL and Key can be found in the Azure Portal under the Model Management resource.
