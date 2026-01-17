"""Tests for chatbot system"""

import json
import uuid
from datetime import datetime
from app import create_app, db
from app.models import User, ChatMessage, SurveyResponse, Instrument, Instru_ownership
from flask_jwt_extended import create_access_token


def test_chatbot_setup():
    """Setup test client and database"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # Create test user
        user = User(
            email='testuser@example.com',
            name='Test User',
            phone='1234567890',
            user_type='renter'
        )
        user.set_password('testpass123')
        db.session.add(user)
        
        # Create survey response for the user
        survey = SurveyResponse(
            user_id=1,
            preferred_instruments='Guitar, Piano',
            experience_level='intermediate',
            favorite_genres='Jazz, Blues',
            budget_range='25-50',
            rental_frequency='weekly',
            use_case='hobby',
            location='New York'
        )
        db.session.add(survey)
        
        # Create test instruments
        guitar = Instrument(
            name='Acoustic Guitar',
            category='String',
            brand='Yamaha',
            model='FS800'
        )
        piano = Instrument(
            name='Digital Piano',
            category='Keyboard',
            brand='Casio',
            model='CDP-S110'
        )
        db.session.add(guitar)
        db.session.add(piano)
        db.session.commit()
        
        # Create instrument ownerships
        ownership1 = Instru_ownership(
            user_id=1,
            instrument_id=1,
            condition='good',
            daily_rate=20.0,
            location='Manhattan',
            is_available=True
        )
        ownership2 = Instru_ownership(
            user_id=1,
            instrument_id=2,
            condition='excellent',
            daily_rate=35.0,
            location='Brooklyn',
            is_available=True
        )
        db.session.add(ownership1)
        db.session.add(ownership2)
        db.session.commit()
        
        return app


def test_chat_endpoint():
    """Test basic chatbot endpoint"""
    app = test_chatbot_setup()
    
    with app.test_client() as client:
        # Get JWT token
        response = client.post('/api/auth/login', json={
            'email': 'testuser@example.com',
            'password': 'testpass123'
        })
        
        if response.status_code == 200:
            token = response.json.get('access_token')
            
            # Test chat endpoint
            session_id = str(uuid.uuid4())
            response = client.post(
                '/api/chatbot/chat',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'session_id': session_id,
                    'message': 'What instruments would be good for learning jazz?'
                }
            )
            
            print("Chat Response Status:", response.status_code)
            print("Chat Response:", json.dumps(response.json, indent=2))
            
            assert response.status_code == 200
            assert 'assistant_response' in response.json
            assert 'session_id' in response.json


def test_conversation_history():
    """Test getting conversation history"""
    app = test_chatbot_setup()
    
    with app.app_context():
        with app.test_client() as client:
            # Get token and create messages
            response = client.post('/api/auth/login', json={
                'email': 'testuser@example.com',
                'password': 'testpass123'
            })
            
            if response.status_code == 200:
                token = response.json.get('access_token')
                session_id = str(uuid.uuid4())
                
                # Create test messages
                msg1 = ChatMessage(
                    user_id=1,
                    session_id=session_id,
                    message_type='user',
                    content='What is a good starter instrument?'
                )
                msg2 = ChatMessage(
                    user_id=1,
                    session_id=session_id,
                    message_type='assistant',
                    content='For beginners, I recommend starting with...'
                )
                db.session.add(msg1)
                db.session.add(msg2)
                db.session.commit()
                
                # Get history
                response = client.get(
                    f'/api/chatbot/history/{session_id}',
                    headers={'Authorization': f'Bearer {token}'}
                )
                
                print("History Response Status:", response.status_code)
                print("History Response:", json.dumps(response.json, indent=2))
                
                assert response.status_code == 200
                assert len(response.json) == 2


def test_get_sessions():
    """Test getting all user sessions"""
    app = test_chatbot_setup()
    
    with app.app_context():
        with app.test_client() as client:
            # Get token
            response = client.post('/api/auth/login', json={
                'email': 'testuser@example.com',
                'password': 'testpass123'
            })
            
            if response.status_code == 200:
                token = response.json.get('access_token')
                
                # Create multiple sessions with messages
                for i in range(2):
                    session_id = str(uuid.uuid4())
                    msg = ChatMessage(
                        user_id=1,
                        session_id=session_id,
                        message_type='user',
                        content=f'Test message {i}'
                    )
                    db.session.add(msg)
                db.session.commit()
                
                # Get sessions
                response = client.get(
                    '/api/chatbot/sessions',
                    headers={'Authorization': f'Bearer {token}'}
                )
                
                print("Sessions Response Status:", response.status_code)
                print("Sessions Response:", json.dumps(response.json, indent=2))
                
                assert response.status_code == 200
                assert 'sessions' in response.json


def test_empty_message_error():
    """Test error handling for empty message"""
    app = test_chatbot_setup()
    
    with app.test_client() as client:
        response = client.post('/api/auth/login', json={
            'email': 'testuser@example.com',
            'password': 'testpass123'
        })
        
        if response.status_code == 200:
            token = response.json.get('access_token')
            
            # Send empty message
            response = client.post(
                '/api/chatbot/chat',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'session_id': str(uuid.uuid4()),
                    'message': ''
                }
            )
            
            print("Empty Message Response Status:", response.status_code)
            assert response.status_code == 400


def test_unauthorized_access():
    """Test that unauthenticated users cannot access chatbot"""
    app = test_chatbot_setup()
    
    with app.test_client() as client:
        response = client.post(
            '/api/chatbot/chat',
            json={
                'session_id': str(uuid.uuid4()),
                'message': 'Hello'
            }
        )
        
        print("Unauthorized Response Status:", response.status_code)
        assert response.status_code == 401


def test_clear_session():
    """Test clearing a conversation session"""
    app = test_chatbot_setup()
    
    with app.app_context():
        with app.test_client() as client:
            response = client.post('/api/auth/login', json={
                'email': 'testuser@example.com',
                'password': 'testpass123'
            })
            
            if response.status_code == 200:
                token = response.json.get('access_token')
                session_id = str(uuid.uuid4())
                
                # Create messages
                for i in range(3):
                    msg = ChatMessage(
                        user_id=1,
                        session_id=session_id,
                        message_type='user' if i % 2 == 0 else 'assistant',
                        content=f'Message {i}'
                    )
                    db.session.add(msg)
                db.session.commit()
                
                # Clear session
                response = client.delete(
                    f'/api/chatbot/clear-session/{session_id}',
                    headers={'Authorization': f'Bearer {token}'}
                )
                
                print("Clear Session Response:", json.dumps(response.json, indent=2))
                assert response.status_code == 200
                assert response.json['deleted_count'] == 3


if __name__ == '__main__':
    print("=" * 60)
    print("CHATBOT SYSTEM TESTS")
    print("=" * 60)
    
    print("\n1. Testing Chat Endpoint...")
    try:
        test_chat_endpoint()
        print("✓ Chat endpoint test passed")
    except AssertionError as e:
        print(f"✗ Chat endpoint test failed: {e}")
    except Exception as e:
        print(f"✗ Chat endpoint test error: {e}")
    
    print("\n2. Testing Conversation History...")
    try:
        test_conversation_history()
        print("✓ Conversation history test passed")
    except Exception as e:
        print(f"✗ Conversation history test error: {e}")
    
    print("\n3. Testing Get Sessions...")
    try:
        test_get_sessions()
        print("✓ Get sessions test passed")
    except Exception as e:
        print(f"✗ Get sessions test error: {e}")
    
    print("\n4. Testing Empty Message Error...")
    try:
        test_empty_message_error()
        print("✓ Empty message error test passed")
    except Exception as e:
        print(f"✗ Empty message error test error: {e}")
    
    print("\n5. Testing Unauthorized Access...")
    try:
        test_unauthorized_access()
        print("✓ Unauthorized access test passed")
    except Exception as e:
        print(f"✗ Unauthorized access test error: {e}")
    
    print("\n6. Testing Clear Session...")
    try:
        test_clear_session()
        print("✓ Clear session test passed")
    except Exception as e:
        print(f"✗ Clear session test error: {e}")
    
    print("\n" + "=" * 60)
    print("Test suite complete!")
    print("=" * 60)
