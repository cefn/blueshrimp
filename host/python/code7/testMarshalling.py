# This code fuzz-tests the logic of 'long value' encoding over a 7-bit transport
# suited for encapsulation inside Firmata (MIDI) Sysex packets

# long_value is expected to fall within the bounds of like a 4 byte integer (arduino long value)
# any values outside this are ignored (lost) in the encoding and will therefore create a mismatch
# between the python canonical string and the Arduino sprintf-encoded reply after decoding


# Firmata-unique header, and assignment of Stepper "command" data space
# Not currently used - to be reincorporated in test when mature
'''
STEPPER_HEADER = 0x0D
STEPPER_SPEED = 0x01
STEPPER_POSITION = 0x02 
STEPPER_LEFT = 0x02 
STEPPER_LEFT = 0x04
STEPPER_RIGHT = 0x08
'''

from code7 import *
import serial
import time
import array
from random import randint

def print_as_binary(number):
	return bin(number).zfill(9).replace('b','0')
	
usbSerial = serial.Serial('/dev/ttyUSB0', 115200, timeout=2)

time.sleep(1)

long_value = 9

while 1 :

	#long_value = randint( -2147483648, 2147483647) # choose a random long
	#long_value = randint( 0, 256) # choose a random long
	marshalled=[]
	marshall_long(long_value,marshalled)
	
	#create strings for debugging output
	canonicalLong = str(long_value)
	canonicalBytes = " ".join(print_as_binary(entry) for entry in marshalled)
	
	#execute encoding, serialization usbSerial.write method
	encoded = encode7(marshalled)
	serialized = serialize_bytes(encoded)
	arrayed = bytearray(serialized)
	
	# responses are only triggered by sending a serial line, so anything still in the buffer now is spurious
	usbSerial.flushInput()
	
	usbSerial.write(arrayed)
	usbSerial.write('\n')
	receivedString = usbSerial.readline()
	
	if len(receivedString) > 0:
		receivedNumbers = receivedString.split(" ")
		receivedLong = receivedNumbers[0]
		receivedBytes = [int(receivedNumbers[1]), int(receivedNumbers[2]), int(receivedNumbers[3]), int(receivedNumbers[4])] ;
		if receivedLong.strip() != canonicalLong.strip():
			print("Encoding Failure")
		print("Send: " + canonicalLong + ", " + canonicalBytes)
		print("Recv: " + receivedLong + ", " + " ".join(print_as_binary(receivedByte) for receivedByte in receivedBytes) )
	else:
		print("Nothing received over serial - timeout")

	if long_value % 1024 == 0:
		print("Successfully reached:" + str(long_value))
	long_value += 1
