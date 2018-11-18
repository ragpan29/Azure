from app import appvar
from azure.storage.blob import BlockBlobService
from util.comptuer_vision import ocr_image
from mgmt.search_add_to_index import add_to_index
from mgmt.search_mgmt import create_index
import base64
import json
import os

# Add Search Index
print("Working on creating index")
create_index()
print("Created index")

# For every image in the ocr images raw, run ocr on it
# Take the data and append to the index
blob_service = BlockBlobService(account_name= appvar.config["BLOB_ACCT_NAME"], account_key= appvar.config["BLOB_KEY"])

all_images = blob_service.list_blobs(container_name = appvar.config["BLOB_OCR_RAW_CONTAINER"])

for img_blob in all_images:
    print(img_blob.name)
    blob_url = blob_service.make_blob_url(container_name = appvar.config["BLOB_OCR_RAW_CONTAINER"] , 
        blob_name = img_blob.name, sas_token=appvar.config["BLOB_SAS"])
    
    results = ocr_image(img_url=blob_url, from_lang="en", mode="Handwritten")
    # Using the file path as the id won't work for some strings
    # Base64 encode can be used for the ID field
    encoded = base64.b64encode(img_blob.name.encode())

    output = {
        "id": encoded.decode(),
        "filepath": img_blob.name,
        "content":results,
        "entities":[],
        "parentDoc":None,
        "pageNum": None,
        "docType":"Handwritten"
    }
    with open("./data/{}.json".format(encoded.decode()), 'w') as f:
        json.dump(output, f)
        print("Successfully written")

# Add to the index
files_to_index = [os.path.join("./data", f) for f in os.listdir("./data")]

add_to_index(files_to_index)

print("Success!")
