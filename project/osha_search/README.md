# Using Azure Search and Python

Using the Azure Search rest API, I explore how you can create and query 
an index built in Azure Search.

I also explore a simple example of scoring profiles to help you 
understand the difference between linear and quadratic scoring.

This example scrapes the OSHA SIC website and pulls every page in the 
SIC glossary.  **Run src/scrape.py** to begin scraping.  Be sure to 
specify an --out directory.  Warning, there are over 1,000 pages and a 
two second delay on scraping by default.

Check out the src or report section for the ipynb or .md files 
(respectively) to learn more about the REST API for Azure Search.

* [Build the Index](./report/Azure%20Search%20and%20Python.md)
* [Scoring Profiles](./report/Azure%20Search%20and%20Interpolation.md)
