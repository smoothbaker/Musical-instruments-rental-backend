# Survey Feature - Integration Guide

## Summary

The musical preferences survey feature has been successfully implemented in your Musical Instruments Rental API. This feature collects user preferences during or after account creation for renters, which will power your AI recommendation engine.

## What's Been Implemented

### 1. **Database Model** (`app/models/survey_response.py`)
- `SurveyResponse` model with 8 key fields:
  - `preferred_instruments`: Comma-separated list of instruments
  - `experience_level`: User's playing experience (beginner, intermediate, advanced)
  - `favorite_genres`: Comma-separated list of music genres
  - `budget_range`: Daily rental budget (0-25, 25-50, 50-100, 100+)
  - `rental_frequency`: How often user rents (rarely, monthly, weekly, frequently)
  - `use_case`: Primary usage (hobby, professional, learning, jamming, etc.)
  - `location`: Preferred pickup/return location
  - `additional_notes`: Optional free-form text for preferences

### 2. **API Endpoints** (`app/routes/survey.py`)

#### Create Survey (POST)
```
POST /api/survey
Authorization: Bearer {token}
Content-Type: application/json

Body:
{
  "preferred_instruments": "guitar,piano",
  "experience_level": "intermediate",
  "favorite_genres": "rock,jazz",
  "budget_range": "50-100",
  "rental_frequency": "monthly",
  "use_case": "hobby",
  "location": "New York",
  "additional_notes": "Prefer quality instruments"
}

Response: 201 Created
```

#### Get Current User's Survey (GET)
```
GET /api/survey
Authorization: Bearer {token}

Response: 200 OK
{
  "id": 1,
  "user_id": 1,
  "preferred_instruments": "guitar,piano",
  ...
}
```

#### Get Survey by ID (GET)
```
GET /api/survey/{survey_id}
Authorization: Bearer {token}

Response: 200 OK
```

#### Update Survey (PUT)
```
PUT /api/survey/{survey_id}
Authorization: Bearer {token}
Content-Type: application/json

Body: (any fields to update)
{
  "experience_level": "advanced",
  "budget_range": "100+"
}

Response: 200 OK
```

#### Delete Survey (DELETE)
```
DELETE /api/survey/{survey_id}
Authorization: Bearer {token}

Response: 204 No Content
```

### 3. **Validation & Security**
- ✅ Only renters can submit surveys (owners get 403 Forbidden)
- ✅ Each user can only have one survey (duplicate attempts get 400 Bad Request)
- ✅ Users can only access/modify their own surveys (403 Unauthorized for others)
- ✅ All enum fields validated against allowed values
- ✅ JWT authentication required on all endpoints

### 4. **Frontend Assets**
- **HTML Form** (`survey_form.html`): Production-ready survey form with:
  - Beautiful gradient design
  - Form validation (client-side)
  - Loading state
  - Success message
  - Mobile responsive
  - Proper accessibility
  
- **API Documentation** (`SURVEY_FEATURE_GUIDE.md`): Complete guide with:
  - Field descriptions and valid values
  - API endpoint specifications
  - React integration example
  - Frontend implementation tips

## How to Use

### For Backend Integration

1. **Database Migration** (Already handled by Flask-SQLAlchemy)
   ```bash
   python
   from app import create_app, db
   app = create_app()
   with app.app_context():
       db.create_all()
   ```

2. **Test the Survey Feature**
   ```bash
   python tests/survey_test.py
   ```
   All 10 tests should pass ✓

### For Frontend Integration

#### Option 1: Use the Provided HTML Form
```html
<!-- Include the survey form in your registration flow -->
<iframe src="survey_form.html"></iframe>

<!-- Or redirect after successful registration -->
<script>
  if (userType === 'renter') {
    window.location.href = '/survey_form.html?token=' + accessToken;
  }
</script>
```

#### Option 2: Build Your Own Form
```javascript
// After user registration
async function submitSurvey(token, surveyData) {
  const response = await fetch('/api/survey', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      preferred_instruments: 'guitar,piano',
      experience_level: 'intermediate',
      favorite_genres: 'rock,jazz',
      budget_range: '50-100',
      rental_frequency: 'monthly',
      use_case: 'hobby',
      location: 'New York',
      additional_notes: 'Optional notes'
    })
  });

  if (response.status === 201) {
    const survey = await response.json();
    console.log('Survey submitted:', survey);
  }
}
```

#### Option 3: React Component Example
```javascript
import React, { useState } from 'react';

function SurveyForm({ token, onSuccess }) {
  const [formData, setFormData] = useState({
    preferred_instruments: [],
    experience_level: '',
    favorite_genres: [],
    budget_range: '',
    rental_frequency: '',
    use_case: '',
    location: '',
    additional_notes: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const payload = {
      ...formData,
      preferred_instruments: formData.preferred_instruments.join(','),
      favorite_genres: formData.favorite_genres.join(',')
    };

    const response = await fetch('/api/survey', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      onSuccess();
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields here */}
      <button type="submit">Submit Survey</button>
    </form>
  );
}

export default SurveyForm;
```

## Using Survey Data for AI Recommendations

The collected survey data can be used to power recommendations:

### 1. **Content-Based Filtering**
```python
# Find instruments matching user preferences
def recommend_by_preferences(user_id):
    survey = SurveyResponse.query.filter_by(user_id=user_id).first()
    
    # Match preferred instruments
    instruments = Instrument.query.filter(
        Instrument.category.in_(survey.preferred_instruments.split(','))
    ).all()
    
    return instruments
```

### 2. **Budget-Based Recommendations**
```python
def recommend_by_budget(user_id):
    survey = SurveyResponse.query.filter_by(user_id=user_id).first()
    budget_max = float(survey.budget_range.split('-')[1] or survey.budget_range.split('+')[0])
    
    ownerships = Instru_ownership.query.filter(
        Instru_ownership.daily_rate <= budget_max
    ).all()
    
    return ownerships
```

### 3. **Machine Learning Features**
The survey data provides rich features for ML models:
- **User Profile Vector**: [experience_level, budget_range, rental_frequency]
- **Preference Vector**: [preferred_instruments, favorite_genres]
- **Context**: [location, use_case]

These can be used with libraries like scikit-learn or TensorFlow for:
- Collaborative filtering
- Content-based recommendation
- Hybrid recommendation systems
- Personality-based clustering

## File Structure

```
app/
├── models/
│   └── survey_response.py       # Survey data model
├── routes/
│   └── survey.py                # Survey API endpoints
├── schemas.py                   # (Updated) Survey schemas added
└── init.py                      # (Updated) Survey blueprint registered

tests/
└── survey_test.py               # Complete test suite (10 tests)

docs/
├── SURVEY_FEATURE_GUIDE.md      # Detailed field documentation
└── survey_form.html             # Production-ready form

Root/
└── survey_form.html             # Standalone HTML form
```

## Testing

### Run All Survey Tests
```bash
python tests/survey_test.py
```

### Expected Output
```
============================================================
SURVEY FEATURE TEST SUITE
============================================================

[TEST 1] Register Renter User
✓ Renter created with ID: 1

[TEST 2] Login as Renter
✓ Renter logged in successfully

[TEST 3] Submit Survey Response
✓ Survey response submitted with ID: 1

[TEST 4] Get Survey Response
✓ Survey response retrieved successfully

[TEST 5] Get Survey by ID
✓ Survey retrieved by ID successfully

[TEST 6] Update Survey Response
✓ Survey response updated successfully

[TEST 7] Try to Submit Survey Twice (Should Fail)
✓ Correctly prevented duplicate survey submission

[TEST 8] Owner Tries to Submit Survey (Should Fail)
✓ Correctly prevented owner from submitting survey

[TEST 9] Delete Survey Response
✓ Survey response deleted successfully

[TEST 10] Get Deleted Survey (Should Fail)
✓ Correctly returned 404 for deleted survey

============================================================
ALL SURVEY TESTS PASSED! ✓
============================================================
```

## Next Steps for AI Recommendations

1. **Data Collection**: Let survey responses accumulate over time
2. **Feature Engineering**: Convert categorical data to numerical vectors
3. **Choose Algorithm**: 
   - Simple: Content-based filtering (fast, no data required)
   - Medium: Collaborative filtering (requires rental history)
   - Advanced: Hybrid systems (combines multiple approaches)
4. **Integration**: Create `/api/recommendations` endpoint
5. **A/B Testing**: Test recommendation quality with real users

## API Swagger Documentation

When you start the server, visit: `http://localhost:5000/api/docs`

All survey endpoints are documented with:
- Request/response schemas
- Parameter descriptions
- Error codes
- Try-it-out functionality

## Security Considerations

✅ **Implemented**:
- JWT authentication required
- User isolation (can't access others' surveys)
- Input validation
- Role-based access (only renters)

🔒 **Future Enhancements**:
- Rate limiting on survey endpoints
- Data encryption for sensitive preferences
- GDPR compliance (right to delete)
- Survey response versioning
- Audit logging

## Support & Troubleshooting

### Survey not being created
- Ensure user is logged in (`Authorization` header present)
- Check user is a `renter` (not `owner`)
- Verify all required fields are provided

### Can't update survey
- Verify you're updating your own survey (not another user's)
- Check that the survey exists before updating

### Form validation failing
- Check browser console for specific errors
- Ensure all enum values match accepted values
- Verify token is still valid

## Contact & Support

For questions or improvements to the survey feature, refer to the comprehensive test suite and API documentation included in this package.

---

**Feature Status**: ✅ Complete & Production-Ready
**Tests**: ✅ All 10 passing
**Documentation**: ✅ Complete
**Frontend Assets**: ✅ Provided
**Ready for AI Integration**: ✅ Yes
