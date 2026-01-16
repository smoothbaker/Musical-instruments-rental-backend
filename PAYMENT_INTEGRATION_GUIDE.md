# Payment Integration Guide

## Overview

This guide explains how to integrate Stripe payments into your Musical Instruments Rental API. The implementation is **PCI compliant** - no credit card data is stored in your database.

## Security Architecture

### What Gets Stored in Your Database
- **Payment records**: Status, amounts, rental references
- **Stripe IDs only**: `stripe_payment_intent_id`, `stripe_charge_id`
- **Transaction details**: Fees, payouts, timestamps

### What Does NOT Get Stored
- ❌ Credit card numbers
- ❌ CVV/CVC codes
- ❌ Expiry dates
- ❌ Cardholder names
- ❌ Any PII beyond what's needed

**All sensitive payment data is handled entirely by Stripe's secure servers.**

---

## Setup Instructions

### 1. Get Stripe API Keys

1. Go to [https://dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys)
2. Sign up if you don't have an account (free)
3. Copy your keys:
   - **Secret Key** (starts with `sk_test_` for testing)
   - **Publishable Key** (starts with `pk_test_` for testing)

### 2. Configure Environment Variables

Create a `.env` file in your project root:

```bash
# .env
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLIC_KEY=pk_test_your_publishable_key_here
FLASK_ENV=development
JWT_SECRET_KEY=your_jwt_secret_here
PLATFORM_FEE_PERCENT=0.10  # 10% platform fee
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The payment integration adds:
- `stripe>=5.0.0` - Stripe Python SDK
- `python-dotenv` - Environment variable management

### 4. Run Database Migration

```bash
flask db upgrade
```

This creates the `payments` table with the new Payment model.

---

## API Endpoints

### 1. Initiate Payment

**Endpoint**: `POST /api/payments/<rental_id>/initiate`

**Authentication**: Required (JWT)

**Purpose**: Create a payment record and get Stripe client secret for frontend

**Request**:
```bash
curl -X POST http://localhost:5000/api/payments/1/initiate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

**Response** (201):
```json
{
  "client_secret": "pi_test_1234567890_secret_abcdefghijk",
  "amount": 150.0,
  "currency": "usd",
  "stripe_public_key": "pk_test_your_publishable_key"
}
```

**What happens**:
1. Validates rental exists and user is the renter
2. Calculates total cost (rental + platform fee)
3. Creates Payment record in database
4. Creates Stripe PaymentIntent (10% platform fee)
5. Returns client secret for frontend

### 2. Confirm Payment

**Endpoint**: `POST /api/payments/<rental_id>/confirm`

**Authentication**: Required (JWT)

**Purpose**: Finalize payment after Stripe processes the card on frontend

**Request**:
```bash
curl -X POST http://localhost:5000/api/payments/1/confirm \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stripe_payment_intent_id": "pi_test_1234567890"
  }'
```

**Response** (200):
```json
{
  "id": 1,
  "rental_id": 1,
  "renter_id": 2,
  "owner_id": 1,
  "amount": 150.0,
  "status": "completed",
  "payment_method": "stripe",
  "transaction_fee": 15.0,
  "owner_payout_amount": 135.0,
  "created_at": "2026-01-16T18:57:53.102777",
  "completed_at": "2026-01-16T18:58:15.234567"
}
```

**What happens**:
1. Retrieves PaymentIntent from Stripe
2. Verifies payment succeeded
3. Updates Payment status to "completed"
4. Activates the rental
5. Marks instrument as unavailable

### 3. Get Payment Details

**Endpoint**: `GET /api/payments/<rental_id>`

**Authentication**: Required (JWT)

**Purpose**: Retrieve payment information for a specific rental

**Request**:
```bash
curl http://localhost:5000/api/payments/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response** (200):
```json
{
  "id": 1,
  "rental_id": 1,
  "status": "completed",
  "amount": 150.0,
  "transaction_fee": 15.0,
  "owner_payout_amount": 135.0,
  "created_at": "2026-01-16T18:57:53",
  "completed_at": "2026-01-16T18:58:15"
}
```

### 4. List All Payments

**Endpoint**: `GET /api/payments`

**Authentication**: Required (JWT)

**Purpose**: Get all payments for current user (as renter or owner)

**Request**:
```bash
curl http://localhost:5000/api/payments \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response** (200):
```json
[
  {
    "id": 1,
    "rental_id": 1,
    "amount": 150.0,
    "status": "completed",
    "owner_payout_amount": 135.0,
    "created_at": "2026-01-16T18:57:53"
  },
  {
    "id": 2,
    "rental_id": 2,
    "amount": 200.0,
    "status": "pending",
    "owner_payout_amount": 180.0,
    "created_at": "2026-01-16T19:00:00"
  }
]
```

### 5. Refund Payment

**Endpoint**: `POST /api/payments/<payment_id>/refund`

**Authentication**: Required (JWT)

**Purpose**: Refund a completed payment

**Request**:
```bash
curl -X POST http://localhost:5000/api/payments/1/refund \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

**Response** (200):
```json
{
  "id": 1,
  "rental_id": 1,
  "status": "refunded",
  "amount": 150.0,
  "created_at": "2026-01-16T18:57:53"
}
```

**What happens**:
1. Validates user is renter or owner
2. Refunds the charge via Stripe
3. Marks payment as "refunded"
4. Marks rental as "cancelled"
5. Makes instrument available again

---

## Frontend Integration

### Using Stripe.js (React)

```jsx
import { Elements, CardElement, useElements, useStripe } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/js';

const stripe = loadStripe('pk_test_your_publishable_key');

function PaymentForm({ rentalId, token }) {
  const stripe = useStripe();
  const elements = useElements();

  const handlePayment = async (e) => {
    e.preventDefault();

    // Step 1: Initiate payment and get client secret
    const initiateRes = await fetch(`/api/payments/${rentalId}/initiate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    const { client_secret } = await initiateRes.json();

    // Step 2: Confirm payment with Stripe
    const cardElement = elements.getElement(CardElement);
    const { paymentIntent, error } = await stripe.confirmCardPayment(client_secret, {
      payment_method: {
        card: cardElement
      }
    });

    if (error) {
      console.error('Payment failed:', error);
      return;
    }

    // Step 3: Confirm with your backend
    const confirmRes = await fetch(`/api/payments/${rentalId}/confirm`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        stripe_payment_intent_id: paymentIntent.id
      })
    });

    if (confirmRes.ok) {
      const payment = await confirmRes.json();
      console.log('Payment successful!', payment);
      // Redirect to success page or update UI
    }
  };

  return (
    <form onSubmit={handlePayment}>
      <CardElement />
      <button type="submit">Pay Now</button>
    </form>
  );
}

export default function RentalPayment({ rentalId, token }) {
  return (
    <Elements stripe={stripe}>
      <PaymentForm rentalId={rentalId} token={token} />
    </Elements>
  );
}
```

### Using HTML + Vanilla JavaScript

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://js.stripe.com/v3/"></script>
</head>
<body>
  <form id="payment-form">
    <div id="card-element"></div>
    <button type="submit">Pay</button>
  </form>

  <script>
    const stripe = Stripe('pk_test_your_publishable_key');
    const elements = stripe.elements();
    const cardElement = elements.create('card');
    cardElement.mount('#card-element');

    document.getElementById('payment-form').addEventListener('submit', async (e) => {
      e.preventDefault();

      const rentalId = new URLSearchParams(window.location.search).get('rental_id');
      const token = localStorage.getItem('access_token');

      // Step 1: Get client secret
      const initiateRes = await fetch(`/api/payments/${rentalId}/initiate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const { client_secret } = await initiateRes.json();

      // Step 2: Confirm payment
      const { paymentIntent } = await stripe.confirmCardPayment(client_secret, {
        payment_method: {
          card: cardElement
        }
      });

      // Step 3: Notify backend
      await fetch(`/api/payments/${rentalId}/confirm`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          stripe_payment_intent_id: paymentIntent.id
        })
      });

      alert('Payment successful!');
    });
  </script>
</body>
</html>
```

---

## Testing the Payment Flow

### Run Unit Tests

```bash
cd "Musical instruments rental API"
python tests/payment_test.py
```

Expected output:
```
============================================================
PAYMENT INTEGRATION TEST SUITE
============================================================

[TEST 1] Create Owner and Renter
✓ Owner created with ID: 1
✓ Renter created with ID: 2

[TEST 2] Create Instrument and Ownership
✓ Instrument created: Guitar
✓ Ownership created with daily rate: $25.0

[TEST 3] Create Rental
✓ Rental created with ID: 1
...
ALL PAYMENT TESTS PASSED! ✓
```

### Test with Stripe Test Cards

Use these card numbers in test mode:

| Card Number | Result | Description |
|-------------|--------|-------------|
| `4242 4242 4242 4242` | Success | Standard test card |
| `4000 0000 0000 0002` | Decline | Card declined |
| `4000 0025 0000 3155` | 3D Secure | Requires authentication |

**Expiry**: Any future date
**CVC**: Any 3 digits

---

## Database Schema

### Payment Table

```sql
CREATE TABLE payments (
  id INTEGER PRIMARY KEY,
  rental_id INTEGER NOT NULL FOREIGN KEY,
  renter_id INTEGER NOT NULL FOREIGN KEY,
  owner_id INTEGER NOT NULL FOREIGN KEY,
  amount FLOAT NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  payment_method VARCHAR(50),
  stripe_payment_intent_id VARCHAR(255) UNIQUE,
  stripe_charge_id VARCHAR(255) UNIQUE,
  stripe_transfer_id VARCHAR(255),
  stripe_payout_id VARCHAR(255),
  transaction_fee FLOAT DEFAULT 0,
  owner_payout_amount FLOAT,
  error_message TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME
);
```

### Key Fields

- **status**: pending → completed → refunded
- **stripe_payment_intent_id**: Used to track payment state
- **stripe_charge_id**: Used for refunds
- **transaction_fee**: 10% platform fee (configurable)
- **owner_payout_amount**: Amount owner receives after fees

---

## Error Handling

### Common Error Responses

**400 - Card Declined**
```json
{
  "code": "invalid_request_error",
  "message": "Your card was declined"
}
```

**400 - Invalid Amount**
```json
{
  "code": "invalid_request_error",
  "message": "Amount must be at least 50 cents"
}
```

**403 - Unauthorized**
```json
{
  "code": "permission_error",
  "message": "Only the renter can pay for this rental"
}
```

**404 - Not Found**
```json
{
  "code": "resource_not_found_error",
  "message": "Payment not found for this rental"
}
```

---

## Security Checklist

- ✅ **PCI Compliance**: No card data stored locally
- ✅ **HTTPS Only**: Always use HTTPS in production
- ✅ **JWT Auth**: All endpoints require authentication
- ✅ **User Isolation**: Renters can only pay their own rentals
- ✅ **Server-side Verification**: Always verify amounts on backend
- ✅ **Rate Limiting**: Recommended for payment endpoints
- ✅ **Audit Logging**: All payments logged with timestamps
- ✅ **Webhook Handling**: (Recommended for production)

---

## Production Considerations

### 1. Use Live Stripe Keys

In production, replace test keys with live keys:
```bash
STRIPE_SECRET_KEY=sk_live_your_live_secret_key
STRIPE_PUBLIC_KEY=pk_live_your_live_publishable_key
```

### 2. Enable Stripe Webhooks

Add webhook handler for payment confirmations, refunds, and disputes:

```python
from flask import request

@bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    event = stripe.Event.construct_from(
        request.get_json(), stripe.api_key
    )
    
    if event.type == 'payment_intent.succeeded':
        # Mark payment as completed
        pass
    elif event.type == 'payment_intent.payment_failed':
        # Mark payment as failed
        pass
    
    return {'success': True}, 200
```

### 3. Implement Payout Management

```python
# Transfer funds to owner
transfer = stripe.Transfer.create(
    amount=int(owner_payout_amount * 100),
    currency='usd',
    destination=owner.stripe_account_id
)
```

### 4. Add Rate Limiting

```bash
pip install Flask-Limiter
```

### 5. Set Up Monitoring

Use Stripe Dashboard to monitor:
- Payment success rates
- Failed transactions
- Disputes and chargebacks
- Failed refunds

---

## Cost Structure

### Default Platform Fee: 10%

Example for $100 rental:
```
Rental Amount:        $100.00
Platform Fee (10%):   -$10.00
Owner Receives:       $90.00

Stripe Processing Fee: ~$2.90 (2.9% + $0.30)
Your Net Revenue:     ~$7.10
```

**Adjust fee in code**:
```python
PLATFORM_FEE_PERCENT = 0.10  # Change to 0.15 for 15%, etc
```

---

## Troubleshooting

### "Stripe API key not set"
- Check `.env` file exists and contains `STRIPE_SECRET_KEY`
- Verify environment variables are loaded: `python -c "import os; print(os.getenv('STRIPE_SECRET_KEY'))"`

### "Payment Intent not found"
- Ensure payment was initiated before confirming
- Check that `stripe_payment_intent_id` matches

### "Card declined" errors
- Use Stripe test card: `4242 4242 4242 4242`
- Check card expiry and CVC are valid

### Refund issues
- Only completed payments can be refunded
- Refunds take 5-10 business days to appear

---

## Additional Resources

- [Stripe Python SDK Docs](https://stripe.com/docs/api?lang=python)
- [Stripe.js Docs](https://stripe.com/docs/stripe-js)
- [PCI Compliance Guide](https://stripe.com/docs/security/compliance)
- [Testing Guide](https://stripe.com/docs/testing)
