# 🔥 Real-Time Word Frequency Application

A scalable real-time word frequency application built with **PySpark Structured Streaming**, **Apache Kafka**, **Streamlit**, and **Docker**. This application supports concurrent user input, processes text in real-time, and displays live word frequency statistics.

## 🎯 Features

- **Multi-user Support**: Handle concurrent users submitting text simultaneously
- **Real-time Processing**: Process text streams using PySpark Structured Streaming
- **Live Dashboard**: Interactive Streamlit dashboard with real-time updates
- **Scalable Architecture**: Microservices architecture with Docker containers
- **Data Persistence**: Redis for storing word frequency data
- **API-based**: RESTful API for text submission
- **Containerized**: Fully containerized with Docker Compose

## 🏗️ Architecture

```graph

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │     FastAPI     │    │     Kafka       │
│   Dashboard     │◄──►│     Producer    │───►│     Broker      │
│                 │    │       API       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         │              ┌─────────────────┐             │
         │              │      Redis      │             │
         └─────────────►│   (Word Counts) │◄────────────┘
                        │                 │             │
                        └─────────────────┘             │
                                   ▲                    │
                                   │                    │
                        ┌─────────────────┐             │
                        │     PySpark     │◄────────────┘
                        │    Streaming    │
                        │                 │
                        └─────────────────┘
```

## 🛠️ Tech Stack

- **Apache Kafka**: Message streaming platform
- **Apache Spark (PySpark)**: Real-time stream processing
- **Streamlit**: Interactive web dashboard
- **FastAPI**: High-performance API framework
- **Redis**: In-memory data store
- **Docker & Docker Compose**: Containerization
- **Python 3.10+**: Primary programming language

## 📦 Project Structure

```structure
aio2025-pyspark/
├── docker-compose.yml          # Multi-container Docker application
├── producer-api/               # FastAPI producer service
│   ├── main.py                # API endpoints and Kafka producer
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Container configuration
├── spark-job/                 # PySpark streaming application
│   ├── wordcount.py          # Spark Structured Streaming job
│   └── Dockerfile            # Container configuration
├── dashboard/                 # Streamlit dashboard
│   ├── app.py                # Dashboard application
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Container configuration
├── scripts/                   # Utility scripts
│   ├── kafka-init.sh         # Kafka topic initialization
│   └── simulate_users.py     # User simulation script
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 8GB of available RAM
- Ports 8000, 8501, 9092, 6379 available

### 1. Clone and Start Services

```bash
# Clone the repository
cd /Users/thuanduong/Repository/aio2025-pyspark

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 2. Wait for Services to Initialize

```bash
# Monitor logs to ensure all services are ready
docker-compose logs -f

# Check individual service logs
docker-compose logs kafka
docker-compose logs spark-job
docker-compose logs producer-api
docker-compose logs dashboard
```

### 3. Access the Application

- **Streamlit Dashboard**: http://localhost:8501
- **Producer API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Test the Application

1. Open the Streamlit dashboard at http://localhost:8501
2. Enter text in the input box and click "Submit Text"
3. Watch the word frequencies update in real-time
4. Try submitting multiple texts to see cumulative counts

## 🧪 Testing & Simulation

### Manual Testing

1. Open the dashboard: http://localhost:8501
2. Submit various texts through the web interface
3. Observe real-time updates in charts and tables

### Automated User Simulation

```bash
# Install Python dependencies for simulation
pip install requests

# Run user simulation script
python scripts/simulate_users.py
```

This will simulate multiple users submitting text at random intervals.

### API Testing

```bash
# Test API health
curl http://localhost:8000/health

# Submit text via API
curl -X POST "http://localhost:8000/submit_text" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello world from API", "user_id": "test_user"}'
```

## 📊 Dashboard Features

### Real-time Visualizations

- **Bar Chart**: Top words by frequency
- **Pie Chart**: Word distribution
- **Data Table**: Searchable word frequency table

### Interactive Controls

- **Auto-refresh**: Configurable refresh intervals
- **Search**: Filter words by text search
- **Display Settings**: Adjust number of words shown
- **Export**: Download word frequency data as CSV

### System Monitoring

- **Health Checks**: Monitor API and Redis connectivity
- **Metrics**: Track total words, unique words, last update time
- **Real-time Updates**: Live data refresh without page reload

## 🔧 Configuration

### Environment Variables

#### Producer API

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker addresses (default: kafka:29092)
- `REDIS_HOST`: Redis hostname (default: redis)
- `REDIS_PORT`: Redis port (default: 6379)

#### Spark Job

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker addresses
- `REDIS_HOST`: Redis hostname
- `REDIS_PORT`: Redis port

#### Dashboard

- `PRODUCER_API_URL`: Producer API URL (default: http://producer-api:8000)
- `REDIS_HOST`: Redis hostname
- `REDIS_PORT`: Redis port

### Scaling Configuration

#### Kafka Partitions

```bash
# Increase partitions for higher throughput
docker exec kafka kafka-topics --alter --topic user_text --partitions 6 --bootstrap-server localhost:9092
```

#### Spark Resources

```yaml
# In docker-compose.yml
spark-job:
  environment:
    - SPARK_WORKER_CORES=4
    - SPARK_WORKER_MEMORY=4g
    - SPARK_DRIVER_MEMORY=2g
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Services Not Starting

```bash
# Check logs
docker-compose logs [service-name]

# Restart specific service
docker-compose restart [service-name]

# Complete reset
docker-compose down -v
docker-compose up -d
```

#### 2. Kafka Connection Issues

```bash
# Check Kafka topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Check consumer groups
docker exec kafka kafka-consumer-groups --list --bootstrap-server localhost:9092
```

#### 3. No Data in Dashboard

```bash
# Check Redis data
docker exec redis redis-cli get word_counts

# Check Spark job logs
docker-compose logs spark-job

# Test API connectivity
curl http://localhost:8000/health
```

#### 4. Memory Issues

```bash
# Check container resource usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Memory > Increase to 8GB+
```

### Performance Tuning

#### 1. Kafka Optimization

```yaml
kafka:
  environment:
    KAFKA_NUM_NETWORK_THREADS: 8
    KAFKA_NUM_IO_THREADS: 8
    KAFKA_SOCKET_SEND_BUFFER_BYTES: 102400
    KAFKA_SOCKET_RECEIVE_BUFFER_BYTES: 102400
```

#### 2. Spark Optimization

```python
# In wordcount.py
spark = SparkSession.builder \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.streaming.metricsEnabled", "true")
```

## 🚀 Production Deployment

### Security Considerations

1. **API Authentication**: Add JWT or API key authentication
2. **Network Security**: Use VPC and security groups
3. **Data Encryption**: Enable SSL/TLS for Kafka and Redis
4. **Container Security**: Scan images for vulnerabilities

### Scaling Recommendations

1. **Horizontal Scaling**: Multiple Spark workers and API instances
2. **Load Balancing**: Use nginx or cloud load balancers
3. **Data Persistence**: Use managed Redis or persistent volumes
4. **Monitoring**: Add Prometheus, Grafana, and log aggregation

### Cloud Deployment

#### AWS

- Use EKS for container orchestration
- Amazon MSK for managed Kafka
- ElastiCache for managed Redis
- Application Load Balancer for traffic distribution

#### Azure

- Use AKS for container orchestration
- Event Hubs for Kafka-compatible messaging
- Azure Cache for Redis
- Application Gateway for load balancing

## 📈 Monitoring & Observability

### Metrics to Monitor

1. **Throughput**: Messages per second processed
2. **Latency**: End-to-end processing latency
3. **Error Rates**: Failed message processing
4. **Resource Usage**: CPU, memory, disk usage
5. **Queue Depth**: Kafka topic lag

### Logging

Each service produces structured logs:

- **Producer API**: Request/response logs, error tracking
- **Spark Job**: Processing metrics, batch information
- **Dashboard**: User interactions, system status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.
#   R e a l - T i m e - W o r d - F r e q u e n c y - A n a l y t i c s - P l a t f o r m  
 # Desuuy-Real-Time-Word-Frequency-Analytics-Platform
