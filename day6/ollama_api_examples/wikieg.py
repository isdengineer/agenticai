import requests

topic = "Apache Spark"
url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"

wiki_data = requests.get(url,headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"}).text
print(wiki_data)
prompt = f"""
Explain this topic in simple words:

{wiki_data}
"""

res = requests.post("http://localhost:11434/api/generate",
                    json={"model": "mistral", "prompt": prompt},
                    stream=True)

for l in res.iter_lines():
    if l:
        print(l.decode())
