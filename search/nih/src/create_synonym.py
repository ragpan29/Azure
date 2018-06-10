import json
import requests
import config


URL = 'https://{}.search.windows.net/synonymmaps?api-version={}'


KEY = config.config["KEY"]
service = config.config["service_name"]
API = config.config["API"]

URL = URL.format(service,API)

headers = {'content-type': 'application/json', 'api-key': KEY}

json_dict = dict()

json_dict["name"] = 'bio-terms'
json_dict["format"] = 'solr'
with open('./src/synonym.txt','r') as syn_file:
    syns = syn_file.read()

print(syns)

json_dict["synonyms"] = syns


post_value = requests.post(URL, headers=headers, data = json.dumps(json_dict))
if post_value.status_code == 400:
    print("Synonym map already exists.  Trying an update")
    PUT_URL = 'https://{}.search.windows.net/synonymmaps/{}?api-version={}'.format(service,json_dict["name"], API)
    print(PUT_URL)
    del json_dict["name"]
    put_value = requests.put(PUT_URL, headers=headers, data = json.dumps(json_dict))
    if put_value.status_code == 204:
        print("Successfully updated")
    else:
        print('Status Code: {}'.format(put_value.status_code))
        print(json.dumps(put_value.json(),indent=2))
else:
    print('Status Code: {}'.format(post_value.status_code))
    print(json.dumps(post_value.json(),indent=2))