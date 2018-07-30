# Model Training and Deployment Options 
|Resource |Use Case|Benefits|Challenges|Documentation|Deployment Strategy|
|-----|-----|-----|-----|-----|-----|
Databricks|Train single large model w/ Python / Scala|Fast, parallelizable algorithms.  Designed for massive scale of data.  User friendly UI.  Integration with GitHub.  Performance improvements due to proprietary Databricks enhancements over HDInsight.|Requires using Pyspark or Scala spark.  Higher cost than HDInsight.|[Docs](https://docs.azuredatabricks.net/)<br>[Pyspark API](https://spark.apache.org/docs/latest/api/python/index.html)<br>[Scala API](http://spark.apache.org/docs/latest/api/scala/index.html)|Deploy Spark Model with MML Spark.<br>Take sklearn model and deploy elsewhere.|
HDInsight|Train single large model w/ Python / Scala|Fast, parallelizable algorithms.  Designed for massive scale of data.|10-20 minute start up of cluster.  Potentially slower than Databricks.  Less user friendly than Databricks.  IaaS offering.|[Docs](https://docs.microsoft.com/en-us/azure/hdinsight/)|Deploy Spark Model with MML Spark.<br>Take sklearn model and deploy elsewhere.|
Batch / Batch AI|Train many models or Deep Neural Net|Train models on independent data sets in parallel or build deep learning neural networks.  Can use any language that has a machine learning library (R, Python, C#, Scala, etc.)|Limited use case to parallel model training or deep neural networks.|[Docs](https://docs.microsoft.com/en-us/azure/batch-ai/)|Models can be applied to new data in batch.<br>Take trained models and deploy elsewhere|
AZTK (Spark on Batch)|Train single large model w/ Python / Scala|Fast, parallelizable algorithms.  Designed for massive scale of data.   Run cheaper than HDInsight if using "Low Priority" nodes.|While Microsoft provides an open source option, it's not an official product and customers are responsible for keeping their "cluster" maintained.|[Github](https://github.com/Azure/aztk)|Deploy Spark Model with MML Spark.<br>Take sklearn model and deploy elsewhere.|
ML Server|Dedicated server for running Python or R APIs|Run Pyspark, Python, Models on a performant, dedicated server.|Focused on R and Python only.  Leverages Microsoft developed packages for optimal performance.|[Docs](https://docs.microsoft.com/en-us/machine-learning-server/what-is-machine-learning-server) |Deployable as a Web Service.|
Docker / Kubernetes|Train models on a provisioned cluster.|Scale your model training or deployment by running your models on a kubernetes cluster.  Run any language depending on the containers provisioned.|Have to create your own processes to scale your training or a web server to create a web service.|[Docs](https://docs.microsoft.com/en-us/azure/aks/intro-kubernetes)|You create the API service.|
SQL Server|Keep data in your database and still use ML.|Avoid moving data outside of your database but still leverage machine learning in Python and R.|Limited to Python and R and Microsoft developed algorithms.|[Docs](https://docs.microsoft.com/en-us/sql/advanced-analytics/r/sql-server-r-services?view=sql-server-2017)|Deployable as Stored Procedures|
DSVM|Trying out different ML tools.  Scaling up your local work.|Provides many different tools and languages pre-installed.  Can scale to very large sizes and include GPUs for deep learning.  Can be used to host deployed models as well.|General purpose and doesn't necessarily contain unique optimizations as other tools do.|[Docs](https://docs.microsoft.com/en-us/azure/machine-learning/machine-learning-data-science-virtual-machine-overview)|Take trained model and turn DSVM into a web server.|
Azure ML Studio|Train and deploy models with a GUI. |GUI for machine learning that provides an easy way to train models and deploy them as a web service. |Limited number of algorithms to choose from.  GUI can be constraining to some advanced users.|[Homepage](https://studio.azureml.net/)|Deployable as a Web Service.|
Azure Model Management / Workbench|Write code in one spot, train with multiple services, and deploy as a web service.|Provides a way of organizing your and your team's analyses into different projects and workspaces.  Provides a way to write code locally and deploy to other services (DSVM, HDInsight).  Provides a command line interface for deploy web services.|Undergoing an update soon.|[Docs](https://docs.microsoft.com/en-us/azure/machine-learning/desktop-workbench/model-management-overview)|This service deploys an AKS cluster and a Web Service.|
Locally|Training on small to medium size data.  Small sample experiment.|Using your own, already purchased hardware incurs no operations costs.  Complete control of your own tool chain and software.|Hard to scale.  May run into IT bottlenecks.  Limited to the size of your local machine(s).|N/A|Take trained model and deploy elsewhere|
  
**Special Notes**

At the time of writing, the version of Spark running on the cluster deployed by Azure Model Management is 2.1.1. 
This leads to some inconsistencies if your models take advantage of newer features. 
  
## MMLSpark and MLFlow Deployments 
  
[MML Spark Homepage](https://github.com/Azure/mmlspark)
  
MMLSpark is an open source Scala package designed to simplify the modeling process and to deploy Spark models as web services. 
  
The web service deployment creates a structured streaming job on your spark cluster.  Behind the scenes, this tools is used to serve Spark models via Azure Model Management. 
  
[MLFlow Homepage](https://github.com/databricks/mlflow)
  
Databricks' open source product called MLFlow is another recent entrant in simplifying the model building process and deploying the models as web services. 
  
It is currently in alpha and still incubating under guidance of the databricks team.