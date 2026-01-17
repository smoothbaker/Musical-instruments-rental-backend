#!/usr/bin/env python
"""
Musical Instruments Rental API - Quick Start Guide
===================================================

This file provides quick reference commands for running and testing the API.
"""

import subprocess
import sys

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def run_api():
    """Start the Flask API"""
    print_section("🚀 STARTING API SERVER")
    print("Starting Flask development server...")
    print("API will be available at: http://localhost:5000")
    print("Swagger UI: http://localhost:5000/api-docs")
    print("ReDoc: http://localhost:5000/redoc")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        from app import create_app
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def test_api():
    """Run quick tests"""
    print_section("🧪 RUNNING TESTS")
    try:
        subprocess.run([sys.executable, 'quick_test.py'], check=True)
    except subprocess.CalledProcessError:
        print("Tests failed!")
        sys.exit(1)

def show_endpoints():
    """Show all available endpoints"""
    print_section("📋 AVAILABLE ENDPOINTS")
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        # Group routes by prefix
        routes = {}
        for rule in app.url_map.iter_rules():
            if not rule.rule.startswith('/static'):
                prefix = rule.rule.split('/')[1] if rule.rule != '/' else 'root'
                if prefix not in routes:
                    routes[prefix] = []
                methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
                routes[prefix].append((rule.rule, methods))
        
        for prefix in sorted(routes.keys()):
            print(f"\n[{prefix.upper()}]")
            for route, methods in sorted(routes[prefix]):
                print(f"  {methods.ljust(10)} {route}")

def show_setup_guide():
    """Show setup instructions"""
    print_section("📚 SETUP INSTRUCTIONS")
    
    guide = """
1. INITIAL SETUP
   pip install -r requirements.txt

2. (OPTIONAL) FOR CHATBOT FEATURES
   pip install langchain langchain-ollama
   
3. START OLLAMA (in separate terminal, optional)
   ollama serve
   
4. RUN THE API
   python quick_start.py api
   
5. TEST THE API
   python quick_start.py test

6. VIEW ENDPOINTS
   python quick_start.py endpoints

7. ACCESS DOCUMENTATION
   http://localhost:5000/api-docs (Swagger UI)
   http://localhost:5000/redoc (ReDoc)

ENVIRONMENT VARIABLES (optional):
   DATABASE_URL=postgresql://user:pass@localhost/dbname
   JWT_SECRET_KEY=your-secret-key
   STRIPE_API_KEY=sk_test_...
   OLLAMA_HOST=http://localhost:11434
"""
    print(guide)

def main():
    """Main CLI"""
    if len(sys.argv) < 2:
        print("""
        
╔═══════════════════════════════════════════════════════════════════╗
║   Musical Instruments Rental API - Quick Start Tool               ║
╚═══════════════════════════════════════════════════════════════════╝

USAGE:
    python quick_start.py <command>

COMMANDS:
    api         - Start the Flask API server
    test        - Run quick tests
    endpoints   - Show all available endpoints
    setup       - Show setup instructions
    help        - Show this help message

EXAMPLES:
    python quick_start.py api
    python quick_start.py test
    python quick_start.py endpoints

For more information, see TEST_AND_OPTIMIZATION_REPORT.md
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'api':
        run_api()
    elif command == 'test':
        test_api()
    elif command == 'endpoints':
        show_endpoints()
    elif command == 'setup':
        show_setup_guide()
    elif command == 'help':
        print("Use: python quick_start.py api|test|endpoints|setup|help")
    else:
        print(f"Unknown command: {command}")
        print("Use: python quick_start.py help")
        sys.exit(1)

if __name__ == '__main__':
    main()
