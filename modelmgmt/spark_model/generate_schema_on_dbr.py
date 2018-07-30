# Databricks notebook source
# MAGIC %md
# MAGIC ### Generate the Schema
# MAGIC When generating the schema, you need to make sure you have the `azure-ml-api-sdk` PyPi library installed.
# MAGIC This library is reference by the `azureml.api` imports in the second cell.

# COMMAND ----------
from pyspark.ml import PipelineModel
global loadedpipe

loadedpipe = PipelineModel.load('mnt/misc/models/predict_abstracts.model')

# COMMAND ----------

from azureml.api.schema.dataTypes import DataTypes
from azureml.api.schema.sampleDefinition import SampleDefinition
from azureml.api.realtime.services import generate_schema
from pyspark.sql.types import StringType, StructField, StructType
import json

# COMMAND ----------

# Run the model and return the scored result.    
# This function is duplicated from the `score.py` file held locally.
# The local version will be pushed to Azure Model Management.
# This Databricks copy will be used by the `azure-ml-api-sdk` package to create the schema for the Swagger API documentation.
def run(input_df):
    import json
    from pyspark.sql.functions import lit
    
    try:
        # Append the label column due to the SQLTransformer in the pipeline.
        input_df_lit = input_df.withColumn("amt",lit(0))
        # Get prediction results for the dataframe
        score = loadedpipe.transform(input_df_lit)
        predictions = score.collect()

        #Get each scored result in a dictionary
        preds = {idx:val for idx,val in enumerate([r.prediction for r in predictions])}
    except Exception as e:
        print("Error: {0}",str(e))
        return (str(e))
    
    # Return results as json string
    return json.dumps(preds)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Test the run function before generating schema
# MAGIC 
# MAGIC Set up some fake data as an example.

# COMMAND ----------

input_features = ["abstract"]
sch = StructType([StructField("abstract", StringType())])
input_df = spark.createDataFrame([["this grant will provide funding for biostatistics and neuroscience"],["this is an example abstract"]],schema= sch)

print(run(input_df))
# COMMAND ----------

# MAGIC %md
# MAGIC ### Write the Schema to Blob

# COMMAND ----------

# define the input data frame
inputs = {"input_df": SampleDefinition(DataTypes.SPARK, input_df.select(input_features))}

# The Generate_Schema will attempt to write the file to the databricks cluster.
# But we will take the results and write it to our blob storage account defined in the `train_on_dbr.py` file.
json_schema = generate_schema(run_func=run, inputs=inputs, filepath='service_schema.json')
with open("/dbfs/mnt/misc/service_schema.json", 'w') as f:
  f.write(json.dumps(json_schema))

# COMMAND ----------

# Take a look at the schema
print(json.dumps(json_schema,indent=2))