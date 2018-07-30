import os
import argparse
from azure.storage.blob import BlockBlobService

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a","--account", help="Name of your blob storage account.")
    parser.add_argument("-k","--key", help="Storage key for your blob storage account.")
    parser.add_argument("-c","--container", help="Container name for your blob storage account.")
    parser.add_argument("-p","--pattern", help="Pattern to filter for your files to be downloaded.")

    args = parser.parse_args()

    ACCOUNT_NAME = args.account
    ACCOUNT_KEY = args.key
    CONTAINER_NAME = args.container
    PATTERN = args.pattern

    blob_service = BlockBlobService(account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)

    blob_names = blob_service.list_blobs(CONTAINER_NAME)

    blob_names = [blob.name for blob in blob_names if blob.name.startswith(PATTERN)]

    print("Working with {} blobs".format(len(blob_names)))

    for blob in blob_names:
        print("Working on...{}".format(blob))
        dest = os.path.join(os.getcwd(), blob)
        folder,file = os.path.split(dest)

        if not os.path.exists(folder):
            print("\tThe folders for {} did not exist.  Adding them.".format(blob))
            os.makedirs(folder)

        # Download the blob
        blob_service.get_blob_to_path(CONTAINER_NAME, blob, file_path = dest)
        # Validate that there is data there
        if os.path.getsize(dest) == 0:
            print("\tRemoved due to it being a zero byte file")
            os.remove(dest)