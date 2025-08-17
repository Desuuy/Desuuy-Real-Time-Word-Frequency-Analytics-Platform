import requests
import time
import random

# Configuration
PRODUCER_API_URL = "http://localhost:8000"

# Sample texts for testing
sample_texts = [
    "The quick brown fox jumps over the lazy dog",
    "Python is a great programming language for data science",
    "Apache Kafka enables real-time data streaming",
    "Streamlit makes building data apps incredibly easy",
    "Docker containers provide consistent deployment environments",
    "Machine learning models require quality training data",
    "Real-time analytics help businesses make faster decisions",
    "Cloud computing has revolutionized software development",
    "Big data processing requires distributed computing frameworks",
    "User experience design is crucial for application success"
]

def simulate_user_input():
    """Simulate multiple users submitting text"""
    user_count = 1
    
    while True:
        try:
            # Random text and user
            text = random.choice(sample_texts)
            user_id = f"user_{random.randint(1, 10)}"
            
            # Submit text
            response = requests.post(
                f"{PRODUCER_API_URL}/submit_text",
                json={"text": text, "user_id": user_id},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ Submission {user_count}: User {user_id} - '{text[:50]}...'")
            else:
                print(f"❌ Failed submission {user_count}: {response.text}")
            
            user_count += 1
            
            # Random delay between 1-5 seconds
            time.sleep(random.uniform(1, 5))
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping simulation...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    print("🚀 Starting user simulation...")
    print("Press Ctrl+C to stop")
    simulate_user_input()
