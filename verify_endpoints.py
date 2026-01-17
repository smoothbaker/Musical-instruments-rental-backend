#!/usr/bin/env python
"""Verify Flask-Smorest endpoint documentation"""

import json
from app import create_app

def verify_endpoints():
    """Verify all endpoints are properly registered and documented"""
    app = create_app()
    
    print("=" * 70)
    print("🔍 FLASK API ENDPOINT VERIFICATION")
    print("=" * 70)
    
    # Get all registered routes
    print("\n📋 All Registered Flask Routes:")
    print("-" * 70)
    
    routes_by_module = {}
    for rule in app.url_map.iter_rules():
        if not rule.rule.startswith('/static') and not rule.rule.startswith('/debug'):
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            module = rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'root'
            
            if module not in routes_by_module:
                routes_by_module[module] = []
            
            routes_by_module[module].append((rule.rule, methods, rule.endpoint))
    
    total_routes = 0
    for module in sorted(routes_by_module.keys()):
        routes = routes_by_module[module]
        print(f"\n{module.upper()} ({len(routes)} endpoints):")
        for route, methods, endpoint in sorted(routes):
            print(f"  {methods.ljust(15)} {route.ljust(40)} [{endpoint}]")
            total_routes += 1
    
    print(f"\n✅ Total Routes Registered: {total_routes}")
    
    # Check Swagger/OpenAPI documentation
    print("\n" + "=" * 70)
    print("📚 SWAGGER/OPENAPI DOCUMENTATION")
    print("=" * 70)
    
    with app.test_client() as client:
        # Get OpenAPI spec
        response = client.get('/swagger.json')
        
        if response.status_code == 200:
            swagger_data = response.get_json()
            
            print(f"\n✅ Swagger JSON is accessible")
            print(f"   Title: {swagger_data.get('info', {}).get('title')}")
            print(f"   Version: {swagger_data.get('info', {}).get('version')}")
            print(f"   OpenAPI Version: {swagger_data.get('openapi')}")
            
            # Count endpoints in Swagger
            endpoints_in_swagger = len(swagger_data.get('paths', {}))
            print(f"\n📊 Endpoints in Swagger Documentation: {endpoints_in_swagger}")
            
            if endpoints_in_swagger > 0:
                print(f"\n   Documented Paths:")
                for path in sorted(swagger_data.get('paths', {}).keys()):
                    methods = list(swagger_data['paths'][path].keys())
                    methods = [m.upper() for m in methods if m not in ['parameters']]
                    print(f"      {', '.join(methods).ljust(15)} {path}")
            
            # Check for security schemes
            has_security = 'securitySchemes' in swagger_data.get('components', {})
            print(f"\n🔐 Security Schemes Defined: {'✅ Yes' if has_security else '❌ No'}")
            
            if has_security:
                for scheme_name, scheme_data in swagger_data['components']['securitySchemes'].items():
                    print(f"    - {scheme_name}: {scheme_data.get('scheme', 'custom')}")
        
        else:
            print(f"❌ Error: Swagger JSON not accessible (Status: {response.status_code})")
    
    # Verify Flask-Smorest configuration
    print("\n" + "=" * 70)
    print("⚙️  FLASK-SMOREST CONFIGURATION")
    print("=" * 70)
    
    config_keys = [
        'API_TITLE',
        'API_VERSION', 
        'OPENAPI_VERSION',
        'OPENAPI_SWAGGER_UI_PATH',
        'OPENAPI_REDOC_PATH',
        'OPENAPI_URL_PREFIX'
    ]
    
    print("\nConfiguration Values:")
    for key in config_keys:
        value = app.config.get(key, 'NOT SET')
        status = '✅' if value != 'NOT SET' else '❌'
        print(f"  {status} {key}: {value}")
    
    # Test Swagger UI
    print("\n" + "=" * 70)
    print("🌐 SWAGGER UI ACCESSIBILITY")
    print("=" * 70)
    
    with app.test_client() as client:
        endpoints = [
            ('/swagger-ui', 'Swagger UI'),
            ('/redoc', 'ReDoc'),
            ('/swagger.json', 'OpenAPI JSON'),
            ('/', 'API Root'),
            ('/health', 'Health Check')
        ]
        
        for endpoint, name in endpoints:
            response = client.get(endpoint)
            status = '✅' if response.status_code in [200, 302] else '❌'
            print(f"  {status} {name.ljust(20)} {endpoint.ljust(20)} [HTTP {response.status_code}]")
    
    print("\n" + "=" * 70)
    print("✨ VERIFICATION COMPLETE")
    print("=" * 70)
    print("\n📌 To test endpoints:")
    print("   1. Start server: python run.py")
    print("   2. Open: http://localhost:5000/swagger-ui")
    print("   3. Click 'Try it out' on any endpoint")
    print("\n🔑 Authentication:")
    print("   - Register: POST /api/auth/register")
    print("   - Login: POST /api/auth/login (get JWT token)")
    print("   - Use token: Add 'Authorization: Bearer <token>' header")

if __name__ == '__main__':
    verify_endpoints()
