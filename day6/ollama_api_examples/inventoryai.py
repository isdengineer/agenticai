import requests

product=input("Enter the product")
# 1. Get GitHub repo metadata

url = f" http://127.0.0.1:5000/inventory/{product}"
inventory_data = requests.get(url).json()

# 2. Summarize using Ollama
prompt = f"""
Based on following data

{inventory_data}

Explain:
- What the product is available with how much stocks
"""

ollama_res = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "mistral", "prompt": prompt},
    stream=True
)
import json
for c in ollama_res.iter_lines():
    if c:
        print(json.loads(c.decode())["response"])
