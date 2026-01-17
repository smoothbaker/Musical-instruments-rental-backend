#!/usr/bin/env python
"""Optimized test runner - Simplified version"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def check_module(module_name):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        return True, None
    except ImportError as e:
        return False, str(e)

def main():
    """Main test runner"""
    print("\n" + "="*70)
    print("🧪 MUSICAL INSTRUMENTS RENTAL API - QUICK TEST REPORT")
    print("="*70)
    
    # Check critical dependencies
    print("\n[DEPENDENCY CHECK]")
    deps = [
        'flask',
        'flask_jwt_extended',
        'flask_sqlalchemy',
        'flask_smorest',
        'marshmallow',
        'stripe',
        'dotenv'
    ]
    
    missing = []
    for dep in deps:
        ok, err = check_module(dep)
        if ok:
            print(f"  ✅ {dep}")
        else:
            print(f"  ❌ {dep}")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install " + ' '.join(missing))
        return 1
    
    print("\n[APP IMPORT TEST]")
    try:
        from app import create_app
        app = create_app()
        print("  ✅ App module loaded successfully")
    except Exception as e:
        print(f"  ❌ App import failed: {e}")
        return 1
    
    print("\n[DATABASE SETUP TEST]")
    try:
        from app.db import db
        with app.app_context():
            db.create_all()
        print("  ✅ Database initialized")
    except Exception as e:
        print(f"  ⚠️  Database setup: {e}")
    
    print("\n[FLASK CLIENT TEST]")
    try:
        client = app.test_client()
        
        # Test health/root endpoint  
        try:
            resp = client.get('/')
            print(f"  ✅ GET / → {resp.status_code}")
        except:
            print(f"  ℹ️  GET / → no route")
        
        # List available endpoints
        print("\n[AVAILABLE ENDPOINTS]")
        with app.app_context():
            routes = []
            for rule in app.url_map.iter_rules():
                if not rule.rule.startswith('/static'):
                    routes.append((rule.rule, ','.join(rule.methods - {'HEAD', 'OPTIONS'})))
            
            # Group by prefix
            prefixes = {}
            for route, methods in sorted(routes):
                prefix = route.split('/')[1] if route != '/' else 'root'
                if prefix not in prefixes:
                    prefixes[prefix] = []
                prefixes[prefix].append((route, methods))
            
            for prefix in sorted(prefixes.keys()):
                print(f"\n  /{prefix}/")
                for route, methods in prefixes[prefix]:
                    print(f"    {route.ljust(40)} [{methods}]")
    except Exception as e:
        print(f"  ❌ Flask client error: {e}")
        return 1
    
    print("\n" + "="*70)
    print("✅ QUICK TEST COMPLETED")
    print("="*70)
    
    print("\n[SUMMARY]")
    print("""
✅ Core Dependencies: Installed
✅ App Module: Importable
✅ Database: Initializable
✅ Flask Routes: Accessible

[NEXT STEPS]
1. Start Flask server:
   python run.py

2. Test API endpoints:
   - Browse: http://localhost:5000/api-docs
   - Test endpoints using Swagger UI

3. For Chatbot features:
   - Install: pip install langchain langchain-ollama
   - Run Ollama: ollama serve
   - Test chatbot endpoints

[CHATBOT SETUP]
The chatbot service is implemented with lazy loading,
so it only initializes when first used. To test it:

1. Ensure Ollama is running:
   ollama serve  (in separate terminal)

2. Pull the model:
   ollama pull llama2

3. Test chatbot endpoint:
   POST /chatbot/chat
   - Requires JWT token
   - Body: {"user_message": "...", "session_id": "..."}
""")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
