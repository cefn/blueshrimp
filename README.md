blueshrimp
==========

This repository contains some example scripts and code to support the use of Bluetooth serial with the Shrimp, permitting developers to explore the possibility of physical prototyping networked via desktop or Android phone. 

In particular...
* ShrimpFirmata Sketch and Python module which demonstrates how to seamlessly communicate from python to a serially-connected Arduino-compatible microcontroller to monitor and control digital and analog pins, servos and I2C connected devices, as well as application-specific actuators and sensors, with slave-hosted management code such as stepper motors or Ultrasonic sensors
* Code7 Arduino library, sketches and Python scripts demonstrating multi-byte communication over 7 bits
* Python examples demonstrating applications designed building on this control layer, and deployed over a (Bluetooth) serial link 
* Android-hosted scripts which connect from a phone (with "Scripting Layer for Android" and "Python for Android") and interact with a serially-connected ShrimpFirmata
* Utility scripts used in development, such as those to auto-connect a paired Bluetooth device, or configure remote Android screen sharing. These will be authored to work and tested on Linux, but will likely run on Mac unmodified or be easy to port to either Mac or Windows.
