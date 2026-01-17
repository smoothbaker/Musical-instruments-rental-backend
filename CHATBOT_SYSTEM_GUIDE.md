# Chatbot System Documentation

## Overview

The chatbot system is an intelligent assistant that helps users:
1. **Answer Questions** about musical instruments, music, genres, and learning techniques
2. **Recommend Instruments** based on user profile (experience level, budget, preferences)
3. **Maintain Conversation History** with personalized context
4. **Suggest Rentals** from available inventory matched to user needs

## Architecture

### Components

#### 1. **ChatMessage Model** (`app/models/chat_message.py`)
Stores all chat messages with metadata for conversation tracking.

**Fields:**
- `id`: Unique message identifier
- `user_id`: Reference to the user
- `session_id`: Groups messages into conversations
- `message_type`: Either 'user' or 'assistant'
- `content`: The actual message text
- `context_data`: JSON metadata (user preferences used, recommendations made)
- `created_at`: Timestamp

#### 2. **ChatbotService** (`app/services/chatbot_service.py`)
Core business logic for chatbot interactions.

**Key Functions:**

- **`chat_with_user(user_id, session_id, user_message)`**
  - Processes user messages
  - Fetches user profile and context
  - Calls LLM for response generation
  - Extracts instrument recommendations
  - Saves messages to database
  - Returns structured response with recommendations

- **`get_user_profile(user_id)`**
  - Retrieves user's survey responses
  - Returns experience level, preferences, budget, genres, use case
  - Used to personalize chatbot responses

- **`get_available_instruments()`**
  - Fetches all available instruments for rent
  - Returns formatted list for LLM context
  - Limited to prevent token overflow

- **`get_conversation_history(session_id, user_id, limit)`**
  - Retrieves recent messages for context
  - Helps LLM maintain conversation continuity
  - Default limit: 5 message pairs

- **`extract_recommendations(response)`**
  - Parses JSON recommendations from LLM output
  - Structures instrument suggestions with reasoning
  - Gracefully handles missing recommendations

#### 3. **Chatbot Routes** (`app/routes/chatbot.py`)
REST API endpoints for chatbot functionality.

## API Endpoints

### 1. **Main Chat Endpoint**
```
POST /api/chatbot/chat
```

**Request Body:**
```json
{
  "session_id": "uuid-string or auto-generated",
  "message": "What instruments would be good for a beginner guitarist?"
}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "user_message": "What instruments would be good for a beginner guitarist?",
  "assistant_response": "Based on your profile, I'd recommend...",
  "recommendations": [
    {
      "name": "Acoustic Guitar",
      "reason": "Perfect for beginners, affordable daily rates available"
    },
    {
      "name": "Ukulele",
      "reason": "Great for learning fundamentals with smaller strings"
    }
  ],
  "context": {
    "user_profile": {
      "experience_level": "beginner",
      "budget_range": "0-25",
      "preferred_instruments": "Guitar"
    }
  },
  "created_at": "2026-01-17T10:30:00"
}
```

**Status Codes:**
- `200`: Success
- `400`: Empty message
- `401`: Unauthorized (no JWT token)
- `500`: Server error

---

### 2. **Get Conversation History**
```
GET /api/chatbot/history/<session_id>
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 5,
    "session_id": "abc123",
    "message_type": "user",
    "content": "What's the best violin for beginners?",
    "context_data": null,
    "created_at": "2026-01-17T10:00:00"
  },
  {
    "id": 2,
    "user_id": 5,
    "session_id": "abc123",
    "message_type": "assistant",
    "content": "For beginners, I recommend starting with...",
    "context_data": {
      "recommendations": [...]
    },
    "created_at": "2026-01-17T10:00:30"
  }
]
```

---

### 3. **Get All User Sessions**
```
GET /api/chatbot/sessions
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "abc123",
      "started_at": "2026-01-17T10:00:00",
      "last_message_at": "2026-01-17T10:15:30",
      "message_count": 8
    },
    {
      "session_id": "def456",
      "started_at": "2026-01-16T15:30:00",
      "last_message_at": "2026-01-16T16:00:00",
      "message_count": 4
    }
  ],
  "total_sessions": 2
}
```

---

### 4. **Ask Instrument Question**
```
POST /api/chatbot/ask-instrument-question
```

**Request Body:**
```json
{
  "session_id": "optional-uuid",
  "message": "Is a violin harder to learn than guitar?"
}
```

**Purpose:** Specialized endpoint for instrument-related questions. Auto-enhances context for better instrument-focused responses.

---

### 5. **Get Personalized Recommendations**
```
POST /api/chatbot/recommend-for-me
```

**Request Body:**
```json
{
  "session_id": "optional-uuid",
  "message": "I'm interested in jazz music"  // Optional additional context
}
```

**Response:**
Returns instrument recommendations tailored to user's profile with detailed reasoning.

---

### 6. **Clear Session History**
```
DELETE /api/chatbot/clear-session/<session_id>
```

**Response:**
```json
{
  "message": "Cleared 12 messages from session abc123",
  "deleted_count": 12
}
```

---

## LLM Integration

### Model Details
- **Model Used:** Ollama (runs locally, no API key needed)
- **Model Name:** llama2
- **Framework:** LangChain for prompt management and chain execution

### Prompt Template

The chatbot uses a sophisticated prompt that includes:

1. **System Instructions:** Role definition and behavior guidelines
2. **Conversation History:** Previous messages for context
3. **User Profile Data:**
   - Experience level (beginner, intermediate, advanced)
   - Preferred instruments
   - Favorite genres
   - Budget range
   - Rental frequency
   - Use case (hobby, professional, learning, etc)
4. **Available Inventory:** Current rental instruments with prices
5. **User Question:** The actual query

### Response Generation

The LLM generates:
1. **Primary Response:** Natural conversation answer about instruments/music
2. **Recommendations Block:** Optional JSON-formatted instrument suggestions

```
[RECOMMENDATIONS]
{"recommendations": [
    {"name": "Instrument Name", "reason": "Why this is good for you"},
    ...
]}
[/RECOMMENDATIONS]
```

The service automatically:
- Extracts recommendations from the response
- Cleans the response by removing recommendation blocks
- Formats both for return to user

---

## User Profile Context

The chatbot leverages user survey data to personalize responses:

| Field | Source | Usage |
|-------|--------|-------|
| Experience Level | SurveyResponse | Adjust learning depth and difficulty level |
| Preferred Instruments | SurveyResponse | Focus recommendations on user interests |
| Favorite Genres | SurveyResponse | Match instrument recommendations to music style |
| Budget Range | SurveyResponse | Filter rental prices to user's budget |
| Rental Frequency | SurveyResponse | Suggest appropriate instruments for usage pattern |
| Use Case | SurveyResponse | Recommend instruments based on purpose (hobby, professional, etc) |

---

## Conversation Sessions

### Session Management

Each conversation is identified by a `session_id`:
- **Auto-generated:** If not provided, UUID is generated
- **User-scoped:** Each user has separate sessions
- **Persistent:** Messages stored indefinitely in database
- **Retrievable:** Full history available via `/history` endpoint

### Why Sessions Matter

1. **Context Awareness:** LLM uses previous messages in the conversation
2. **Conversation Continuity:** Follow-up questions understand prior context
3. **User Organization:** Users can have multiple parallel conversations
4. **Analytics:** Track conversation patterns and popular questions

---

## Instrument Recommendations

### Recommendation Flow

1. User asks about instruments or requests recommendations
2. Chatbot fetches user's profile (experience, budget, preferences)
3. LLM generates response with suggested instruments
4. Service extracts recommendations in structured format
5. Response includes:
   - Instrument name
   - Reason tailored to user profile
   - Match to rental inventory

### Example Recommendation

For a beginner with $25/day budget interested in jazz:

```json
{
  "name": "Acoustic Guitar",
  "reason": "Great starter instrument for jazz, matches your budget with rental rates at $15-18/day, and perfect for learning jazz fundamentals"
}
```

---

## Setup and Configuration

### Prerequisites
1. **Ollama Installation:** Download from https://ollama.ai
2. **llama2 Model:** `ollama pull llama2`
3. **Python Dependencies:** Install from requirements.txt

### Installation Steps

```bash
# 1. Install Ollama from https://ollama.ai
# 2. Pull llama2 model
ollama pull llama2

# 3. Start Ollama service
ollama serve

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Database migration for ChatMessage table
flask db upgrade
```

### Environment Variables

No additional environment variables needed for chatbot beyond existing Flask setup.

---

## Usage Examples

### Example 1: Basic Instrument Question
```bash
curl -X POST http://localhost:5000/api/chatbot/chat \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-1",
    "message": "What is the easiest string instrument to learn?"
  }'
```

### Example 2: Get Personalized Recommendations
```bash
curl -X POST http://localhost:5000/api/chatbot/recommend-for-me \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-1",
    "message": ""
  }'
```

### Example 3: View Conversation History
```bash
curl -X GET http://localhost:5000/api/chatbot/history/session-1 \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### Example 4: List All Sessions
```bash
curl -X GET http://localhost:5000/api/chatbot/sessions \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

## Data Flow Diagram

```
User Question
    ↓
[JWT Authentication Check]
    ↓
[Get User Profile from DB]
[Get Available Instruments]
[Get Conversation History]
    ↓
[Build LLM Prompt]
    ↓
[Ollama/llama2 LLM]
    ↓
[Extract Recommendations]
[Clean Response]
    ↓
[Save Messages to DB]
    ↓
[Return Response + Recommendations]
```

---

## Performance Considerations

1. **LLM Processing Time:**
   - First response: 5-15 seconds (model loading)
   - Subsequent responses: 2-5 seconds
   - Depends on Ollama setup and hardware

2. **Database Queries:**
   - User profile fetch: Single query + join
   - Available instruments: Single query with limit
   - Conversation history: Single query with ordering

3. **Token Limits:**
   - Instrument list limited to 15 to prevent token overflow
   - Conversation history limited to 5 message pairs for context

---

## Error Handling

| Scenario | Response | Status |
|----------|----------|--------|
| Empty message | "Message cannot be empty" | 400 |
| Session not found | "No conversation history found" | 404 |
| No user profile | Uses defaults (beginner, no preferences) | 200 |
| No available instruments | "No instruments currently available for rent" | 200 |
| LLM error | Specific error message | 500 |
| Unauthorized | "Missing or invalid JWT token" | 401 |

---

## Future Enhancements

1. **Multi-language Support:** Extend to French and Arabic
2. **Voice Integration:** Accept voice messages and return voice responses
3. **Real-time Recommendations:** Query available instruments in real-time
4. **User Feedback Loop:** Rate recommendations to improve accuracy
5. **Advanced Analytics:** Track which instruments are recommended vs rented
6. **Streaming Responses:** Stream LLM responses for better UX
7. **Caching:** Cache LLM responses for common questions
8. **Fine-tuning:** Fine-tune LLM on domain-specific instrument data

---

## Troubleshooting

### Issue: "LLM connection error"
**Solution:** 
- Ensure Ollama is running: `ollama serve`
- Check port 11434 is accessible

### Issue: "Model not found"
**Solution:**
- Pull the model: `ollama pull llama2`
- Verify: `ollama list`

### Issue: Slow responses
**Solution:**
- Use GPU acceleration if available
- Reduce conversation history limit in chatbot_service.py
- Pre-cache frequently asked instruments

### Issue: "No available instruments"
**Solution:**
- Add instrument listings through `/api/instru-ownership` endpoint
- Mark instruments as `is_available=true`

---

## Testing

### Manual Testing via Swagger UI
1. Navigate to `http://localhost:5000/api/docs`
2. Authorize with JWT token
3. Try endpoints in Swagger interface

### Testing Recommendations Feature
1. Fill out survey at `/api/survey` endpoint
2. Request recommendations at `/api/chatbot/recommend-for-me`
3. Verify recommendations match profile

---

## API Documentation

All endpoints are documented in Swagger/OpenAPI. Access at:
```
http://localhost:5000/api/docs
```

## Support

For issues or questions about the chatbot system:
1. Check conversation history with `/api/chatbot/history/<session_id>`
2. Review error messages returned by LLM
3. Verify user profile data with survey endpoint
4. Check available instruments with `/api/instru-ownership`
