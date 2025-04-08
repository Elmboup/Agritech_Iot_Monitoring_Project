from pyspark.sql import SparkSession
from pyspark.sql.functions import expr

# Créer une session Spark
spark = SparkSession.builder \
    .appName("KafkaSparkStreaming") \
    .master("local[*]") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
    .getOrCreate()

# Lire les données de Kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "test_topic") \
    .load()

# Kafka stocke les messages en format binaire, donc nous devons les convertir
messages_df = kafka_df.selectExpr("CAST(value AS STRING)")

# Convertir la colonne 'value' en un format JSON et extraire les champs
json_df = messages_df.selectExpr("json_tuple(value, 'name', 'age') as (name, age)")

# Afficher les résultats dans la console (streaming)
query = json_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# Attendre la fin du streaming
query.awaitTermination()
