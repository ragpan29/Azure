# Using Multiple Models

The input data is a set of restaurant reviews and whether the reviewer liked the restaurant.

You can download the data [here](https://www.kaggle.com/c/restaurant-reviews/data).  Credit to [Zenodia Charpy](https://github.com/Zenodia) for the model training.

This example pulls in multiple models and produces a dataframe like output containing the original data and multiple model predictions.

It does so by using sklearn's `joblib.dump` to store a dictionary of...

* "cv": CountVectorizer to convert the review to a set of features.
* "model": A list of (Name, TrainedModelObject).

The `run` function extracts the `CountVectorizer`, applies it to the input dataframe.

Next we loop through the list of models and collect the predictions into an output data frame.

Follow the instructions in the `modelmgmt` parent folder.