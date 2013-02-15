#!/bin/sh
# Connects to a paired Serial Bluetooth device
# to provide a serial connection for use by Arduino IDE 
# or pyfirmata-based python scripts 
# (proven with a JY-MCU baseboard and HC-06 module 
sudo rfcomm release /dev/rfcomm0
MACADDRESS="00:12:10:22:09:14"
rfcomm connect /dev/rfcomm0 ${MACADDRESS}
