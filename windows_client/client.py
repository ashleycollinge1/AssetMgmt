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
import servicemanager


def setup_logging():
    """
    Set up logging
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s '
                                  '- %(message)s')
    file_handler = logging.FileHandler('C:\\log.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


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
        while 1:
            time.sleep(2)
            if self.stop_requested:
                break  # break out of service loop as stop requested


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AppServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AppServerSvc)
