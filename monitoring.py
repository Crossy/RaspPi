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
    internet_connection = False
    DEVNULL= open(os.devnull,'wb')

    print "------------------------------------------------------------------------"
    sys.stdout.flush()
    sys.stderr.write("------------------------------------------------------------------------\n")

    #Preemptively create debug file in case of major issue
    call(["touch", path+"debug"])

    flags = []

    i2c = I2C_link.I2CConnection()
    dw = data_writer.DataWriter()

    #Check if mobile broadband USB is connected
    if call(["ls /dev/tty* | grep USB"], shell=True,stderr=DEVNULL,stdout=DEVNULL) != 0:
        sys.stderr.write("ERROR: Modem is not connected. Exiting\n")
        return 3
    sms = SMS.SMS()

    #Start the internet connection
    if DEBUG:
        print "Starting Internet connection"
        sys.stdout.flush()
    call(["sudo",path+"/internet.sh"])

    if call(["ping", "-c", "4" ,"www.google.com.au"], stderr=DEVNULL, stdout=DEVNULL) == 0:
        internet_connection = True
    else:
        internet_connection = False
        sys.stderr.write("Ping failed. No internet connection\n")

    dbHelper = Dropbox.DropboxHelper()

    #Sychronise time
    if DEBUG:
        print "Attempting to update time"
        sys.stdout.flush()
    if internet_connection and call(["sudo sntp -s 0.au.pool.ntp.org"], shell=True) != 0:
       sys.stderr.write("Cannot sychronise time\n")

    now = datetime.datetime.now()
    if DEBUG:
        print now.ctime()
        sys.stdout.flush()
        sys.stderr.write(now.ctime()+'\n')

    #Update config file
    if DEBUG:
        print "Updating Dropbox"
        sys.stdout.flush()
    try:
        if internet_connection:
            dbHelper.get_file('config.ini',path+'/config.ini')
    except rest.ErrorResponse as details:
       sys.stderr.write("MONITORING: Error getting config file from Dropbox\n" + str(details) + '\n')
       pass
    except rest.RESTSocketError as details:
        sys.stderr.write("MONITORING: Error getting config file from Dropbox\n" + str(details) + '\n')
        pass

    #Parse config file
    if DEBUG:
        print "Reading config file"
    config = monitor_config.Config()
    config.read_config_file()
    i2c.update_off_period(config.off_time)

    prevData = dw.get_previous_datapoints(5)    #TODO: Add max
    if DEBUG:
        print "Getting and validating datapoint"

    for retries in range(10):
        #Get sensor readings
        datapoint = i2c.get_distance()
        print "Raw datapoint = " + str(datapoint)
        now = datetime.datetime.now()

        if datapoint < 0 and retries < 9:
            time.sleep(config.retry_time)      #Try again later
            continue
        elif datapoint  == -1:
            #No or invalid response
            sys.stderr.write("Problem with ultrasonic sensor\n")
            if call(["ls "+path+" | grep alarm &> /dev/null"],shell=True,stderr=DEVNULL,stdout=DEVNULL) != 0:
                call(["touch", path+"/alarm"])
                msg = "Problem with sensor for tank {0} @ {1}".format(config.name, now.strftime("%H:%M %d/%m/%Y"))
                sms.sendMessage(config.master,msg)
            return 1
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
                        msg = "Problem with sensor for tank {0} @ {1}".format(config.name, now.strftime("%H:%M %d/%m/%Y"))
                        sms.sendMessage(config.master,msg)
                    return 2
            #If ok to, set datapoint to be previous datapoint
            datapoint = prevData[-1][1]
            print "Setting datapoint to {0} from {1}".format(prevData[-1][1], prevData[-1][0].strftime("%H:%M %d/%m/%Y"))
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
    try:
        if internet_connection:
            dbHelper.put_file(filename, filename, True)
    except rest.ErrorResponse as details:
        sys.stderr.write("MONITORING: Error updating datafile in Dropbox\n" + str(details) + '\n')
        pass
    except rest.RESTSocketError as details:
        sys.stderr.write("MONITORING: Error updating datafile in Dropbox\n" + str(details) + '\n')
        pass

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
            return 3
        msg = "ALERT: Water level at {0}% in {1} tank @ {2}".format(datapoint, config.name,now.strftime("%H:%M %d/%m/%Y"))
        for no in config.white_list:
            sms.sendMessage(no, msg)


    #Send stopping and shutdown command
    return 0

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

"""#Don't think I need this
def validate_data(datapoint, prevData):
    derivative = []
    for i in range(1,len(prevData)):
        d = (prevData[i][1] - prevData[i-1][1])/((prevData[i][0] - prevData[i-1][0]).seconds/3600.0)
        derivative.append(d)"""


main()
