import requests

# 1. Get GitHub repo metadata
repo = "tensorflow/tensorflow"
url = f"https://api.github.com/repos/{repo}"
github_data = requests.get(url).json()

# 2. Summarize using Ollama
prompt = f"""
Summarize this GitHub repository for a beginner:

{github_data}

Explain:
- What the project does
- Who should use it
- Popularity signals (stars, forks, watchers)
- Licensing
"""

ollama_res = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "mistral", "prompt": prompt},
    stream=True
)

for c in ollama_res.iter_lines():
    if c:
        print(c.decode())
