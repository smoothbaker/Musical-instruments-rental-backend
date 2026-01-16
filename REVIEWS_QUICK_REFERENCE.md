# Reviews System - Quick Reference

## The Concept

**Reviews are tied to specific instrument ownership copies, not the general instrument catalog.**

If an owner has 2 identical guitars:
- **Guitar A** (ownership_id=4): Has its own reviews, e.g., 4.5⭐ average
- **Guitar B** (ownership_id=5): Has its own reviews, e.g., 5.0⭐ average

Renters see reviews for the **exact copy** they're renting.

---

## Quick API Reference

### Create Review (After returning rental)
```bash
POST /api/reviews
{
  "rental_id": 42,
  "rating": 5,
  "comment": "Perfect condition!"
}
```

### View All Reviews (Filter by ownership)
```bash
GET /api/reviews
GET /api/reviews?instru_ownership_id=5        # Reviews for guitar #5
GET /api/reviews?instru_ownership_id=5&rating=5  # 5-star only
```

### View Specific Guitar's Reviews + Stats
```bash
GET /api/reviews/ownership/5
# Returns: guitar info, all reviews, avg rating, rating distribution
```

### Owner Views All Their Instruments with Reviews
```bash
GET /api/reviews/owner/20
# Returns: all guitars owned by user 20, each with its own reviews
```

### View Single Review
```bash
GET /api/reviews/1
```

### Update Your Review
```bash
PUT /api/reviews/1
{
  "rating": 4,
  "comment": "Updated comment"
}
```

### Delete Your Review
```bash
DELETE /api/reviews/1
```

---

## Review Lifecycle

1. **Renter completes rental** → Rental status: `completed`
2. **Renter submits review** → `POST /api/reviews` with rental_id
3. **Review linked to ownership** → Appears under that specific guitar
4. **Others see review** → When browsing that guitar
5. **Renter can edit** → `PUT /api/reviews/{id}`
6. **Renter can delete** → `DELETE /api/reviews/{id}`

---

## Key Rules

| Rule | Details |
|------|---------|
| **Who** | Only renters (of completed rentals) |
| **What** | Reviews on specific owned instrument, not catalog |
| **How Many** | One per rental (UNIQUE constraint) |
| **Rating** | 1-5 stars (required) |
| **Comment** | Optional text |
| **Edit/Delete** | Renter only |
| **View** | Public (no auth needed) |

---

## Example Responses

### Get Ownership with Reviews
```bash
GET /api/reviews/ownership/5
```

```json
{
  "ownership": {
    "id": 5,
    "instrument": {
      "name": "Acoustic Guitar",
      "brand": "Fender",
      "model": "Dreadnought"
    },
    "owner": {"name": "Bob Owner"},
    "condition": "new",
    "daily_rate": 30,
    "location": "Studio B",
    "is_available": true
  },
  "reviews": [
    {
      "id": 1,
      "rating": 5,
      "comment": "Perfect!",
      "renter_name": "John",
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "rating": 4,
      "comment": "Very good",
      "renter_name": "Jane",
      "created_at": "2024-01-14T15:00:00"
    }
  ],
  "stats": {
    "average_rating": 4.5,
    "total_reviews": 2,
    "rating_distribution": {
      "5": 1,
      "4": 1,
      "3": 0,
      "2": 0,
      "1": 0
    }
  }
}
```

### Get Owner's Instruments
```bash
GET /api/reviews/owner/20
```

```json
{
  "owner": {
    "id": 20,
    "name": "Bob Owner"
  },
  "instruments": [
    {
      "id": 4,
      "instrument": {"name": "Acoustic Guitar"},
      "condition": "good",
      "daily_rate": 25,
      "location": "Studio A",
      "review_count": 1,
      "average_rating": 5.0,
      "reviews": [
        {"id": 1, "rating": 5, "comment": "Perfect!"}
      ]
    },
    {
      "id": 5,
      "instrument": {"name": "Acoustic Guitar"},
      "condition": "new",
      "daily_rate": 30,
      "location": "Studio B",
      "review_count": 2,
      "average_rating": 4.5,
      "reviews": [
        {"id": 2, "rating": 5, "comment": "Brand new!"},
        {"id": 3, "rating": 4, "comment": "Very good"}
      ]
    }
  ]
}
```

---

## Common Errors & Solutions

| Error | Solution |
|-------|----------|
| "Rental not found" | Check rental_id is correct |
| "Can only review completed rentals" | Wait for rental to be marked completed |
| "Can only review your own rentals" | Can't review others' rentals |
| "Rental has already been reviewed" | Use PUT to update, not POST to create |
| "Rating must be 1-5" | Use integer 1-5 |
| "Can only update your own reviews" | Can't edit others' reviews |

---

## Database Fields

**Review Table:**
- `id` - Primary key
- `rental_id` - Links to rental (UNIQUE)
- `instru_ownership_id` - Links to specific guitar copy
- `renter_id` - Who left the review
- `rating` - 1-5 stars
- `comment` - Optional text
- `created_at`, `updated_at` - Timestamps

---

## Testing

```bash
python tests/review_test.py
# Result: 12/12 tests passing ✅
```

---

## Example Workflow

```
1. Owner has 2 guitars
   └─ Guitar A (ownership_id=4)
   └─ Guitar B (ownership_id=5)

2. Renter rents Guitar A
   └─ Completes rental
   └─ Reviews: "Great!" (5⭐)

3. Another renter rents Guitar A
   └─ Completes rental
   └─ Reviews: "Good" (4⭐)
   
4. Owner checks Guitar A
   └─ Sees 2 reviews, 4.5⭐ average
   
5. Owner checks Guitar B
   └─ Sees 3 different reviews (different renters)
   └─ Sees 5.0⭐ average
   
6. New renter looking to rent
   └─ Sees Guitar A: 4.5⭐
   └─ Sees Guitar B: 5.0⭐
   └─ Chooses Guitar B based on reviews
```

---

## Permissions Matrix

| Action | Auth Required | Who Can Do It |
|--------|--------|--------|
| View reviews | No | Anyone |
| Create review | Yes | Renter only |
| Update review | Yes | Review creator only |
| Delete review | Yes | Review creator only |
| View stats | No | Anyone |

---

**Status:** ✅ Ready to Use  
**Tests:** 12/12 Passing  
**Full Docs:** See [REVIEWS_SYSTEM_GUIDE.md](REVIEWS_SYSTEM_GUIDE.md)
