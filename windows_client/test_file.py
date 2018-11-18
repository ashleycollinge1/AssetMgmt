import requests, json, time,os, socket, wmi


def generate_data():
    """
    generate data and save in json format to be sent up to the
    service
    """
    hostname socket.gethostname()
    c = wmi.WMI()
    for bios in c.Win32_BIOS():
        serialnumber = bios.SerialNumber
    print serialnumber
generate_data()

data = {"data": {"generic": {"hostname": "test01",
                             "serialnumber": "af13wd13",
                             "domain": "domain",
                             "operating_system": "wi7",
                             "service_pack_version": "701",
                             "last_bootup_time": "",
                             "manufacturer": "manufact",
                             "model": "model",
                             "memorygb": "8",
                             "physical_arch": "laptop"},
  "cpu_info": {"model": "i7",
                              "maxclockspeed": 8302,
                              "logicalcorecount": 3,
                              "physicalcorecount": 8},
  "disk_info": {"caption": "C"},
  "network_interfaces": [{"ip_address": "192.168.0.52",
                                         "mac_address": "fnoi2n",
                                         "subnet_mask": "255.255.255.0",
                                         "gateway": "10.1.1.1"},
                                         {"ip_address": "192.168.0.53",
                                         "mac_address": "fnofasn",
                                         "subnet_mask": "255.255.255.0",
                                         "gateway": "10.1.1.1"}],
  "installed_software": [{"DisplayVersion": "34.23",
                                         "DisplayName": "Software",
                                         "Publisher": "Microsoft"},
                                         {"DisplayVersion": "34.23",
                                         "DisplayName": "Software",
                                         "Publisher": "Microsoft"},
                                         {"DisplayVersion": "34.23",
                                         "DisplayName": "Software",
                                         "Publisher": "Microsoft"}]
}
}

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
        r = requests.get("http://assetmgmt.core.local:5000/{}".format(config_uri))
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
        r = requests.post("http://assetmgmt.core.local:5000/agent/register", data=json.dumps(data), headers=headers)
        asset_id = r.json()['asset_id']
        config_uri = r.json()['config_uri']
        registered = True
    except requests.exceptions.ConnectionError:
        print("Could not connect to service")
        print("Trying again...")
while not no_config:
    time.sleep(2)
    try:
        r = requests.get("http://assetmgmt.core.local:5000{}".format(config_uri))
        config = r.json()['configuration']
        writeconfigtofile(config)
        no_config = True
    except requests.exceptions.ConnectionError:
        print("Could not connect to service")
        print("Trying again...")

start_heartbeating(config['heartbeat_interval'])


