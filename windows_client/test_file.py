import requests

r = requests.post("http://127.0.0.1:5000/agent/register")
print(r.content)

r = requests.post("http://127.0.0.1:5000/agent/heartbeat")
print(r.content)