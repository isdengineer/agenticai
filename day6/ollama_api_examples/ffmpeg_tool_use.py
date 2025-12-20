
import subprocess, json, requests

cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", "sample.mp4"]
meta = subprocess.run(cmd, capture_output=True, text=True)
data = meta.stdout

prompt = f"Analyze this video metadata: {data}"

res = requests.post("http://localhost:11434/api/generate",
                    json={"model": "llama3", "prompt": prompt},
                    stream=True)

for l in res.iter_lines():
    if l:
        print(l.decode())
