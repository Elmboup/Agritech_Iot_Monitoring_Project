FROM apache/airflow:2.9.2-python3.10

# Ajouter requirements.txt et installer les dépendances Python
ADD requirements.txt .

RUN pip install -r requirements.txt

# Installer PySpark
RUN pip install pyspark

USER root
RUN apt-get update && apt-get install -y curl && \
    curl -o /tmp/openjdk.tar.gz https://download.java.net/openjdk/jdk11/ri/openjdk-11+28_linux-x64_bin.tar.gz && \
    mkdir -p /usr/lib/jvm/java-11-openjdk && \
    tar -xzf /tmp/openjdk.tar.gz -C /usr/lib/jvm/java-11-openjdk --strip-components=1 && \
    rm /tmp/openjdk.tar.gz




# Définir JAVA_HOME (important pour Spark)
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER airflow



