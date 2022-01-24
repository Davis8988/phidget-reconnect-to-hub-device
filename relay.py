from Phidget22.Phidget import *
from Phidget22.Devices.Hub import *
from Phidget22.Devices.DigitalOutput import *


ch = DigitalOutput()
# ch.setDeviceSerialNumber(635957)
ch.setIsHubPortDevice(True)
ch.setHubPort(1)
ch.setChannel(0)
# ch.setDeviceLabel("MainHub")

ch.openWaitForAttachment(5000)


ch.setDutyCycle(1.0)
print ("ch.getState()", ch.getState())


input("press enter to continue..")
ch.close()