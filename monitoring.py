#!/usr/bin/env python
import datetime
import monitor_config
import Dropbox
import Xively
import I2C_link
import data_writer
import SMS
import sys
from subprocess import call
import time
import datetime

DEBUG = True

def main():
    #Start the internet connection
    if DEBUG:
        print "Starting Internet connection"
    call(["sudo","./internet.sh"])
    
    #Sychronise time
    if DEBUG:
        print "Attempting to update time"
    call(["sudo","ntpd", "-g"])
    if call(["ntp-wait"]) != 0:
        sys.stderr.write("Cannot sychronise time\n")
        
    #Update config file
    if DEBUG:
        print "Updating Dropbox"
    dbHelper = Dropbox.DropboxHelper()
    dbHelper.get_file('config.ini','config.ini')

    #TODO: Add configuration stuff here
    if DEBUG:
        print "Reading config file"
    config = monitor_config.Config()
    config.read_config_file()

    #Maybe add the ability to send log files via dropbox

    if DEBUG:
        print "Getting and validating datapoint"
    validData = False
    dw = data_writer.DataWriter()
    for i in range(10):
        #Get sensor readings
        us = I2C_link.I2CConnection()
        datapoint = us.get_distance()
        if datapoint < 0:
            time.sleep(30)      #Try again later
            continue
        #datapoint = 100     #TODO: Fix this when sensor is connected
        datapoint = 100 - (float(datapoint)/config.tank_height * 100) #Convert to perentage

        #Validate sensor reading
        prevData = dw.get_previous_datapoints(10)
        #TODO: Add validation logic
        validData = True
        break; 

    #Write datapoint to file
    if DEBUG:
        print "Writing data to file"
    if validData:
        filename = dw.write_datapoint(datapoint)
    else:
        sys.stderr.write("Data seems to be invalid\n")
        exit(1)
        
    #Write datafile to dropbox
    if DEBUG:
        print "Updating datafile in Dropbox"
    dbHelper.put_file(filename, filename, True)

    #Send datapoint to Xively
    if DEBUG:
        print "Sending data to Xively"       
    xively = Xively.XivelyHelper()
    if not xively.get_datastream("test"):
        xively.create_datastream("test","test")
    xively.put_datapoint(datapoint)

    #Disconnect internet so I can send SMS
    """if DEBUG:
        print "Disconnecting internet"
    call(["sudo", "./sakis3g", "disconnect"])
    time.sleep(20)"""
    
    #TODO: SMS stuff here
    if DEBUG:
        print "Up to SMS stuff"
    sms = SMS.SMS()
    if datapoint < config.low_water_level:
        if DEBUG:
            print "Low water alarm"
        sms.sendCommand("")
        #Read the \r\n
        dummy = sms.serialReadline(eol='\n')
        #Read response
        response = sms.serialReadline().strip()
        if response != "OK":
            print "Not ready to send message"
            del sms
            exit(2)
        now = datetime.datetime.now()
        #TODO add formating to now using strftime
        msg = "ALERT: Water level at {0}% in {1} tank @ {2}".format(datapoint, config.name,now.strftime("%X %x"))
        for no in config.white_list:
            sms.sendMessage(no, msg)
        

    #Send stopping and shutdown command
    if DEBUG:
        print "Sending stop"
    #us.send_stop()
    #Then call sudo halt here or in the script calling this?
    
    

    #Need to make function to check for new SMS's
    
    #Maybe add functionality to update files via dropbox remotely
    
    return

    

main()
