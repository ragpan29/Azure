import requests
import argparse
import json

# https://docs.azuredatabricks.net/api/latest/libraries.html#managedlibrarieslibrary

def define_auth(token):
    bearer = "Bearer {}".format(token)
    hdr = {"authorization": bearer}

    return hdr

def define_uri(location,noun,verb):
    return "https://{}.azuredatabricks.net/api/2.0/{}/{}".format(location,noun,verb)

def install_library_from_config(config_json, token, location, noun, verb):
    config_txt = json.dumps(config_json)
    hdr = define_auth(token)
    URI = define_uri(location, noun, verb)

    r = requests.post(URI, headers = hdr, data = config_txt)

    if r.status_code == 200:
        print("Successfully queued installation of libraries")
    elif r.status_code == 400:
        print("Make sure the cluster is either starting or running to install libraries.")
        print(json.dumps(r.json(), indent=2))

def check_status_from_id(cluster_id, token, location, noun, verb):
    hdr = define_auth(token)
    URI = define_uri(location, noun, verb)

    r = requests.get(URI, headers = hdr, params = {"cluster_id": cluster_id})

    print(json.dumps(r.json(),indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--location', help = "The location of your databricks cluster such as eastus2",required = True)
    parser.add_argument('-t', '--token', help = "The access token for your databricks workspace",required = True)
    parser.add_argument('-c', '--config', help = "The filepath of the JSON configuration file")
    parser.add_argument('--id', help = "The cluster id to be used in looking up the status")
    parser.add_argument('--status', help = "Look at the status of your installations for given configuration file", action='store_true')

    args = parser.parse_args()

    if args.config is not None:
        with open(args.config, 'r') as config_conn:
            config_json = json.load(config_conn)
    
    if args.status:
        cluster_id = None
        if args.id is not None:
            cluster_id = args.id
        else:
            cluster_id = config_json["cluster_id"]
        check_status_from_id(cluster_id, args.token, args.location, "libraries", "cluster-status")
    else:
        install_library_from_config(config_json, args.token, args.location,"libraries","install")
