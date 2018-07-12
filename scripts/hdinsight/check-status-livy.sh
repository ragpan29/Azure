# Check the status of a cluster using livy
# https://docs.microsoft.com/en-us/azure/hdinsight/spark/apache-spark-livy-rest-interface#show-me-an-example
# http://livy.incubator.apache.org/docs/latest/rest-api.html
curl -k --user "adminuser:adminpassword" -v -X GET "https://HDICLUSTERNAME.azurehdinsight.net/livy/sessions" | jq
