# Databricks notebook source
# MAGIC %md
# MAGIC ### Prepare Databricks Workspace for Training
# MAGIC * On a Databricks 4.0+ cluster, run the scala command to mount a blob storage container.
# MAGIC * Return to this notebook on a 3.5 LTS cluster running Spark 2.2.1 or at least lower than Spark 2.3.0.
# MAGIC * Azure Model Management runs Spark 2.1.1 and the LinearRegression model gained a new param (epsilon) in 2.3.0.
# MAGIC * Be cautious of other models you select

# COMMAND ----------

# MAGIC %scala
# MAGIC dbutils.fs.mount(
# MAGIC   source = "wasbs://<CONTAINER>@<STORAGEACCT>.blob.core.windows.net/",
# MAGIC   mountPoint = "/mnt/misc",
# MAGIC   extraConfigs = Map("fs.azure.account.key.<STORAGEACCT>.blob.core.windows.net" -> "<STORAGEACCTKEY>"))

# COMMAND ----------

from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import Tokenizer, StopWordsRemover, CountVectorizer, SQLTransformer, VectorAssembler, HashingTF, IDF
from pyspark.ml.regression import LinearRegression
from pyspark.sql import SQLContext
sqlContext = SQLContext(sc)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Load in the text files
# MAGIC The data is from the [NSF Research Award Abstracts 1990-2003](https://archive.ics.uci.edu/ml/datasets/NSF+Research+Award+Abstracts+1990-2003).
# MAGIC The data has been loaded into a blob storage account and mounted in the top scala step above.
# MAGIC For this example, we are only loading in a single year's worth of data.

# COMMAND ----------

d = sc.wholeTextFiles("/mnt/misc/awd_1990_00/*.txt")
df = d.toDF().withColumnRenamed("_1", "fname").withColumnRenamed("_2", "contents")
df.createOrReplaceTempView("docs")
# Cleaning up text to one line to make parsing easier
df_flat_contents = sqlContext.sql("""
SELECT fname, contents, regexp_replace(regexp_replace(contents, "\n|\t", " "), ' +', ' ') as flatcon from docs
""")
df_flat_contents.createOrReplaceTempView("docs")
# Using SQL, extract the abstract's content and the grant amount.

df_w_depend = sqlContext.sql("""
    SELECT fname,
    trim(regexp_extract(docs.flatcon, 'Abstract *:(.+)', 1)) as abstract,
    cast(trim(substring(regexp_extract(docs.contents, 'Total Amt[\\. ]*: *(.+) +?', 1), 2, 12)) as int) as amt from docs
""")
# Perist the data for faster processing.
df_w_depend.persist()

# COMMAND ----------

df_w_depend.count()

# COMMAND ----------

display(df_w_depend.show())

# COMMAND ----------

# MAGIC %md
# MAGIC ### Prepare the Pipeline
# MAGIC For compataibility with Azure Model Management, make sure you are training the model on a cluster with Spark less than 2.3.0 since Model Management runs on Spark 2.1.1 and the Linear Regression model has a new param (epsilon) added in 2.3.0.

# COMMAND ----------


tkn = Tokenizer().setInputCol("abstract").setOutputCol("tokens")

englishStopWords = StopWordsRemover.loadDefaultStopWords("english")
stops = StopWordsRemover().setStopWords(englishStopWords).setInputCol("tokens").setOutputCol("tokens_no_stop")

tf = HashingTF().setInputCol("tokens_no_stop").setOutputCol("TFOut").setNumFeatures(1000)
idf = IDF().setInputCol("TFOut").setOutputCol("IDFOut").setMinDocFreq(1)
assem = VectorAssembler().setInputCols(["TFOut"]).setOutputCol("features")
rename = SQLTransformer().setStatement("SELECT features, amt as label FROM __THIS__")
reg = LinearRegression()

pipe = Pipeline().setStages([tkn, stops, tf, idf, assem, rename, reg])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Fit the Pipeline

# COMMAND ----------

trainedPipe = pipe.fit(df_w_depend)

# COMMAND ----------

display(trainedPipe.transform(df_w_depend))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Save the Pipeline

# COMMAND ----------

trainedPipe.write().overwrite().save('mnt/misc/models/predict_abstracts.model')

# COMMAND ----------

# For future reference, here's how you load a model
from pyspark.ml import PipelineModel
loadedpipe = PipelineModel.load('mnt/misc/models/predict_abstracts.model')