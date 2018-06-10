# Using Azure Search to Query NIH Grant Data

In this project, we scrape NIH grant data from www.nih.gov (responsibly) and upload the relevant pieces to [Azure Search](https://docs.microsoft.com/en-us/azure/search/).

The `src` folder contains the NIH grant data scraping utilities and the interaction with the [Azure Search REST API](https://docs.microsoft.com/en-us/rest/api/searchservice/) via the `requests` library.  You will need to have selenium installed and also grab the appropriate webdriver for your project.  See many of the drivers [here](https://www.seleniumhq.org/download/).  In addition, there is a Product search index that you should populate.  This would then let you query both product data and NIH grant data at the same time.

The `site` folder contains a Flask web app that queries the NIH and product search indexes.  It also uses the [Key Phrase Extraction](https://docs.microsoft.com/en-us/azure/machine-learning/studio-module-reference/extract-key-phrases-from-text) cognitive service to identify important phrases in the abstract of the NIH grant.  This step is no longer necessary if you are using the Key Phrase [Predefined Skill](https://docs.microsoft.com/en-us/azure/search/cognitive-search-predefined-skills) in Cognitive Search.

The site structure is based on an early iteration of my [flask template](https://github.com/wjohnson/flask_template).  The iteration in this folder works best on the localhost and isn't ready to be deployed to an Azure Web App.

## NIH Grant Index

    {"name": "projectnumber", "type":"Edm.String", "key":True, "searchable":True, "retrievable":True},
    {"name": "projecttitle", "type": "Edm.String", "sortable": True},
    {"name": "awardeeorg", "type": "Edm.String", "sortable": True, "facetable":True},
    {"name": "projectleader", "type": "Edm.String", "filterable":True},
    {"name": "abstract", "type": "Edm.String", "analyzer": "en.Microsoft", "synonymMaps": ["bio-terms"]},
    {"name": "publichealth", "type": "Edm.String", "retrievable":False, "analyzer": "contentAnalyzer"},
    {"name": "terms", "type": "Edm.String","retrievable":False}

The NIH grant index uses two different analyzers (one built-in and one custom) and uses a synonym map to change inbound searches to a more standard search pattern.


## Product Data Index

    {"name": "productid", "type":"Edm.String", "key":True, "searchable":True, "retrievable":True},
    {"name": "productname", "type": "Edm.String", "sortable": True,  "analyzer": "en.Microsoft"},
    {"name": "producttagline", "type": "Edm.String", "sortable": True, "analyzer": "en.Microsoft"},
    {"name": "productdetails", "type": "Edm.String", "analyzer": "en.Microsoft"}