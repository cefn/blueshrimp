import sys
sys.path.append('../../../../pyFirmata-cefn/')
from pyfirmata import Arduino,util
import time
from types import MethodType
from code7 import * 

# Command bytes
# These values must be greater than zero, and less than 0x69 (given the current Firmata protocol - ) 
# Future command bytes will be allocated in reverse from 0x69 downwards, so we start getting our app-specific
# command bytes from the other end of the address range. 

#Outbound command bytes
ULTRASONIC_QUERY=0x01
STEPPER_SET_LEFT=0x02
STEPPER_SET_RIGHT=0x03
STEPPER_QUERY_LEFT=0x04
STEPPER_QUERY_RIGHT=0x05

# Inbound command bytes
# We frequently allocate the same byte for the reply to a query
# as there can be no clash of semantics given the asymmetrical host and slave roles 
ULTRASONIC_REPORT=0x01
STEPPER_QUERY_CURRENT_LEFT  = 0x04  #asks for a report of the left motor's position
STEPPER_QUERY_CURRENT_RIGHT = 0x05  #asks for a report of the right motor's position
STEPPER_QUERY_TARGET_LEFT   = 0x06  #asks for a report of the left motor's position
STEPPER_QUERY_TARGET_RIGHT  = 0x07  #asks for a report of the right motor's position

STEPPER_REPORT_CURRENT_LEFT  = STEPPER_QUERY_CURRENT_LEFT  #asks for a report of the left motor's position
STEPPER_REPORT_CURRENT_RIGHT = STEPPER_QUERY_CURRENT_RIGHT #asks for a report of the right motor's position
STEPPER_REPORT_TARGET_LEFT   = STEPPER_QUERY_TARGET_LEFT   #asks for a report of the left motor's position
STEPPER_REPORT_TARGET_RIGHT  = STEPPER_QUERY_TARGET_RIGHT  #asks for a report of the right motor's position

global ultra_args
ultra_args = []

class Robot(Arduino):
    
    def __init__(self, *args,**kwargs):
        super(Robot, self).__init__(*args,**kwargs)
        self.ping_roundtrip = -1
        self.ping_timestamp = -1
        self.add_cmd_handler(ULTRASONIC_REPORT, self.handlePingReport)
        self.add_cmd_handler(STEPPER_REPORT_CURRENT_LEFT, self.handleStepperLeftCurrentReport)
        self.add_cmd_handler(STEPPER_REPORT_CURRENT_RIGHT, self.handleStepperRightCurrentReport)
        self.left = 0
        self.right = 0
        
    def turnAround(self, rotation):
        self.setLeft(self.left - ((rotation * 2048)//360))
        self.setRight(self.right + ((rotation * 2048)//360))

    def goForward(self, steps):
        self.setLeft(self.left + steps)
        self.setRight(self.right + steps)

    def setLeft(self, position):        
        self.send_sysex(STEPPER_SET_LEFT, encode7(marshall_long(-position)))
        self.left = position

    def setRight(self, position):        
        self.send_sysex(STEPPER_SET_RIGHT, encode7(marshall_long(position)))
        self.right = position
            
    def handlePingReport(self, *args, **kwargs):
        self.ping_roundtrip = unmarshall_long(decode7(args), 0)
        #self.ping_timestamp = unmarshall_unsigned_long(unencoded_payload, 4)
        print("Received Ping Report us: " + str(self.ping_roundtrip)) # + " at: " + str(self.ping_timestamp) )

    def handleStepperLeftCurrentReport(self, *args, **kwargs):
        print("Left Stepper Current: " + str(unmarshall_long(decode7(args), 0)))

    def handleStepperRightCurrentReport(self, *args, **kwargs):
        print("Right Stepper Current: " + str(unmarshall_long(decode7(args), 0)))

    def handleStepperLeftTargetReport(self, *args, **kwargs):
        print("Left Stepper Target: " + str(unmarshall_long(decode7(args), 0)))

    def handleStepperRightTargetReport(self, *args, **kwargs):
        print("Right Stepper Target: " + str(unmarshall_long(decode7(args), 0)))

android = False
if android :
    try:
        import android
        from pyfirmata import AndroidBluetoothUart
        uart = AndroidBluetoothUart()
    except ImportError:
        uart = None
        raise Error("Targeting wrong platform")
else:
    try:
        import serial
        uart = serial.Serial("/dev/rfcomm0", baudrate=115200)
    except ImportError:
        uart = None
        raise Error("Targeting wrong platform")

if uart == None:
    print("No Uart available in this environment, bailing")
    sys.exit()

robot = Robot(uart)
iterator = util.Iterator(robot)
iterator.setDaemon(True)
iterator.start()

#turn on and off LED for Debugging
robot.digital[13].write(1)
time.sleep(1)
robot.digital[13].write(0)

'''
while True:
    try:
        robot.send_sysex(ULTRASONIC_QUERY)
        time.sleep(0.05)
    except KeyboardInterrupt :
        break
'''
