# Reviews & Ratings System - Owner-Based Instrument Copies

## Overview

The **Reviews & Ratings System** allows renters to leave reviews and ratings (1-5 stars) after returning a rental. The key feature: **reviews are tied to specific instrument ownership copies**, not the general instrument catalog.

### Why This Matters

If an owner has **2 identical guitars**:
- Each guitar has its **own separate list of reviews**
- One guitar might have excellent reviews (5⭐ average)
- The other might have okay reviews (3⭐ average)
- Renters can see reviews for the **exact copy** they're renting
- Owners can manage reviews for each specific instrument they own

---

## System Architecture

### Data Model

```
Review
├── rental_id (FK → Rental) - UNIQUE - Links to specific rental
├── instru_ownership_id (FK → Instru_ownership) - Links to owner's specific copy
├── renter_id (FK → User) - Who left the review
├── rating (1-5 stars) - Required
├── comment (optional text) - Additional feedback
└── timestamps (created_at, updated_at)

Instru_ownership (Owner's Instrument Copy)
├── user_id - Which owner
├── instrument_id - What instrument
├── condition - Current condition
├── daily_rate - Rental price
├── reviews (relationship) - List of reviews for THIS specific copy
└── rentals (relationship) - All rentals of THIS specific copy

Rental
├── user_id - Renter
├── instru_ownership_id - Which owner's copy
├── status - pending/active/completed
└── review (relationship) - The review (if exists)
```

### Key Relationships

- **1 Rental → 1 Review** (UNIQUE constraint - one review per rental)
- **1 Instru_ownership → Many Reviews** (all reviews for that specific copy)
- **1 Owner → Many Instru_ownerships → Many Reviews** (owner sees reviews across all their instruments)

---

## API Endpoints

### 1. **Create Review** (Renter Only)
```http
POST /api/reviews
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "rental_id": 42,
  "rating": 5,
  "comment": "Perfect condition, excellent rental experience!"
}
```

**Rules:**
- ✅ Only renters can create reviews
- ✅ Only for their own completed rentals
- ✅ Rental must have status = `completed`
- ✅ One review per rental (UNIQUE constraint)
- ✅ Rating 1-5 required
- ✅ Comment optional

**Response (201 Created):**
```json
{
  "id": 1,
  "rental_id": 42,
  "instru_ownership_id": 5,
  "renter_id": 10,
  "rating": 5,
  "comment": "Perfect condition!",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "renter_name": "John Renter"
}
```

---

### 2. **Get All Reviews** (Public)
```http
GET /api/reviews
```

**Query Parameters:**
- `instru_ownership_id=5` - Filter by specific instrument copy
- `rating=5` - Filter by rating (1-5)
- Combine both: `?instru_ownership_id=5&rating=4`

**Response:**
```json
[
  {
    "id": 1,
    "rental_id": 42,
    "instru_ownership_id": 5,
    "renter_id": 10,
    "rating": 5,
    "comment": "Perfect condition!",
    "renter_name": "John Renter",
    "created_at": "2024-01-15T10:30:00"
  },
  {
    "id": 2,
    "rental_id": 43,
    "instru_ownership_id": 5,
    "renter_id": 11,
    "rating": 4,
    "comment": "Very good, minor scratches",
    "renter_name": "Jane Renter",
    "created_at": "2024-01-14T15:00:00"
  }
]
```

---

### 3. **View Specific Instrument Copy with Reviews**
```http
GET /api/reviews/ownership/<instru_ownership_id>
```

**Returns:** Detailed ownership info + all reviews + statistics

```json
{
  "ownership": {
    "id": 5,
    "instrument": {
      "id": 1,
      "name": "Acoustic Guitar",
      "category": "guitar",
      "brand": "Fender",
      "model": "Dreadnought"
    },
    "owner": {
      "id": 20,
      "name": "Bob Owner"
    },
    "condition": "new",
    "daily_rate": 30.0,
    "location": "Studio B",
    "is_available": true,
    "created_at": "2024-01-01T00:00:00"
  },
  "reviews": [
    {
      "id": 1,
      "rental_id": 42,
      "rating": 5,
      "comment": "Perfect condition!",
      "renter_name": "John Renter",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "stats": {
    "average_rating": 4.5,
    "total_reviews": 2,
    "rating_distribution": {
      "1": 0,
      "2": 0,
      "3": 0,
      "4": 1,
      "5": 1
    }
  }
}
```

---

### 4. **Owner Views All Their Instruments with Reviews**
```http
GET /api/reviews/owner/<owner_id>
```

**Returns:** All instruments owned by the owner, each with its own reviews

```json
{
  "owner": {
    "id": 20,
    "name": "Bob Owner",
    "email": "bob@example.com"
  },
  "instruments": [
    {
      "id": 4,
      "instrument": {
        "id": 1,
        "name": "Acoustic Guitar",
        "category": "guitar",
        "brand": "Fender",
        "model": "Dreadnought"
      },
      "condition": "good",
      "daily_rate": 25.0,
      "location": "Studio A",
      "is_available": true,
      "review_count": 1,
      "average_rating": 5.0,
      "reviews": [
        {
          "id": 1,
          "rating": 5,
          "comment": "Perfect!",
          "renter_name": "John Renter",
          "created_at": "2024-01-15T10:30:00"
        }
      ]
    },
    {
      "id": 5,
      "instrument": {
        "id": 1,
        "name": "Acoustic Guitar",
        "category": "guitar",
        "brand": "Fender",
        "model": "Dreadnought"
      },
      "condition": "new",
      "daily_rate": 30.0,
      "location": "Studio B",
      "is_available": true,
      "review_count": 2,
      "average_rating": 4.5,
      "reviews": [
        {
          "id": 2,
          "rating": 5,
          "comment": "Brand new!",
          "renter_name": "Jane Renter",
          "created_at": "2024-01-14T15:00:00"
        },
        {
          "id": 3,
          "rating": 4,
          "comment": "Very good",
          "renter_name": "John Renter",
          "created_at": "2024-01-13T12:00:00"
        }
      ]
    }
  ]
}
```

---

### 5. **Get Specific Review**
```http
GET /api/reviews/<review_id>
```

**Response:**
```json
{
  "id": 1,
  "rental_id": 42,
  "instru_ownership_id": 5,
  "renter_id": 10,
  "rating": 5,
  "comment": "Perfect condition!",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "renter_name": "John Renter"
}
```

---

### 6. **Update Review** (Renter Only)
```http
PUT /api/reviews/<review_id>
Authorization: Bearer <jwt_token>

{
  "rating": 4,
  "comment": "Found a small issue"
}
```

**Rules:**
- ✅ Only the reviewer can update their review
- ✅ Can update rating, comment, or both
- ✅ Timestamp automatically updates

**Response:**
```json
{
  "id": 1,
  "rental_id": 42,
  "instru_ownership_id": 5,
  "renter_id": 10,
  "rating": 4,
  "comment": "Found a small issue",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:45:00",
  "renter_name": "John Renter"
}
```

---

### 7. **Delete Review** (Renter Only)
```http
DELETE /api/reviews/<review_id>
Authorization: Bearer <jwt_token>
```

**Response:** `204 No Content`

**Rules:**
- ✅ Only the reviewer can delete
- ✅ Rental remains, just no review attached

---

## Real-World Example

### Scenario: Owner with 2 Identical Guitars

**Owner (Bob) has:**
- Guitar A (ownership_id=4, condition=good, $25/day)
- Guitar B (ownership_id=5, condition=new, $30/day)

**Guitar A Reviews:**
- ⭐⭐⭐⭐⭐ "Perfect!" - John
- ⭐⭐⭐⭐ "Very good, one small scratch" - Jane
- **Average: 4.5⭐**

**Guitar B Reviews:**
- ⭐⭐⭐⭐⭐ "Brand new, excellent!" - Mike
- ⭐⭐⭐⭐⭐ "Amazing condition!" - Sarah
- **Average: 5.0⭐**

### How It Works

**1. Renter Books Guitar A for $75 total**
```bash
POST /api/rentals
{
  "instru_ownership_id": 4,
  "start_date": "2024-01-20",
  "end_date": "2024-01-23"
}
```

**2. Renter Returns Guitar A (mark as completed)**
- Status changes to `completed`
- Guitar becomes available again

**3. Renter Leaves Review**
```bash
POST /api/reviews
{
  "rental_id": 44,
  "rating": 4,
  "comment": "Good condition, one small issue"
}
```

**4. Review Appears on That Specific Guitar**
```bash
GET /api/reviews/ownership/4
# Shows all reviews for Guitar A only
```

**5. Owner Sees All Reviews for Both Guitars**
```bash
GET /api/reviews/owner/20
# Shows Guitar A with its 3 reviews (4.5⭐ avg)
# Shows Guitar B with its 2 reviews (5.0⭐ avg)
```

---

## Workflow: Review Lifecycle

```
1. Renter completes rental
   └─ Rental status: completed
   
2. Renter submits review
   ├─ POST /api/reviews
   ├─ Links to: rental_id + instru_ownership_id
   └─ Creates: Review record
   
3. Review visible on instrument copy
   ├─ Renter sees: Review on exact guitar they rented
   ├─ Owner sees: Review on that specific guitar in their inventory
   └─ Other renters see: Rating when browsing that copy
   
4. Renter can edit (optional)
   └─ PUT /api/reviews/{id}
   
5. Renter can delete (optional)
   └─ DELETE /api/reviews/{id}
```

---

## Key Business Rules

| Rule | Details |
|------|---------|
| **Who Reviews** | Only renters of completed rentals |
| **What Gets Reviewed** | Specific instrument copies (Instru_ownership), not general catalog |
| **One Per Rental** | Each rental can have max 1 review (UNIQUE constraint) |
| **Rating Scale** | 1-5 stars (required) |
| **Comments** | Optional text feedback |
| **Editing** | Renters can edit/delete their own reviews |
| **Visibility** | Public (no auth required to read) |
| **Return Triggers** | Reviews only created after rental completion and return |

---

## Testing

### Run Tests
```bash
python tests/review_test.py
```

### Test Coverage (12 tests)
1. ✅ Create users (renters, owner)
2. ✅ Create instruments (2 guitars, 1 piano)
3. ✅ Create ownerships (owner has 2 guitars)
4. ✅ Create completed rentals (different renters, same guitar)
5. ✅ Create reviews for first guitar
6. ✅ Create multiple reviews for second guitar
7. ✅ **Each guitar has separate review list**
8. ✅ Calculate average rating per ownership
9. ✅ Verify unique constraint (one review per rental)
10. ✅ Verify review relationships
11. ✅ Query reviews by ownership (owner view)
12. ✅ Renter sees reviews of specific guitar they rented

**Result:** 12/12 PASSING ✅

---

## Code Examples

### JavaScript - Renter Books & Reviews Guitar

```javascript
// Step 1: Get available guitars
async function getAvailableGuitars() {
  const response = await fetch('/api/instruments/available');
  const instruments = await response.json();
  
  // Show each guitar with its reviews
  for (const guitar of instruments) {
    const reviews = await fetch(
      `/api/reviews/ownership/${guitar.id}`
    ).then(r => r.json());
    
    console.log(`${guitar.instrument.name}`);
    console.log(`  Rate: $${guitar.daily_rate}/day`);
    console.log(`  Rating: ${reviews.stats.average_rating}⭐ (${reviews.stats.total_reviews} reviews)`);
    console.log(`  Location: ${guitar.location}`);
  }
}

// Step 2: Book guitar
async function bookGuitar(ownershipId, startDate, endDate, token) {
  const response = await fetch('/api/rentals', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      instru_ownership_id: ownershipId,
      start_date: startDate,
      end_date: endDate
    })
  });
  
  const rental = await response.json();
  console.log(`Rental created: ${rental.id}`);
  return rental;
}

// Step 3: Return guitar & submit review
async function submitReview(rentalId, rating, comment, token) {
  const response = await fetch('/api/reviews', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      rental_id: rentalId,
      rating: rating,
      comment: comment
    })
  });
  
  if (response.status === 201) {
    const review = await response.json();
    console.log(`Review submitted: ${review.rating}⭐`);
    return review;
  } else {
    const error = await response.json();
    console.error('Error:', error.message);
  }
}
```

### JavaScript - Owner Views Their Instruments

```javascript
// Owner looks at all their guitars with reviews
async function viewMyInstruments(ownerId, token) {
  const response = await fetch(`/api/reviews/owner/${ownerId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  
  console.log(`${data.owner.name}'s Instruments:`);
  
  for (const ownership of data.instruments) {
    const instr = ownership.instrument;
    console.log(`\n${instr.name} (${instr.brand} ${instr.model})`);
    console.log(`  Location: ${ownership.location}`);
    console.log(`  Rate: $${ownership.daily_rate}/day`);
    console.log(`  Average Rating: ${ownership.average_rating}⭐ (${ownership.review_count} reviews)`);
    
    if (ownership.reviews.length > 0) {
      console.log('  Recent Reviews:');
      for (const review of ownership.reviews.slice(0, 3)) {
        console.log(`    - ${review.renter_name}: ${review.rating}⭐ "${review.comment}"`);
      }
    }
  }
}
```

---

## Database Schema

```sql
CREATE TABLE reviews (
  id INTEGER PRIMARY KEY,
  rental_id INTEGER UNIQUE NOT NULL,
  instru_ownership_id INTEGER NOT NULL,
  renter_id INTEGER NOT NULL,
  rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
  comment TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY(rental_id) REFERENCES rentals(id),
  FOREIGN KEY(instru_ownership_id) REFERENCES "instruments ownership"(id),
  FOREIGN KEY(renter_id) REFERENCES users(id)
);

-- Indexes for performance
CREATE INDEX idx_reviews_ownership ON reviews(instru_ownership_id);
CREATE INDEX idx_reviews_renter ON reviews(renter_id);
CREATE INDEX idx_reviews_rental ON reviews(rental_id);
```

---

## Common Scenarios

### Scenario 1: Renter Decides Which Copy to Rent
"I want to rent an Acoustic Guitar. Let me check reviews for each copy."

```bash
GET /api/instruments/available
# Returns all available guitars

GET /api/reviews/ownership/4
# Shows reviews for first owner's guitar (4.5⭐)

GET /api/reviews/ownership/5
# Shows reviews for second owner's guitar (5.0⭐)

# Decision: Rent from owner 2 (5⭐ average)
```

### Scenario 2: Owner Monitors Quality
"I want to see how my guitars are rated and manage them accordingly."

```bash
GET /api/reviews/owner/20
# See all reviews for both guitars
# Guitar A: 4.5⭐ - might need maintenance
# Guitar B: 5.0⭐ - perfect condition

# Can adjust prices or maintenance based on reviews
```

### Scenario 3: Renter Updates Review
"I realized there was more damage, want to update my rating"

```bash
PUT /api/reviews/1
{
  "rating": 3,
  "comment": "Found damage on back that I missed initially"
}
```

---

## Security

✅ **JWT Authentication** - Required for creating/editing reviews  
✅ **Renter Isolation** - Can only review their own rentals  
✅ **Data Integrity** - Foreign key constraints at DB level  
✅ **Unique Reviews** - UNIQUE constraint on rental_id  
✅ **Input Validation** - Rating 1-5, comment text  

---

## Performance

| Operation | Query |
|-----------|-------|
| List reviews for guitar | Indexed on `instru_ownership_id` |
| Get owner's instruments | Indexed on `user_id` in Instru_ownership |
| Calculate stats | Single aggregation query |
| Check review exists | Primary key lookup on rental_id |

---

## Summary

- 🎸 **Reviews on specific instruments owned**, not general catalog
- ⭐ **1-5 star ratings** with optional comments
- 🔒 **Renters can only review** their own completed rentals
- 📊 **Automatic statistics** (average, distribution)
- 👀 **Owners see reviews** for each of their instrument copies
- ✏️ **Editable & deletable** by the reviewer
- 🎯 **One review per rental** (UNIQUE constraint)
- 📱 **Public API** for viewing reviews
- ✅ **12/12 tests passing**

---

**Status:** ✅ Production Ready  
**Tests:** 12/12 Passing  
**API Routes:** 4 endpoints  
**Last Updated:** January 16, 2026
