from pyspark.sql import SparkSession
from pyspark.sql.functions import expr

spark = SparkSession.builder \
    .appName("KafkaSparkStreaming") \
    .master("spark://spark:7077") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Read stream from Kafka
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "test-topic") \
    .option("startingOffsets", "earliest") \
    .load()

# Just print raw value
value_df = df.selectExpr("CAST(value AS STRING) as value")

query = value_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()
