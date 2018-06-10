# Example Azure Batch to Build Models in Parallel

Using Azure Batch, you can train models in parallel on different sets of training data.  In this toy example, I create multiple linear models based on store transaction data split by country.  So each **country** would receive its own unique model.

This example uses Pandas and SKLearn for the simple modeling.

The majority of the `batch_controls.py` content comes from the excellent [Azure Batch Python tutorial](https://docs.microsoft.com/en-us/azure/batch/quick-run-python).

In order to run this example, you will need...
* pip install the requirements file: `python -m pip install -r requirements.txt`
* Create a blob storage account and containers (input, output).
* Upload the data files to that container.
* Create a batch resource via the [portal](https://docs.microsoft.com/en-us/azure/batch/quick-create-portal).
* The `main.py` script will create a pool and job based on your config file.
  * The `make_lm.py` application requires a Linux DSVM as it has the packages required pre-installed.
  * If you want, you can create a [pool and job](https://docs.microsoft.com/en-us/azure/batch/quick-create-portal#create-a-pool-of-compute-nodes) via the portal.
* Zip the make_lm.py file and [upload it as an application](https://docs.microsoft.com/en-us/azure/batch/batch-application-packages#upload-and-manage-applications).
* Update the batch_config.json file to reflect your unique details.
* Run the `main.py` file.
* Examine the output stored in your output container.