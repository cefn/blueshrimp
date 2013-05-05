#!/bin/sh
# relies on package bluez-utils
# get the mac address with...
#   hcitool scan
#MACADDRESS="07:12:11:23:70:57"
MACADDRESS="00:13:01:07:04:24"
# possibly needed to workaround the fact rfcomm needs to be 
# run as sudo all the time
sudo chmod u+s /usr/bin/rfcomm
# tells the system what the pairing code will be when needed
echo "1234" | bluez-simple-agent hci0 ${MACADDRESS}
# activate bluetooth baseband to device (not paired or connected)
# and trigger the pairing
sudo bash -c "hcitool cc ${MACADDRESS} && hcitool auth ${MACADDRESS}"
# triggers the connection
rfcomm connect rfcomm0 ${MACADDRESS}
# alternatives below
#rfcomm -i hci0 connect 0 ${MACADDRESS}
#rfcomm bind rfcomm0 07:12:11:23:70:57
