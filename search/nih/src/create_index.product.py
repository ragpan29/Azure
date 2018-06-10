import requests
import json
import config

URL = 'https://{}.search.windows.net'.format(config.config["service_name"])
KEY = config.config["KEY"]
INDEX_NAME = 'product-data'

API = config.config["API"]
headers = {'content-type': 'application/json', 'api-key': KEY}

index_url = ''.join([URL, '/indexes/',INDEX_NAME,'?api-version=',API])

azure_index = dict()
azure_index["name"] = INDEX_NAME

# retrievable is default to true
# searchable is default to true (index the content)
azure_index["fields"] = [
    {"name": "productid", "type":"Edm.String", "key":True, "searchable":True, "retrievable":True},
    {"name": "productname", "type": "Edm.String", "sortable": True,  "analyzer": "en.Microsoft"},
    {"name": "producttagline", "type": "Edm.String", "sortable": True, "analyzer": "en.Microsoft"},
    {"name": "productdetails", "type": "Edm.String", "analyzer": "en.Microsoft"}
]

drop = requests.delete(index_url, headers=headers)

print(drop.status_code)
print(drop.content)

json_index = json.dumps(azure_index, ensure_ascii=False,indent=2)

index_check = requests.get(index_url, headers=headers)

if index_check.status_code == 200:
    print("Index does exist, time to UPDATE it")
    print(json.dumps(index_check.json(),indent=2))

    #put_index = requests.put(index_url, headers=headers, data = json_index)
    #print(put_index.status_code)
    #print(put_index.content)
    #print(json.dumps(put_index.json(),indent=2))
else:
    print("Index doesn't exist yet, time to MAKE it")
    put_index = requests.put(index_url, headers=headers, data = json_index)
    print(put_index.status_code)
    print(json.dumps(put_index.json(),indent=2))

