from pyfirmata import Arduino,util
from time import sleep
from types import MethodType
from code7 import * 

global ultra_args
ultra_args = []

# These values must be greater than zero, and less than 0x69 (given the current Firmata protocol - ) 
# Future command bytes will be allocated in reverse from 0x69 downwards, so we start getting our app-specific
# command bytes from the other end of the address range. We are allocating the same byte for each direction
# as there can be no clash of semantics given the asymmetrical host and slave roles 
ULTRASONIC_DISTANCE_RESPONSE=0x01
ULTRASONIC_DISTANCE_QUERY=0x01

#shrimp = Arduino("/dev/rfcomm0",baudrate=115200)
shrimp = Arduino("/dev/ttyUSB0", baudrate=115200)
iterator = util.Iterator(shrimp)
iterator.start()

# bind a convenience function to permit stopping the iterator
def stop_iterator(self):
	self._Thread__stop()
iterator.stop = MethodType(stop_iterator,iterator)

def debug_sysex_ultrasonic(*args, **kwargs):
	global ultra_args
	ultra_args = args
	decoded_bytes = decode7(args)
	decoded_long = unmarshall_long(decoded_bytes)
	print("Ultrasonic distance response received : number " + str(decoded_long))	
		
shrimp.add_cmd_handler(ULTRASONIC_DISTANCE_RESPONSE, debug_sysex_ultrasonic)

while True:
	shrimp.send_sysex(ULTRASONIC_DISTANCE_QUERY)
	sleep(0.05)
