# This script generates the schema when ran directly.
# You will send the score.py file up to Azure and it will run...
# init() and run() whenever you call the models web service
from azureml.api.schema.dataTypes import DataTypes
from azureml.api.schema.sampleDefinition import SampleDefinition
from azureml.api.realtime.services import generate_schema
import pandas
import os

# Loads the model object to the global namespace
def init():
    from sklearn.externals import joblib

    # load the model file
    global model
    model = joblib.load('model_object_dict.pkl')
    print("Made it here")
    print(len(model))
    print(model.keys())
    print(model.values())

# This function does the actual scoring and
# will be used in the web service
def run(input_df):
    # Add any data processing being done to the input data here
    transformed_text = model["cv"].transform(input_df.Review).toarray()
    df_out = pandas.DataFrame({"Review":input_df.Review.values})
    for model_name, modelObj in model["models"]:
        df_out[model_name+"_pred"] = modelObj.predict(transformed_text)
    return df_out.to_json()

def main():
    # This is used to define the schema and example
    df = pandas.DataFrame(data=[["That was a good meal"], ["What poor service"]],columns=["Review"])
    print("Initializing")
    init()
    print("After Init")
    print(len(model))

    results = run(df)

    print(results)

    print(df)

    inputs = {"input_df": SampleDefinition(DataTypes.PANDAS, df)}
    # The prepare statement writes the scoring file (main.py) and
    # the scchema file (service_schema.json) the the output folder.
    #prepare(run_func=run, init_func=init, input_types=inputs, )
    generate_schema(run_func=run, inputs=inputs, filepath='./outputs/service_schema.json')

    print("Schema generated")

if __name__ == "__main__":
    main()