import requests

url = "http://127.0.0.1:5000/openai"

messages=[{"role": "system", "content": "Summarize this weather forecast in plain English."},
          {"role": "user", "content": "Scattered thunderstorms after 2pm, highs near 84 F wind 10-15 mph"}]

response = requests.post(url, json={"messages": messages})

print("Summary:", response.json().get("summary"))
