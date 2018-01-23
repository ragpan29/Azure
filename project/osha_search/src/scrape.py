from bs4 import BeautifulSoup
import urllib.request
import re
import time
import sys
import os
import argparse

class URL_ENTRY:
    def __init__(self, URL):
        self.URL = URL
        self.visited = False
        self.localURL = ''
    def __str__(self):
        return self.URL+'\t'+self.localURL

TITLE_PATTERN = re.compile("^(.*) \|")
URL_PARENT = 'https://www.osha.gov/pls/imis/'
VALID_URL_PATTERN = re.compile("^sic_manual\.")

URL = 'sic_manual.html'
URL_VISITED = {URL:URL_ENTRY(URL)}
URL_TO_VISIT = [URL]



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='C:\temp')
    args = parser.parse_args()

    LOCAL_DIR = args.out

    while(len(URL_TO_VISIT) > 0):
        URL = URL_TO_VISIT[0]
        if URL_VISITED[URL].visited == True:
            URL_TO_VISIT.remove(URL)
        elif URL in URL_VISITED.keys():
            with urllib.request.urlopen(URL_PARENT+URL) as response:
                html = response.read()
                html_str = html.decode("utf-8", 'ignore')
                # Clean up newlines and carriage returns
                html_str = re.sub(r'\\n|\\r','',html_str)

                soup = BeautifulSoup(html_str, 'html5lib')

                # Get Title
                # OSHA titles are <REAL INFO> | <BRAND>
                title = TITLE_PATTERN.match(soup.title.get_text())[1]
                title = str(title)
                # Clean up title for windows naming conventions
                title = re.sub(r'[:,\']', '',string=title)
                title = re.sub(r'/', '',string=title)
                title = re.sub(r'[\s]', '_',string=title)

                # Get main content
                content = soup.find(id='maincontain')

                # Create HTML file in local directory
                localURL = os.path.join(LOCAL_DIR, str(title)+".html")
                URL_VISITED[URL].localURL = localURL
                f = open(localURL, 'w')
                f.write(content.prettify())
                f.close()

                # Get all links inside the maincontain
                maincontain = soup.find(id='maincontain').find_all('a')
                for link in maincontain:
                    if VALID_URL_PATTERN.match(str(link.get('href'))):
                        link_text = str(link.get('href'))
                        if link_text in URL_VISITED.keys():
                            pass
                        else:
                            URL_VISITED[link_text] = URL_ENTRY(link_text)
                            URL_TO_VISIT.append(link_text)

                # Out of For Loop
                URL_VISITED[URL].visited = True
                URL_TO_VISIT.remove(URL)
                print("Gathered stats on: "+URL+" ("+str(len(URL_TO_VISIT))+" to visit)")
                time.sleep(2.5)
            # Out of With Statement
        # Out of If Statement

    with open(os.path.join(LOCAL_DIR,"old_to_new_links.txt"),'w') as txt:
        for each in URL_VISITED.values():
            txt.write(str(each)+"\n")
        # Manually add in this search link
        txt.write('/pls/imis/sicsearch.html'+'\t'+'sic_search.html')
