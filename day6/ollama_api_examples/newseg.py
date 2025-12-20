import requests
from bs4 import BeautifulSoup

url = "https://news.ycombinator.com/"
html = requests.get(url).text

soup = BeautifulSoup(html, "html.parser")
titles = [t.get_text() for t in soup.find_all("a")][:10]
print(titles)
prompt = f"""
Summarize these news headlines:

{titles}

Return output in bullets.
"""

res = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "mistral", "prompt": prompt},
    stream=True
)
import json
for line in res.iter_lines():
    if line:
        print(json.loads(line.decode())["response"])
