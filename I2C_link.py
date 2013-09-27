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

    def get_distance(self):
        self.bus.write_byte(self.addr, 0x10)
        time.sleep(0.2)
        ret = (self.bus.read_byte_data(self.addr, 0x30)&0x0F)<<12
        ret |= (self.bus.read_byte_data(self.addr, 0x40)&0x0F)<<8
        ret |= (self.bus.read_byte_data(self.addr, 0x50)&0x0F)<<4
        ret |= (self.bus.read_byte_data(self.addr, 0x60)&0x0F)

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
        self.bus.write_byte(self.addr, 0x20)
        print "stop sent"
        return
