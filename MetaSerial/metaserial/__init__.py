import base64

# sketch out contract for Serial objects

device_names_arg = 'device_names'
dialog_title_arg = 'dialog_title'

class Serial:
    def __init__(self, *vargs, **kwargs):
        try:
            self.android = kwargs['android']
        except KeyError:
            pass

    # intended to return a bytearray with bytes read from serial, up to a maximum of numbytes
    # should ideally be implemented to block until at least one line is read, or a timeout is reached
    def read_line(self, maxBytes=1024):
        lineBytes = bytearray()
        lastRead = None
        for count in xrange(maxBytes):
            lastRead = bytearray(self.read(1))
            lineBytes.extend(lastRead)
            if lastRead == '\n' :
                break
        return lineBytes
    
    # intended to return a bytearray with bytes read from serial, up to a maximum of numbytes
    # should ideally be implemented to block until at least one byte is read, or a timeout is reached
    # when numbytes is not specified, it defaults to 1
    # when timeout is not specified, it defaults to -1 (block forever until the number of bytes is read)
    def read(self, numbytes=1,timeout=-1):
        raise NotImplementedError

    def write(self, data):
        raise NotImplementedError

    def close(self, data):
        raise NotImplementedError

    # provide generic routines for serial choosing

    def select_device(self, *args, **kwargs):
        
        try:
            selected_position = self.select_device_android(*args,**kwargs)
        except ImportError:
            selected_position = self.select_device_console(*args,**kwargs)
        
        return selected_position

    # common argument validation for all device selection routines
    def select_device_validate(*args,**kwargs):
        
        # autopopulate where possible
        for key, default in {
            device_names_arg:None,
            dialog_title_arg:'Please choose a device'
        }.iteritems() :
            if not(key) in kwargs:
                kwargs[key]=default

        # fail hard where key arguments are missing
        for key, error in {
            device_names_arg:'Please pass in a device_names array',
            dialog_title_arg:'A title is needed for the dialog'
        }.iteritems() :
            if not(key) in kwargs or kwargs[key]==None :
                raise ValueError(error)
        
        return (args, kwargs)

    # console based device choosing - returns position
    def select_device_console(self, *args, **kwargs):
        
        (args, kwargs) = self.select_device_validate(*args,**kwargs)

        try:
            dialogList = ','.join([(str(pos) + ') ' + name  + ' ') for pos,name in device_names])
            return int(raw_input(dialogTitle + dialogList))
        except ValueError:
            return None
        

    # android ui device choosing - returns position
    def select_device_android(self, *args, **kwargs):

        (args, kwargs) = self.select_device_validate(*args,**kwargs)
        
        droid = self.get_android(*args, **kwargs)            
        droid.dialogCreateAlert(kwargs[dialog_title_arg])
        droid.dialogSetSingleChoiceItems(kwargs[device_names_arg])
        #droid.dialogCreateInput(title=dialogTitle, message=dialogMessage)
        droid.dialogSetPositiveButtonText("OK")
        droid.dialogSetNegativeButtonText("Cancel")
        droid.dialogShow()
        
        button_transaction = droid.dialogGetResponse()
        selected_transaction = droid.dialogGetSelectedItems()
        
        print "Button pushed"
        print str(button_transaction)
        print "Selected item(s)"
        print repr(selected_transaction)
        
        if button_transaction.result['which']=='positive':
            return selected_transaction.result[0]
        else:
            return None

    # get hold of a reference to android SL4A object
    def get_android(self, *args, **kwargs):
        
        import android 

        if hasattr(self, 'android') :
            return self.android
        else:
            # populate defaults if not provided to configure android
            if 'android' in kwargs :
                return kwargs['android']
            else: 
                host = kwargs['host'] if 'host' in kwargs else None
                port = kwargs['port'] if 'port' in kwargs else None
                if host != None and port != None:
                    return android.Android([host,port])
                else:
                    return android.Android()


try:
    
    # attempt to define wrapper class for Android's native bluetooth serial support
    import android

    class SL4ASerial(Serial):

        def __init__(self, *args, **kwargs):
            Serial.__init__(self, *args, **kwargs)

            self.droid = self.get_android(*args,**kwargs)

            # connect bluetooth link
            SERIAL_UUID='00001101-0000-1000-8000-00805F9B34FB'
            if 'device_id' in kwargs:
                self.connection = self.droid.bluetoothConnect(SERIAL_UUID, kwargs['device_id']).result
            else:
                self.connection = self.droid.bluetoothConnect(SERIAL_UUID).result

        def port(self):
            return self.droid.bluetoothGetLocalName()

        def inWaiting(self): # TODO CH this should perhaps return a number of bytes, not a true/false, though it will probably work
            return self.droid.bluetoothReadReady().result

        def write(self,data):
            self.droid.bluetoothWriteBinary(base64.b64encode(data))

        def read(self, numbytes=1):
            result = self.droid.bluetoothReadBinary(numbytes).result
            if result != False :
                return base64.b64decode(result)
            else : 
                return result

        def close(self):
            self.droid.bluetoothStop()
            
except ImportError:
    pass

try:

    # attempt to define wrapper class for Bluez-based serial

    import bluetooth

    class BluezSerial(Serial):

        def __init__(self, *args, **kwargs):
            Serial.__init__(self, *args, **kwargs)

            bluetooth_service = kwargs['bluetooth_service'] if 'bluetooth_service' in kwargs else self.select_serial(*args,**kwargs)

            self.host = bluetooth_service['host']
            self.port = bluetooth_service['port']
            
            self.sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            self.sock.connect((self.host,self.port))

        def select_serial(self, *args, **kwargs):
            
            matches = bluetooth.find_service(uuid='00001101-0000-1000-8000-00805F9B34FB', address = None)

            for match in matches:
                match['friendlyName'] = bluetooth.lookup_name(match['host'])

            alternatives = [match['friendlyName'] for match in matches]
            
            kwargs[device_names_arg]=alternatives
            
            selected_position=self.select_device(*args,**kwargs)
            
            bluetooth_service = matches[selected_position]
            
            return bluetooth_service
        
        def write(self, data):
            self.sock.send(data)

        def read(self, maxBytes=1024):
            return self.sock.recv(maxBytes)

        def close(self):
            if self.sock != None:
                self.sock.close()
            self.host = None
            self.port = None
            self.sock = None

except ImportError: # 'bluetooth' module not available
    pass
    
try:

    # attempt to define wrapper class for Python-serial based serial
    import serial

    class PySerial(Serial):
        def __init__(self, *vargs, **kwargs):
            Serial.__init__(self, *vargs, **kwargs)
            self.port = kwargs['port'] if 'port' in kwargs else '/dev/ttyUSB0'
            self.baudrate = kwargs['baudrate'] if 'baudrate' in kwargs else 115200
            self.serial = serial.Serial(port=self.port,baudrate=self.baudrate)
            
        def read(self, size=1):
            self.serial.read(size)
        
        def write(self, data):
            self.serial.write(data)
            
        def close(self):
            self.serial.close()    
            
except ImportError: # 'serial' module not available
    pass
