import sys, os
sys.path.append(os.getcwd())

import requests
from app import appvar
import json
from util.common import pretty_print_POST
from util.search import search_header, search_url


def create_index():
    with open("./mgmt/python-files-index.json") as schema_path:
        index_schema = json.load(schema_path)
        index_schema.update({"name": appvar.config["SEARCH_INDEX_NAME"]})

    index_url = search_url()

    put_results = requests.put(index_url, headers=search_header(), data = json.dumps(index_schema))

    try:
        put_results.raise_for_status()
    except requests.exceptions.HTTPError as httperr:
        pretty_print_POST(put_results.request)
        raise httperr
    finally:
        print( json.dumps(put_results.json(), indent= 2) )