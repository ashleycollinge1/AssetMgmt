# windows client to run as a windows service
# collect data and push back up to the controller

# process
"""
2) Tell the service our serial number and confirm registration
    /api/agent/registration POST serialnumber, hostname, externalip, internalip
    returns our asset_id, api_key, uri to recieve instructions
3) Pull the instructions down from the service
    /api/agent/instructions GET apikey
    returns:
    {"heartbeat": "100",
     "data_upload_interval": "60"}
    Tells us how often we need to check and report back
    What info to report on
"""
import sys
import time
import socket
import logging
import win32serviceutil
import win32service
import win32event
import servicemanager, pythoncom
import requests, json, time,os, socket, wmi, pprint

CONFIG = {"HEARTBEAT_INTERVAL": 30}


def setup_logging():
    """
    Set up logging
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s '
                                  '- %(message)s')
    file_handler = logging.FileHandler('log.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def generate_data():
    """
    generate data and save in json format to be sent up to the
    service
    """
    data = {}
    generic = {}
    generic['hostname'] = socket.gethostname()
    c = wmi.WMI()
    for bios in c.Win32_BIOS():
        serialnumber = bios.SerialNumber
    generic['serialnumber'] = serialnumber
    for os in c.Win32_OperatingSystem():
        operatingsystem = os.caption
        servicepackversion = os.ServicePackMajorVersion
    generic['operatingsystem'] = operatingsystem
    generic['servicepackversion'] = servicepackversion
    for cs in c.Win32_ComputerSystem():
        manufacturer = cs.Manufacturer
        model = cs.Model
    generic['manufacturer'] = manufacturer
    generic['model'] = model
    logicalcorecount = 0
    physicalcorecount = 0
    for cpu in c.Win32_Processor():
        maxclockspeed = cpu.MaxClockSpeed
        logicalcorecount = logicalcorecount + cpu.NumberOfLogicalProcessors
        physicalcorecount = physicalcorecount + cpu.NumberOfCores
        cpu_model = cpu.Name
    generic['cpu_model'] = cpu_model
    generic['logicalcorecount'] = logicalcorecount
    generic['physicalcorecount'] = physicalcorecount
    generic['maxclockspeed'] = maxclockspeed
    memcapingb = 0
    for mem in c.Win32_PhysicalMemory():
        memcapingb = memcapingb + int(mem.Capacity)
    generic['memcapingb'] = memcapingb
    data['generic'] = generic
    return data


def writeconfigtofile(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)

def start_heartbeating(config):
    data = {"asset_id": config['asset_id']}
    headers = {'Content-type': 'application/json'}
    try:
        r = requests.post(config['heartbeat_uri'], data=json.dumps(data), headers=headers, verify=False)
    except requests.exceptions.ConnectionError:
        print("Could not connect to service")

class AppServerSvc(win32serviceutil.ServiceFramework):
    """
    Main class which allows controlling the service from Windows
    """
    _svc_name_ = "AssetMgmtClient"
    _svc_display_name_ = "AssetMgmt Client"

    def __init__(self, args):
        """
        Create the new service, create new event stating service is starting
        """
        self.logger = setup_logging()
        self.logger.info('Started AssetMgmtClient')
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.h_waitstop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.stop_requested = False

    def SvcStop(self):
        """
        Callback for when a stop is requested, the loops look at this to
        determine when to close themselves
        """
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.h_waitstop)
        self.stop_requested = True
        self.logger.info('Stop requested')

    def SvcDoRun(self):
        """
        Log message telling service manager that the service has started
        and start the main function which starts everything else
        """
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()


    def main(self):
        """
        creates a new thread for the web server and starts it
        Waits for stop requested to stop the web server thread
        """
        # start service loop
        pythoncom.CoInitialize()
        config = ""
        if os.path.isfile('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.logger.info('Config existed, loading it')
        if config:
            config_uri = "agent/configuration"
            try:
                r = requests.get("https://assetmgmt.ashleycollinge.co.uk/{}".format(config_uri), verify=False)
                config = r.json()['configuration']
                self.logger.info('Config loaded, writing it to file')
                writeconfigtofile(config)
            except requests.exceptions.ConnectionError:
                print("Could not connect to service")
        c = wmi.WMI()
        for bios in c.Win32_BIOS():
            serialnumber = bios.SerialNumber
        data = {"serialnumber": serialnumber, "hostname": socket.gethostname(), "domain": "synseal.com", "operating_system": "win7", "servicepackversion": 4}
        headers = {'Content-type': 'application/json'}
        registered = False
        no_config = False
        while not registered:
            time.sleep(2)
            if self.stop_requested:
                break  # break out of service loop as stop requested
            try:
                self.logger.info('not registered, trying to register now')
                r = requests.post("https://assetmgmt.ashleycollinge.co.uk/agent/register", data=json.dumps(data), headers=headers, verify=False)
                asset_id = r.json()['asset_id']
                config_uri = r.json()['config_uri']
                self.logger.info('registered successfully')
                registered = True
            except requests.exceptions.ConnectionError:
                print("Could not connect to service")
                print("Trying again...")
        while not no_config:
            time.sleep(2)
            if self.stop_requested:
                break  # break out of service loop as stop requested
            try:
                r = requests.get("https://assetmgmt.ashleycollinge.co.uk{}".format(config_uri), verify=False)
                config = r.json()['configuration']
                config['asset_id'] = asset_id
                writeconfigtofile(config)
                no_config = True
            except requests.exceptions.ConnectionError:
                print("Could not connect to service")
                print("Trying again...")

        data = generate_data()
        r = requests.post("https://assetmgmt.ashleycollinge.co.uk/agent/information_upload", data=json.dumps(data), headers=headers, verify=False)
        while 1:
            self.logger.info('start heartbeating')
            start_heartbeating(config)
            time.sleep(config['heartbeat_interval'])
            if self.stop_requested:
                break  # break out of service loop as stop requested


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AppServerSvc)
