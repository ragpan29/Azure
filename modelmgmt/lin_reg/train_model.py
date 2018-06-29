from sklearn.linear_model import LinearRegression
import pandas as pd
import pickle

# Generate some data
independent_df = pd.DataFrame({"x1":[1,2,3,4,5,6],"x2":[2,1,2,0,1,2]})
dependent_df = pd.DataFrame({"y":[4,5,8,8,11,14]})

model = LinearRegression()

model.fit(independent_df, dependent_df)
scores = model.predict(independent_df)

print(scores)

# Needs to be sent to the outputs folder for the workbench to see it
# And make it available for "download" to your file system.
with open('./outputs/model.pkl', 'wb') as f:
    pickle.dump(model, f)
