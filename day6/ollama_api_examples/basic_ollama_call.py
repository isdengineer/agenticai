
import requests

url = "http://localhost:11434/api/generate"
payload = {"model": "llama3", "prompt": "Explain what an API is."}

resp = requests.post(url, json=payload, stream=True)
for line in resp.iter_lines():
    if line:
        print(line.decode())
