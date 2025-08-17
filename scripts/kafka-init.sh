#!/bin/bash

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
while ! nc -z kafka 29092; do
  sleep 1
done

echo "Kafka is ready. Creating topics..."

# Create topics
kafka-topics --create --topic user_text --bootstrap-server kafka:29092 --replication-factor 1 --partitions 3 --if-not-exists
kafka-topics --create --topic word_counts --bootstrap-server kafka:29092 --replication-factor 1 --partitions 1 --if-not-exists

echo "Topics created successfully!"

# List topics to verify
kafka-topics --list --bootstrap-server kafka:29092
