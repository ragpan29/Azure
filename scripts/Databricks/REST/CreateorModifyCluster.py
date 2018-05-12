import requests
import argparse
import json
import time
import InstallLibraries as dbr_library

def define_auth(token):
    bearer = "Bearer {}".format(token)
    hdr = {"authorization": bearer}

    return hdr

def define_uri(location,verb):
    return "https://{}.azuredatabricks.net/api/2.0/clusters/{}".format(location,verb)

def manage_cluster(config_json, token, location, verb):
    config_txt = json.dumps(config_json)
    hdr = define_auth(token)
    URI = define_uri(location, verb)

    r = requests.post(URI, headers = hdr, data = config_txt)

    past_tense = "created"
    cluster_id = None
    if r.status_code == 200:
        if verb == "edit":
            past_tense = "modified"
            cluster_id = config_json["cluster_id"]
        else:
            cluster_id = r.json()["cluster_id"]
        print("Successfully {} the cluster with id {}".format(past_tense, cluster_id))
    
    else:
        print("There was an error during processing of the cluster:")
        print(r.status_code)
        print(r.reason)
        print(json.dumps(r.json()))
    
    return cluster_id

def start_delete_cluster(cluster_id, token, location, action):
    config_txt = json.dumps({"cluster_id":cluster_id})
    hdr = define_auth(token)
    URI = define_uri(location, action)

    r = requests.post(URI, headers = hdr, data = config_txt)
    if r.status_code == 200:
        print("Successful {} of cluster {}".format(action, cluster_id))
    else:
        print("There was an error during processing of the cluster:")
        print(r.status_code)
        print(r.reason)
        print(json.dumps(r.json(), indent=2))


def start_cluster(cluster_id, token, location):
   start_delete_cluster(cluster_id, token, location, "start")
   

def delete_cluster(cluster_id, token, location):
   start_delete_cluster(cluster_id, token, location, "delete")


def list_cluster(token, location):
    hdr = define_auth(token)
    URI = define_uri(location,"list")

    r = requests.get(URI, headers = hdr)

    return r.json()["clusters"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--location', help = "The location of your databricks cluster such as eastus2",required = True)
    parser.add_argument('-t', '--token', help = "The access token for your databricks workspace",required = True)
    parser.add_argument('-c', '--config', help = "The filepath of the JSON configuration file", required = True)
    parser.add_argument('--libraries', help = "The filepath to the json containing the libraries to install")
    parser.add_argument('--startup', help="Start the cluster after modification (starts automatically when created). Required for libary modification", action="store_true")
    parser.add_argument('--shutdown', help="Shut down the cluster after library installation.", action="store_true")

    args = parser.parse_args()

    with open(args.config, 'r') as config_conn:
        config_json = json.load(config_conn)
    
    clusters = list_cluster(args.token, args.location)
    print("Checking for existence of cluster across {} clusters".format(len(clusters)))

    action = "create"
    cluster_id = None
    # Check if the cluster name exists already across 
    # the existing set of clusters from the past 7 days
    for cluster in clusters:
        if config_json["cluster_name"] == cluster["cluster_name"]:
            action = "edit"
            cluster_id = cluster["cluster_id"]
            config_json["cluster_id"] = cluster_id
            break
        else:
            pass
    
    print("ACTION:{} for cluster named {}".format(action, config_json["cluster_name"]))
    cluster_id = manage_cluster(config_json, args.token, args.location,action)

    if args.startup:
        print("Starting up cluster {}".format(cluster_id))
        start_cluster(cluster_id, args.token, args.location)
        print("Waiting 10 seconds for cluster to begin startup")
        time.sleep(10)


    if args.libraries is not None:
        print("Installing libraries on {}".format(cluster_id))
        with open(args.libraries, 'r') as lib_conn:
            lib_json = json.load(lib_conn)
            lib_json["cluster_id"] = cluster_id
        
        dbr_library.install_library_from_config(lib_json, args.token, args.location,"libraries","install")
    
    if args.shutdown:
        print("Shutting down cluster {}".format(cluster_id))
        delete_cluster(cluster_id, args.token, args.location)
