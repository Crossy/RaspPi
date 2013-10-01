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
    flags = []
    dbHelper = Dropbox.DropboxHelper()
    dw = data_writer.DataWriter()
    sms = SMS.SMS()

    print "------------------------------------------------------------------------"
    sys.stderr.write("------------------------------------------------------------------------\n")

    #Start the internet connection
    if DEBUG:
        print "Starting Internet connection"
    call(["sudo","./internet.sh"])

    #Sychronise time
    #TODO: Fix this
    if DEBUG:
        print "Attempting to update time"
    #call(["sudo","service", "ntp", "restart"])
    call(["sudo", "ntpd", "-g"])
    if call(["ntp-wait", "-v"]) != 0:
       sys.stderr.write("Cannot sychronise time\n")

    #Update config file
    if DEBUG:
        print "Updating Dropbox"
    dbHelper.get_file('config.ini','config.ini')

    #TODO: Add configuration stuff here
    if DEBUG:
        print "Reading config file"
    config = monitor_config.Config()
    config.read_config_file()

    #Maybe add the ability to send log files via dropbox
    if DEBUG:
        print "Sending log files for previous runs to Dropbox"
    dbHelper.put_file('info.log', 'info.log', True)
    dbHelper.put_file('error.log', 'error_log', True)

    prevData = dw.get_previous_datapoints(5)    #TODO: Add max
    if DEBUG:
        print "Getting and validating datapoint"
    retries = 0
    for i in range(10):
        #Get sensor readings
        us = I2C_link.I2CConnection()
        datapoint = us.get_distance()
        now = datetime.datetime.now()
        if datapoint < 0 and retries < 9:
            retries = retries + 1
            time.sleep(5)      #TODO: Change this back to 20 for field operation #Try again later
            continue
        elif datapoint  == -1:
            #No response
            sys.stderr.write("Problem with ultrasonic sensor\n")
            msg = "Problem with sensor for tank {0} @ {1}".format(config.name, now.strftime("%X %x"))
            sms.sendMessage(config.master,msg)
            exit(1)
        elif datapoint == -2:
            #No echo recieved
            print "Exceeded max retries with ultrasonic sensor. Tank may be full, very empty or the sensor needs to be checked"
            #Check for previous extrapolated data
            extraps = 0
            for dp in range(len(prevData), -1, 0):
                if len(dp) > 2 and 'extrapolated' in dp:
                    extraps = extraps + 1
                else:
                    extraps = 0
                if extraps > 2:
                    #TODO: Error. Do I exit here or just write -1 as the data? Probably exit. Sending useless data is not very helpful
                    break
            #If ok to, set datapoint to be previous datapoint
            datapoint = prevData[-1]
            flags.append('extrapolated')

        if datapoint >= 0:
            datapoint = 100 - ((float(datapoint)-config.sensorheightabovewater)/config.maxwaterheight * 100) #Convert to perentage

        break;

    #Check if any alerts need to be sent
    prevData = dw.get_previous_datapoints(24)
    oneDay = datetime.timedelta(days=1)
    prevAlarms = 0
    for dp in prevData:
        if dp[0].time() > now.time()-oneDay and len(dp) > 2 and 'alarm' in dp:  #TODO: fix this
            prevAlarm = prevAlarms + 1
    if datapoint < config.low_water_level:
        if DEBUG:
            print "Low water alarm"
        if now().time() < config.quiet_time_start.time() and now().time() > config.quiet_time_end.time() and prevAlarms < config.max_alarms_per_day:
            flags.append('alarm')
        else:
            flags.append('muted')

    #Write datapoint to file
    if DEBUG:
        print "Writing data to file"
    filename = dw.write_datapoint(datapoint, flags)

    #Write datafile to dropbox
    if DEBUG:
        print "Updating datafile in Dropbox"
    dbHelper.put_file(filename, filename, True)

    #Send datapoint to Xively
    if DEBUG:
        print "Sending data to Xively"
    if datapoint > -1:
        xively = Xively.XivelyHelper()
        if not xively.get_datastream("test"):
            xively.create_datastream("test","test")
        xively.put_datapoint(datapoint)

    #TODO: SMS stuff here
    if DEBUG:
        print "Up to SMS stuff"
    if 'alarm' in flags:
        sms.sendCommand("")
        #Read the \r\n
        dummy = sms.serialReadline(eol='\n')
        #Read response
        response = sms.serialReadline().strip()
        if response != "OK":
            print "Not ready to send message"
            del sms
            exit(2)
        msg = "ALERT: Water level at {0}% in {1} tank @ {2}".format(datapoint, config.name,now.strftime("%X %x"))
        for no in config.white_list:
            sms.sendMessage(no, msg)


    #Send stopping and shutdown command
    if DEBUG:
        print "Sending stop"
    #us.send_stop()
    #TODO: Add sudo halt to script



    #Need to make function to check for new SMS's

    #Maybe add functionality to update files via dropbox remotely

    return 0

#Don't think I need this
def validate_data(datapoint, prevData):
    derivative = []
    for i in range(1,len(prevData)):
        d = (prevData[i][1] - prevData[i-1][1])/((prevData[i][0] - prevData[i-1][0]).seconds/3600.0)
        derivative.append(d)


main()
