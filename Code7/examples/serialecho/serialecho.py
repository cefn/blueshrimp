# This code fuzz-tests the logic of 'long value' over a 7-bit transport
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
import sys
import serial
import time
import array
from random import randint

def print_binary_number(number):
	return bin(number).zfill(9).replace('0b','')

def print_binary_series(series):
	return " ".join(print_binary_number(entry) for entry in series)
		
if len(sys.argv) > 1 :
	devname = sys.argv[1]
else:
	devname = raw_input("What is the device name (e.g. ttyUSB0)? : ")

usbSerial = serial.Serial(('/dev/' + devname), 115200, timeout=2)

time.sleep(1)

#count steps for report
step=0

while 1 :

	long_value = randint( -2147483648, 2147483647) # choose a random long
	#long_value = randint( 0, 2147483647) # choose a random long
	#long_value = randint( 0, 256) # choose a random long
	#long_value = step  + 32768
	marshalled=[]
	marshall_long(long_value,marshalled)
	
	#create strings for debugging output
	canonicalLong = str(long_value)
	canonicalMarshalled = print_binary_series(marshalled)
	
	#execute encoding, serialization usbSerial.write method
	encoded = encode7(marshalled)
	canonicalEncoded = print_binary_series(encoded)
	serialized = serialize_bytes(encoded)
	arrayed = bytearray(serialized)
	
	# responses are only triggered by sending a serial line, so anything still in the buffer now is spurious
	usbSerial.flushInput()
	
	usbSerial.write(arrayed)
	receivedString = usbSerial.readline()
	
	if len(receivedString) > 0:
		receivedNumbers = receivedString.split(" ")
		receivedLong = receivedNumbers[0]
		receivedMarshalled = [int(receivedNumbers[1]), int(receivedNumbers[2]), int(receivedNumbers[3]), int(receivedNumbers[4])] ;
		receivedEncoded = [int(receivedNumbers[5]), int(receivedNumbers[6]), int(receivedNumbers[7]), int(receivedNumbers[8]), int(receivedNumbers[9])] ;
		if receivedLong.strip() != canonicalLong.strip():
			print("Encoding Failure")
		#print("Send: " + canonicalLong + ", " + canonicalMarshalled + ", " + canonicalEncoded)
		#print("Recv: " + receivedLong + ", " + print_binary_series(receivedMarshalled) + ", " + print_binary_series(receivedEncoded))
	else:
		print("Nothing received over serial - timeout")

	if step % 1024 == 0:
		print("Successfully reached:" + str(step) + " values encoded and decoded")
	step += 1
