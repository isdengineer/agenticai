
import requests

stock = requests.get("https://dummyjson.com/quotes/1").json()

prompt = f"Analyze this stock quote and return JSON: {stock}"

res = requests.post("http://localhost:11434/api/generate",
                    json={"model": "llama3", "prompt": prompt})

print(res.text)
