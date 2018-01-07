# Paid Search Query Report Parser

This project uses Powershell, Python, Apache Pig, and Apache Hive to take in a set of search query reports and list of negatives for each adgroup and campaign for a given advertiser.  

The sripts creates term-frequency inverse-document-frequency files for every token and ngrams (both 2gram contingous and 2gram separated by at least one token).  Then a final output lists every token / ngram that could be added as a negative and is not already a negative.

## This example should not be used in production and is only for demonstration purposes.

* Powershell script deploys an Azure HDInsight cluster.
* Need to create a parameters and template json files for your cluster.
* Python scripts are example UDFs used inside of the Pig and Hive QL scripts.
* Pig script creates the TFIDF files.
* Hive script eliminates the existing negatives.