#!/usr/bin/env python
import os
import argparse
from sklearn import linear_model
import pandas as pd
import azure.storage.blob as azureblob


if __name__ == "__main__":    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', help = "The location of the input file", required = True)
    parser.add_argument('--storageaccount', required=True,
                        help='The name the Azure Storage account that owns the blob storage container to which to upload results.')
    parser.add_argument('--storagecontainer', required=True,
                        help='The Azure Blob storage container')
    parser.add_argument('--key', required=True,
                        help='The access key providing write access to the Storage container.')
    args = parser.parse_args()

    df = pd.read_csv(args.inputfile)
    features = ["UnitPrice"]

    # Fit the model using sklearn's LinearRegression()
    X = df.loc[:,features]
    Y = df.loc[:,["Quantity"]]
    lm = linear_model.LinearRegression()
    mod = lm.fit(X,Y)

    # Write the file to the local filesystem    
    output_file = "{}_MODEL_INFO.txt".format(os.path.splitext(args.inputfile)[0])

    with open(output_file, 'w') as out:
        out.write("Model Information for {}\n".format(args.inputfile))
        for feat, coef in zip(features, mod.coef_):
            out.write("{} {}\n".format(feat, coef))
    
    # Write the file to Blob storage for later analysis and processing
    output_file_path = os.path.realpath(output_file)

    blob_client = azureblob.BlockBlobService(account_name=args.storageaccount, account_key=args.key)

    blob_client.create_blob_from_path(args.storagecontainer,output_file,output_file_path)

