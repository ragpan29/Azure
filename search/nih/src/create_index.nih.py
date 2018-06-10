import requests
import json
import config

URL = 'https://{}.search.windows.net'.format(config.config["service_name"])
KEY = config.config["KEY"]
INDEX_NAME = 'nih-data'

API = config.config["API"]
headers = {'content-type': 'application/json', 'api-key': KEY}

index_url = ''.join([URL, '/indexes/',INDEX_NAME,'?api-version=',API])

azure_index = dict()
azure_index["name"] = INDEX_NAME

# retrievable is default to true
# searchable is default to true (index the content)
azure_index["fields"] = [
    {"name": "projectnumber", "type":"Edm.String", "key":True, "searchable":True, "retrievable":True},
    {"name": "projecttitle", "type": "Edm.String", "sortable": True},
    {"name": "awardeeorg", "type": "Edm.String", "sortable": True, "facetable":True},
    {"name": "projectleader", "type": "Edm.String", "filterable":True},
    {"name": "abstract", "type": "Edm.String", "analyzer": "en.Microsoft", "synonymMaps": ["bio-terms"]},
    {"name": "publichealth", "type": "Edm.String", "retrievable":False, "analyzer": "contentAnalyzer"},
    {"name": "terms", "type": "Edm.String","retrievable":False}
]

azure_index["analyzers"] = [
   {"name": "contentAnalyzer",
   "@odata.type": "#Microsoft.Azure.Search.CustomAnalyzer",
   "charFilters": [ "html_strip" ],
   "tokenizer": "standard_v2"}
]

azure_index["scoringProfiles"] = [
   {"name": "weightedTitleTerms",
   "text":{
       "weights":{"projecttitle":0.5, "abstract":100}
   }
   }
]

json_index = json.dumps(azure_index, ensure_ascii=False,indent=2)

index_check = requests.get(index_url, headers=headers)

if index_check.status_code == 200:
    print("Index does exist, time to UPDATE it")
    print(json.dumps(index_check.json(),indent=2))

    put_index = requests.put(index_url, headers=headers, data = json_index)
    print(put_index.status_code)
    print(put_index.content)

else:
    print("Index doesn't exist yet, time to MAKE it")
    put_index = requests.put(index_url, headers=headers, data = json_index)
    print(put_index.status_code)
    print(json.dumps(put_index.json(),indent=2))



