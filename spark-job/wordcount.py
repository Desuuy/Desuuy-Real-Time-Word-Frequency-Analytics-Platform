from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, explode, split, lower, regexp_replace, length, desc
from pyspark.sql.types import StructType, StructField, StringType
import redis
import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Create Spark session with Kafka support"""
    return SparkSession.builder \
        .appName("RealTimeWordCount") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
        .config("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.HDFSBackedStateStoreProvider") \
        .getOrCreate()

def process_batch(batch_df, batch_id):
    """Process each batch of streaming data"""
    try:
        if batch_df.count() > 0:
            logger.info(f"Processing batch {batch_id} with {batch_df.count()} records")
            
            # Show some sample data for debugging
            logger.info("Sample data from batch:")
            batch_df.show(5, truncate=False)
            
            # Connect to Redis
            redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', '6379')),
                decode_responses=True
            )
            
            # Get current word counts from Redis
            current_counts = {}
            try:
                stored_counts = redis_client.get('word_counts')
                if stored_counts:
                    current_counts = json.loads(stored_counts)
            except Exception as e:
                logger.warning(f"Could not load existing counts from Redis: {e}")
            
            # Convert batch to list of word counts
            word_counts = batch_df.collect()
            
            # Update cumulative counts
            for row in word_counts:
                word = row['word']
                count = row['count']
                current_counts[word] = current_counts.get(word, 0) + count
            
            # Store updated counts in Redis
            redis_client.set('word_counts', json.dumps(current_counts))
            
            # Store metadata
            metadata = {
                'last_updated': datetime.now().isoformat(),
                'total_words': len(current_counts),
                'batch_id': batch_id,
                'processed_records': batch_df.count()
            }
            redis_client.set('word_counts_metadata', json.dumps(metadata))
            
            logger.info(f"Updated Redis with {len(current_counts)} unique words")
            
    except Exception as e:
        logger.error(f"Error processing batch {batch_id}: {e}")

def main():
    """Main streaming application"""
    
    # Environment variables
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    kafka_topic = 'user_text'
    
    logger.info(f"Starting Spark Streaming job with Kafka servers: {kafka_servers}")
    
    # Create Spark session
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    # Define schema for the incoming JSON data
    json_schema = StructType([
        StructField("text", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("timestamp", StringType(), True)
    ])
    
    try:
        # Read from Kafka
        df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_servers) \
            .option("subscribe", kafka_topic) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()
        
        logger.info("Successfully connected to Kafka stream")
        
        # Parse JSON data
        parsed_df = df.select(
            from_json(col("value").cast("string"), json_schema).alias("data")
        ).select("data.*")
        
        # Clean and split text into words
        words_df = parsed_df \
            .filter(col("text").isNotNull() & (col("text") != "")) \
            .select(
                explode(
                    split(
                        lower(
                            regexp_replace(col("text"), "[^a-zA-Z0-9\\s]", "")
                        ), 
                        "\\s+"
                    )
                ).alias("word")
            ) \
            .filter(
                (col("word") != "") & 
                (length(col("word")) > 2)  # Filter out very short words
            )
        
        # Count words in each batch
        word_counts = words_df \
            .groupBy("word") \
            .count() \
            .orderBy(desc("count"))
        
        # Start streaming query with batch processing
        query = word_counts \
            .writeStream \
            .outputMode("complete") \
            .foreachBatch(process_batch) \
            .option("checkpointLocation", "/tmp/checkpoint") \
            .trigger(processingTime='5 seconds') \
            .start()
        
        logger.info("Streaming query started successfully")
        
        # Wait for termination
        query.awaitTermination()
        
    except Exception as e:
        logger.error(f"Error in main streaming loop: {e}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
