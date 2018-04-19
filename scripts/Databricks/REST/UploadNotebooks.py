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

def create_directory(directory, location, token):
    hdr = define_auth(token)
    uri = define_uri(location, 'mkdirs')
    data = {"path":directory}
    data_txt = json.dumps(data)
    r = requests.post(uri,
         headers = hdr,
         data = data_txt)

    if r.status_code == 200:
        print("Added the directory {}".format(directory))
    elif r.status_code == 400:
        if r.json()['error_code'] == "RESOURCE_ALREADY_EXISTS":
            print("The directory {} exists already".format(directory))
    else:
        print(r.status_code)
        print(r.reason)
        print(r.json())
        raise AttributeError("Something went wrong creating the directory, parent directories may have been created.")
    
    return r
    

def upload_notebook(file, location, token, dbr_path=None, dbr_fname=None):
    filename, ext = os.path.splitext(file)
    print(filename)
    src_type = SOURCE_MAP[ext]

    if dbr_path is None:
        dbr_path = '/'

    if dbr_fname is None:
        print(os.path.split(filename))
        dbr_fname = os.path.split(filename)[-1]
    
    if dbr_path[-1:] != '/':
        dbr_path = dbr_path + '/'

    data = {"path":"{}{}".format(dbr_path, dbr_fname),
     "format":src_type,
     "language":"PYTHON",
     "overwrite":"true",
     }

    hdr = define_auth(token)
    uri = define_uri(location, 'import')

    r = requests.post(uri,
         headers = hdr,
         data = data,
         files = {'content': open(file,'rb')})

    print(r.status_code)
    if (r.status_code != 200):
        print(r.json())

    return r

def discover_notebooks(directory):
    notebooks = []
    root_path_len = len(directory.split(os.sep))
    print("The root path is {} directories long".format(root_path_len))

    files = os.walk(directory)
    for fpath, _, fnames in files:
        for f in fnames:
            f_left, ext = os.path.splitext(f)
            if ext not in SOURCE_MAP.keys():
                print("Skipping {}".format(f))
                continue
            dbr_directory = '/'+'/'.join(fpath.split(os.sep)[root_path_len:])
            dbr_fname = f_left
            local_fpath = os.path.join(fpath, f)
            notebooks.append( (local_fpath, dbr_directory, dbr_fname))
    
    return notebooks


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--location', help = "The location of your databricks cluster such as eastus2", required = True)
    parser.add_argument('-t', '--token', help = "The access token for your databricks workspace",required = True)
    parser.add_argument('-f', '--file', help = "The single file to upload")
    parser.add_argument('-d', '--localdir', help = "The directory containing files to upload")
    parser.add_argument('-c', '--clouddir', help = "The databricks directory")
    
    args = parser.parse_args()
    if args.localdir is not None:
        notebooks = discover_notebooks(args.localdir)
        seen_dirs = set()
        for local_fpath, dbr_directory, dbr_fname in notebooks:
            print("Working on {}/{}".format(dbr_directory, dbr_fname))

            if dbr_directory not in seen_dirs and dbr_directory != '/':
                create_directory(dbr_directory,args.location, args.token)
                seen_dirs.add(dbr_directory)

            resp = upload_notebook(local_fpath, args.location, args.token, dbr_path = dbr_directory, dbr_fname=dbr_fname)
    else:
        dbr_directory = '/'
        if args.clouddir is not None:
            dbr_directory = args.clouddir
        
        if dbr_directory != '/':
            dbr_directory = '/' + dbr_directory if dbr_directory[0] != '/' else dbr_directory
            create_directory(dbr_directory,args.location, args.token)
        
        resp = upload_notebook(args.file, args.location, args.token, dbr_path = dbr_directory)

    print("Upload complete")