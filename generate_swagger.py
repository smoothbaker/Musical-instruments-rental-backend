#!/usr/bin/env python
"""Generate swagger.json from the Flask API"""

import json
from app import create_app

def main():
    app = create_app()
    client = app.test_client()
    
    # Get the swagger specification
    response = client.get('/swagger.json')
    
    if response.status_code == 200:
        swagger_data = response.get_json()
        
        # Save to file
        with open('swagger.json', 'w') as f:
            json.dump(swagger_data, f, indent=2)
        
        print("✅ swagger.json generated successfully!")
        print(f"   📋 API Title: {swagger_data.get('info', {}).get('title', 'N/A')}")
        print(f"   📌 API Version: {swagger_data.get('info', {}).get('version', 'N/A')}")
        print(f"   🔗 Endpoints: {len(swagger_data.get('paths', {}))}")
        
        # Print available paths
        print("\n📊 Available Endpoints:")
        for path, methods in sorted(swagger_data.get('paths', {}).items()):
            http_methods = list(methods.keys())
            http_methods = [m.upper() for m in http_methods if m not in ['parameters']]
            print(f"   {', '.join(http_methods).ljust(20)} {path}")
    else:
        print(f"❌ Error: Failed to get swagger.json (Status {response.status_code})")

if __name__ == '__main__':
    main()
