import android
import time

BT_DEVICE_ID = '00:11:11:18:62:60'

ACCELERATION_SERIAL_PREFIX='acc'
ACCELERATION_SL4A_EVENT='display_acc'

BUTTON_SERIAL_PREFIX='btn'
BUTTON_SL4A_EVENT='display_btn'

RATE_SL4A_EVENT='display_rate'

droid = android.Android()
"""The first parameter is the service UUID for SerialPortServiceClass.
The second one is the address of your bluetooth module.
If the second one is ommited, Android shows you a selection at program start.
When this function succeeds the little led on the bluetooth module should stop blinking.
"""
droid.bluetoothConnect('00001101-0000-1000-8000-00805F9B34FB')

droid.webViewShow('file:///sdcard/sl4a/scripts/demoday.html')

begin = time.time()

uiRefreshed = 0
uiRefreshPeriod = 0.25

pushed = False
x      = 0 
y      = 0
z      = 0

sampleCount = 0

while True:
    
    now = time.time()
  
    sensor_data = droid.bluetoothReadLine().result  # read the line with the sensor value from arduino
    
    droid.eventClearBuffer()  # workaround for a bug in SL4A r4.
            
    if sensor_data.startswith(BUTTON_SERIAL_PREFIX) :
        payload = sensor_data[len(BUTTON_SERIAL_PREFIX):] # chop off prefix
        pushed = bool(int(payload)==1)
        sampleCount += 1        
        
    elif sensor_data.startswith(ACCELERATION_SERIAL_PREFIX) :
        payload = sensor_data[len(ACCELERATION_SERIAL_PREFIX):] # chop off prefix
        [x,y,z] = [int(item) for item in payload.split(',')]
        sampleCount += 1
        
    if now - uiRefreshed > uiRefreshPeriod :
        sampleRate = (sampleCount / (now - begin) )
        droid.eventPost(ACCELERATION_SL4A_EVENT, str([x,y,z]))
        droid.eventPost(BUTTON_SL4A_EVENT, str(pushed))
        droid.eventPost(RATE_SL4A_EVENT, str(sampleRate))
        uiRefreshed = now
