import smbus
import time
import os
import sys

"""Requires root priveleges to run"""
class I2CConnection:
    bus = smbus.SMBus(1)
    addr = 0x10
    def __init__(self):
        pass

    #TODO: IOError Exception handling
    def get_distance(self):
        try:
            self.bus.write_byte(self.addr, 0x10)
            time.sleep(0.2)
            ret = (self.bus.read_byte_data(self.addr, 0x30)&0x0F)<<12
            ret |= (self.bus.read_byte_data(self.addr, 0x40)&0x0F)<<8
            ret |= (self.bus.read_byte_data(self.addr, 0x50)&0x0F)<<4
            ret |= (self.bus.read_byte_data(self.addr, 0x60)&0x0F)
        except IOError as detail:
            sys.stderr.write("I2C: ",str(detail))
            return -2

        if ret > 65000:
            #print hex(ret)
            ret-=0x10000
            if ret == -1:
                sys.stderr.write("Ultrasonic Sensor: No response\n")
                return -1
            elif ret == -2:
                sys.stderr.write("No echo received\n")
                return -2
        return ret

    def send_stop(self):
        try:
            self.bus.write_byte(self.addr, 0x20)
        except IOError as detail:
            sys.stderr.write("I2C: ",str(detail))
            return
        print "Stop sent"
        return

    def update_off_period(self, mins):
        poweroffCycles = int(round((mins*60)/8.3885))
        if poweroffCycles < 0 or poweroffCycles > 65535:
            sys.stderr.write("Invalid minutes parameter. Must be uint16\n")
            return False
        try:
            self.bus.write_byte(self.addr, 0x70)    #USI_SET_OFF_PERIOD
            time.sleep(0.2)
            self.bus.write_byte(self.addr,poweroffCycles>>8)
            time.sleep(0.2)
            self.bus.write_byte(self.addr, 0x00FF&poweroffCycles)
        except IOError as detail:
            sys.stderr.write("I2C: ",str(detail))
            return False
        return True
