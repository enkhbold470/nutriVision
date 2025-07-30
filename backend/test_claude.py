#!/usr/bin/env python3
"""
Test script for Claude integration in NurtiVision
Run this to verify that Claude is working correctly
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_claude_connection():
    """Test if Claude API key is configured correctly"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env file")
        print("   Please add your Claude API key to .env:")
        print("   ANTHROPIC_API_KEY=your_api_key_here")
        return False
    
    if api_key == 'your_claude_api_key_here':
        print("❌ Please replace the placeholder API key with your actual Claude API key")
        return False
    
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        # Test simple message
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[{"role": "user", "content": "Hello! This is a test."}]
        )
        
        print("✅ Claude API connection successful!")
        print(f"   Response: {message.content[0].text[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Claude API connection failed: {str(e)}")
        return False

def test_food_analyzer():
    """Test the ClaudeFoodAnalyzer class"""
    try:
        from claude_food_analyzer import ClaudeFoodAnalyzer
        
        analyzer = ClaudeFoodAnalyzer()
        print("✅ ClaudeFoodAnalyzer imported successfully!")
        
        # Test recommendations without image
        test_goals = {"goal_weight_loss": 10, "max_daily_calories": 1800}
        test_nutrition = {"calories": 1200, "protein": 80}
        
        recommendations = analyzer.get_food_recommendations(test_goals, test_nutrition)
        print("✅ Food recommendations working!")
        print(f"   Sample recommendation: {recommendations.get('recommendations', ['None'])[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ ClaudeFoodAnalyzer test failed: {str(e)}")
        return False

def test_flask_endpoints():
    """Test if Flask endpoints are working"""
    base_url = "http://localhost:5000"
    
    # Test basic endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Flask server is running!")
        else:
            print(f"❌ Flask server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask server not running. Start it with: python app.py")
        return False
    
    # Test chat endpoint
    try:
        response = requests.post(f"{base_url}/api/chat", json={
            "message": "What's a healthy snack?",
            "user_id": None
        })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint working!")
            print(f"   Sample response: {data.get('message', '')[:50]}...")
        else:
            print(f"❌ Chat endpoint failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Chat endpoint test failed: {str(e)}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Claude Integration for NurtiVision\n")
    
    tests = [
        ("Claude API Connection", test_claude_connection),
        ("Food Analyzer Module", test_food_analyzer),
        ("Flask Endpoints", test_flask_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append(False)
    
    print(f"\n📊 Test Results:")
    print(f"   Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! Claude integration is ready to use.")
        print("\n🚀 Next steps:")
        print("   1. Start your Flask server: python app.py")
        print("   2. Test food image upload to /api/analyze-food")
        print("   3. Integrate with your VR frontend")
    else:
        print("\n⚠️  Some tests failed. Check the errors above and:")
        print("   1. Ensure your .env file has the correct ANTHROPIC_API_KEY")
        print("   2. Install requirements: pip install -r requirements.txt")
        print("   3. Start Flask server: python app.py")

if __name__ == "__main__":
    main()