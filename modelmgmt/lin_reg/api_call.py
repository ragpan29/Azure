import requests
import json
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u","--url", required=True)
    parser.add_argument("-k","--key", required=True)
    args = parser.parse_args()

    data = {"input_df": [{"x1": 10, "x2": 3}]}
    body = str.encode(json.dumps(data))

    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ args.key)}

    resp = requests.post(args.url, body, headers=headers)
    print(json.loads(resp.json()))