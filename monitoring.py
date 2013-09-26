import datetime
import monitor_config
import Dropbox
import Xively
import I2C_link
import data_writer
import sys
from subprocess import call
import time
import datetime

def main():
    #Start the internet connection
    call(["./internet.sh"])
    
    #Sychronise time
    call(["ntpd", "-g"])
    if call(["ntp-wait"]) != 0:
        sys.stderr.write("Cannot sychronise time\n")
        
    #Update config file
    dbHelper = DropboxHelper(APP_KEY, APP_SECRET)
    dbHelper.get_file('config.ini','config.ini')

    #TODO: Add configuration stuff here
    config = Config()
    config.read_config_file()

    #Maybe add the ability to send log files via dropbox

    validData = False
    for i in range(10):
        #Get sensor readings
        us = I2CConnection()
        datapoint = us.get_distance();
        datapoint = datapoint/config.height * 100 #Convert to perentage

        #Validate sensor reading
        dw = DataWriter()
        prevData = dw.get_previous_datapoints(10)
        #TODO: Add validation logic
        validData = True
        break;
        time.sleep(30)      #Try again later

    #Write datapoint to file
    if validData:
        dw.write_datapoint(datapoint)
    else:
        sys.stderr.write("Data seems to be invalid\n")
        exit(1)

    #Send datapoint to Xively
    xively = XivelyHelper()
    if not xively.get_datastream("test"):
        xively.create_datastream("test","test")
    xively.put_datapoint(datapoint)

    #TODO: SMS stuff here
    if datapoint < config.low_water_level:
        sms.sendCommand("")
        #Read the \r\n
        dummy = sms.serialReadline(eol='\n')
        #Read response
        response = sms.serialReadline().strip()
        if response != "OK":
            print port + " is not ready to send message"
            del sms
            exit(2)
        now = datetime.datetime.now()
        #TODO add formating to now using strftime
        msg = "ALERT: Water level at {0}% in {1} tank @ {2}".format(datapoint, config.name,now)
        for no in config.white_list:
            sms.sendMessage(no, msg)
        

    #Send stopping and shutdown command
    us.send_stop()
    #Then call sudo halt here or in the script calling this?
    
    

    #Need to make function to check for new SMS's
    
    #Maybe add functionality to update files via dropbox remotely
    
    return

    

main()
