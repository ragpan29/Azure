from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import requests
import os
import time
import config
import random

random.uniform(1,10)

# Set up for Adding to Index
URL = 'https://nih.search.windows.net'.format(config.config["service_name"])
KEY = config.config["KEY"]
INDEX_NAME = 'nih-data'
API = config.config["API"]
headers = {'content-type': 'application/json', 'api-key': KEY}

def extract_text(html):
    small_soup = BeautifulSoup(html, "html.parser")
    return small_soup.get_text().strip().encode("ASCII","ignore").decode("ASCII")

def get_contents_of_links(links, browser):
    URL_PATTERN = 'project_info_description.cfm'
    content_list = []
    for link in links:
        if URL_PATTERN in link:
            # link.click()
            print("Extracting: {}".format(link))
            sleep_len = 10 + random.uniform(1,10)
            print("Sleeping for {}".format(sleep_len))
            time.sleep(sleep_len)
            browser.get(link)

            link_details = dict()

            # Extract meta data about grant
            project_meta = browser.find_element_by_css_selector("div.search_criteria")
            project_meta_cells = project_meta.find_elements_by_css_selector("td")

            link_details["projectnumber"] = extract_text(project_meta_cells[1].get_attribute("innerHTML"))
            link_details["projectleader"] = extract_text(project_meta_cells[3].get_attribute("innerHTML"))
            link_details["projecttitle"] = extract_text(project_meta_cells[5].get_attribute("innerHTML"))
            link_details["awardeeorg"] = extract_text(project_meta_cells[7].get_attribute("innerHTML"))

            # Extract main content
            project_table = browser.find_element_by_css_selector("table.proj_info_cont")
            grant_content = project_table.find_elements_by_css_selector("td")

            link_details["abstract"] = extract_text(grant_content[0].get_attribute("innerHTML"))
            link_details["publichealth"] = extract_text(grant_content[1].get_attribute("innerHTML"))
            link_details["terms"] = extract_text(grant_content[2].get_attribute("innerHTML"))

            # full_content = browser.find_element_by_css_selector(".project_res")
            # html = full_content.get_attribute("innerHTML")
            # soup = BeautifulSoup(html, 'html.parser')

            # link_details["full_content"] = soup.get_text().strip().replace("  ", " ")

            link_details['@search.action'] = 'upload'

            content_list.append(link_details)

    return content_list

if __name__ == "__main__":
    # Initialize browser for web scraping
    browser = webdriver.Firefox()

    # Scraping pages and collecting data into content_list
    content_list = []
    for page in range(4,10):
        URL_PARENT = 'https://report.nih.gov/award/index.cfm?ot=&fy=2018&state=&ic=&fm=&orgid=&distr=&rfa=&om=n&pid=&view=data&pagenum={}&sortcol=pn&sortdir=asc#tab5'.format(page)
        browser.get(URL_PARENT)

        table_links = browser.find_elements_by_css_selector("table.res_cont tbody tr td a.tablelink")

        links = [link.get_attribute("href") for link in table_links]
        try:
            content_list = content_list + get_contents_of_links(links, browser)
        except Exception as e:
            temp_content_in_json = json.dumps({'value':content_list}, ensure_ascii=False,indent=2)
            output_name = "CRASH_upload_{}.json".format(datetime.now().strftime("%Y%M%d%H%S"))
            with open(os.path.join(".","data","nih",output_name), 'w') as f:
                json.dump(temp_content_in_json, f)


    browser.quit()

    # Uploading to Index
    content_url = ''.join([URL, '/indexes/',INDEX_NAME,'/docs/index?api-version=',API])

    content_in_json = json.dumps({'value':content_list}, ensure_ascii=False,indent=2)

    output_name = "upload_{}.json".format(datetime.now().strftime("%Y%m%d%H%S"))
    with open(os.path.join(".","data","nih",output_name), 'w') as f:
        json.dump(content_in_json, f)

    post_value = requests.post(content_url, headers=headers, data = content_in_json)

    print('Status Code: {}'.format(post_value.status_code))
    print(post_value.json())



