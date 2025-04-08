from pyspark.sql import SparkSession

def run_spark_job():
    # Création de la session Spark
    spark = SparkSession.builder \
        .appName("Airflow-Spark-Test") \
        .master("spark://spark-master:7077") \
        .getOrCreate()

    # Exemple de transformation
    data = [("Alice", 29), ("Bob", 34), ("Charlie", 23)]
    df = spark.createDataFrame(data, ["Name", "Age"])
    df.show()

    # Afficher le nombre de lignes
    count = df.count()
    print(f"Nombre de lignes: {count}")

    spark.stop()
    return count
