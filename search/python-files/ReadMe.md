# A Simplified JFK Files for Python

A flask app that mimics the functionality of the JFK Files.

## Getting Started

 * Deploy Azure Search
 * Deploy Text Analytics API
 * Deploy Blob Storage Account
 * Deploy Computer Vision API for OCR

You'll need to set up these environment variables:

    $env:TEXTANALYTICS_KEY=''
    $env:TEXTANALYTICS_URL='https://<LOCATION>.api.cognitive.microsoft.com/text/analytics/v2.0/'

    $env:SEARCH_NAME=''
    $env:SEARCH_KEY=''
    $env:SEARCH_QUERY_KEY=''
    $env:SEARCH_INDEX_NAME = ''
    $env:SEARCH_API = '2017-11-11'

    $env:BLOB_ACCT_NAME = ''
    $env:BLOB_KEY = ''
    $env:BLOB_URL = 'https://<blob-acct-name>.blob.core.windows.net/'

    $env:VISION_KEY = ''
    $env:VISION_URL = 'https://<LOCATION>.api.cognitive.microsoft.com/vision/v2.0/'