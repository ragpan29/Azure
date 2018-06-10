import requests
import json
import datetime
import os
import argparse
import config

# Set up for Adding to Index
URL = 'https://{}.search.windows.net'.format(config.config["service_name"])
KEY = config.config["KEY"]
INDEX_NAME = 'nih-data'
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
        json_dict = json.loads(content_in_json)
    
    print(len(json_dict["value"]))
    for idx, d in enumerate(json_dict["value"]):
        json_dict["value"][idx]["projectnumber"] = d["projectnumber"].replace("-","_").strip()
        if "Former Number" in json_dict["value"][idx]["projectnumber"]:
            del json_dict["value"][idx]
        else:
            print(json_dict["value"][idx]["projectnumber"])

    print(len(json_dict["value"]))


    post_value = requests.post(content_url, headers=headers, data = json.dumps(json_dict))

    print('Status Code: {}'.format(post_value.status_code))
    print(json.dumps(post_value.json(), indent=2))
