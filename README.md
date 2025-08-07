# spark-streaming-kafka-flink

✅ Kafka Setup (shared across examples)
Create a Kafka topic:
```bash

docker exec -it kafka kafka-topics --create \
  --topic test-topic \
  --bootstrap-server kafka:9092 \
  --replication-factor 1 \
  --partitions 1
```
Produce test data to Kafka:
```bash
docker exec -it kafka kafka-console-producer \
  --topic test-topic \
  --bootstrap-server kafka:9092
```
Type some messages like:
```bash
hello
spark
flink
streaming
```
then ctrl + c

🧪 Example 1: Spark Structured Streaming from Kafka
🔸 Create PySpark script: spark_kafka_stream.py
```bash
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
```

🔸 Copy script into the spark container:
```bash
docker cp spark_kafka_stream.py spark:/tmp/
```

🔸 Run the script inside the container:
```bash
docker exec -it spark bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /tmp/spark_kafka_stream.py
```

🧪 Example 2: Flink Kafka Streaming Job (Flink SQL CLI)
## Steps

### 1. Download Kafka Connector JARs

Create a directory to store the required JARs:

```bash
mkdir -p ./jars/
wget https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/1.18.0/flink-connector-kafka-1.18.0.jar -P ./jars/
wget https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/3.0.1/flink-connector-kafka-3.0.1.jar -P ./jars/
wget https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/3.0.2-1.18/flink-connector-kafka-3.0.2-1.18.jar -P ./jars/
wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.6.1/kafka-clients-3.6.1.jar -P ./jars/

docker cp ./jars/flink-connector-kafka-3.0.2-1.18.jar flink-jobmanager:/opt/flink/lib/
docker cp ./jars/kafka-clients-3.6.1.jar flink-jobmanager:/opt/flink/lib/

docker cp ./jars/flink-connector-kafka-3.0.2-1.18.jar flink-taskmanager:/opt/flink/lib/
docker cp ./jars/kafka-clients-3.6.1.jar flink-taskmanager:/opt/flink/lib/
docker restart flink-jobmanager flink-taskmanager
docker exec -it flink-jobmanager bash
```
Step 1: Start Flink SQL CLI:
```bash

docker exec -it flink-jobmanager bash
./bin/sql-client.sh
```

Step 2: Run the following SQL commands:
```bash
-- Create source table
CREATE TABLE kafka_source (
  `value` STRING
) WITH (
  'connector' = 'kafka',
  'topic' = 'test-topic',
  'properties.bootstrap.servers' = 'kafka:9092',
  'properties.group.id' = 'flink-group',
  'format' = 'raw',
  'scan.startup.mode' = 'latest-offset'
);

-- Create print sink
CREATE TABLE print_sink (
  `value` STRING
) WITH (
  'connector' = 'print'
);

-- Stream data
INSERT INTO print_sink
SELECT * FROM kafka_source;

exit;
```
Then exit from the container and run following commands

✅ 3. Send messages to the topic
In a separate terminal, produce some Kafka messages:
```bash
docker exec -it kafka kafka-console-producer --topic test-topic --bootstrap-server kafka:9092
```
Or view logs from the TaskManager container:
Type a few lines:
```bash
flink test
flink + kafka rocks
hello again
```

```bash
docker logs -f flink-taskmanager
```
✅ 6. See output in Flink logs
In your Flink JobManager container logs, you’ll now see lines like:
```bash
+I[flink test]
+I[flink + kafka rocks]
+I[hello again]
```
