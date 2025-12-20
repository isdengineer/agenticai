
import requests

def call_ollama(msg):
    r = requests.post("http://localhost:11434/api/generate",
                      json={"model": "llama3", "prompt": msg})
    return r.json().get("response", "")

context = "You are a tool-using agent."

while True:
    user = input("User: ")
    prompt = f"{context}\nUser: {user}\nAssistant:"
    print(call_ollama(prompt))
