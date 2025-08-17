#!/usr/bin/env python3

import requests
import time
import sys

def test_api_health():
    """Test if the producer API is healthy"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Producer API health check passed")
            return True
        else:
            print(f"❌ Producer API health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Producer API health check failed: {e}")
        return False

def test_text_submission():
    """Test text submission to the API"""
    try:
        test_data = {
            "text": "This is a test message for the real-time word count application",
            "user_id": "test_user"
        }
        
        response = requests.post(
            "http://localhost:8000/submit_text",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Text submission test passed")
            return True
        else:
            print(f"❌ Text submission test failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Text submission test failed: {e}")
        return False

def test_dashboard_access():
    """Test if the Streamlit dashboard is accessible"""
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard accessibility test passed")
            return True
        else:
            print(f"❌ Dashboard accessibility test failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard accessibility test failed: {e}")
        return False

def main():
    print("🧪 Running application tests...")
    print("=" * 40)
    
    tests = [
        ("API Health", test_api_health),
        ("Text Submission", test_text_submission),
        ("Dashboard Access", test_dashboard_access)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        if test_func():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the logs and services.")
        sys.exit(1)

if __name__ == "__main__":
    main()
