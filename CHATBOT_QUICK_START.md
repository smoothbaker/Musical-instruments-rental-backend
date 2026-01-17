# Chatbot Quick Start Guide

## Installation & Setup

### 1. Install Ollama (Local LLM)
The chatbot uses Ollama to run the llama2 model locally (no API key needed).

**Download & Install:**
- Visit https://ollama.ai
- Download for your OS (Mac, Windows, Linux)
- Install and run

**Pull the Model:**
```bash
ollama pull llama2
```

**Start Ollama Service:**
```bash
ollama serve
```
Ollama will run on `http://localhost:11434`

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Update Database Schema
```bash
flask db upgrade
```

This creates the `chat_messages` table for storing conversations.

---

## How It Works

### User Flow

1. **User asks a question** about instruments or music
2. **Chatbot fetches user's profile** (experience, budget, preferences from survey)
3. **LLM generates personalized response** using available instruments
4. **Returns response + instrument recommendations** if applicable
5. **Saves conversation** for history and context

### Example Conversation

**User:** "I'm a beginner interested in jazz, budget is $25/day"

**Chatbot:** "For jazz beginners with your budget, I'd recommend starting with saxophone or trumpet. Here are some options currently available in our rental catalog..."

**Response includes:**
- Detailed explanation of why each instrument is good
- Matching instruments from our rental inventory
- Care tips and practice suggestions

---

## Key Features

### 1. **Intelligent Recommendations**
- Considers user experience level
- Respects budget constraints
- Matches musical preferences
- Suggests instruments from available inventory

### 2. **Conversation Context**
- Remembers previous messages in session
- Uses context to answer follow-up questions
- Maintains conversation history in database

### 3. **User Profile Integration**
- Pulls data from user's survey responses
- Personalizes all recommendations
- Adapts responses to experience level

### 4. **Real Inventory Matching**
- Recommends instruments available for rent
- Includes daily rates and locations
- Helps users find exactly what they're looking for

---

## API Endpoints Quick Reference

### Chat Endpoint
**Send a message to the chatbot:**
```bash
POST /api/chatbot/chat

Body:
{
  "session_id": "unique-session-id",
  "message": "Your question here"
}
```

### Get Session History
**View all messages in a conversation:**
```bash
GET /api/chatbot/history/<session_id>
```

### Get All Sessions
**List all your conversations:**
```bash
GET /api/chatbot/sessions
```

### Ask About Instruments
**Specialized endpoint for instrument questions:**
```bash
POST /api/chatbot/ask-instrument-question

Body:
{
  "message": "What's the best instrument for jazz?"
}
```

### Get Recommendations
**Get personalized instrument recommendations:**
```bash
POST /api/chatbot/recommend-for-me

Body:
{
  "message": ""  // Leave empty or add context
}
```

### Clear Session
**Delete conversation history:**
```bash
DELETE /api/chatbot/clear-session/<session_id>
```

---

## Using with Swagger UI

1. Start your Flask app: `python run.py`
2. Open browser: `http://localhost:5000/api/docs`
3. Click "Authorize" and enter your JWT token
4. Try out any endpoint in the interface

---

## Example Usage

### Step 1: Get Auth Token
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Step 2: Ask Chatbot a Question
```bash
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my-session-123",
    "message": "I want to learn guitar but I'm on a tight budget. What do you recommend?"
  }'
```

Response:
```json
{
  "session_id": "my-session-123",
  "user_message": "I want to learn guitar but I'm on a tight budget...",
  "assistant_response": "Great question! For beginners on a budget, I highly recommend starting with...",
  "recommendations": [
    {
      "name": "Acoustic Guitar",
      "reason": "Perfect for beginners, affordable at $15-20/day..."
    },
    {
      "name": "Ukulele", 
      "reason": "Even more budget-friendly and great for learning fundamentals..."
    }
  ],
  "context": {
    "experience_level": "beginner",
    "budget_range": "0-25"
  }
}
```

### Step 3: Continue the Conversation
```bash
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my-session-123",
    "message": "What about maintenance? How do I care for an acoustic guitar?"
  }'
```

The chatbot remembers your previous question and gives context-aware answers!

### Step 4: View Conversation History
```bash
curl -X GET http://localhost:5000/api/chatbot/history/my-session-123 \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## Tips for Best Results

### 1. Complete Your Survey First
Before asking for recommendations, fill out your music preferences survey:
```bash
POST /api/survey
```

The chatbot uses this to personalize recommendations.

### 2. Be Specific
**Good:** "I want to learn jazz piano on a $50/day budget"

**Less helpful:** "What instruments are there?"

Specific questions get better recommendations.

### 3. Use Sessions Consistently
Use the same `session_id` for related questions in one conversation. This gives the chatbot context.

### 4. Ask Follow-up Questions
The chatbot remembers previous messages, so you can ask follow-ups:
- "Can you tell me more?"
- "What about maintenance?"
- "Are there cheaper options?"

### 5. Request Recommendations
Use the `/recommend-for-me` endpoint to get curated suggestions based on your profile.

---

## Troubleshooting

### Issue: "Connection refused" when starting app
**Problem:** Ollama is not running
**Solution:** Start Ollama: `ollama serve`

### Issue: "Model not found"
**Problem:** llama2 model not downloaded
**Solution:** Run `ollama pull llama2`

### Issue: "404 endpoint not found"
**Problem:** Chatbot blueprint not registered
**Solution:** Check that `app/init.py` imports and registers chatbot blueprint

### Issue: Slow responses (5+ seconds)
**Problem:** This is normal! LLM inference takes time
**Solutions:**
- First response loads model (~10 sec)
- Subsequent responses are faster (2-3 sec)
- Consider GPU acceleration for faster processing

### Issue: "User has no survey data"
**Problem:** User hasn't filled out survey
**Solution:** Chatbot uses defaults (beginner, no special preferences). User can fill survey anytime via `/api/survey`

---

## Common Questions

### Q: Does the chatbot need internet?
**A:** No! Ollama runs locally. The chatbot doesn't make external API calls.

### Q: How accurate are the recommendations?
**A:** The LLM uses your survey data and available inventory to make educated suggestions. Results improve as you interact more.

### Q: Can I export my conversation?
**A:** Yes! The conversation history is stored in the database and accessible via `/api/chatbot/history/<session_id>`

### Q: What languages does the chatbot support?
**A:** Currently English. Future versions will support French and Arabic.

### Q: How long are conversations stored?
**A:** Indefinitely. Users can manually clear sessions with the `/clear-session` endpoint.

### Q: Can multiple users chat simultaneously?
**A:** Yes! Each user has their own sessions and messages are isolated.

---

## Next Steps

1. **Test Basic Chat** - Ask a simple question to verify setup
2. **Complete Survey** - Fill out music preferences for better recommendations
3. **Get Recommendations** - Use `/recommend-for-me` endpoint
4. **Rent an Instrument** - Browse recommendations and rent from catalog
5. **Give Feedback** - Let us know which recommendations you found helpful!

---

## Support & Feedback

If you encounter issues or have feature requests:
1. Check conversation history for context
2. Review error messages in API responses
3. Consult full documentation: `CHATBOT_SYSTEM_GUIDE.md`
4. Check available instruments in catalog

Enjoy exploring instruments with your new AI assistant! 🎵
