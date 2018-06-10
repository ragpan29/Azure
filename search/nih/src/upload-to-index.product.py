import requests
import json
import datetime
import os
import argparse
import config

# Set up for Adding to Index
URL = 'https://{}.search.windows.net'.format(config.config["service_name"])
KEY = config.config["KEY"]
INDEX_NAME = 'product-data'
API = config.config["API"]
headers = {'content-type': 'application/json', 'api-key': KEY}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--filepath',help="Filepath containing file to upload")

    args=parser.parse_args()
    # Uploading to Index
    content_url = ''.join([URL, '/indexes/',INDEX_NAME,'/docs/index?api-version=',API])

    with open(args.filepath, 'r') as f:
        content_in_json = json.load(f)
        if isinstance(content_in_json,dict):
            json_dict = content_in_json
        else:
            json_dict = json.loads(content_in_json)
    
    print(len(json_dict["value"]))

    post_value = requests.post(content_url, headers=headers, data = json.dumps(json_dict))

    print('Status Code: {}'.format(post_value.status_code))
    print(json.dumps(post_value.json(), indent=2))
