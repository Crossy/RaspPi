import serial
import sys
import time
from serial.tools import list_ports

#debug
debug = True

#Useful commands
text_mode = "+CMGF=1"       #Set to text mode for sms communication
pdu_mode = "+CMGF=0"
send_sms = "+CMGS="
list_all_received_sms = '+CMGL='
list_all = '"ALL"'
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

#params for message
port = "/dev/ttyUSB2"
number = "0488598262"
#msg = "This is sent from my Raspberry Pi."
#msg = "Look I got it working"
msg = "ALERT: TANK 1 was 20% full at 12:00PM on 13/05/2013"

"""ser = serial.Serial('COM11', 115200, timeout = 5)
print ser.portstr
#check if sim responds
ser.write("at\r")
#Set to text mode
ser.write("at+cmgf=1\r")
#set phone number
ser.write('at+cmgs="+61488598262"\r')
#set message
ser.write("This is sent from the computer\r")
#send ctrl-Z to send
ser.write(chr(26))
ser.close()"""

def _debug_(response):
    if debug:
        sys.stdout.write(response)
        
def ser_readline(ser, eol='\n'):
    line = ""
    while 1:
        char = ser.read()
        line += char
        if (char == eol or char == ''):
            break
    _debug_(line)
    line = line.strip()
    return line

def openPort(port, to):
    ser = None
    try:
        ser = serial.Serial(port, 115200, timeout = to)
    except ValueError:
        print "Port parameters are out of range"
        exit(1)
    except serial.SerialException :
        print port+" cannot be found or cannot be configured"
        exit(1)
    return ser

def checkMode(ser):
    sendCommand(ser, op_mode+'?')
    dummy = ser_readline(ser)       #\r\n
    response = ser_readline(ser).strip()       #mode
    dummy = ser_readline(ser)       #\r\n
    dummy = ser_readline(ser)       #OK
    return response

def sendCommand(ser, cmd):
    if ser is None:
        print "Serial port is not open. Please call openPort first"
    #Check if port open
    if not ser.isOpen():
        print "Serial port is not open. Please call openPort first"
    ser.write("AT" + cmd + "\r")
    #_debug_("AT" + cmd)
    return

def sendMessage(ser, number, msg):
    response = checkMode(ser).strip()
    if response != '+CFUN: 1':
        print "Device not in online mode"
        sendCommand(ser, op_mode + "=" + str(online))
        dummy = ser_readline(ser, eol='\n')     #\r\n
        dummy = ser_readline(ser, eol='\n')     #OK\r\n
        time.sleep(5)
        response = checkMode(ser).strip()
        if response != '+CFUN: 1':
            print "Failed to get into online mode"
            exit(1)
    sendCommand(ser, text_mode)
    #Read the \n\r\n
    dummy = ser_readline(ser, eol='\n')
    #dummy = ser_readline(ser, eol='\n')
    #Read response
    response = ser_readline(ser).strip()    #should be OK
    if response != "OK":
        print "Device can't get into text mode"
    sendCommand(ser, send_sms+'"'+number+'"\r')
    dummy = ser.read(3)     #\n\r\n>
    ser.write(msg)
    ser.write(ctrl_z)
    #Read the \r\n
    dummy = ser_readline(ser, eol='\n')      #> \r
    dummy = ser_readline(ser, eol='\n')      #\r
    dummy = ser_readline(ser, eol='\n')      #\r
    #Read response
    response = ser_readline(ser).strip()     
    if len(response) < 8:
	print "response is of length " + str(len(response))	#TODO
        print response + ": Error sending" 
    elif response[:5] != "+CMGS":
	print "response is not +CMGS"	#TODO
        print response + ": Error sending"
    else:
        print "Sent " + '"' +msg + '"' + " to " + str(number)
    #Read the \r\n
    dummy = ser_readline(ser, eol='\n')      #Nothing due to strip
    #Read response
    response = ser_readline(ser, eol='\n').strip()
    if response != "OK":
        print "Error sending"
    return

def printPorts():
    for port in list_ports.comports():
        print port
    return

def main():
    printPorts()
    ser = openPort(port, 5)
    #Check if dongle is ready to communicate
    sendCommand(ser, "")
    #Read the \r\n
    dummy = ser_readline(ser, eol='\n')
    #Read response
    response = ser_readline(ser).strip()
    if response != "OK":
        print port + " is not ready to send message"
        ser.close()
        exit(1)
    sendMessage(ser, number, msg)
    ser.close()
    return
    
main()  
    