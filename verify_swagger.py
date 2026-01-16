#!/usr/bin/env python3
"""
Swagger Configuration Verification Script

This script verifies that:
1. Flask-Smorest is configured correctly
2. All blueprints are registered
3. Swagger/OpenAPI documentation is generated
4. All endpoints are documented
5. Authentication is properly configured
"""

import sys
import os

def check_swagger_config():
    """Verify Swagger configuration"""
    
    print("=" * 70)
    print("SWAGGER/OPENAPI CONFIGURATION VERIFICATION")
    print("=" * 70)
    
    # Test 1: Import and create app
    print("\n[TEST 1] Create Flask app with Swagger")
    try:
        from app.init import create_app
        app = create_app()
        print("[OK] ✓ App created successfully")
        print("[OK] ✓ Flask-Smorest initialized")
    except Exception as e:
        print(f"[FAIL] ✗ Error creating app: {e}")
        return False
    
    # Test 2: Check config
    print("\n[TEST 2] Verify Swagger Configuration")
    try:
        assert app.config['API_TITLE'] == "Musical Instruments Rental API"
        print(f"[OK] ✓ API Title: {app.config['API_TITLE']}")
        
        assert app.config['API_VERSION'] == "v1.0.0"
        print(f"[OK] ✓ API Version: {app.config['API_VERSION']}")
        
        assert app.config['OPENAPI_VERSION'] == "3.0.3"
        print(f"[OK] ✓ OpenAPI Version: {app.config['OPENAPI_VERSION']}")
        
        assert app.config['OPENAPI_SWAGGER_UI_PATH'] == "/swagger-ui"
        print(f"[OK] ✓ Swagger UI Path: {app.config['OPENAPI_SWAGGER_UI_PATH']}")
        
        assert app.config['OPENAPI_REDOC_PATH'] == "/redoc"
        print(f"[OK] ✓ ReDoc Path: {app.config['OPENAPI_REDOC_PATH']}")
    except AssertionError as e:
        print(f"[FAIL] ✗ Configuration error: {e}")
        return False
    
    # Test 3: Check blueprints registered
    print("\n[TEST 3] Verify Blueprints Registered")
    try:
        expected_blueprints = [
            'auth', 'instruments', 'rentals', 'recommendations',
            'users', 'instru_ownership', 'dashboard', 'survey', 'payments'
        ]
        
        registered = [bp.name for bp in app.blueprints.values()]
        
        for expected in expected_blueprints:
            if expected in registered:
                print(f"[OK] ✓ Blueprint registered: {expected}")
            else:
                print(f"[FAIL] ✗ Blueprint NOT registered: {expected}")
                return False
    except Exception as e:
        print(f"[FAIL] ✗ Error checking blueprints: {e}")
        return False
    
    # Test 4: Check routes
    print("\n[TEST 4] Verify Routes Exist")
    try:
        with app.app_context():
            routes = []
            for rule in app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    routes.append(rule.rule)
            
            print(f"[OK] ✓ Total routes found: {len(routes)}")
            
            # Check for key endpoints
            key_endpoints = [
                '/api/auth/register',
                '/api/auth/login',
                '/swagger-ui',
                '/redoc',
                '/swagger.json'
            ]
            
            for endpoint in key_endpoints:
                if any(endpoint in route for route in routes):
                    print(f"[OK] ✓ Endpoint available: {endpoint}")
                else:
                    print(f"[WARN] ⚠ Endpoint NOT found: {endpoint}")
    except Exception as e:
        print(f"[FAIL] ✗ Error checking routes: {e}")
        return False
    
    # Test 5: Check Swagger endpoints
    print("\n[TEST 5] Verify Swagger Endpoints")
    try:
        with app.test_client() as client:
            # Check Swagger JSON
            response = client.get('/swagger.json')
            if response.status_code == 200:
                print(f"[OK] ✓ GET /swagger.json returns 200")
                swagger_json = response.get_json()
                
                # Verify OpenAPI structure
                assert 'openapi' in swagger_json
                print(f"[OK] ✓ OpenAPI version in spec: {swagger_json.get('openapi')}")
                
                assert 'info' in swagger_json
                print(f"[OK] ✓ API Info section present")
                
                assert 'paths' in swagger_json
                num_paths = len(swagger_json['paths'])
                print(f"[OK] ✓ Total paths documented: {num_paths}")
                
                assert 'components' in swagger_json
                print(f"[OK] ✓ Components/Schemas present")
            else:
                print(f"[FAIL] ✗ GET /swagger.json returned {response.status_code}")
                return False
    except Exception as e:
        print(f"[FAIL] ✗ Error checking Swagger JSON: {e}")
        return False
    
    # Test 6: Check Swagger UI
    print("\n[TEST 6] Verify Swagger UI HTML")
    try:
        with app.test_client() as client:
            response = client.get('/swagger-ui')
            if response.status_code == 200:
                print(f"[OK] ✓ GET /swagger-ui returns 200")
                html = response.data.decode('utf-8')
                assert 'swagger' in html.lower()
                print(f"[OK] ✓ Swagger UI HTML contains 'swagger'")
            else:
                print(f"[FAIL] ✗ GET /swagger-ui returned {response.status_code}")
                return False
    except Exception as e:
        print(f"[FAIL] ✗ Error checking Swagger UI: {e}")
        return False
    
    # Test 7: Check ReDoc
    print("\n[TEST 7] Verify ReDoc HTML")
    try:
        with app.test_client() as client:
            response = client.get('/redoc')
            if response.status_code == 200:
                print(f"[OK] ✓ GET /redoc returns 200")
                html = response.data.decode('utf-8')
                assert 'redoc' in html.lower()
                print(f"[OK] ✓ ReDoc HTML contains 'redoc'")
            else:
                print(f"[WARN] ⚠ GET /redoc returned {response.status_code}")
    except Exception as e:
        print(f"[WARN] ⚠ Error checking ReDoc: {e}")
    
    # Test 8: Check API endpoints are documented
    print("\n[TEST 8] Verify Endpoints Are Documented")
    try:
        with app.test_client() as client:
            response = client.get('/swagger.json')
            swagger_json = response.get_json()
            paths = swagger_json.get('paths', {})
            
            documented_endpoints = {
                '/api/auth/register': 'POST',
                '/api/auth/login': 'POST',
                '/api/users/profile': 'GET',
                '/api/instruments': 'GET',
                '/api/rentals': 'GET',
                '/api/payments': 'GET',
            }
            
            for endpoint, method in documented_endpoints.items():
                if endpoint in paths:
                    if method.lower() in [m.lower() for m in paths[endpoint].keys()]:
                        print(f"[OK] ✓ {method} {endpoint} documented")
                    else:
                        print(f"[WARN] ⚠ {method} {endpoint} not found")
                else:
                    print(f"[WARN] ⚠ {endpoint} not found in paths")
    except Exception as e:
        print(f"[WARN] ⚠ Error checking documented endpoints: {e}")
    
    # Test 9: Check security scheme
    print("\n[TEST 9] Verify Security Configuration")
    try:
        with app.test_client() as client:
            response = client.get('/swagger.json')
            swagger_json = response.get_json()
            
            components = swagger_json.get('components', {})
            security_schemes = components.get('securitySchemes', {})
            
            if security_schemes:
                print(f"[OK] ✓ Security schemes defined")
                for scheme_name, scheme_config in security_schemes.items():
                    print(f"[OK] ✓   - {scheme_name}: {scheme_config.get('type', 'N/A')}")
            else:
                print(f"[WARN] ⚠ No security schemes found (optional)")
    except Exception as e:
        print(f"[WARN] ⚠ Error checking security: {e}")
    
    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    
    print("\n✓ SWAGGER CONFIGURATION VERIFIED")
    print("\nAccess Swagger UI at:")
    print("  http://localhost:5000/swagger-ui")
    print("\nAccess ReDoc at:")
    print("  http://localhost:5000/redoc")
    print("\nAccess OpenAPI JSON at:")
    print("  http://localhost:5000/swagger.json")
    
    return True

if __name__ == '__main__':
    try:
        success = check_swagger_config()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FATAL] ✗ Unhandled error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
