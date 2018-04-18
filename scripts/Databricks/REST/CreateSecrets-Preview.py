import requests
import argparse
import json

def define_auth(token):
    bearer = "Bearer {}".format(token)
    hdr = {"authorization": bearer}

    return hdr

def define_uri(location, noun, verb):
    return "https://{}.azuredatabricks.net/api/2.0/preview/secret/{}/{}".format(location, noun, verb)

def define_scope(scope):
    d = {'scope':scope}
    return json.dumps(d)

def list_scopes(token, location):
    hdr = define_auth(token)
    URI = define_uri(location, 'scopes', 'list')

    results = requests.get(URI, headers = hdr)

    return results.json()


def list_secrets(scope, token, location):
    # Databricks Secrets (Preview) requires a string be passed as data
    # Cannot use a dictionary
    scope_txt = define_scope(scope)
    hdr = define_auth(token)
    URI = define_uri(location, 'secrets', 'list')

    results = requests.get(URI, headers = hdr, data = scope_txt)

    return results.json()


def create_scope(scope, token, location):
    # Databricks Secrets (Preview) requires a string be passed as data
    # Cannot use a dictionary
    scope_txt = define_scope(scope)
    hdr = define_auth(token)
    URI = define_uri(location, 'scopes', 'create')

    r = requests.post(URI, headers = hdr, data = scope_txt)

    if r.status_code == 200:
        pass
    elif r.status_code == 400:
        if r.json()['error_code'] == "RESOURCE_ALREADY_EXISTS":
            raise FileExistsError
    else:
        print(r.status_code)
        print(r.reason)
        print(r.json())
        raise AttributeError("Something went wrong creating the Scope")

    return r


def create_secret(scope, token, location, key, value):
    hdr = define_auth(token)
    URI = define_uri(location, 'secrets', 'write')
    d = {'scope':scope, 'key':key, 'string_value':value}
    secret_def = json.dumps(d)

    r = requests.post(URI, headers = hdr, data = secret_def)

    return r



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--scope',  help = "The scope for the set of secrets",required = True)
    parser.add_argument('-l', '--location', help = "The location of your databricks cluster such as eastus2",required = True)
    parser.add_argument('-t', '--token', help = "The access token for your databricks workspace",required = True)
    parser.add_argument('-n', '--name', nargs = '*', help = "The secret names")
    parser.add_argument('-v', '--value', nargs = '*', help = "The secret values")

    args = parser.parse_args()

    if args.scope is None:
        raise AttributeError ("Scope Not Defined")
    
    if args.name is None or args.value is None:
        raise AttributeError ("The secret name or value hasn't been defined")
    
    if len(args.name) != len(args.name):
        raise KeyError("There must be an equal number of keys and values")
    
    secrets_values = {args.name[idx]: args.value[idx] for idx in range(len(args.name))}

    try:
        results = create_scope(args.scope, args.token, args.location)
    except FileExistsError:
        # Scope already existed
        pass
    
    print(list_scopes(args.token,args.location))
    
    # Create the Secrets
    for k,v in secrets_values.items():
        create_secret(args.scope, args.token, args.location, k, v)

    print(list_secrets(args.scope, args.token,args.location))

