import requests, json, time,os

def writeconfigtofile(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)

def start_heartbeating(interval):
    print("Heartbeat Interval: {}".format(interval))
    print("Start heartbeating...")

    while 1:
        time.sleep(interval)
        data = {"asset_id": config['asset_id']}
        headers = {'Content-type': 'application/json'}
        try:
            r = requests.post(config['heartbeat_uri'], data=json.dumps(data), headers=headers)
            print(r.json()['message'])
        except requests.exceptions.ConnectionError:
            print("Could not connect to service")

config = ""
if os.path.isfile('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)


if config:
    config_uri = "agent/configuration"
    try:
        r = requests.get("http://127.0.0.1:5000/{}".format(config_uri))
        config = r.json()['configuration']
        writeconfigtofile(config)
        start_heartbeating(config['heartbeat_interval'])
    except requests.exceptions.ConnectionError:
        print("Could not connect to service")

data = {"serialnumber": "hosefn93hr283n", "hostname": "host01", "domain": "test.com", "operating_system": "win7", "servicepackversion": 4}
headers = {'Content-type': 'application/json'}
registered = False
no_config = False
while not registered:
    time.sleep(2)
    try:
        r = requests.post("http://127.0.0.1:5000/agent/register", data=json.dumps(data), headers=headers)
        asset_id = r.json()['asset_id']
        config_uri = r.json()['config_uri']
        registered = True
    except requests.exceptions.ConnectionError:
        print("Could not connect to service")
        print("Trying again...")
while not no_config:
    time.sleep(2)
    try:
        r = requests.get("http://127.0.0.1:5000{}".format(config_uri))
        config = r.json()['configuration']
        writeconfigtofile(config)
        no_config = True
    except requests.exceptions.ConnectionError:
        print("Could not connect to service")
        print("Trying again...")

start_heartbeating(config['heartbeat_interval'])


