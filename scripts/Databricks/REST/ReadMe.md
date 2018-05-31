# Working with Databricks REST API in Python

**Disclaimer**: The scripts in this folder are meant for illustration and do not have any guarantee or warranty.  Use at your own risk.

**Requirements**
* Python 3.5.2 or higher
* requests==2.18.4

## Creating a Basic Cluster

    python CreateorModifyCluster.py -c basic-cluster-config.json -t ACCESSTOKEN -l LOCATION

The basic-cluster-config.json looks like:

    {
    "cluster_name": "yet-another-cluster",
    "spark_version": "4.0.x-scala2.11",
    "node_type_id": "Standard_DS3_v2",
    "autoscale" : {
        "min_workers": 1,
        "max_workers": 2
        }
    }

### With a set of libraries

When you create a cluster, you might also want to add libraries to it.

    python CreateorModifyCluster.py -c basic-cluster-config.json -t ACCESSTOKEN -l LOCATION --libraries library-config-no-id.json

The library-config-no-id.json might look like the json below that installs two packages from pypi.

    {
    "libraries": [
        {
        "pypi": {
            "package": "azure-storage"
        }
        },
        {
        "pypi": {
            "package": "azure-batch"
        }
        }
    ]
    }


## Modifying a Cluster

Modifying an existing cluster is very similar.  These new changes won't go into effect until the cluster has been restarted.

    python CreateorModifyCluster.py -c modified-cluster-config.json -t ACCESSTOKEN -l LOCATION

The modified-cluster-config.json looks like:

    {
    "cluster_name": "yet-another-cluster",
    "spark_version": "4.0.x-scala2.11",
    "node_type_id": "Standard_DS3_v2",
    "autoscale" : {
        "min_workers": 10,
        "max_workers": 20
        }
    }

Behind the scenes, the cluster_id of "cluster_name" is looked up and appended to your JSON request.  **Databricks does not enforce unique names, but this script will only update the first cluster with the name inside the json**.  There is no guarantee on ordering, so **I would encourage you to keep cluster names unique.**

### With a set of libraries

If you want to modify and existing cluster and add new libraries to it, it gets tricker.  If the cluster is currently turned off, you need to turn it on and then install the libraries.  If a cluster is in a TERMINATED or TERMINATING state, the Databricks API won't be able to recognize a given cluster.  Depending on your release workflow, you may want to turn the cluster on, install the libraries, and then shut down the cluster.  The `--startup` and `--shutdown` command line switches will help in that situation.

        python CreateorModifyCluster.py -c modified-cluster-config.json -t ACCESSTOKEN -l LOCATION --libraries library-config-no-id.json --startup --shutdown


### Getting the resulting cluster id

You can use the `--id` switch to have the last line of output represent the cluster id.  You might use this cluster id for later consumption.  I would store the last line as a variable.

        clusterid=$(python CreateorModifyCluster.py -c basic-cluster-config.json -t ACCESSTOKEN -l LOCATION --id | tail -1)


## Installing Libraries

The CreateorModifyCluster module uses the InstallLibraries module but InstallLibraries can be used on its own.

    python InstallLibraries.py -c library-config-with-id.json -t ACCESSTOKEN -l LOCATION

The library-config-with-id.json file looks like:

    {
    "cluster_id": "TheUniqueClusterID",
    "libraries": [
        {
        "pypi": {
            "package": "azure-storage"
        }
        },
        {
        "pypi": {
            "package": "azure-batch"
        }
        }
    ]
    }

### Checking the Status of Installation

Another use for the InstallLibraries module is to quickly check the status of package installation.  The following command returns a JSON print-out to the screen of each package and their installation status.

    python InstallLibraries.py -c library-config-with-id.json -t ACCESSTOKEN -l LOCATION --status

Alternatively, if you don't have a JSON file you're just checking on, you can specify the ID itself.

    python InstallLibraries.py --id CLUSTERID -t ACCESSTOKEN -l LOCATION --status

## Creating Secrets

One option for making notebooks work across environments is to use Databricks secrets (currently in preview).

    python CreateSecrets-Preview.py --scope MySecrets -t ACCESSTOKEN -l LOCATION -p SecretName SecretValue -p Secret2 Value2

* Scope is a logical grouping of your secrets which can be tightly governed if needed.
* The -p (--pair) argument is the name of the secret and the value of the secret **in that order**.
* You can specify -p key value as many times as you'd like, for as many secrets as you need to create.

In Python, you can load secrets into a variables via the `dbutils.preview.secret.get` function.

```python
secret1 = dbutils.preview.secret.get(scope="MySecrets", key="SecretName")
secret2 = dbutils.preview.secret.get(scope="MySecrets", key="Secret2")
```

## Uploading Notebooks

The latest version works only for **python (.py) and IPython notebooks (.ipynb)** files.  You can upload either a single file or an entire directory of files.

### Upload a Single File

    python UploadNotebook.py -t ACCESSTOKEN -l LOCATION -f ExampleScript.py --clouddir "/MyScripts"

* This uploads ExampleScript.py to /MyScripts/ExampleScript

    python UploadNotebook.py -t ACCESSTOKEN -l LOCATION -f ExampleScript.py

* This uploads ExampleScript.py to /ExampleScript (a file at root)

### Upload a Directory of Files (and Mirror that Structure in Databricks)

    python UploadNotebook.py -t ACCESSTOKEN -l LOCATION --localdir ".\DataBricksFiles"

If `.\DataBricksFiles` follows this structure...

    DataBricksFiles/
    |--WeeklyJobs/
    |  |--Invoicing/
    |  |  |-- WeeklySummary
    |  |--Marketing/
    |     |-- CustomerMetrics
    |-- RootLevelJob

Then your Databricks workspace will look like...

    (root)/
    |--WeeklyJobs/
    |  |--Invoicing/
    |  |  |-- WeeklySummary
    |  |--Marketing/
    |     |-- CustomerMetrics
    |-- RootLevelJob

The folder you point it at will become the root in Databricks.

Note that if a folder doesn't exist in your workspace, one will be created.  If the uploaded notebook fails to upload, the folder may have already been created and will not be removed due to a failed upload.

## Downloading Notebooks

The latest version will download a Databricks Notebook as a Python file.  At this time, you can only download one file at a time, since Databricks forces you to use their DBC file format when downloading directories.

    python DownloadNotebook.py -t ACCESSTOKEN -l LOCATION --source "/My/Notebook/Path" --destination .\My\Notebook\Local\Destination

