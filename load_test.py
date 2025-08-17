#!/usr/bin/env python3

import requests
import time
import threading
import random
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
PRODUCER_API_URL = "http://localhost:8000"
NUM_USERS = 10
NUM_MESSAGES_PER_USER = 20
DELAY_BETWEEN_MESSAGES = 1  # seconds

# Sample texts for load testing
SAMPLE_TEXTS = [
    "The quick brown fox jumps over the lazy dog",
    "Python is an amazing programming language for data processing",
    "Apache Kafka provides reliable real-time data streaming capabilities",
    "Streamlit makes building interactive data applications incredibly simple",
    "Docker containers ensure consistent deployment across different environments",
    "Machine learning algorithms require high-quality training datasets",
    "Real-time analytics enable businesses to make data-driven decisions quickly",
    "Cloud computing has fundamentally transformed modern software development",
    "Big data processing demands scalable distributed computing frameworks",
    "User experience design is critical for successful application adoption",
    "Microservices architecture promotes scalability and maintainability",
    "Continuous integration and deployment accelerate software delivery",
    "API-first design enables seamless system integration and interoperability",
    "Data visualization helps stakeholders understand complex information patterns",
    "Performance monitoring is essential for maintaining system reliability"
]

class LoadTester:
    def __init__(self):
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_response_time = 0
        self.lock = threading.Lock()
    
    def submit_text(self, user_id, message_id):
        """Submit a single text message"""
        try:
            text = random.choice(SAMPLE_TEXTS)
            
            start_time = time.time()
            response = requests.post(
                f"{PRODUCER_API_URL}/submit_text",
                json={"text": text, "user_id": f"load_test_user_{user_id}"},
                timeout=10
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            with self.lock:
                if response.status_code == 200:
                    self.successful_requests += 1
                    self.total_response_time += response_time
                    print(f"✅ User {user_id}, Message {message_id}: Success ({response_time:.2f}s)")
                else:
                    self.failed_requests += 1
                    print(f"❌ User {user_id}, Message {message_id}: Failed (HTTP {response.status_code})")
            
            return True
            
        except Exception as e:
            with self.lock:
                self.failed_requests += 1
            print(f"❌ User {user_id}, Message {message_id}: Exception - {e}")
            return False
    
    def user_simulation(self, user_id):
        """Simulate a single user sending multiple messages"""
        print(f"🚀 Starting user {user_id} simulation...")
        
        for message_id in range(1, NUM_MESSAGES_PER_USER + 1):
            self.submit_text(user_id, message_id)
            
            # Random delay between messages
            delay = random.uniform(0.5, DELAY_BETWEEN_MESSAGES * 2)
            time.sleep(delay)
        
        print(f"✅ User {user_id} simulation completed")
    
    def run_load_test(self):
        """Run the complete load test"""
        print(f"🧪 Starting load test with {NUM_USERS} users")
        print(f"   Each user will send {NUM_MESSAGES_PER_USER} messages")
        print(f"   Total expected messages: {NUM_USERS * NUM_MESSAGES_PER_USER}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Create thread pool for concurrent users
        with ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
            futures = [
                executor.submit(self.user_simulation, user_id)
                for user_id in range(1, NUM_USERS + 1)
            ]
            
            # Wait for all users to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"❌ User simulation failed: {e}")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Print results
        self.print_results(total_duration)
    
    def print_results(self, duration):
        """Print load test results"""
        total_requests = self.successful_requests + self.failed_requests
        success_rate = (self.successful_requests / total_requests * 100) if total_requests > 0 else 0
        avg_response_time = (self.total_response_time / self.successful_requests) if self.successful_requests > 0 else 0
        throughput = total_requests / duration if duration > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 LOAD TEST RESULTS")
        print("=" * 60)
        print(f"Duration:              {duration:.2f} seconds")
        print(f"Total Requests:        {total_requests}")
        print(f"Successful Requests:   {self.successful_requests}")
        print(f"Failed Requests:       {self.failed_requests}")
        print(f"Success Rate:          {success_rate:.1f}%")
        print(f"Average Response Time: {avg_response_time:.3f} seconds")
        print(f"Throughput:            {throughput:.2f} requests/second")
        print("=" * 60)
        
        if success_rate >= 95:
            print("🎉 Load test PASSED! System performed well under load.")
            return True
        else:
            print("❌ Load test FAILED! System performance needs improvement.")
            return False

def check_api_availability():
    """Check if the API is available before running load test"""
    try:
        response = requests.get(f"{PRODUCER_API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is available. Starting load test...")
            return True
        else:
            print(f"❌ API health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure the application is running with: ./start.sh")
        return False

def main():
    print("🔥 Real-Time Word Count Application - Load Test")
    print("=" * 60)
    
    # Check API availability
    if not check_api_availability():
        sys.exit(1)
    
    # Run load test
    tester = LoadTester()
    success = tester.run_load_test()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
