import requests
import argparse
import json
import os

SOURCE_MAP = {
    ".py":"SOURCE",
    ".ipynb":"NOTEBOOK"
}


def define_auth(token):
    bearer = "Bearer {}".format(token)
    hdr = {"authorization": bearer}

    return hdr

def define_uri(location,verb):
    return "https://{}.azuredatabricks.net/api/2.0/workspace/{}".format(location, verb)

def download_notebook(source, destination, location, token, src_type = "SOURCE", direct_download = "true"):

    hdr = define_auth(token)
    uri = define_uri(location, 'export')


    params = {"path":source,
     "format":src_type,
     "direct_download": direct_download
     }

    r = requests.get(uri,
         headers = hdr,
         params = params     
    )

    print(r.status_code)
    if (r.status_code != 200):
        print(json.dumps(r.json(), indent=2))
        if r.json()["error_code"] == "RESOURCE_DOES_NOT_EXIST":
            raise FileNotFoundError("Resource does not exist in databricks.  Please verify your -s|--source")
    else:
        with open(destination, 'wb') as f:
            for chunk in r.iter_content(chunk_size = 1024):
                f.write(chunk)

    return r


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--location', help = "The location of your databricks cluster such as eastus2", required = True)
    parser.add_argument('-t', '--token', help = "The access token for your databricks workspace",required = True)
    parser.add_argument('-s', '--source', help = "The single file to download from databricks, including the leading /")
    parser.add_argument('-d', '--destination', help = "The local directory/file to download the databricks source file to")
    
    args = parser.parse_args()

    download_notebook(args.source, args.destination, args.location, args.token)

    print("Download complete")