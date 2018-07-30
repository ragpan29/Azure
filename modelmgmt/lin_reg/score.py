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
    model = joblib.load('model.pkl')

# This function does the actual scoring and
# will be used in the web service
def run(input_df):
    import json
    # Add any data processing being done to the input data here
    pred = model.predict(input_df)
    return json.dumps(str(pred))

# Run this once to generate the scehma for the swagger API
# Gets uploaded with the deployment
def create_schema():
    # This is used to define the schema and example
    df = pandas.DataFrame(data=[[10,5]],columns=["x1","x2"])

    init()
    # This is used to execute the run to get the schema of the prediction
    input1 = pandas.DataFrame(data=[[10,5]])
    run(input1)

    print(os.getcwd())

    print(df)
    print(input1)

    inputs = {"input_df": SampleDefinition(DataTypes.PANDAS, df)}
    # The prepare statement writes the scoring file (main.py) and
    # the scchema file (service_schema.json) the the output folder.
    #prepare(run_func=run, init_func=init, input_types=inputs, )
    generate_schema(run_func=run, inputs=inputs, filepath='./outputs/service_schema.json')

    print("Schema generated")

if __name__ == "__main__":
    create_schema()