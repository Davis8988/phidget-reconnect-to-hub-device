
from pathlib import Path
import os
import sys
import psutil
import time
import logging
from Phidget22.Devices.DigitalOutput import *
from Phidget22.Devices.Manager import Manager


# Dynamic path to this script's dir
script_dir = str((Path(sys.argv[0])).parent)
# script_dir = os.path.dirname(__file__)

log_file_path = os.environ.get("LOGFILE", os.path.join(f"{script_dir}", "hub_relay_phidget.log"))
# Set env var: LOGLEVEL  to:  'NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
log_format = '%(asctime)s %(levelname)-3s : %(message)s'
log_date_format = '%H:%M:%S'
log_level = os.environ.get("LOGLEVEL", "INFO")

phidget_manager_exe_process_name =                      os.environ.get("PHIDGET_MANAGER_EXE_PROCESS_NAME", "Phidget22Manager")
sleep_seconds_between_loops =                           int(str(os.environ.get("SLEEP_BETWEEN_LOOPS_SECONDS", 10)).strip())  # Default 10 seconds
phidget_hub_serial_number =                             int(str(os.environ.get("PHIDGET_HUB_SERIAL_NUMBER", 635957)).strip())
phidget_hub_name =                                      os.environ.get("PHIDGET_HUB_NAME", "Hub Port - Digital Output Mode").strip()
phidget_hub_port_number =                               int(str(os.environ.get("PHIDGET_HUB_PORT_NUMBER", 1)).strip())
phidget_hub_channel_number =                            int(str(os.environ.get("PHIDGET_HUB_CHANNEL_NUMBER", 0)).strip())
phidget_hub_wait_for_attachments_milliseconds_timeout = int(str(os.environ.get("PHIDGET_HUB_WAIT_FOR_ATTACHMENTS_MILLISECONDS_TIMEOUT", 5000)).strip())  # Default wait for 5 seconds
phidget_hub_power_on_duty_cycle =                       int(str(os.environ.get("PHIDGET_HUB_POWER_ON_DUTY_CYCLE", 1)).strip())
phidget_hub_power_off_duty_cycle =                      int(str(os.environ.get("PHIDGET_HUB_POWER_OFF_DUTY_CYCLE", 0)).strip())

# Global instances
logger = None
ch = None
manager = Manager()


print("Reconnect to HUB script - By David Yair [E030331]")

def get_running_process(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as err_msg:
            logger.error(err_msg)
            logger.info("Continuing anyway..")
    return None;


def validate_envs():
    global phidget_manager_exe_process_name
    logger.info("Validating envs")
    if phidget_manager_exe_process_name.lower().endswith(".exe"):
        logger.info(f"Removing '.exe' from env: PHIDGET_MANAGER_EXE_PROCESS_NAME={phidget_manager_exe_process_name}")
        lenToRemove = len('.exe')
        phidget_manager_exe_process_name = phidget_manager_exe_process_name[:-lenToRemove]
    logger.info("OK")


def reset_log_file():
    print(f"Checking if log file exist: {log_file_path}")
    try:
        if os.path.isfile(log_file_path):
            print(f"Removing old log file: {log_file_path}")
            os.remove(log_file_path)
    except BaseException as err_msg:
        logger.error(f"Failed removing old log file: {log_file_path}\nErr Msg:\n{err_msg}")
        sys.exit(1)


def configure_logger():
    global logger
    print(f"Writing logs to file: {log_file_path}")
    logging.basicConfig(level=log_level,
                        format=log_format,
                        filename=log_file_path,
                        filemode='a',
                        datefmt=log_date_format
                        )
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(log_format, datefmt=log_date_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def init_hub_obj():
    global ch
    logger.info("Initializing DigitalOutput() obj in 'ch' var")
    ch = DigitalOutput()
    logger.info(f"Setting hub serial number to: {phidget_hub_serial_number}")
    ch.setDeviceSerialNumber(phidget_hub_serial_number)
    logger.info("Setting hub port device: True")
    ch.setIsHubPortDevice(True)
    logger.info(f"Setting hub port number to: {phidget_hub_port_number}")
    ch.setHubPort(phidget_hub_port_number)
    logger.info(f"Setting hub channel to: {phidget_hub_channel_number}")
    ch.setChannel(phidget_hub_channel_number)


def connect_hub():
    global ch
    if ch.getAttached():
        logger.info("hub already attached")
        return
    logger.info("Attempting to connect to hub")
    logger.info(f"Please attach it via USB to this machine if not already attached")
    logger.info(f"Waiting for attachments (Timeout: {phidget_hub_wait_for_attachments_milliseconds_timeout} milliseconds)")
    ch.openWaitForAttachment(phidget_hub_wait_for_attachments_milliseconds_timeout)
    logger.info("OK - Found an attachment")   # Exception thrown if not - so wouldn't get here if an attachment wasn't found..


def manager_func_attached(manager, device):
    device_name = device.getDeviceName()
    logger.debug(f"Something was just attached. Checking if it's name: {device_name} is: '{phidget_hub_name}'")
    if device_name.lower().strip() != phidget_hub_name.lower():
        logger.debug(f"Attached device's name is different from: '{phidget_hub_name}'. New connected device is not '{phidget_hub_name}'. Continuing..")
        return
    logger.debug(f"Comparing attached device port number: {device.getHubPort()} to: {phidget_hub_port_number}")
    if device.getHubPort() != phidget_hub_port_number:
        logger.debug(f"Attached device's port number is different from: {phidget_hub_port_number}. New connected device is not '{phidget_hub_name}'. Continuing..")
        return
    logger.debug(f"Comparing attached device channel: {device.getChannel()} to: {phidget_hub_channel_number}")
    if device.getChannel() != phidget_hub_channel_number:
        logger.debug(f"Attached device's channel is different from: {phidget_hub_channel_number}. New connected device is not '{phidget_hub_name}'. Continuing..")
        return
    logger.info(f"OK - Found attached device and verified that it is the requested device. Connecting to it now")
    close_hub_connection()
    init_hub_obj()


def power_on_hub_relay_switch():
    global ch
    if not ch:
        logger.info(f"DigitalOutput() obj 'ch' is not initialized")
        logger.info(f"Please attach requested device to initialize it")
        logger.info(f"Requested Device:")
        logger.info(f"  phidget_hub_name: {phidget_hub_name}")
        logger.info(f"  phidget_hub_port_number: {phidget_hub_port_number}")
        logger.info(f"  phidget_hub_channel_number: {phidget_hub_channel_number}")
        return
    connect_hub()
    logger.info(f"Making sure hub has power on: ")
    logger.info(f"  port: {ch.getHubPort()} ")
    logger.info(f"  channel {ch.getChannel()} ")
    current_duty_cycle = ch.getDutyCycle()
    logger.info(f"Current relay switch state: {ch.getState()}")
    logger.info(f"Current relay switch cycle duty: {current_duty_cycle}")
    if current_duty_cycle != phidget_hub_power_on_duty_cycle:
        logger.info(f"Relay switch is NOT powered on")
        logger.info(f"Powering on the relay switch by sending duty cycle: {phidget_hub_power_on_duty_cycle}  to hub-port: {phidget_hub_port_number}  on channel: {phidget_hub_channel_number}")
        ch.setDutyCycle(phidget_hub_power_on_duty_cycle)
        logger.info(f"After powering on: relay switch state: {ch.getState()}")
    logger.info(f"OK. Relay switch is powered on")
    logger.info(f"Done")


def kill_running_phidget_manager_exe():
    # Check if any Phidget22Manager.exe process is running and kill it.
    global phidget_manager_exe_process_name
    logger.info(f"Checking if process: '{phidget_manager_exe_process_name}' is running")
    proc = get_running_process(phidget_manager_exe_process_name)
    if not proc:
        return
    logger.info(f"Found - Killing process..")
    try:
        proc.kill()
        logger.info(f"OK")
    except BaseException as err_msg:
        logger.error(err_msg)
        logger.info(f"Continuing anyway..")
    logger.info(f"Sleeping for: 1 seconds")
    time.sleep(1)


def init_manager_obj():
    logger.info("Initializing manager obj var")
    manager.setOnAttachHandler(manager_func_attached)
    manager.open()


def close_hub_connection():
    if not ch:
        return
    logger.info("Closing existing hub connection to relay switch")
    ch.close()
    ch.setDutyCycle(phidget_hub_power_off_duty_cycle)
    logger.info("hub connection closed successfully")


def close_manager_connection():
    if not manager:
        return
    logger.info("Closing existing manager connection to relay switch")
    manager.close()
    logger.info("manager connection closed successfully")


def main():
    reset_log_file()
    configure_logger()
    validate_envs()
    init_manager_obj()
    logger.info("Looping forever")
    try:
        while True:
            try:
                logger.info("")
                logger.info("Loop Started")
                kill_running_phidget_manager_exe()
                power_on_hub_relay_switch()
                logger.info("Finished")
                logger.info(f"Sleeping for: {sleep_seconds_between_loops} seconds")
                time.sleep(sleep_seconds_between_loops)
            except BaseException as err_msg:
                logger.error(f"Failure during loop forever of powering on relay switch\n{err_msg}")
                logger.info(f"Sleeping for: {sleep_seconds_between_loops} seconds")
                time.sleep(sleep_seconds_between_loops)
    finally:
        global ch
        close_hub_connection()
        close_manager_connection()





main()