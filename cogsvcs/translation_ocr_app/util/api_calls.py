import requests
from app import appvar
import json
import uuid
import urllib.parse as urlparse
from urllib.parse import urlencode
import time

PATH_LOOKUP = {
    "detect":'/detect',
    "translate":'/translate',
    "alternatives":'/dictionary/lookup',
    "list":"/languages"
}

def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


def headers(subscription_key):
    return {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

def translate_text(contents, from_lang, to_lang):
    header = headers(appvar.config["COGS_KEY"])
    contents_json = [{"Text":contents}]
    detected_dict = {"language":from_lang, "score":1.0}

    base_url = appvar.config["LANGUAGE_URL"]+PATH_LOOKUP["translate"]
    params = {"api-version":'3.0', "to":to_lang}
    if from_lang is not None:
        params.update({"from":from_lang})

    service_url = "{}?{}".format(base_url,urlencode(params))

    req = requests.post(
        url = service_url,
        headers = header, 
        data = json.dumps(contents_json)
    )
    
    results = ""
    try:
        if req.status_code == 200:
            # If the language was guessed, reach into the response and get the language and score
            if from_lang is None:
                detected_dict = req.json()[0]["detectedLanguage"]

            results = {"content":req.json()[0]["translations"][0]["text"], "language":detected_dict}
        else:
            # Try to get the error message
            results = {"content":"Error Code:{} | {} | Please contact your administrator.".format(req.json()["error"]["code"],req.json()["error"]["message"]),
                "language": {"language":"Error", "score":0.0}
                }
    except (KeyError, IndexError):
        results = {"content":"There was an error during processing. ({})".format(req.status_code),
            "language": {"language":"Error", "score":0.0}
            }
        print(req.json())

    return results

def translate_custom(contents, from_lang, to_lang, category):
    raise NotImplementedError

def detect_language(content):
    raise NotImplementedError

def translate_alternatives(content, from_lang, to_lang):
    results = []
    header = headers(appvar.config["COGS_KEY"])

    base_url = appvar.config["LANGUAGE_URL"]+PATH_LOOKUP["alternatives"]
    params = {"api-version":'3.0',"from":from_lang, "to":to_lang}

    service_url = "{}?{}".format(base_url,urlencode(params))
    
    data = json.dumps({"Text":content})


    req = requests.post(
        url = service_url,
        headers = header,
        data = data
    )

    if req.status_code == 200:
        results = req.json().get("translations")
    else:
        print(req.status_code)
        print(req.json())

    
    return results

def list_languages():
    header = headers(appvar.config["COGS_KEY"])

    base_url = appvar.config["LANGUAGE_URL"]+PATH_LOOKUP["list"]
    params = {"api-version":'3.0',"scope":"translation"}

    service_url = "{}?{}".format(base_url,urlencode(params))

    req = requests.get(
        url = service_url,
        headers = header
    )
    
    results = {"Error":{"name":"Error during processing"}}

    if "translation" in req.json():
        results = req.json()["translation"]

    return results


def ocr_image(img_url, from_lang, mode=None):
    header = headers(appvar.config["VISION_KEY"])
    service_url = appvar.config["VISION_URL"]

    params = {"language":from_lang, "detectOrientation":True}

    if mode == "Handwritten":
        params = {"mode":"Handwritten"}
        service_url = service_url + "recognizeText"
    else:
        service_url = service_url + "ocr"

    req = requests.post(
        url = service_url,
        params = params,
        headers = header,
        data = json.dumps({"url":img_url})
    )
    print(req.status_code)
    # If we don't get a 200, blow up
    try:
        req.raise_for_status()
    except Exception:
        print(req.status_code)
        prepared = req.request
        
        pretty_print_POST(prepared)

    if mode == "Handwritten":
        results = ocr_parse_handwritten(req, header)
    else:
        results = ocr_parse_printed(req.json())
    
    return results
        

def ocr_parse_printed(json_object):
    line_infos = [region["lines"] for region in json_object["regions"]]
    word_infos = []
    for line in line_infos:
        for word_metadata in line:
            for word_info in word_metadata["words"]:
                word_infos.append(word_info["text"])

    return ' '.join(word_infos)

def ocr_parse_handwritten(req,headers):
    print(req.headers)
    operation_url = req.headers["Operation-Location"]

    # The recognized text isn't immediately available, so poll to wait for completion.
    analysis = {}
    while "recognitionResult" not in analysis:
        response_final = requests.get(
            url = operation_url, 
            headers=headers
        )
        analysis = response_final.json()
        print("Looping")
        time.sleep(1)

    # Extract the recognized text
    tokens = [line["text"] for line in analysis["recognitionResult"]["lines"]]

    results = ' '.join(tokens)

    return results

if __name__ == "__main__":
    # translate_text("ZZZZZ!", "en","de")
    x = ocr_image(None, "unk")
    print(x)