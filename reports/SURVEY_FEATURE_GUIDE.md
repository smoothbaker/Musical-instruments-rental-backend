# Musical Instrument Rental API - Survey Form Guide

## Overview
The survey feature collects musical preferences and habits from renters to power AI-driven recommendations. The survey is submitted after user registration via JWT-authenticated endpoint.

## Survey Form Fields

### 1. **Preferred Instruments** (Text, Comma-separated)
- **Field:** `preferred_instruments`
- **Type:** String (comma-separated list)
- **Example:** "guitar,piano,violin"
- **Description:** Instruments the user is interested in renting
- **For Frontend:** Display as multi-select checkboxes or tags input
- **Options:** guitar, piano, drums, violin, flute, saxophone, trumpet, bass, ukulele, synthesizer, harmonica, banjo, mandolin, cello, harp, etc.

### 2. **Experience Level** (Dropdown/Radio)
- **Field:** `experience_level`
- **Type:** Enum string
- **Valid Values:** 
  - `beginner` - Just starting out
  - `intermediate` - Playing for 1-3 years
  - `advanced` - Playing for 3+ years
- **Example Value:** "intermediate"
- **For Frontend:** Display as radio buttons or dropdown

### 3. **Favorite Music Genres** (Text, Comma-separated)
- **Field:** `favorite_genres`
- **Type:** String (comma-separated list)
- **Example:** "rock,jazz,classical"
- **Description:** Musical genres the user enjoys
- **For Frontend:** Display as multi-select checkboxes
- **Common Options:** rock, jazz, classical, pop, hip-hop, country, blues, folk, metal, electronic, R&B, reggae, latin, world, etc.

### 4. **Budget Range** (Dropdown/Radio)
- **Field:** `budget_range`
- **Type:** Enum string
- **Valid Values:**
  - `0-25` - Budget-friendly ($0-$25/day)
  - `25-50` - Moderate ($25-$50/day)
  - `50-100` - Premium ($50-$100/day)
  - `100+` - Luxury ($100+/day)
- **Example Value:** "50-100"
- **For Frontend:** Display as radio buttons or dropdown

### 5. **Rental Frequency** (Dropdown/Radio)
- **Field:** `rental_frequency`
- **Type:** Enum string
- **Valid Values:**
  - `rarely` - Less than once a month
  - `monthly` - Once a month
  - `weekly` - Multiple times a week
  - `frequently` - Almost daily
- **Example Value:** "monthly"
- **For Frontend:** Display as radio buttons or dropdown

### 6. **Primary Use Case** (Text Input)
- **Field:** `use_case`
- **Type:** String (max 200 characters)
- **Example:** "hobby and learning"
- **Description:** What will the user primarily use the instruments for?
- **For Frontend:** Display as text input with suggestions
- **Suggestions:** hobby, professional, learning, teaching, jamming with friends, studio recording, live performances, home practice, events, etc.

### 7. **Location** (Text Input)
- **Field:** `location`
- **Type:** String (max 100 characters)
- **Example:** "New York"
- **Description:** Preferred location or city for pickups/returns
- **For Frontend:** Display as text input with autocomplete

### 8. **Additional Notes** (Text Area - Optional)
- **Field:** `additional_notes`
- **Type:** String (Text, max unlimited)
- **Example:** "Looking for quality instruments for weekend jamming sessions"
- **Description:** Any additional preferences or notes
- **For Frontend:** Display as textarea with max 500 character limit

## API Endpoints

### Submit Survey (After Registration)
```
POST /api/survey
Authorization: Bearer {token}
Content-Type: application/json

{
  "preferred_instruments": "guitar,piano,violin",
  "experience_level": "intermediate",
  "favorite_genres": "rock,jazz,classical",
  "budget_range": "50-100",
  "rental_frequency": "monthly",
  "use_case": "hobby and learning",
  "location": "New York",
  "additional_notes": "Looking for quality instruments for weekend jamming sessions"
}

Response: 201 Created
{
  "id": 1,
  "user_id": 1,
  "preferred_instruments": "guitar,piano,violin",
  "experience_level": "intermediate",
  "favorite_genres": "rock,jazz,classical",
  "budget_range": "50-100",
  "rental_frequency": "monthly",
  "use_case": "hobby and learning",
  "location": "New York",
  "additional_notes": "Looking for quality instruments for weekend jamming sessions",
  "created_at": "2026-01-16T18:55:21.132524",
  "updated_at": "2026-01-16T18:55:21.132524"
}
```

### Get User's Survey
```
GET /api/survey
Authorization: Bearer {token}

Response: 200 OK
{
  "id": 1,
  "user_id": 1,
  "preferred_instruments": "guitar,piano,violin",
  ...
}
```

### Get Survey by ID
```
GET /api/survey/{survey_id}
Authorization: Bearer {token}

Response: 200 OK
```

### Update Survey
```
PUT /api/survey/{survey_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "experience_level": "advanced",
  "budget_range": "100+",
  "rental_frequency": "weekly"
}

Response: 200 OK
```

### Delete Survey
```
DELETE /api/survey/{survey_id}
Authorization: Bearer {token}

Response: 204 No Content
```

## Frontend Implementation Example (React)

```javascript
// After successful registration and login
const [surveyData, setSurveyData] = useState({
  preferred_instruments: [],
  experience_level: 'beginner',
  favorite_genres: [],
  budget_range: '25-50',
  rental_frequency: 'monthly',
  use_case: '',
  location: '',
  additional_notes: ''
});

const instrumentOptions = [
  'guitar', 'piano', 'drums', 'violin', 'flute', 'saxophone',
  'trumpet', 'bass', 'ukulele', 'synthesizer', 'harmonica'
];

const genreOptions = [
  'rock', 'jazz', 'classical', 'pop', 'hip-hop', 'country',
  'blues', 'folk', 'metal', 'electronic', 'R&B', 'reggae'
];

const handleSurveySubmit = async (token) => {
  const payload = {
    ...surveyData,
    preferred_instruments: surveyData.preferred_instruments.join(','),
    favorite_genres: surveyData.favorite_genres.join(',')
  };

  const response = await fetch('/api/survey', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (response.status === 201) {
    console.log('Survey submitted successfully!');
    // Redirect to dashboard or recommendations
  }
};
```

## Data for AI Recommendations

The survey data collected is structured to provide rich context for AI recommendation engine:

1. **User Profile:** experience_level + budget_range + rental_frequency
2. **Preferences:** preferred_instruments + favorite_genres + use_case
3. **Logistics:** location (for proximity-based recommendations)
4. **Context:** additional_notes (for nuanced preferences)

This data can be used to:
- Recommend instruments matching user's experience level
- Filter by budget preferences
- Suggest similar instruments based on genres
- Prioritize listings by location
- Personalize search results based on use case
- Predict next instrument user might want

## Notes

- Only renters can submit surveys (owners cannot)
- Each user can only have one survey response
- Survey can be updated anytime after submission
- All fields are optional except during initial design (can be made optional in future)
- Timestamp fields (created_at, updated_at) are auto-generated
