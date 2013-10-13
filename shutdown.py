#!/usr/bin/env python
import Dropbox
import I2C_link
from subprocess import call
import os.path
from dropbox import client, rest
import sys

DEBUG = True

def main():
    path = "/home/ashley/thesis"
    debug_enable = False
    i2c = I2C_link.I2CConnection()
    dbHelper = Dropbox.DropboxHelper()

    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    sys.stdout.flush()
    sys.stderr.write("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")

    #Check if ethernet is plugged in for debug purposes
    if call([path+"/ethernet.sh"]) == 0:
        print "Raspi will not shutdown because ethernet is connected. Debug mode is enabled"
        debug_enable = True

    #Send log files to Dropbox
    if DEBUG:
        print "Sending log files for previous runs to Dropbox"
    try:
        dbHelper.put_file(path+'/info.log', 'info.log', True)
        dbHelper.put_file(path+'/error.log', 'error.log', True)
    except rest.ErrorResponse as details:
        sys.stderr.write("SHUTDOWN: Error putting logfiles into dropbox\n" + str(details)+ '\n')
        pass
    except rest.RESTSocketError as details:
        sys.stderr.write("SHUTDOWN: Error putting logfiles into Dropbox\n" + str(details) + '\n')

    DEVNULL = open(os.devnull,'wb')
    if debug_enable:
        call(["touch", "debug"])
    else:
        call(["sudo rm debug"],shell=True,stderr=DEVNULL,stdout=DEVNULL)
        if DEBUG:
            print "Sending stop via I2C. Power off in 30 secs"
            sys.stdout.flush()
        i2c.send_stop()

    print "#########################################################################"
    sys.stdout.flush()
    sys.stderr.write("#########################################################################\n")

    return

main()
