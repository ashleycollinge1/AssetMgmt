import requests, json, time

print("Registering as a client")


data = {"serialnumber": "hosefn93hr283n", "ipaddress": "192.168.0.56"}
headers = {'Content-type': 'application/json'}
r = requests.post("http://127.0.0.1:5000/agent/register", data=json.dumps(data), headers=headers)
asset_id = r.json()['asset_id']
config_uri = r.json()['config_uri']

print("Registered")
print(asset_id)
print("Pulling down configuration")

r = requests.get("http://127.0.0.1:5000{}".format(config_uri))
heartbeat_interval = r.json()['configuration']['heartbeat_interval']
heartbeat_uri = r.json()['configuration']['heartbeat_uri']

print("Heartbeat Interval: {}".format(heartbeat_interval))
print("Start heartbeating...")

while 1:
    time.sleep(heartbeat_interval)
    data = {"asset_id": asset_id}
    headers = {'Content-type': 'application/json'}
    r = requests.post(heartbeat_uri, data=json.dumps(data), headers=headers)
    print(r.json()['message'])