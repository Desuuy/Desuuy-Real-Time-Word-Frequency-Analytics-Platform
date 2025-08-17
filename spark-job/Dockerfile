FROM apache/spark:3.5.0-scala2.12-java11-python3-ubuntu

USER root

# Install Python dependencies
RUN pip3 install --no-cache-dir redis

# Copy application code
COPY . /app
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.7-src.zip:$PYTHONPATH

# Command to run the application
CMD ["/opt/spark/bin/spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0", "wordcount.py"]
