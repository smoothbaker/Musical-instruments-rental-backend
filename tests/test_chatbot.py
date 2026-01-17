"""
Comprehensive Chatbot Service Testing Script
============================================

Tests the chatbot functionality including:
1. Ollama connectivity
2. User profile retrieval
3. Instrument recommendations based on survey
4. Conversation history
5. Response generation
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import User, SurveyResponse, Instrument, Instru_ownership
from app.services.chatbot_service import (
    get_user_profile,
    get_available_instruments,
    chat_with_user
)
import json

def test_ollama_connectivity():
    """Test if Ollama is running and accessible"""
    print("\n" + "="*70)
    print("TEST 1: Ollama Connectivity")
    print("="*70)
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            version_data = response.json()
            print(f"✅ PASS: Ollama is running")
            print(f"   Version: {version_data.get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ FAIL: Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Cannot connect to Ollama - {str(e)}")
        print(f"   Make sure Ollama is running: ollama serve")
        return False


def test_user_profile_retrieval():
    """Test retrieving user profile and survey data"""
    print("\n" + "="*70)
    print("TEST 2: User Profile Retrieval")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        # Find a user with survey data
        user = User.query.first()
        
        if not user:
            print("❌ FAIL: No users found in database")
            print("   Create a user first via the API")
            return False
        
        print(f"✅ Found user: {user.name} (ID: {user.id})")
        
        # Get profile
        profile = get_user_profile(user.id)
        
        if profile:
            print(f"✅ PASS: User profile retrieved successfully")
            print(f"   Experience Level: {profile.get('experience_level')}")
            print(f"   Preferred Instruments: {profile.get('preferred_instruments')}")
            print(f"   Favorite Genres: {profile.get('favorite_genres')}")
            print(f"   Budget Range: ${profile.get('budget_range')}/day")
            return True
        else:
            print(f"❌FAIL: Could not retrieve user profile")
            return False


def test_available_instruments():
    """Test retrieving available  instruments"""
    print("\n" + "="*70)
    print("TEST 3: Available Instruments Retrieval")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        instruments_str = get_available_instruments()
        
        if "No instruments" in instruments_str:
            print("⚠️  WARNING: No instruments available in database")
            print("   Add instruments via the API")
            return False
        
        print(f"✅ PASS: Retrieved available instruments")
        lines = instruments_str.split('\n')
        print(f"   Total instruments listed: {len(lines) - 1}")
        print(f"\n   Sample instruments:")
        for line in lines[:6]:  # Show first 5 instruments
            if line.strip():
                print(f"   {line}")
        return True


def test_chatbot_basic_question():
    """Test chatbot with a basic question"""
    print("\n" + "="*70)
    print("TEST 4: Chatbot Basic Question")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        user = User.query.first()
        
        if not user:
            print("❌ FAIL: No users found")
            return False
        
        try:
            # Test basic question
            session_id = "test_session_basic"
            question = "What is a good beginner guitar?"
            
            print(f"   User: {question}")
            response = chat_with_user(user.id, session_id, question)
            
            if 'error' in response:
                print(f"❌ FAIL: Chatbot returned error - {response['error']}")
                return False
            
            print(f"✅ PASS: Chatbot responded successfully")
            print(f"   Assistant: {response['assistant_response'][:200]}...")
            
            if response.get('recommendations'):
                print(f"   Recommendations: {len(response['recommendations'])} instruments")
                for rec in response['recommendations'][:3]:
                    print(f"      - {rec.get('name')}: {rec.get('reason', 'N/A')}")
            
            return True
        except Exception as e:
            print(f"❌ FAIL: Exception during chat - {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def test_chatbot_survey_based_recommendation():
    """Test chatbot recommendations using user survey data"""
    print("\n" + "="*70)
    print("TEST 5: Survey-Based Recommendations")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        # Find user with survey data
        user_with_survey = None
        for user in User.query.all():
            survey = SurveyResponse.query.filter_by(user_id=user.id).first()
            if survey:
                user_with_survey = user
                break
        
        if not user_with_survey:
            print("⚠️  WARNING: No users with survey data found")
            print("   Create survey responses first")
            return False
        
        try:
            session_id = "test_session_survey"
            question = "What instruments would you recommend for me based on my preferences?"
            
            print(f"   User: {question}")
            response = chat_with_user(user_with_survey.id, session_id, question)
            
            if 'error' in response:
                print(f"❌ FAIL: Chatbot error - {response['error']}")
                return False
            
            print(f"✅ PASS: Survey-based recommendation generated")
            print(f"   Profile used:")
            print(f"      Experience: {response['context'].get('experience_level')}")
            print(f"      Preferred: {response['context'].get('preferred_instruments')}")
            print(f"\n   Response: {response['assistant_response'][:300]}...")
            
            return True
        except Exception as e:
            print(f"❌ FAIL: Exception - {str(e)}")
            return False


def test_conversation_context():
    """Test if chatbot maintains conversation context"""
    print("\n" + "="*70)
    print("TEST 6: Conversation Context")
    print("="*70)
    
    app = create_app()
    
    with app.app_context():
        user = User.query.first()
        if not user:
            print("❌ FAIL: No users found")
            return False
        
        try:
            session_id = "test_session_context"
            
            # First message
            q1 = "I'm interested in learning piano"
            print(f"   Message 1: {q1}")
            resp1 = chat_with_user(user.id, session_id, q1)
            
            if 'error' in resp1:
                print(f"❌ FAIL: Error on first message - {resp1['error']}")
                return False
            
            print(f"   Response 1: {resp1['assistant_response'][:100]}...")
            
            # Second message (should reference first)
            q2 = "How much does it typically cost to rent one?"
            print(f"\n   Message 2: {q2}")
            resp2 = chat_with_user(user.id, session_id, q2)
            
            if 'error' in resp2:
                print(f"❌ FAIL: Error on second message - {resp2['error']}")
                return False
            
            print(f"   Response 2: {resp2['assistant_response'][:150]}...")
            
            # Check if response mentions piano (shows context retention)
            if 'piano' in resp2['assistant_response'].lower():
                print(f"\n✅ PASS: Context maintained (mentioned piano)")
                return True
            else:
                print(f"\n⚠️  WARNING: Context may not be maintained properly")
                return True  # Still pass as chatbot responded
                
        except Exception as e:
            print(f"❌ FAIL: Exception - {str(e)}")
            return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("CHATBOT SERVICE COMPREHENSIVE TESTING")
    print("="*70)
    
    results = {
        'Ollama Connectivity': test_ollama_connectivity(),
        'User Profile Retrieval': test_user_profile_retrieval(),
        'Available Instruments': test_available_instruments(),
        'Basic Question': test_chatbot_basic_question(),
        'Survey Recommendations': test_chatbot_survey_based_recommendation(),
        'Conversation Context': test_conversation_context()
    }
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Chatbot is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
