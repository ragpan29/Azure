from util import common
from util.doc_cracking import paginate_pdf, crack_pdf
from util.text_analytics import extract_keyphrases
import json
import uuid
import os

# Get list of PDFs
list_of_pdf = ["filepaths","to","pdfs"]
# Paginate PDFs for processing
# TODO: Threshold for page count
original_pdflist = dict()
for pdf_path in list_of_pdf:
    list_of_paginated_pdfs = paginate_pdf(pdf_path)
    original_pdflist[pdf_path] = list_of_paginated_pdfs

text_analytics_input = []
# Dictionary for holding id, , content, key phrases
pdf_content_entities = dict()

# Use TIKA to extract the content
for parent_path in original_pdflist:
    for pdf_path_type, single_page_pdf_path in original_pdflist[parent_path]:
        # Get page number
        pageNum = None
        if pdf_path_type == 'multi':
            single_page_name, ext = os.path.splitext(single_page_pdf_path)
            reversed_single_page_name = single_page_name[::-1]
            pageNum = int(reversed_single_page_name[0:(reversed_single_page_name.index("-"))])
        
        content = crack_pdf(single_page_pdf_path)
        pdf_id = str(uuid.uuid4())
        text_analytics_input.append( {"id":pdf_id, "language":"en","text":content} )

        pdf_content_entities[pdf_id] = {
            "id": pdf_id, 
            "content":content,
            "entities":None,
            "parentDoc":parent_path,
            "pageNum": pageNum,
            "docType":"Batch Record"
        }

# Get Keyphrases of all objects
# TODO: Check the length and chunk it if necessary
entities_list = extract_keyphrases(text_analytics_input)

for ent_dict in entities_list:
    lookup_id = ent_dict["id"]
    pdf_content_entities[lookup_id].update({"entities": ent_dict["keyPhrases"][0:10]})


# Write it out as json
with open("./pdf_content_entities5.json", 'w') as jsonout:
    json.dump(list(pdf_content_entities.values()), jsonout)