# Chatbot Implementation Examples

## Complete Implementation Guide with Code Examples

### Table of Contents
1. [Frontend Integration](#frontend-integration)
2. [Backend Usage](#backend-usage)
3. [Advanced Scenarios](#advanced-scenarios)
4. [Integration Patterns](#integration-patterns)

---

## Frontend Integration

### JavaScript/TypeScript Examples

#### Basic Chat Function
```javascript
class InstrumentChatbot {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.apiBase = 'http://localhost:5000/api';
    this.sessionId = this.generateSessionId();
    this.conversationHistory = [];
  }

  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  async sendMessage(message) {
    try {
      const response = await fetch(`${this.apiBase}/chatbot/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          message: message
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      this.conversationHistory.push({
        userMessage: data.user_message,
        assistantResponse: data.assistant_response,
        recommendations: data.recommendations,
        timestamp: data.created_at
      });

      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async getRecommendations(additionalContext = '') {
    try {
      const response = await fetch(`${this.apiBase}/chatbot/recommend-for-me`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          message: additionalContext
        })
      });

      return await response.json();
    } catch (error) {
      console.error('Error getting recommendations:', error);
      throw error;
    }
  }

  async getHistory() {
    try {
      const response = await fetch(`${this.apiBase}/chatbot/history/${this.sessionId}`, {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`
        }
      });

      return await response.json();
    } catch (error) {
      console.error('Error fetching history:', error);
      throw error;
    }
  }

  async clearSession() {
    try {
      const response = await fetch(`${this.apiBase}/chatbot/clear-session/${this.sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.accessToken}`
        }
      });

      return await response.json();
    } catch (error) {
      console.error('Error clearing session:', error);
      throw error;
    }
  }
}

// Usage Example
const chatbot = new InstrumentChatbot(accessToken);

// Send a message
const response = await chatbot.sendMessage("What's a good starter guitar for jazz?");
console.log(response.assistant_response);
console.log(response.recommendations);

// Get recommendations
const recommendations = await chatbot.getRecommendations();
console.log(recommendations.recommendations);
```

#### React Component Example
```jsx
import React, { useState, useRef, useEffect } from 'react';

const ChatbotComponent = ({ accessToken }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(generateSessionId());
  const messagesEndRef = useRef(null);

  function generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message to UI
    setMessages(prev => [...prev, { type: 'user', content: input }]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/chatbot/chat', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: input
        })
      });

      const data = await response.json();

      // Add assistant response
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: data.assistant_response,
        recommendations: data.recommendations
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        type: 'error',
        content: `Error: ${error.message}`
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message message-${msg.type}`}>
            <p>{msg.content}</p>
            {msg.recommendations && msg.recommendations.length > 0 && (
              <div className="recommendations">
                <h4>Recommended Instruments:</h4>
                <ul>
                  {msg.recommendations.map((rec, i) => (
                    <li key={i}>
                      <strong>{rec.name}</strong>: {rec.reason}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
        {loading && <div className="message message-loading">Thinking...</div>}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="chatbot-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about instruments, music, recommendations..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>Send</button>
      </form>
    </div>
  );
};

export default ChatbotComponent;
```

#### Vue.js Component Example
```vue
<template>
  <div class="chatbot-container">
    <div class="chat-messages">
      <div
        v-for="(message, idx) in messages"
        :key="idx"
        :class="`message message-${message.type}`"
      >
        <p>{{ message.content }}</p>
        <div v-if="message.recommendations" class="recommendations">
          <h4>Recommended Instruments:</h4>
          <ul>
            <li v-for="(rec, i) in message.recommendations" :key="i">
              <strong>{{ rec.name }}</strong>: {{ rec.reason }}
            </li>
          </ul>
        </div>
      </div>
      <div v-if="loading" class="message message-loading">Thinking...</div>
      <div ref="messagesEnd"></div>
    </div>

    <form @submit.prevent="sendMessage" class="chat-input">
      <input
        v-model="input"
        type="text"
        placeholder="Ask about instruments, music, recommendations..."
        :disabled="loading"
      />
      <button type="submit" :disabled="loading">Send</button>
    </form>
  </div>
</template>

<script>
export default {
  props: {
    accessToken: String
  },
  data() {
    return {
      messages: [],
      input: '',
      loading: false,
      sessionId: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
  },
  methods: {
    async sendMessage() {
      if (!this.input.trim()) return;

      this.messages.push({ type: 'user', content: this.input });
      const userMessage = this.input;
      this.input = '';
      this.loading = true;

      try {
        const response = await fetch('http://localhost:5000/api/chatbot/chat', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            session_id: this.sessionId,
            message: userMessage
          })
        });

        const data = await response.json();
        this.messages.push({
          type: 'assistant',
          content: data.assistant_response,
          recommendations: data.recommendations
        });
      } catch (error) {
        this.messages.push({
          type: 'error',
          content: `Error: ${error.message}`
        });
      } finally {
        this.loading = false;
        this.$nextTick(() => {
          this.$refs.messagesEnd.scrollIntoView({ behavior: 'smooth' });
        });
      }
    }
  }
};
</script>
```

---

## Backend Usage

### Flask Route Integration
```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.chatbot_service import chat_with_user

chatbot_bp = Blueprint('custom_chatbot', __name__)

@chatbot_bp.route('/instrument-advice', methods=['POST'])
@jwt_required()
def get_instrument_advice():
    """Custom endpoint for instrument-specific advice"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    session_id = data.get('session_id')
    question = data.get('question')
    
    # Enhance the question with context
    enhanced_question = f"I'm interested in learning {question}. What instrument would you recommend?"
    
    response = chat_with_user(user_id, session_id, enhanced_question)
    
    return jsonify(response), 200
```

### Python Client Library
```python
import requests
import json

class MusicalInstrumentsChatbot:
    def __init__(self, access_token, base_url='http://localhost:5000'):
        self.access_token = access_token
        self.base_url = base_url
        self.session_id = None
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def initialize_session(self):
        """Start a new chat session"""
        import uuid
        self.session_id = str(uuid.uuid4())
        return self.session_id
    
    def ask(self, message):
        """Send a message to the chatbot"""
        if not self.session_id:
            self.initialize_session()
        
        url = f'{self.base_url}/api/chatbot/chat'
        payload = {
            'session_id': self.session_id,
            'message': message
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_recommendations(self, context=''):
        """Get instrument recommendations"""
        url = f'{self.base_url}/api/chatbot/recommend-for-me'
        payload = {
            'session_id': self.session_id,
            'message': context
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_history(self):
        """Get conversation history"""
        url = f'{self.base_url}/api/chatbot/history/{self.session_id}'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def clear_session(self):
        """Clear conversation history"""
        url = f'{self.base_url}/api/chatbot/clear-session/{self.session_id}'
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

# Usage
chatbot = MusicalInstrumentsChatbot(access_token='your_jwt_token')
chatbot.initialize_session()

# Ask a question
response = chatbot.ask("I'm interested in jazz. What instrument would you recommend?")
print(response['assistant_response'])
print(response['recommendations'])

# Get recommendations
recs = chatbot.get_recommendations()
print(recs)
```

---

## Advanced Scenarios

### Scenario 1: Recommendation-Based Rental Flow
```python
def recommend_and_rent_workflow(user_id, access_token):
    """
    Complete workflow: Get recommendation -> Show rental options -> Rent
    """
    from app.services.chatbot_service import chat_with_user, get_available_instruments
    from app.models import Instru_ownership
    
    session_id = str(uuid.uuid4())
    
    # Step 1: Get recommendations
    recommendation_prompt = "Based on my profile, what instruments should I rent?"
    response = chat_with_user(user_id, session_id, recommendation_prompt)
    
    recommendations = response['recommendations']
    
    # Step 2: Find available instruments matching recommendations
    rental_options = []
    for rec in recommendations:
        instruments = Instru_ownership.query.filter(
            Instru_ownership.is_available == True,
            Instru_ownership.instrument.has(name=rec['name'])
        ).all()
        
        for inst in instruments:
            rental_options.append({
                'recommendation': rec,
                'ownership_id': inst.id,
                'daily_rate': inst.daily_rate,
                'condition': inst.condition,
                'location': inst.location
            })
    
    # Step 3: Present to user and let them choose
    return {
        'chatbot_response': response['assistant_response'],
        'rental_options': rental_options
    }
```

### Scenario 2: Follow-up Conversation with Context
```python
async def interactive_instrument_discovery(user_id, access_token):
    """
    Multi-turn conversation for discovering instruments
    """
    chatbot = InstrumentChatbot(access_token)
    
    # Turn 1: Initial question
    response1 = await chatbot.sendMessage(
        "I want to start learning a new instrument"
    )
    print("Bot:", response1['assistant_response'])
    
    # Turn 2: Provide more context (bot remembers turn 1)
    response2 = await chatbot.sendMessage(
        "I have about 2 hours a week to practice and a $30/day budget"
    )
    print("Bot:", response2['assistant_response'])
    
    # Turn 3: Ask for specifics
    response3 = await chatbot.sendMessage(
        "I mostly listen to rock and blues music"
    )
    print("Bot:", response3['assistant_response'])
    print("Recommendations:", response3['recommendations'])
    
    # Bot now has full context and can recommend accurately!
    return chatbot.sessionId
```

### Scenario 3: Batch Processing Survey Responses
```python
def recommend_instruments_for_survey_takers():
    """
    For all users who completed survey, generate personalized recommendations
    """
    from app.models import User, SurveyResponse, ChatMessage
    
    users_with_surveys = User.query.join(SurveyResponse).all()
    
    recommendations_generated = []
    
    for user in users_with_surveys:
        session_id = f"batch_recommendations_{user.id}_{datetime.now().isoformat()}"
        
        # Generate recommendation
        response = chat_with_user(
            user.id,
            session_id,
            "Based on my complete profile, what instruments would you most recommend for me?"
        )
        
        # Store in database
        msg = ChatMessage(
            user_id=user.id,
            session_id=session_id,
            message_type='batch_recommendation',
            content=response['assistant_response'],
            context_data={
                'recommendations': response['recommendations'],
                'generated_for_all': True
            }
        )
        db.session.add(msg)
        recommendations_generated.append({
            'user_id': user.id,
            'session_id': session_id,
            'recommendations': response['recommendations']
        })
    
    db.session.commit()
    return recommendations_generated
```

---

## Integration Patterns

### Pattern 1: Embed Chatbot in Dashboard
```python
# routes/dashboard.py
@dashboard_bp.route('/chat-widget')
@jwt_required()
def get_chat_widget_config():
    """Return config for embedding chatbot widget"""
    user_id = get_jwt_identity()
    
    return jsonify({
        'widget_type': 'chatbot',
        'endpoints': {
            'chat': '/api/chatbot/chat',
            'history': f'/api/chatbot/history/<session_id>',
            'recommendations': '/api/chatbot/recommend-for-me'
        },
        'features': {
            'show_recommendations': True,
            'show_history': True,
            'allow_clear_session': True
        },
        'session_config': {
            'auto_create_session': True,
            'max_history_messages': 50
        }
    })
```

### Pattern 2: Chatbot + Email Notification
```python
def send_recommendation_email(user_id):
    """Send chatbot recommendations via email"""
    from app.models import User
    from app.services.chatbot_service import chat_with_user
    
    user = User.query.get(user_id)
    session_id = f"email_recommendations_{user_id}_{datetime.now().isoformat()}"
    
    response = chat_with_user(
        user_id,
        session_id,
        "Based on my profile, what are your top 3 instrument recommendations?"
    )
    
    # Build email
    email_body = f"""
    Hello {user.name},
    
    Based on your preferences and profile, we have some recommendations for you:
    
    {response['assistant_response']}
    
    Recommended Instruments:
    """
    
    for rec in response['recommendations']:
        email_body += f"\n- {rec['name']}: {rec['reason']}"
    
    # Send email
    send_email(user.email, 'Instrument Recommendations', email_body)
```

### Pattern 3: Mobile API Integration
```python
# Special mobile endpoint with stripped responses
@chatbot_bp.route('/chat/mobile', methods=['POST'])
@jwt_required()
def mobile_chat():
    """Optimized chatbot endpoint for mobile apps"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    response = chat_with_user(
        user_id,
        data['session_id'],
        data['message']
    )
    
    # Return minimal response for mobile
    return jsonify({
        'response': response['assistant_response'],
        'recommendations': [
            {
                'name': rec['name'],
                'reason': rec['reason'][:100]  # Truncate for mobile
            }
            for rec in response['recommendations']
        ]
    }), 200
```

---

## Testing the Integration

### Using cURL
```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}' | jq -r '.access_token')

# Chat with bot
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "message": "What violin should I learn on?"
  }'
```

### Using Postman
1. Set up environment variable: `token = <your_jwt_token>`
2. Create POST request to: `http://localhost:5000/api/chatbot/chat`
3. Headers: `Authorization: Bearer {{token}}`
4. Body (JSON):
```json
{
  "session_id": "postman-session",
  "message": "I want to learn piano"
}
```

---

This comprehensive guide should help you integrate the chatbot into any frontend or backend system!
