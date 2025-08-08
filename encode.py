import base64

with open('gdrive-key.json', 'r') as f:
    content = f.read()

encoded = base64.b64encode(content.encode()).decode()
print(encoded)