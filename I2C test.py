#!/usr/bin/env python
import smbus
import time
import os
import I2C_link

def main():
    i2c = I2C_link.I2CConnection()
    print "START..."
    print "dist: " + str(i2c.get_distance())
    i2c.update_off_period(6)
    #send_stop()
    #os.system("sudo halt")

main()
