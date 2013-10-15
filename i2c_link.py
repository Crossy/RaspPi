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
            time.sleep(0.1)
            ret |= (self.bus.read_byte_data(self.addr, 0x40)&0x0F)<<8
            time.sleep(0.1)
            ret |= (self.bus.read_byte_data(self.addr, 0x50)&0x0F)<<4
            time.sleep(0.1)
            ret |= (self.bus.read_byte_data(self.addr, 0x60)&0x0F)
        except IOError as detail:
            sys.stderr.write("I2C GET_DISTANCE: "+str(detail)+'\n')
            return -2

        if ret > 65000:
            ret-=0x10000
            if ret == -1:
                sys.stderr.write("Ultrasonic Sensor: No or invalid response\n")
                return -1
            elif ret == -2:
                sys.stderr.write("Ultrasonic Sensor: No echo received\n")
                return -2
            else:
                sys.stderr.write("Ultrasonic Sensor: Unknown response received\n")
                return -1
        return ret

    def send_stop(self):
        sent = False
        retries = 0
        while not sent and retries < 10:
            try:
                self.bus.write_byte(self.addr, 0x20)
                sent = True
            except IOError as detail:
                sys.stderr.write("I2C SEND_STOP: "+str(detail)+'\n')
                sys.stderr.write("\tRetrying in 1 sec\n")
                sent = False
                retries = retries + 1
                time.sleep(1)
        if sent:
            print "Stop sent"
        else:
            sys.stderr.write("I2C SEND_STOP: Failed to send. Rebooting\n")
        return sent

    def update_off_period(self, mins):
        poweroffCycles = int(round((mins*60)/8.3885))
        if poweroffCycles < 0 or poweroffCycles > 65535:
            sys.stderr.write("Invalid minutes parameter. Must be uint16\n")
            return False
        sent = False
        for i in range(10):
            n = 0
            if sent:
                break
            for n in range(3):
                try:
                    self.bus.write_byte(self.addr, 0x70)    #USI_SET_OFF_PERIOD
                    time.sleep(0.2)
                    self.bus.write_byte(self.addr,poweroffCycles>>8)
                    time.sleep(0.2)
                    self.bus.write_byte(self.addr, 0x00FF&poweroffCycles)
                    time.sleep(0.2)
                except IOError as detail:
                    sys.stderr.write("I2C UPDATE_OFF_PERIOD: "+str(detail)+'\n')
                    return False
            if self.bus.read_byte_data(self.addr, 0x80) & 0x0F == 0x01:
                #Send success
                sent = True
                break
            else:
                #Send failure
                sys.stderr.write("I2C UPDATE_OFF_PERIOD: Failed to correctly send. Retrying ...\n")
        if sent:
            print "Updated off period to "+str(mins)+" mins"
            return True
        else:
            sys.stderr.write("I2C UPDATE_OFF_PERIOD: Failed to correctly send too many times\n")
            return False

    def debug_mode(self):
        sent = False
        retries = 0
        while not sent and retries < 10:
            try:
                self.bus.write_byte(self.addr, 0xA0)
                sent = True
            except IOError as detail:
                sys.stderr.write("I2C DEBUG_MODE "+str(detail)+'\n')
                sys.stderr.write("\tRetrying in 1 sec\n")
                sent = False
                retries = retries + 1
                time.sleep(1)
        if sent:
            print "ATtiny now in debug mode. Watchdog is disabled. Won't reenable until power reset"
        else:
            sys.stderr.write("I2C DEBUG_MODE: Failed to set debug mode.\n")
        return sent
