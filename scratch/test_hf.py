import requests
API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
# No token for test
response = requests.post(API_URL, json={"inputs": "test query"})
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")
