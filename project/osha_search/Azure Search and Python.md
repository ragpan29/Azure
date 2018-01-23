
# Using Python in Azure Search

Azure Search is a Full-Text Search engine inside of Azure built on top of the Apache Lucene project.

There is a REST API exposed that allows you to administer and query your search index.

This notebook shows the basics of:

* Creating an index
* Loading data to an index
* Querying that index (and using a few parameters in the queries).
* Using Search Profiles to boost pages

It all boils down to following a template JSON (in Python, using requests, you can just use dictionaries).  I have included links to Microsoft documentation for each section.

### Setting up the Environment

You'll need to create an Azure Search Service before executing this script.  The accompanying powershell script will launch an Azure Search Service called osha and resolve to osha.search.windows.net.  It will also pull the admin secret key that we will use to create the index.  The powershell script will pull that key into a file called config.config.  

For production use, you should consider generating "**Query Keys**" which are read-only access to your Azure Search Service.

Lastly, we manually specify the API version here and it may change in later updates.  Find more here: https://docs.microsoft.com/en-us/azure/search/search-api-versions


```python
URL = 'https://osha2.search.windows.net'
with open('./config.config', 'r') as f:
    KEY = f.read()
INDEX_NAME = 'sicdesc'

API = '2016-09-01'
headers = {'content-type': 'application/json', 'api-key': KEY}

index_url = ''.join([URL, '/indexes/',INDEX_NAME,'?api-version=',API])
```


```python
import json
import requests
import os
import re
import datetime
import random
```

The packages json and requests are the core of the REST API work.  The remaining packages are used for working with the demo data.

The first steps below is to create a dictionary that will eventually be our search index.


```python
azure_index = dict()
azure_index["name"] = INDEX_NAME
```

Within the index, you have to define the field:
* name - The name of the field.
* type - one of these options:
 * Edm.String
 * Collection(Edm.String)
 * Edm.Boolean
 * Edm.Int32
 * Edm.Int64
 * Edm.Double
 * Edm.DateTimeOffset
 * Edm.GeographyPoint
* retrievable - Do you get this data back?  Defaults to true
* searchable - Should content in this field be broken up and used in searching?  Defaults to true
* filterable - Should content not be broken up?  Exact match filter of results.
* sortable - Allows for sorting
* facetable
* key - Is it a key?  Can also be used to look up documents directly (https://docs.microsoft.com/en-us/rest/api/searchservice/lookup-document)

More information on creating an index can be found here: https://docs.microsoft.com/en-us/rest/api/searchservice/create-index


```python
azure_index["fields"] = [
       {"name": "sic4", "type": "Edm.String", "key":True, "searchable": True},
       {"name": "sic4title", "type": "Edm.String","filterable": False, "sortable": False, "facetable": False},
       {"name": "content", "type": "Edm.String", "filterable": False, "sortable": False, "facetable": False, 'retrievable':False},
       {"name": "oshaURL", "type": "Edm.String", "filterable": False, "sortable": False, "facetable": False},
       {"name": "sic2", "type": "Edm.String", "searchable": False},
       {"name": "updateDate", "type": "Edm.DateTimeOffset", "searchable": False,"facetable":False},
      ]
```

### Scoring Profiles

A scoring profile allows you to augment the relevancy score of each document.  In the case below, I am boosting any page that was updated in the last 60 days by a huge amount (boost: 1000).  The "interpolation" attribute controls the effect over a range of values.  In this case, I'm using **linear** so a one day difference is the same across the past 60 days.  Other options like Quadratic and Log10 would have greater differences between documents in the middle than documents at the end.

More here: https://docs.microsoft.com/en-us/rest/api/searchservice/add-scoring-profiles-to-a-search-index


```python
azure_index["scoringProfiles"] = []

scoreProfile = dict()

scoreProfile["name"] = "newerPages"
scoreProfile["functions"] = []

score_func = {"type": "freshness", "fieldName": "updateDate", "boost": 1000,\
              "interpolation": "linear",\
              "freshness": {"boostingDuration": "P60D"}
             }

scoreProfile["functions"].append(score_func)

azure_index["scoringProfiles"].append(scoreProfile)
```

## Drop the Index (In Case it Exists)

A status code of 204 is a successful drop of the index with no content being returned.


```python
drop = requests.delete(index_url, headers=headers)
```


```python
print(drop.status_code)
print(drop.content)
```

    204
    b''
    

## Put the Index

In order to create the initial index, we PUT the azure_index dictionary as a json file to the index_url.

A status code of 201 means a successful creation of the index.


```python
json_index = json.dumps(azure_index, ensure_ascii=False,indent=2)
```


```python
put_index = requests.put(index_url, headers=headers, data = json_index)
```


```python
print(put_index.status_code)
print(put_index.content)
```

    201
    b'{"@odata.context":"https://osha2.search.windows.net/$metadata#indexes/$entity","@odata.etag":"\\"0x8D562B32B6551E9\\"","name":"sicdesc","fields":[{"name":"sic4","type":"Edm.String","searchable":true,"filterable":true,"retrievable":true,"sortable":true,"facetable":true,"key":true,"indexAnalyzer":null,"searchAnalyzer":null,"analyzer":null},{"name":"sic4title","type":"Edm.String","searchable":true,"filterable":false,"retrievable":true,"sortable":false,"facetable":false,"key":false,"indexAnalyzer":null,"searchAnalyzer":null,"analyzer":null},{"name":"content","type":"Edm.String","searchable":true,"filterable":false,"retrievable":false,"sortable":false,"facetable":false,"key":false,"indexAnalyzer":null,"searchAnalyzer":null,"analyzer":null},{"name":"oshaURL","type":"Edm.String","searchable":true,"filterable":false,"retrievable":true,"sortable":false,"facetable":false,"key":false,"indexAnalyzer":null,"searchAnalyzer":null,"analyzer":null},{"name":"sic2","type":"Edm.String","searchable":false,"filterable":true,"retrievable":true,"sortable":true,"facetable":true,"key":false,"indexAnalyzer":null,"searchAnalyzer":null,"analyzer":null},{"name":"updateDate","type":"Edm.DateTimeOffset","searchable":false,"filterable":true,"retrievable":true,"sortable":true,"facetable":false,"key":false,"indexAnalyzer":null,"searchAnalyzer":null,"analyzer":null}],"scoringProfiles":[{"name":"newerPages","text":null,"functions":[{"fieldName":"updateDate","freshness":{"boostingDuration":"P60D"},"interpolation":"linear","magnitude":null,"distance":null,"tag":null,"type":"freshness","boost":1000.0}],"functionAggregation":"sum"}],"defaultScoringProfile":null,"corsOptions":null,"suggesters":[],"analyzers":[],"tokenizers":[],"tokenFilters":[],"charFilters":[]}'
    

## Adding Content to the Index

The next step is to get the documents into the index.

We must POST the data as a json object to the index_url.  Each field must be represented and a "@search.action" must be set as "upload" on every entry.

In this example, the data is stored in the /data folder.  For every page, we'll need to create an entry and fill in the values for each element of the index.


```python
content_url = ''.join([URL, '/indexes/',INDEX_NAME,'/docs/index?api-version=',API])
```


```python
files = os.listdir('.\\data')
files_filtered = [file for file in files if re.match('Description_for_',file)]

value = []
```

As an example of boosting based on dates, a random "updateDate" is created for every page.  The months and days code below set up options for the random date generation.


```python
months = list(range(1,13))
days = list(range(1,29))
```


```python
random.seed(1)

for file in files_filtered:
    sic4 = file[16:20]
    sic2 = file[16:18]
    with open(os.path.join(os.getcwd(),'data',file), 'r') as f:
        content = ''.join(f.readlines())
    
    h2_pattern = re.compile(r'<h2>(.*)</h2>')
    
    content_nonewlines = content.replace('\n','')
    
    sic4title = re.findall(h2_pattern, content_nonewlines)[0].strip()
    
    updateDate = datetime.datetime(2017, random.choice(months), random.choice(days))
    
    file_dict = {
        "@search.action": "upload",
        "sic4": sic4,
        "sic4title": sic4title,
        "content": content,
        "oshaURL": "https://www.osha.gov/pls/imis/sic_manual.html",
        "sic2": sic2,
        # Dates are DateTimeOffset based on the OData V4 standard
        "updateDate":updateDate.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    value.append(file_dict)
```


```python
value[0]
```




    {'@search.action': 'upload',
     'content': '<div class="container" id="maincontain">\n <!-- PLACE PAGE CODE BELOW\nuse the code between the START BODY and END BODY comments-->\n <div class="row-fluid">\n  <h2>\n   Description for 0111: Wheat\n  </h2>\n  <p>\n   <a href="sic_manual.display?id=1&amp;tab=division" title="Division A: Agriculture, Forestry, And Fishing">\n    Division A: Agriculture, Forestry, And Fishing\n   </a>\n   <strong>\n    |\n   </strong>\n   <a href="sic_manual.display?id=1&amp;tab=group" title="Major Group 01: Agricultural Production Crops">\n    Major Group 01: Agricultural Production Crops\n   </a>\n  </p>\n  <p>\n   Industry Group 011: Cash Grains\n  </p>\n  <hr/>\n  0111 Wheat\n  <div>\n   <span class="blueTen">\n    Establishments primarily engaged in the production of wheat.\n   </span>\n   <ul>\n    <li>\n     Wheat farms\n    </li>\n   </ul>\n  </div>\n  <br/>\n  <hr/>\n  <p class="text-center">\n  </p>\n  <div class="text-center">\n   <a class="btn btn-small btn-info" href="/pls/imis/sicsearch.html" title="SIC Search">\n    SIC Search\n   </a>\n   <a class="btn btn-small btn-info" href="sic_manual.html" title="Division Structure">\n    Division Structure\n   </a>\n   <a class="btn btn-small btn-info" href="sic_manual.display?id=1&amp;tab=group" title="Major Group Structure">\n    Major Group Structure\n   </a>\n  </div>\n  <p>\n  </p>\n </div>\n <!--end MAIN .row-fluid -->\n <!-- END PLACED CODE -->\n</div>\n',
     'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
     'sic2': '01',
     'sic4': '0111',
     'sic4title': 'Description for 0111: Wheat',
     'updateDate': '2017-03-19T00:00:00Z'}



### Loading the data to the index with POST

You are limited to 1,000 or fewer documents in a single request.  This example has 1,005 so two batches are sent.


```python
units_of_1k = int(round(len(value)/1000,0))
remainder = len(value) % 1000

if len(value) < 1000:
    units_of_1k = 1
elif remainder != 0:
    units_of_1k+=1

for x in range(units_of_1k):
    start = x*1000
    end = x*1000+1000
    print(str(start)+'-'+str(end))
    
    json_value = json.dumps({'value':value[start:end]}, ensure_ascii=False,indent=2)
    post_value = requests.post(content_url, headers=headers, data = json_value)
    
    print('Status Code:'+str(post_value.status_code))
```

    0-1000
    Status Code:200
    1000-2000
    Status Code:200
    

## Query the Index

Using the GET verb and updating the url to be https://app-name.search.windows.net/indexes/index-name/docs?search=

https://docs.microsoft.com/en-us/rest/api/searchservice/Search-Documents

The search and $top parameters are used in this initial query to search for the token '7389' and return the top 2 results.


```python
QUERY = '7389'
search = {'search':QUERY,'$top':2}
search_url = ''.join([URL, '/indexes/',INDEX_NAME,'/docs?api-version=',API])
```


```python
results = requests.get(search_url, params=search,headers=headers)
```


```python
results.json()
```




    {'@odata.context': "https://osha2.search.windows.net/indexes('sicdesc')/$metadata#docs",
     'value': [{'@search.score': 3.068583,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '73',
       'sic4': '7389',
       'sic4title': 'Description for 7389: Business Services, Not Elsewhere Classified',
       'updateDate': '2017-10-17T00:00:00Z'},
      {'@search.score': 0.14266038,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '86',
       'sic4': '8651',
       'sic4title': 'Description for 8651: Political Organizations',
       'updateDate': '2017-06-25T00:00:00Z'}]}



### Lookup with a Key Only

If you are using the key field, you can look up documents directly.


```python
search_key = {'key':'7389'}
key_results = requests.get(search_url, params=search_key,headers=headers)
key_results.json()
```




    {'@odata.context': "https://osha2.search.windows.net/indexes('sicdesc')/$metadata#docs/$entity",
     'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
     'sic2': '73',
     'sic4': '7389',
     'sic4title': 'Description for 7389: Business Services, Not Elsewhere Classified',
     'updateDate': '2017-10-17T00:00:00Z'}



### Change the sort

The $orderby parameter can be used to sort the results.

In this case, notice that the best page isn't even in the result set.  The Top N is performed after the sorting.


```python
QUERY = '7389'
search_sort = {'search':QUERY,'$top':5,'$orderby':'sic2,sic4 desc'}
sort_results = requests.get(search_url, params=search_sort,headers=headers)
sort_results.json()
```




    {'@odata.context': "https://osha2.search.windows.net/indexes('sicdesc')/$metadata#docs",
     'value': [{'@search.score': 0.0840453,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '39',
       'sic4': '3993',
       'sic4title': 'Description for 3993: Signs and Advertising Specialties',
       'updateDate': '2017-09-02T00:00:00Z'},
      {'@search.score': 0.12525646,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '42',
       'sic4': '4225',
       'sic4title': 'Description for 4225: General Warehousing and Storage',
       'updateDate': '2017-09-02T00:00:00Z'},
      {'@search.score': 0.1324496,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '47',
       'sic4': '4783',
       'sic4title': 'Description for 4783: Packing and Crating',
       'updateDate': '2017-09-18T00:00:00Z'},
      {'@search.score': 0.0840453,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '48',
       'sic4': '4813',
       'sic4title': 'Description for 4813: Telephone Communications, Except Radiotelephone',
       'updateDate': '2017-06-13T00:00:00Z'},
      {'@search.score': 0.10787979,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '48',
       'sic4': '4812',
       'sic4title': 'Description for 4812: Radiotelephone Communications',
       'updateDate': '2017-03-07T00:00:00Z'}]}



### Filter the Results

The filter happens before the top N are returned as well.  The filter language consists of gt, lt, eq, ne, ge, le.  More information can be found here: https://docs.microsoft.com/en-us/rest/api/searchservice/odata-expression-syntax-for-azure-search


```python
QUERY = '7389'
search_sort = {'search':QUERY,'$top':5,'$orderby':'sic2,sic4 desc','$filter':"sic2 gt '50' and sic2 lt '80'"}
sort_results = requests.get(search_url, params=search_sort,headers=headers)
sort_results.json()
```




    {'@odata.context': "https://osha2.search.windows.net/indexes('sicdesc')/$metadata#docs",
     'value': [{'@search.score': 0.060283564,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '59',
       'sic4': '5999',
       'sic4title': 'Description for 5999: Miscellaneous Retail Stores, Not Elsewhere Classified',
       'updateDate': '2017-05-22T00:00:00Z'},
      {'@search.score': 3.068583,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '73',
       'sic4': '7389',
       'sic4title': 'Description for 7389: Business Services, Not Elsewhere Classified',
       'updateDate': '2017-10-17T00:00:00Z'},
      {'@search.score': 0.10398239,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '73',
       'sic4': '7336',
       'sic4title': 'Description for 7336: Commercial Art and Graphic Design',
       'updateDate': '2017-01-12T00:00:00Z'},
      {'@search.score': 0.11139457,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '73',
       'sic4': '7335',
       'sic4title': 'Description for 7335: Commercial Photography',
       'updateDate': '2017-05-17T00:00:00Z'},
      {'@search.score': 0.12178051,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '73',
       'sic4': '7334',
       'sic4title': 'Description for 7334: Photocopying and Duplicating Services',
       'updateDate': '2017-06-08T00:00:00Z'}]}



### Facet the Results

Faceting provides a count by each of distinct values for the facet after taking into account filters.  You can use this information to provide feedback to the user for searching criteria.


```python
QUERY = '7389'
search_facet = {'search':QUERY,'facet':'sic2','$top':5,'$filter':"sic2 gt '10' and sic2 lt '80'"}
facet_results = requests.get(search_url, params=search_facet, headers=headers)
facet_results.json()
```




    {'@odata.context': "https://osha2.search.windows.net/indexes('sicdesc')/$metadata#docs",
     '@search.facets': {'sic2': [{'count': 4, 'value': '73'},
       {'count': 2, 'value': '48'},
       {'count': 1, 'value': '39'},
       {'count': 1, 'value': '42'},
       {'count': 1, 'value': '47'},
       {'count': 1, 'value': '59'}],
      'sic2@odata.type': '#Collection(Microsoft.Azure.Search.V2016_09_01.QueryResultFacet)'},
     'value': [{'@search.score': 3.068583,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '73',
       'sic4': '7389',
       'sic4title': 'Description for 7389: Business Services, Not Elsewhere Classified',
       'updateDate': '2017-10-17T00:00:00Z'},
      {'@search.score': 0.1324496,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '47',
       'sic4': '4783',
       'sic4title': 'Description for 4783: Packing and Crating',
       'updateDate': '2017-09-18T00:00:00Z'},
      {'@search.score': 0.12525646,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '42',
       'sic4': '4225',
       'sic4title': 'Description for 4225: General Warehousing and Storage',
       'updateDate': '2017-09-02T00:00:00Z'},
      {'@search.score': 0.12178051,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '73',
       'sic4': '7334',
       'sic4title': 'Description for 7334: Photocopying and Duplicating Services',
       'updateDate': '2017-06-08T00:00:00Z'},
      {'@search.score': 0.11139457,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '73',
       'sic4': '7335',
       'sic4title': 'Description for 7335: Commercial Photography',
       'updateDate': '2017-05-17T00:00:00Z'}]}



## Use Search Profile on the Index to Boost Pages

Search profiles add different ways of creating relevancy scores.  For example, making more recently updated pages come up first.

More on the Scoring Profiles: https://docs.microsoft.com/en-us/rest/api/searchservice/add-scoring-profiles-to-a-search-index

In this example, I'm searching for "bakery" in the OSHA database and it turns up results based on the default TF-IDF scoring.


```python
QUERY = 'bakery'
search_no_profile = {'search':QUERY,'$top':10}
no_profile_results = requests.get(search_url, params=search_no_profile, headers=headers)
no_profile_results.json()
```




    {'@odata.context': "https://osha2.search.windows.net/indexes('sicdesc')/$metadata#docs",
     'value': [{'@search.score': 1.0197592,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '20',
       'sic4': '2053',
       'sic4title': 'Description for 2053: Frozen Bakery Products, Except Bread',
       'updateDate': '2017-10-09T00:00:00Z'},
      {'@search.score': 0.9104632,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '20',
       'sic4': '2051',
       'sic4title': 'Description for 2051: Bread and Other Bakery Products, Except Cookies and Crackers',
       'updateDate': '2017-05-24T00:00:00Z'},
      {'@search.score': 0.19515699,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '54',
       'sic4': '5461',
       'sic4title': 'Description for 5461: Retail Bakeries',
       'updateDate': '2017-05-26T00:00:00Z'},
      {'@search.score': 0.18454346,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '20',
       'sic4': '2052',
       'sic4title': 'Description for 2052: Cookies and Crackers',
       'updateDate': '2017-03-14T00:00:00Z'},
      {'@search.score': 0.15043719,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '35',
       'sic4': '3567',
       'sic4title': 'Description for 3567: Industrial Process Furnaces and Ovens',
       'updateDate': '2017-02-03T00:00:00Z'},
      {'@search.score': 0.13942689,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '20',
       'sic4': '2024',
       'sic4title': 'Description for 2024: Ice Cream and Frozen Desserts',
       'updateDate': '2017-09-22T00:00:00Z'},
      {'@search.score': 0.11001283,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '51',
       'sic4': '5142',
       'sic4title': 'Description for 5142: Packaged Frozen Foods',
       'updateDate': '2017-07-17T00:00:00Z'},
      {'@search.score': 0.102756575,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '34',
       'sic4': '3497',
       'sic4title': 'Description for 3497: Metal Foil and Leaf',
       'updateDate': '2017-08-24T00:00:00Z'},
      {'@search.score': 0.09227173,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '20',
       'sic4': '2038',
       'sic4title': 'Description for 2038: Frozen Specialties, Not Elsewhere Classified',
       'updateDate': '2017-11-19T00:00:00Z'},
      {'@search.score': 0.08595058,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '35',
       'sic4': '3556',
       'sic4title': 'Description for 3556: Food Products Machinery',
       'updateDate': '2017-12-06T00:00:00Z'}]}



Next we use the 'newerPages' scoring profile defined when the index was initially created.  This will boost documents that were last updated in the past 60 days.  You can compare the two scores for SIC 3556 (updated 2017-12-06) and see the dramatic difference.


```python
QUERY = 'bakery'
search_bakery_profile = {'search':QUERY,'$top':5,'scoringProfile':'newerPages'}
profile_results = requests.get(search_url, params=search_bakery_profile, headers=headers)
profile_results.json()
```




    {'@odata.context': "https://osha2.search.windows.net/indexes('sicdesc')/$metadata#docs",
     'value': [{'@search.score': 15.90048,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '35',
       'sic4': '3556',
       'sic4title': 'Description for 3556: Food Products Machinery',
       'updateDate': '2017-12-06T00:00:00Z'},
      {'@search.score': 1.0197592,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '20',
       'sic4': '2053',
       'sic4title': 'Description for 2053: Frozen Bakery Products, Except Bread',
       'updateDate': '2017-10-09T00:00:00Z'},
      {'@search.score': 0.9104632,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '20',
       'sic4': '2051',
       'sic4title': 'Description for 2051: Bread and Other Bakery Products, Except Cookies and Crackers',
       'updateDate': '2017-05-24T00:00:00Z'},
      {'@search.score': 0.19515699,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '54',
       'sic4': '5461',
       'sic4title': 'Description for 5461: Retail Bakeries',
       'updateDate': '2017-05-26T00:00:00Z'},
      {'@search.score': 0.18454346,
       'oshaURL': 'https://www.osha.gov/pls/imis/sic_manual.html',
       'sic2': '20',
       'sic4': '2052',
       'sic4title': 'Description for 2052: Cookies and Crackers',
       'updateDate': '2017-03-14T00:00:00Z'}]}



## Solving Synonyms

Coming soon!  In Preview:

More found here: https://docs.microsoft.com/en-us/rest/api/searchservice/create-synonym-map


```python
synoyms = \
"""bakery, baker\n
boat, yacht, pontoon, ship =>
"""
```


```python
json_syn = {"name" : "basicsynonyms",
 "format" : "solr", 
 "synonyms" : synoyms
}  
```


```python
#synonym_url = ''.join([URL, '//synonymmaps?api-version=',API])
#post_synonym = requests.post(synonym_url, headers=headers, data = json_syn)
```


```python
#post_synonym.content
```


```python
#QUERY = 'baker'
#search_baker1 = {'search':QUERY,'$top':5}
#baker1_results = requests.get(search_url, params=search_baker1, headers=headers)
#baker1_results.json()
```

## Where to go from here?

There are plenty of other options to look into like Language Understanding, advanced text analysis, transforming the data while building the index, etc.  The best way to learn it is to try it out and see what you can build!
