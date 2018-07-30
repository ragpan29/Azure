import requests
import json
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u","--url", required=True)
    parser.add_argument("-k","--key", required=True)
    args = parser.parse_args()

    # This is an example dataframe defined in a dictionary and turned into a json string
    data = {"input_df": [{"Review": "I would never go here again"}, {"Review":"I loved this place"}]}
    
    body = json.dumps(data)
    
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ args.key)}

    resp = requests.post(args.url, body, headers=headers)
    print(json.loads(resp.json()))