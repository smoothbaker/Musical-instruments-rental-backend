"""
Comprehensive API Test Suite
Tests all endpoints across all modules
"""

from app import create_app
import json
import sys
from datetime import datetime, timedelta

class APITester:
    def __init__(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.results = {
            'passed': 0,
            'failed': 0,
            'endpoints_tested': [],
            'failures': []
        }
        self.tokens = {}  # Store tokens for authenticated requests
        self.test_data = {}  # Store IDs for related tests
        
    def log(self, message, status='INFO'):
        """Log test messages"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {status:8} | {message}")
    
    def test_endpoint(self, method, endpoint, data=None, headers=None, expected_status=200, 
                     description="", user_type='renter'):
        """Test an API endpoint"""
        if description:
            self.log(description)
        
        # Add authorization header if token exists
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        else:
            headers = dict(headers)
            headers['Content-Type'] = 'application/json'
        
        if user_type in self.tokens:
            headers['Authorization'] = f"Bearer {self.tokens[user_type]}"
        
        # Make request
        if method == 'GET':
            response = self.client.get(endpoint, headers=headers)
        elif method == 'POST':
            response = self.client.post(endpoint, json=data, headers=headers)
        elif method == 'PUT':
            response = self.client.put(endpoint, json=data, headers=headers)
        elif method == 'DELETE':
            response = self.client.delete(endpoint, headers=headers)
        else:
            self.log(f"Unknown method: {method}", "ERROR")
            return None
        
        # Check response
        is_success = response.status_code == expected_status
        status_str = "PASS" if is_success else "FAIL"
        
        if is_success:
            self.results['passed'] += 1
            self.log(f"  {method} {endpoint} => {response.status_code}", status_str)
        else:
            self.results['failed'] += 1
            error_msg = f"{method} {endpoint} => Expected {expected_status}, got {response.status_code}"
            self.log(f"  {error_msg}", status_str)
            try:
                error_detail = response.get_json()
                self.results['failures'].append({
                    'endpoint': f"{method} {endpoint}",
                    'expected': expected_status,
                    'actual': response.status_code,
                    'response': error_detail
                })
            except:
                pass
        
        self.results['endpoints_tested'].append({
            'method': method,
            'endpoint': endpoint,
            'status': response.status_code,
            'expected': expected_status,
            'passed': is_success
        })
        
        return response
    
    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*80)
        print("COMPREHENSIVE API TEST SUITE")
        print("="*80 + "\n")
        
        # Test basic endpoints
        self.test_basic_endpoints()
        
        # Test authentication
        self.test_auth_endpoints()
        
        # Test instruments
        self.test_instruments_endpoints()
        
        # Test rentals
        self.test_rentals_endpoints()
        
        # Test users
        self.test_users_endpoints()
        
        # Test instru-ownership
        self.test_instru_ownership_endpoints()
        
        # Test payments
        self.test_payments_endpoints()
        
        # Test reviews
        self.test_reviews_endpoints()
        
        # Test dashboard
        self.test_dashboard_endpoints()
        
        # Test recommendations
        self.test_recommendations_endpoints()
        
        # Test survey
        self.test_survey_endpoints()
        
        # Test chatbot
        self.test_chatbot_endpoints()
        
        # Print summary
        self.print_summary()
    
    def test_basic_endpoints(self):
        """Test basic endpoints"""
        print("\n" + "-"*80)
        print("TESTING BASIC ENDPOINTS")
        print("-"*80)
        
        self.test_endpoint('GET', '/', expected_status=200, description="[ROOT] Root endpoint")
        self.test_endpoint('GET', '/health', expected_status=200, description="[HEALTH] Health check")
        self.test_endpoint('GET', '/api', expected_status=302, description="[API] API root redirect")
        self.test_endpoint('GET', '/swagger.json', expected_status=200, description="[SWAGGER] OpenAPI specification")
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n" + "-"*80)
        print("TESTING AUTHENTICATION ENDPOINTS")
        print("-"*80)
        
        # Register a renter user
        renter_email = f"renter_{int(datetime.now().timestamp())}@test.com"
        renter_data = {
            'email': renter_email,
            'name': 'Test Renter',
            'phone': '1234567890',
            'user_type': 'renter',
            'password': 'TestPassword123!'
        }
        response = self.test_endpoint('POST', '/api/auth/register', renter_data, 
                                    expected_status=201, description="[AUTH] Register renter user")
        if response and response.status_code == 201:
            self.test_data['renter_id'] = response.get_json().get('id')
        
        # Register an owner user
        owner_email = f"owner_{int(datetime.now().timestamp())}@test.com"
        owner_data = {
            'email': owner_email,
            'name': 'Test Owner',
            'phone': '0987654321',
            'user_type': 'owner',
            'password': 'TestPassword123!'
        }
        response = self.test_endpoint('POST', '/api/auth/register', owner_data, 
                                    expected_status=201, description="[AUTH] Register owner user")
        if response and response.status_code == 201:
            self.test_data['owner_id'] = response.get_json().get('id')
        
        # Login renter
        login_data = {'email': renter_email, 'password': 'TestPassword123!'}
        response = self.test_endpoint('POST', '/api/auth/login', login_data, 
                                    expected_status=200, description="[AUTH] Login renter")
        if response and response.status_code == 200:
            self.tokens['renter'] = response.get_json().get('access_token')
            self.tokens['renter_refresh'] = response.get_json().get('refresh_token')
        
        # Login owner
        login_data = {'email': owner_email, 'password': 'TestPassword123!'}
        response = self.test_endpoint('POST', '/api/auth/login', login_data, 
                                    expected_status=200, description="[AUTH] Login owner", user_type='owner')
        if response and response.status_code == 200:
            self.tokens['owner'] = response.get_json().get('access_token')
            self.tokens['owner_refresh'] = response.get_json().get('refresh_token')
        
        # Get profile (renter)
        self.test_endpoint('GET', '/api/auth/profile', expected_status=200, 
                         description="[AUTH] Get renter profile", user_type='renter')
        
        # Get profile (owner)
        self.test_endpoint('GET', '/api/auth/profile', expected_status=200, 
                         description="[AUTH] Get owner profile", user_type='owner')
        
        # Refresh token (renter)
        if 'renter_refresh' in self.tokens:
            # Use refresh token specifically for refresh endpoint
            headers = {'Authorization': f"Bearer {self.tokens['renter_refresh']}", 'Content-Type': 'application/json'}
            response = self.client.post('/api/auth/refresh', headers=headers)
            is_success = response.status_code == 200
            status_str = "PASS" if is_success else "FAIL"
            if is_success:
                self.results['passed'] += 1
                self.log(f"  POST /api/auth/refresh => {response.status_code}", status_str)
                # Update access token with new one
                if response.status_code == 200:
                    self.tokens['renter'] = response.get_json().get('access_token')
            else:
                self.results['failed'] += 1
                self.log(f"  POST /api/auth/refresh => Expected 200, got {response.status_code}", status_str)
    
    def test_instruments_endpoints(self):
        """Test instrument endpoints"""
        print("\n" + "-"*80)
        print("TESTING INSTRUMENT ENDPOINTS")
        print("-"*80)
        
        # List instruments (no auth needed)
        self.test_endpoint('GET', '/api/instruments', expected_status=200, 
                         description="[INSTRUMENTS] List all instruments")
        
        # Get available instruments
        self.test_endpoint('GET', '/api/instruments/available', expected_status=200, 
                         description="[INSTRUMENTS] Get available instruments")
        
        # Create instrument (owner only)
        instrument_data = {
            'name': 'Test Acoustic Guitar',
            'category': 'String',
            'brand': 'Fender',
            'model': 'FA-125',
            'description': 'A quality beginner acoustic guitar'
        }
        response = self.test_endpoint('POST', '/api/instruments', instrument_data, 
                                    expected_status=201, description="[INSTRUMENTS] Create new instrument", 
                                    user_type='owner')
        if response and response.status_code == 201:
            self.test_data['instrument_id'] = response.get_json().get('id')
        
        # Get instrument details
        if 'instrument_id' in self.test_data:
            self.test_endpoint('GET', f"/api/instruments/{self.test_data['instrument_id']}", 
                             expected_status=200, description="[INSTRUMENTS] Get instrument details")
            
            # Update instrument
            update_data = {'daily_rate': 30.00}
            self.test_endpoint('PUT', f"/api/instruments/{self.test_data['instrument_id']}", 
                             update_data, expected_status=200, 
                             description="[INSTRUMENTS] Update instrument", user_type='owner')
    
    def test_rentals_endpoints(self):
        """Test rental endpoints"""
        print("\n" + "-"*80)
        print("TESTING RENTAL ENDPOINTS")
        print("-"*80)
        
        # First, create an instrument ownership
        if 'owner_id' not in self.test_data:
            self.log("Skipping rentals - no owner created", "SKIP")
            return
        
        # Create instru_ownership first
        ownership_data = {
            'instrument_id': 1,  # Assuming instrument 1 exists
            'condition': 'Excellent',
            'daily_rate': 25.00,
            'location': 'New York, NY',
            'is_available': True
        }
        response = self.test_endpoint('POST', '/api/instru-ownership', ownership_data, 
                                    expected_status=201, description="[OWNERSHIP] Create ownership", 
                                    user_type='owner')
        if response and response.status_code == 201:
            self.test_data['ownership_id'] = response.get_json().get('id')
        
        # List rentals (renter)
        self.test_endpoint('GET', '/api/rentals', expected_status=200, 
                         description="[RENTALS] List user rentals", user_type='renter')
        
        # Create rental
        if 'ownership_id' in self.test_data:
            rental_data = {
                'instru_ownership_id': self.test_data['ownership_id'],
                'start_date': (datetime.now() + timedelta(days=1)).date().isoformat(),
                'end_date': (datetime.now() + timedelta(days=8)).date().isoformat()
            }
            response = self.test_endpoint('POST', '/api/rentals', rental_data, 
                                        expected_status=201, description="[RENTALS] Create rental", 
                                        user_type='renter')
            if response and response.status_code == 201:
                self.test_data['rental_id'] = response.get_json().get('id')
        
        # Get rental details
        if 'rental_id' in self.test_data:
            self.test_endpoint('GET', f"/api/rentals/{self.test_data['rental_id']}", 
                             expected_status=200, description="[RENTALS] Get rental details", 
                             user_type='renter')
    
    def test_users_endpoints(self):
        """Test user endpoints"""
        print("\n" + "-"*80)
        print("TESTING USER ENDPOINTS")
        print("-"*80)
        
        # List users
        self.test_endpoint('GET', '/api/users', expected_status=200, 
                         description="[USERS] List all users", user_type='renter')
        
        # Get user details
        if 'renter_id' in self.test_data:
            self.test_endpoint('GET', f"/api/users/{self.test_data['renter_id']}", 
                             expected_status=200, description="[USERS] Get user details", 
                             user_type='renter')
            
            # Update user
            update_data = {'name': 'Updated Test Renter', 'phone': '5555555555'}
            self.test_endpoint('PUT', f"/api/users/{self.test_data['renter_id']}", update_data, 
                             expected_status=200, description="[USERS] Update user", user_type='renter')
    
    def test_instru_ownership_endpoints(self):
        """Test instrument ownership endpoints"""
        print("\n" + "-"*80)
        print("TESTING INSTRUMENT OWNERSHIP ENDPOINTS")
        print("-"*80)
        
        # List ownerships
        self.test_endpoint('GET', '/api/instru-ownership', expected_status=200, 
                         description="[OWNERSHIP] List ownerships", user_type='owner')
        
        # Get my instruments
        self.test_endpoint('GET', '/api/instru-ownership/my-instruments', expected_status=200, 
                         description="[OWNERSHIP] Get my instruments", user_type='owner')
        
        # Get ownership details
        if 'ownership_id' in self.test_data:
            self.test_endpoint('GET', f"/api/instru-ownership/{self.test_data['ownership_id']}", 
                             expected_status=200, description="[OWNERSHIP] Get ownership details", 
                             user_type='owner')
    
    def test_payments_endpoints(self):
        """Test payment endpoints"""
        print("\n" + "-"*80)
        print("TESTING PAYMENT ENDPOINTS")
        print("-"*80)
        
        # List payments
        self.test_endpoint('GET', '/api/payments', expected_status=200, 
                         description="[PAYMENTS] List payments", user_type='renter')
        
        # Note: Actual payment creation requires rental setup and Stripe integration
    
    def test_reviews_endpoints(self):
        """Test review endpoints"""
        print("\n" + "-"*80)
        print("TESTING REVIEW ENDPOINTS")
        print("-"*80)
        
        # List reviews
        self.test_endpoint('GET', '/api/reviews/', expected_status=200, 
                         description="[REVIEWS] List reviews")
        
        # Note: Creating reviews requires completed rentals
    
    def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        print("\n" + "-"*80)
        print("TESTING DASHBOARD ENDPOINTS")
        print("-"*80)
        
        # Owner dashboard
        self.test_endpoint('GET', '/api/dashboard/owner', expected_status=200, 
                         description="[DASHBOARD] Owner dashboard", user_type='owner')
        
        # Renter dashboard
        self.test_endpoint('GET', '/api/dashboard/renter', expected_status=200, 
                         description="[DASHBOARD] Renter dashboard", user_type='renter')
    
    def test_recommendations_endpoints(self):
        """Test recommendation endpoints"""
        print("\n" + "-"*80)
        print("TESTING RECOMMENDATION ENDPOINTS")
        print("-"*80)
        
        # Get recommendations
        self.test_endpoint('GET', '/api/recommendations', expected_status=200, 
                         description="[RECOMMENDATIONS] Get recommendations", user_type='renter')
    
    def test_survey_endpoints(self):
        """Test survey endpoints"""
        print("\n" + "-"*80)
        print("TESTING SURVEY ENDPOINTS")
        print("-"*80)
        
        # List surveys
        self.test_endpoint('GET', '/api/survey', expected_status=200, 
                         description="[SURVEY] List surveys")
        
        # Create survey response
        survey_data = {
            'preferred_instruments': 'Guitar, Piano',
            'experience_level': 'beginner',
            'favorite_genres': 'Rock, Pop',
            'budget_range': '25-50',
            'rental_frequency': 'monthly'
        }
        response = self.test_endpoint('POST', '/api/survey', survey_data, 
                                    expected_status=201, description="[SURVEY] Create survey response", 
                                    user_type='renter')
        if response and response.status_code == 201:
            self.test_data['survey_id'] = response.get_json().get('id')
    
    def test_chatbot_endpoints(self):
        """Test chatbot endpoints"""
        print("\n" + "-"*80)
        print("TESTING CHATBOT ENDPOINTS")
        print("-"*80)
        
        # Get sessions
        self.test_endpoint('GET', '/api/chatbot/sessions', expected_status=200, 
                         description="[CHATBOT] Get sessions", user_type='renter')
        
        # Chat endpoint
        chat_data = {'message': 'Hello, what instruments do you have?'}
        response = self.test_endpoint('POST', '/api/chatbot/chat', chat_data, 
                                    expected_status=200, description="[CHATBOT] Send message", 
                                    user_type='renter')
        if response and response.status_code == 200:
            session_data = response.get_json()
            if 'session_id' in session_data:
                self.test_data['chatbot_session_id'] = session_data['session_id']
        
        # Get chat history
        if 'chatbot_session_id' in self.test_data:
            self.test_endpoint('GET', f"/api/chatbot/history/{self.test_data['chatbot_session_id']}", 
                             expected_status=200, description="[CHATBOT] Get chat history", 
                             user_type='renter')
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total = self.results['passed'] + self.results['failed']
        pass_rate = (self.results['passed'] / total * 100) if total > 0 else 0
        
        print(f"\nTotal Endpoints Tested: {total}")
        print(f"[PASS] Passed: {self.results['passed']} ({pass_rate:.1f}%)")
        print(f"[FAIL] Failed: {self.results['failed']} ({100-pass_rate:.1f}%)")
        
        if self.results['failures']:
            print("\n" + "-"*80)
            print("FAILURES DETAIL")
            print("-"*80)
            for i, failure in enumerate(self.results['failures'], 1):
                print(f"\n{i}. {failure['endpoint']}")
                print(f"   Expected: {failure['expected']}")
                print(f"   Actual: {failure['actual']}")
                print(f"   Response: {json.dumps(failure['response'], indent=2)[:500]}")
        
        print("\n" + "="*80)
        if self.results['failed'] == 0:
            print("[OK] ALL TESTS PASSED!")
        else:
            print(f"[ERROR] {self.results['failed']} TEST(S) FAILED - Review details above")
        print("="*80 + "\n")

def main():
    """Run all tests"""
    tester = APITester()
    tester.run_all_tests()

if __name__ == '__main__':
    main()
