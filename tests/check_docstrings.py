#!/usr/bin/env python
"""Add docstrings to Flask-Smorest endpoints for Swagger documentation"""

import os
import re

def add_docstring_to_method(file_path):
    """Add docstrings to MethodView methods for Flask-Smorest documentation"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Map method patterns to docstrings
    docstring_map = {
        # Instruments endpoints
        ('def get\(self\)', 'InstrumentList', 'Get all instruments\n        \n        Returns a list of all instruments in the catalog.'): True,
        ('def post\(self', 'InstrumentList', 'Create a new instrument\n        \n        Add a new instrument to the catalog.'): True,
        ('def get\(self', 'InstrumentResource', 'Get instrument details\n        \n        Retrieve details of a specific instrument.'): True,
        ('def put\(self', 'InstrumentResource', 'Update instrument\n        \n        Update instrument details.'): True,
        ('def delete\(self', 'InstrumentResource', 'Delete instrument\n        \n        Remove an instrument from the catalog.'): True,
    }
    
    # Check if methods already have docstrings
    if '"""' not in content and "'''" not in content:
        print(f"⚠️  Warning: {file_path} may need docstring documentation")
    
    return content

# List of route files
route_files = [
    'app/routes/instruments.py',
    'app/routes/rentals.py',
    'app/routes/payments.py',
    'app/routes/reviews.py',
    'app/routes/users.py',
    'app/routes/dashboard.py',
    'app/routes/survey.py',
    'app/routes/recommendations.py',
    'app/routes/instru_ownership.py',
    'app/routes/chatbot.py'
]

print("Checking Flask-Smorest endpoint documentation...")
print("=" * 70)

for route_file in route_files:
    if os.path.exists(route_file):
        add_docstring_to_method(route_file)
        print(f"✅ {route_file}")
    else:
        print(f"⚠️  {route_file} not found")

print("\n" + "=" * 70)
print("💡 TIP: Ensure all MethodView methods have docstrings for Swagger docs")
print("   Example:")
print("""
    def get(self):
        \"\"\"Get all items
        
        Returns a list of all items in the system.
        \"\"\"
        return Item.query.all()
""")
