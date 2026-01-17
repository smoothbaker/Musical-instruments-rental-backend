from app import create_app
import json

app = create_app()
client = app.test_client()

# Get Swagger JSON
response = client.get('/swagger.json')
data = response.get_json()

print('Swagger Paths Count:', len(data.get('paths', {})))
print()
print('Paths found:')
for path in sorted(data.get('paths', {}).keys())[:20]:
    print(f'  ✓ {path}')

total = len(data.get('paths', {}))
if total > 20:
    print(f'  ... and {total - 20} more')

print()
print('Sample endpoint details:')
if total > 0:
    first_path = sorted(data.get('paths', {}).keys())[0]
    print(f'\nFirst endpoint: {first_path}')
    print(json.dumps(data['paths'][first_path], indent=2)[:500])
