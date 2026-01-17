"""Quick test to verify all Swagger endpoints are accessible and working"""

from app import create_app
import json

def test_endpoints():
    app = create_app()
    client = app.test_client()
    
    print("Testing Swagger Documentation Endpoints...\n")
    
    # Test Swagger UI
    response = client.get('/swagger-ui/')
    print(f"Swagger UI: {response.status_code} {'OK' if response.status_code == 200 else 'FAILED'}")
    
    # Test ReDoc
    response = client.get('/redoc/')
    print(f"ReDoc: {response.status_code} {'OK' if response.status_code == 200 else 'FAILED'}")
    
    # Test OpenAPI JSON
    response = client.get('/swagger.json')
    if response.status_code == 200:
        data = response.get_json()
        print(f"OpenAPI JSON: {response.status_code} OK")
        print(f"   - Endpoints documented: {len(data.get('paths', {}))}")
        print(f"   - Schemas defined: {len(data.get('components', {}).get('schemas', {}))}")
    else:
        print(f"OpenAPI JSON: {response.status_code} FAILED")
    
    # Test a few sample endpoints
    print("\nTesting Sample Endpoints:")
    
    # Root endpoint
    response = client.get('/')
    print(f"GET /: {response.status_code} {'OK' if response.status_code == 200 else 'FAILED'}")
    
    # Health check
    response = client.get('/health')
    print(f"GET /health: {response.status_code} {'OK' if response.status_code == 200 else 'FAILED'}")
    
    # API root
    response = client.get('/api')
    print(f"GET /api: {response.status_code} {'OK' if response.status_code in [200, 302] else 'FAILED'}")
    
    # Instruments list (should work without auth)
    response = client.get('/api/instruments')
    print(f"GET /api/instruments: {response.status_code} {'OK' if response.status_code == 200 else 'FAILED'}")
    
    print("\nAll tests completed!")

if __name__ == '__main__':
    test_endpoints()
