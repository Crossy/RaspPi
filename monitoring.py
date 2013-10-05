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
import os.path
from dropbox import client, rest

DEBUG = True

def main():
    path = "/home/ashley/thesis"
    debug_enable = False
    DEVNULL= open(os.devnull,'wb')
    print "------------------------------------------------------------------------"
    sys.stdout.flush()
    sys.stderr.write("------------------------------------------------------------------------\n")

    #Preemptively create debug file in case of major issue
    call(["touch", path+"debug"])

    #Check if ethernet is plugged in for debug purposes
    if call([path+"/ethernet.sh"]) == 0:
        print "Raspi will not shutdown because ethernet is connected. Debug mode is enabled"
        debug_enable = True

    flags = []

    dbHelper = Dropbox.DropboxHelper()
    i2c = I2C_link.I2CConnection()
    dw = data_writer.DataWriter()

    #Check if mobile broadband USB is connected
    if call(["ls /dev/tty* | grep USB"], shell=True,stderr=DEVNULL,stdout=DEVNULL) != 0:
        sys.stderr.write("ERROR: Modem is not connected. Exiting\n")
        exit_program(3, debug_enable, i2c)
    sms = SMS.SMS()

    #Start the internet connection
    if DEBUG:
        print "Starting Internet connection"
    call(["sudo",path+"/internet.sh"])

    #Sychronise time
    if DEBUG:
        print "Attempting to update time"
    if call(["sudo sntp -s 0.au.pool.ntp.org"], shell=True) != 0:
       sys.stderr.write("Cannot sychronise time\n")

    #Update config file
    if DEBUG:
        print "Updating Dropbox"
    try:
        dbHelper.get_file('config.ini',path+'/config.ini')
    except rest.ErrorResponse as details:
       sys.stderr.write("Error getting config file from dropbox\n")
       pass

    #Config file
    if DEBUG:
        print "Reading config file"
    config = monitor_config.Config()
    config.read_config_file()
    i2c.update_off_period(config.off_time)

    #Send log files to Dropbox
    if DEBUG:
        print "Sending log files for previous runs to Dropbox"
    dbHelper.put_file(path+'/info.log', 'info.log', True)
    dbHelper.put_file(path+'/error.log', 'error.log', True)

    prevData = dw.get_previous_datapoints(5)    #TODO: Add max
    if DEBUG:
        print "Getting and validating datapoint"

    for retries in range(10):
        #Get sensor readings
        datapoint = i2c.get_distance()
        now = datetime.datetime.now()
        if datapoint < 0 and retries < 9:
            time.sleep(config.retry_time)      #TODO: Change this back to 20 for field operation #Try again later
            continue
        elif datapoint  == -1:
            #No response
            sys.stderr.write("Problem with ultrasonic sensor\n")
            if call(["ls "+path+" | grep alarm &> /dev/null"],shell=True,stderr=DEVNULL,stdout=DEVNULL) != 0:
                call(["touch", path+"/alarm"])
                msg = "Problem with sensor for tank {0} @ {1}".format(config.name, now.strftime("%X %x"))
                sms.sendMessage(config.master,msg)
            exit_program(1, debug_enable, i2c)
        elif datapoint == -2:
            #No echo recieved
            print "Exceeded max retries with ultrasonic sensor. Tank may be full, very empty or the sensor needs to be checked"
            #Check for previous extrapolated data
            extraps = 0
            for i in range(1,len(prevData)+1):
                dp = prevData[-i]
                if isinstance(dp,list) and len(dp) > 2 and 'extrapolated' in dp:
                    extraps = extraps + 1
                else:
                    extraps = 0
                if extraps > 3:
                    sys.stderr.write("Too many extrapolated datapoints in a row. Exiting without writing datapoint to file.\n")
                    if call(["ls "+path+" | grep alarm &> /dev/null"],shell=True,stderr=DEVNULL,stdout=DEVNULL) != 0:
                        call(["touch", path+"/alarm"])
                        msg = "Problem with sensor for tank {0} @ {1}".format(config.name, now.strftime("%X %x"))
                        sms.sendMessage(config.master,msg)
                    exit_program(2, debug_enable, i2c)
            #If ok to, set datapoint to be previous datapoint
            datapoint = prevData[-1][1]
            print "Setting datapoint to {0} from {1}".format(prevData[-1][1], prevData[-1][0].strftime("%X %x"))
            flags.append('extrapolated')
        elif datapoint >= 0:
            datapoint = 100 - ((float(datapoint)-config.sensorheightabovewater)/config.maxwaterheight * 100) #Convert to perentage
            call(["rm", path+"/alarm"], stderr=DEVNULL, stdout=DEVNULL)
        break;

    #Check if any alerts need to be sent
    prevData = dw.get_previous_datapoints(24)
    oneDay = datetime.timedelta(days=1)
    prevAlarms = 0
    for dp in prevData:
        if dp[0] > (now-oneDay) and len(dp) > 2 and 'alarm' in dp:  #TODO: fix this
            prevAlarms = prevAlarms + 1
    if datapoint < config.low_water_level:
        if DEBUG:
            print "Low water alarm"
        if now.time() < config.quiet_time_start and now.time() > config.quiet_time_end and prevAlarms < config.max_alarms_per_day:
            flags.append('alarm')
        else:
            print "Muted alarm due to max alarms in a day"
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
    if 'alarm' in flags:
        sms.sendCommand("")
        #Read the \r\n
        dummy = sms.serialReadline(eol='\n')
        #Read response
        response = sms.serialReadline().strip()
        if response != "OK":
            print "Not ready to send message"
            del sms
            exit_program(3,debug_enable, i2c)
        msg = "ALERT: Water level at {0}% in {1} tank @ {2}".format(datapoint, config.name,now.strftime("%X %x"))
        for no in config.white_list:
            sms.sendMessage(no, msg)


    #Send stopping and shutdown command
    exit_program(0,debug_enable, i2c)



    #Need to make function to check for new SMS's
    """
    Can call and immediately hang up. First check for new SMS's, then check number it came from.
    Then check first part of message and if it is "You missed a call from"
    then send most recent data.
    +CMTI: "ME", 0
    Need to delete message

    Do I need a mute SMS function? Yes I do in case it gets annoying
    So check for new message. Check if number is on the whitelist.
    if msg.lower().strip(' .?,!-:;()$%#"') == "mute":
        #Mute all msgs for the next 8 hours
    To show muting is enabled, create a file and check its last modification time
    using os.path.getmtime(<file>)
    Then add the "muted" to the flags
    """
    """
    TODO: Credit check. Another datastream? Also look at expiry date and send alert if close
    TODO: master alerts for errors
    """

    #Maybe add functionality to update files via dropbox remotely

    return 0

def exit_program(exitcode, debug_enable, i2c):
    DEVNULL = open(os.devnull,'wb')
    if debug_enable:
        call(["touch", "debug"])
    else:
        call(["sudo rm debug"],shell=True,stderr=DEVNULL,stdout=DEVNULL)
        if DEBUG:
            print "Sending stop via I2C. Power off in 30 secs"
        i2c.send_stop()
    exit(exitcode)
    return



"""#Don't think I need this
def validate_data(datapoint, prevData):
    derivative = []
    for i in range(1,len(prevData)):
        d = (prevData[i][1] - prevData[i-1][1])/((prevData[i][0] - prevData[i-1][0]).seconds/3600.0)
        derivative.append(d)"""


main()
