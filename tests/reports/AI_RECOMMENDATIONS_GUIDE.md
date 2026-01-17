# AI-Powered Instrument Recommendations

## Overview

The API now includes an intelligent recommendation endpoint that uses natural language processing to analyze user needs and suggest the best instruments from the database.

## Features

✅ **AI-Powered NLP Analysis** - Uses Hugging Face free inference API (optional)
✅ **Smart Matching Algorithm** - Scores instruments based on multiple factors
✅ **Budget-Aware** - Filters recommendations by user budget
✅ **Rating-Based Scoring** - Considers user reviews and ratings
✅ **Keyword Extraction** - Automatically detects instrument types from text
✅ **No API Key Required** - Works without HuggingFace token (uses fallback)

## Endpoint

### POST `/api/recommendations/by-needs`

**Authentication:** Required (JWT Token)

**Request Body:**
```json
{
  "user_needs": "beginner guitarist looking for affordable acoustic guitar",
  "budget": 30.0,
  "experience_level": "beginner"
}
```

**Request Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_needs` | string | Yes | Your requirements in natural language |
| `budget` | float | No | Maximum daily rental budget |
| `experience_level` | string | No | One of: beginner, intermediate, advanced |

**Response (200 OK):**
```json
{
  "recommendations": [
    {
      "id": 1,
      "instrument_id": 5,
      "name": "Professional Acoustic Guitar",
      "category": "Stringed",
      "brand": "Yamaha",
      "model": "FG800",
      "description": "High-quality acoustic guitar perfect for professionals",
      "daily_rate": 25.0,
      "location": "123 Music Street, Nashville, TN",
      "condition": "excellent",
      "average_rating": 4.8,
      "match_score": 85,
      "reasoning": "Matches your need for a guitar at $25/day with 4.8/5 rating"
    },
    {
      "id": 2,
      "instrument_id": 6,
      "name": "Beginner Acoustic Guitar",
      "category": "Stringed",
      "brand": "Epiphone",
      "model": "DR-100",
      "description": "Perfect for beginners learning guitar",
      "daily_rate": 15.0,
      "location": "456 Music Ave, Austin, TX",
      "condition": "good",
      "average_rating": 4.3,
      "match_score": 78,
      "reasoning": "Matches your need for a guitar at $15/day with 4.3/5 rating"
    }
  ],
  "total_available": 12,
  "matched_count": 8,
  "user_needs_analyzed": "beginner guitarist looking for affordable acoustic guitar",
  "matched_categories": ["guitar", "stringed"]
}
```

## How It Works

### 1. **AI Classification (Optional)**
If a HuggingFace API token is provided, the system uses zero-shot text classification to categorize user needs into:
- beginner-friendly, professional-grade, budget-friendly
- acoustic, electric, percussion, wind-instrument
- string-instrument, keyboard

### 2. **Keyword Extraction (Fallback)**
The system automatically detects instrument types by looking for keywords:
- **Guitar:** guitar, acoustic, electric, fender, ibanez, les paul
- **Piano:** piano, keyboard, synthesizer, yamaha
- **Drums:** drums, drum kit, percussion, cymbal
- **Violin:** violin, viola, classical, fiddle
- **Flute:** flute, piccolo, woodwind
- **Bass:** bass, bass guitar, upright

### 3. **Smart Scoring Algorithm**
Each instrument is scored (0-100) based on:
- **Category Match (40 pts):** Does it match the detected instrument type?
- **Budget Match (30 pts):** Is the daily rate within budget?
- **Rating Match (20 pts):** How highly rated is it? (4.5+ = 20pts, 4.0+ = 15pts, etc.)
- **Keyword Match (10 pts):** Do additional keywords match the name/description?

### 4. **Results Ranking**
The top 5 instruments are returned, sorted by match score (highest first).

## Usage Examples

### Example 1: Beginner Guitarist with Budget
```bash
curl -X POST "http://localhost:5000/api/recommendations/by-needs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_needs": "beginner guitarist",
    "budget": 20,
    "experience_level": "beginner"
  }'
```

### Example 2: Professional Drummer (No Budget Limit)
```bash
curl -X POST "http://localhost:5000/api/recommendations/by-needs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_needs": "professional drum kit for jazz performance",
    "experience_level": "advanced"
  }'
```

### Example 3: Open-Ended Search
```bash
curl -X POST "http://localhost:5000/api/recommendations/by-needs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_needs": "I want to learn a string instrument that sounds warm and mellow"
  }'
```

## Using HuggingFace API (Optional)

To enable advanced NLP classification with HuggingFace, add your API token to `.env`:

```bash
HUGGINGFACE_API_KEY=your_hf_token_here
```

**Get a free HuggingFace token:**
1. Visit https://huggingface.co/join
2. Create a free account
3. Go to https://huggingface.co/settings/tokens
4. Create a read token
5. Add to your `.env` file

**Without the token:** The system uses intelligent keyword matching as a fallback (100% free, no API calls).

## Supported Instrument Categories

The system recognizes:
- **Stringed:** Guitar, Violin, Bass, Ukulele, Mandolin
- **Keyboard:** Piano, Synthesizer, Organ, Keyboard
- **Percussion:** Drums, Cymbal, Marimba, Xylophone
- **Wind:** Flute, Saxophone, Trumpet, Trombone, Clarinet
- **Other:** Harmonica, Accordion, Banjo

## Benefits for Users

1. **Personalized Results** - Gets recommendations matching their specific needs
2. **Budget-Friendly** - Can specify budget and get affordable options
3. **Quality-Aware** - Recommends highly-rated instruments
4. **No Guessing** - Doesn't need to know technical details
5. **Fast & Easy** - Just describe what you want in natural language

## Technical Details

- **Service File:** `app/services/recommendation_service.py`
- **Route File:** `app/routes/recommendations.py`
- **Schema:** `InstrumentRecommendationRequestSchema` in `app/schemas.py`
- **Database Models:** Uses `Instrument`, `Instru_ownership`, `Review` models
- **Scoring Algorithm:** Custom matching logic in `score_instrument_match()`

## Error Handling

- **404:** No instruments available in the database
- **400:** Invalid budget or experience level
- **401:** Missing or invalid JWT token
- **422:** Invalid request body

## Scoring Algorithm Details

```python
def score_instrument_match(ownership, user_needs, matched_types, budget=None):
    score = 0
    
    # Category match (40 points)
    if instrument.category.lower() in matched_types:
        score += 40
    
    # Budget match (30 points)
    if budget:
        if ownership.daily_rate <= budget:
            score += 30
        elif ownership.daily_rate <= budget * 1.5:
            score += 15
    else:
        score += 20
    
    # Rating match (20 points)
    if avg_rating >= 4.5:
        score += 20
    elif avg_rating >= 4.0:
        score += 15
    elif avg_rating >= 3.5:
        score += 10
    
    # Keyword match (10 points)
    if any(keyword in combined_text for keyword in user_needs.split()):
        score += 10
    
    return score
```

## Future Enhancements

- [ ] Fine-tuned ML model for better recommendations
- [ ] User feedback loop to improve results
- [ ] Rental history-based recommendations
- [ ] Genre-based recommendations
- [ ] Similar instruments to user's past rentals
- [ ] Collaborative filtering

## Testing

Test the endpoint in Insomnia:
1. Import the API collection
2. Navigate to **Recommendations** folder
3. Use **"Get AI Recommendations by Needs"** request
4. Update the JSON body with your needs
5. Send request with valid JWT token

---

**Feature Status:** ✅ Production Ready
**API Version:** 1.0
**Last Updated:** January 17, 2026
