import sys, os
sys.path.append(os.getcwd())

import requests
from app import appvar
import json
from util.common import pretty_print_POST
from util.search import search_header, search_url


with open("./mgmt/python-files-index.json") as schema_path:
    index_schema = json.load(schema_path)

with open("./mgmt/python-data.json") as python_data_path:
    python_data = json.load(python_data_path)

# Add the @search.action to be upload for each dictionary in the list
for doc in python_data:
    doc.update({'@search.action': 'upload'})

content_url =  search_url(action = '/docs/index')


# TODO: Chunk it by 1,000 docs
post_results = requests.post(content_url, headers=search_header(), 
    data = json.dumps(
        {"value":python_data}
        )
)

try:
    post_results.raise_for_status()
except requests.exceptions.HTTPError as httperr:
    pretty_print_POST(post_results.request)

    print(json.dumps(post_results.json(), indent=2))
    raise httperr

print( json.dumps(post_results.json(), indent= 2) )
