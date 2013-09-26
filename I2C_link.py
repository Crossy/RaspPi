import smbus
import time
import os

"""Requires root priveleges to run"""
class I2CConnection:
    bus = smbus.SMBus(1)
    addr = 0x10
    def __init__():
        pass

    def get_distance():
        bus.write_byte(addr, 0x10)
        time.sleep(0.2)
        ret = (bus.read_byte_data(addr, 0x30)&0x0F)<<12
        ret |= (bus.read_byte_data(addr, 0x40)&0x0F)<<8
        ret |= (bus.read_byte_data(addr, 0x50)&0x0F)<<4
        ret |= (bus.read_byte_data(addr, 0x60)&0x0F)

        if ret > 65000:
            #print hex(ret)
            ret-=0x10000
            if ret == -1:
                return "No response"
            elif ret == -2:
                return "No echo received"
        return ret

    def send_stop():
        bus.write_byte(addr, 0x20)
        print "stop sent"
