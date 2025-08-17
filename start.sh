#!/bin/bash

set -e

echo "🚀 Starting Real-Time Word Count Application"
echo "============================================="

# Check if docker and docker-compose are available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Stop any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose down -v 2>/dev/null || true

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to initialize..."

# Wait for Kafka
echo "   - Waiting for Kafka..."
while ! docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 &>/dev/null; do
    sleep 2
done

# Wait for Redis
echo "   - Waiting for Redis..."
while ! docker exec redis redis-cli ping &>/dev/null; do
    sleep 2
done

# Wait for Producer API
echo "   - Waiting for Producer API..."
while ! curl -s http://localhost:8000/health &>/dev/null; do
    sleep 2
done

echo "✅ All services are ready!"
echo ""
echo "🌐 Access Points:"
echo "   Dashboard:   http://localhost:8501"
echo "   API:         http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo ""
echo "🔍 Service Status:"
docker-compose ps

echo ""
echo "📊 To view live logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"
echo ""
echo "🎉 Application is ready to use!"
