from pyspark.sql.types import StringType, StructField, StructType

import os
# Initialize the deployment environment
def init():
    import pyspark
    from pyspark.ml import PipelineModel

    global spark
    global loadedpipe
    
    spark = pyspark.sql.SparkSession.builder.appName("TextPrediction").getOrCreate()
    

    loadedpipe = PipelineModel.load('predict_abstracts.model')
    
# Run the model and return the scored result.    
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

if __name__=="__main__":
    print("This score file is only used on the cluster.")