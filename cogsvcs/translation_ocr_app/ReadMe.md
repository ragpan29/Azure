# Demonstration of Python Web App, Translation, and OCR Services

This application demonstrates a Python Flask app (deployed locally) that calls Azure Language and OCR services.

## Getting Started

You'll need to install the required python libraries and set a few environment variables (assuming in VS Code with Powershell).  Before you set the environment variables, you'll need to deploy...

 * Computer Vision API for its OCR service.
 * Blob Storage Account with a container of 'ocrimages'.
 * Translation API (and use its key in the `COGS_KEY` env variable).

    pip install -r requirements.txt
    $env:COGS_KEY=''
    $env:LANGUAGE_URL='https://api.cognitive.microsofttranslator.com'
    $env:VISION_KEY=''
    $env:VISION_URL='https://<LOCATION>.api.cognitive.microsoft.com/vision/v2.0/'
    $env:BLOB_KEY=''
    $env:BLOB_ACCT_NAME=''
    $env:BLOB_URL='https://<storage-account-name>.blob.core.windows.net/ocrimages/'

You can use several example files in the img and pdf folders.