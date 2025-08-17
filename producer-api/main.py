from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Word Count Producer API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = 'user_text'

# Initialize Kafka producer
producer = None

def get_kafka_producer():
    global producer
    if producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                retries=5,
                retry_backoff_ms=100,
                request_timeout_ms=30000,
                api_version=(2, 0, 2)
            )
            logger.info(f"Kafka producer initialized with servers: {KAFKA_BOOTSTRAP_SERVERS}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise
    return producer

class TextInput(BaseModel):
    text: str
    user_id: str = "anonymous"

@app.on_event("startup")
async def startup_event():
    """Initialize Kafka producer on startup"""
    try:
        get_kafka_producer()
        logger.info("Producer API started successfully")
    except Exception as e:
        logger.error(f"Failed to start producer API: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close Kafka producer on shutdown"""
    global producer
    if producer:
        producer.close()
        logger.info("Kafka producer closed")

@app.get("/")
async def root():
    return {"message": "Word Count Producer API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Kafka connection
        kafka_producer = get_kafka_producer()
        return {
            "status": "healthy",
            "kafka_connected": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/submit_text")
async def submit_text(text_input: TextInput):
    """Submit text to Kafka for processing"""
    try:
        if not text_input.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Prepare message
        message = {
            "text": text_input.text.strip(),
            "user_id": text_input.user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to Kafka
        kafka_producer = get_kafka_producer()
        future = kafka_producer.send(
            KAFKA_TOPIC,
            value=message,
            key=text_input.user_id
        )
        
        # Wait for the message to be sent
        record_metadata = future.get(timeout=10)
        
        logger.info(f"Message sent to Kafka: topic={record_metadata.topic}, "
                   f"partition={record_metadata.partition}, offset={record_metadata.offset}")
        
        return {
            "status": "success",
            "message": "Text submitted successfully",
            "kafka_metadata": {
                "topic": record_metadata.topic,
                "partition": record_metadata.partition,
                "offset": record_metadata.offset
            }
        }
        
    except KafkaError as e:
        logger.error(f"Kafka error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send message to Kafka: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
