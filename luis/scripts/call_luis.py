import requests
import argparse
import json

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u","--url", help="LUIS Endpoint")
    parser.add_argument("-k","--key", help="LUIS Endpoint Key")
    parser.add_argument("-q","--query", help="Query to send to LUIS")
    args = parser.parse_args()

    data = args.query
    body = json.dumps(data)

    
    headers = {'Content-Type':'application/json', 'Ocp-Apim-Subscription-Key ': args.key}

    resp = requests.post(args.url, data = body, headers=headers)
    print(resp.json())