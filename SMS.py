import serial
import sys
import time
from serial.tools import list_ports

class SMS:
    #debug
    debug = True

    #Useful commands
    text_mode = "+CMGF=1"       #Set to text mode for sms communication
    pdu_mode = "+CMGF=0"
    send_sms = "+CMGS="
    list_sms = '+CMGL='
    list_all = '"ALL"'
    list_unread = '"REC UNREAD"'
    list_read = '"REC READ"'
    delete_sms = "+CMGD="
    ctrl_z = chr(26)        #Used to send message
    signal_strength = "+CSQ"
    netowrk_time = "+CCLK?"     #Get time
    op_mode = "+CFUN"
    low_power = 0
    online = 1
    offline = 4
    reset = 6
    radio_off = 7

    port = None
    def __init__(self, portString="/dev/ttyUSB1", timeout = 5):
        try:
            self.port = self.openPort(portString, timeout)
        except IOError as details:
            sys.stderr.write("SMS: ",str(details))

    def __del__(self):
        if self.checkPort():
            self.port.close()

    def checkPort(self):
        return self.port is not None and self.port.isOpen()

    def _debug_(self,response):
        if self.debug:
            sys.stdout.write(response)

    def serialReadline(self, eol='\n'):
        line = ""
        while 1:
            char = self.port.read()
            line += char
            if (char == eol or char == ''):
                break
        self._debug_(line)
        line = line.strip()
        return line

    def openPort(self, port, to):
        ser = None
        try:
            ser = serial.Serial(port, 115200, timeout = to)
        except ValueError:
            sys.stderr.write("Port parameters are out of range")
            exit(1)
        except serial.SerialException :
            sys.stderr.write(port+" cannot be found or cannot be configured")
            exit(1)
        return ser

    def checkMode(self):
        self.sendCommand(self.op_mode+'?')
        dummy = self.serialReadline()       #\r\n
        response = self.serialReadline().strip()       #mode
        dummy = self.serialReadline()       #\r\n
        dummy = self.serialReadline()       #OK
        return response

    def sendCommand(self, cmd):
        if self.port is None:
            print "Serial port is not open. Please call openPort first"
        #Check if port open
        if not self.port.isOpen():
            print "Serial port is not open. Please call openPort first"
        self.port.write("AT" + cmd + "\r")
        #_debug_("AT" + cmd)
        return

    def sendMessage(self, number, msg):
        response = self.checkMode().strip()
        if response != '+CFUN: 1':
            print "Device not in online mode"
            self.sendCommand(op_mode + "=" + str(online))
            dummy = self.serialReadline(eol='\n')     #\r\n
            dummy = self.serialReadline(eol='\n')     #OK\r\n
            time.sleep(5)
            response = self.checkMode().strip()
            if response != '+CFUN: 1':
                print "Failed to get into online mode"
                exit(1)
        self.sendCommand(self.text_mode)
        #Read the \n\r\n
        dummy = self.serialReadline(eol='\n')
        #dummy = serialReadline(ser, eol='\n')
        #Read response
        response = self.serialReadline().strip()    #should be OK
        if response != "OK":
            print "Device can't get into text mode"
        self.sendCommand(self.send_sms+'"'+number+'"\r')
        dummy = self.port.read(3)     #\n\r\n>
        self.port.write(msg)
        self.port.write(self.ctrl_z)
        #Read the \r\n
        dummy = self.serialReadline(eol='\n')      #> \r
        dummy = self.serialReadline(eol='\n')      #\r
        dummy = self.serialReadline(eol='\n')      #\r
        #Read response
        response = self.serialReadline().strip()
        if len(response) < 8:
            print "response is of length " + str(len(response)) #TODO
            print response + ": Error sending"
        elif response[:5] != "+CMGS":
            print "response is not +CMGS"   #TODO
            print response + ": Error sending"
        else:
            print "Sent " + '"' +msg + '"' + " to " + str(number)
        #Read the \r\n
        dummy = self.serialReadline(eol='\n')      #Nothing due to strip
        #Read response
        response = self.serialReadline(eol='\n').strip()
        if response != "OK":
            print "Error sending"
        return

    def list_unread_messages(self):
        self.sendCommand(self.text_mode)
        #Read the \n\r\n
        dummy = self.serialReadline(eol='\n')
        #dummy = serialReadline(ser, eol='\n')
        #Read response
        response = self.serialReadline().strip()    #should be OK
        if response != "OK":
            print "Device can't get into text mode"

        self.sendCommand(list_sms+list_read)
        response = self.serialReadline().strip()    #should be OK
        if response != "OK":
            print "Device can't get into text mode"

    def readMessage(self):
        self.sendCommand(self.text_mode)
        #Read the \n\r\n
        dummy = self.serialReadline(eol='\n')
        #dummy = serialReadline(ser, eol='\n')
        #Read response
        response = self.serialReadline().strip()    #should be OK
        if response != "OK":
            print "Device can't get into text mode"



    def printPorts(self):
        for port in list_ports.comports():
            print port
        return