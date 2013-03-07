#!/bin/bash
cd ~/Developer/Android/adt-bundle-linux-x86/sdk/platform-tools
# makes it possible to connect in terminal with 'vncviewer localhost:5901' over USB
./adb forward tcp:5901 tcp:5901
# makes it possible to connect in browser with http://localhost:5801 (HTML5) 
./adb forward tcp:5801 tcp:5801
# opens a vnc session using the aliased vncviewer binary on ubuntu (and probably others)
vncviewer localhost:5901
# opens a vnc session using your browser if you have a HTML5 one like Safari or Chrome installed 
#open http://localhost:5801
