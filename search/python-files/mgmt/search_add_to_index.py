import sys, os
sys.path.append(os.getcwd())

import requests
from app import appvar
import json
from util.common import pretty_print_POST
from util.search import search_header, search_url

def add_to_index(list_of_files):
    all_docs_list = []
    for filename in list_of_files:
        with open(filename, 'r') as f:
            doc = json.load(f)
            doc.update({'@search.action': 'upload'})
            all_docs_list.append(doc)

    content_url =  search_url(action = '/docs/index')
    post_results = requests.post(
        url = content_url, 
        headers=search_header(), 
        data = json.dumps({"value":all_docs_list})
    )

    try:
        post_results.raise_for_status()
    except requests.exceptions.HTTPError as httperr:
        pretty_print_POST(post_results.request)

        print(json.dumps(post_results.json(), indent=2))
        raise httperr

    print( json.dumps(post_results.json(), indent= 2) )
