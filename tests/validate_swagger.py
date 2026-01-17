#!/usr/bin/env python
"""Validate and display swagger.json"""

import json

# Load and validate
with open('swagger.json', 'r') as f:
    swagger = json.load(f)

print('✅ swagger.json is valid JSON')
print(f'   API: {swagger["info"]["title"]}')
print(f'   Version: {swagger["info"]["version"]}')
print(f'   Total Endpoints: {len(swagger["paths"])}')
print(f'   OpenAPI: {swagger["openapi"]}')
print()
print('📊 Endpoints by Category:')

# Count by tag
tags_count = {}
for path, methods in swagger["paths"].items():
    for method, details in methods.items():
        if isinstance(details, dict) and 'tags' in details:
            tag = details['tags'][0] if details['tags'] else 'Other'
            if tag not in tags_count:
                tags_count[tag] = 0
            tags_count[tag] += 1

for tag in sorted(tags_count.keys()):
    print(f'   {tag}: {tags_count[tag]} endpoints')

print()
print('🔒 Authentication: JWT Bearer Token')
print('   Get token: POST /api/auth/login')
print('   Use token: Add "Authorization: Bearer YOUR_TOKEN" header')
print()
print('📚 View in Browser:')
print('   Swagger UI: http://localhost:5000/swagger-ui')
print('   ReDoc: http://localhost:5000/redoc')
print('   JSON: http://localhost:5000/swagger.json')
