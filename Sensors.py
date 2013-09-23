#!/usr/bin/python
import smbus
import time
import os

bus = smbus.SMBus(1)
addr = 0x10

def getDistance():
	#bus.write_byte(addr, 0x30)
	#time.sleep(0.2)
	#ret = 0x0000
	#ret = bus.read_byte(addr)
	#ret = ret<<8
	#ret|= bus.read_byte(addr)
	bus.write_byte(addr, 0x10)
	time.sleep(0.2)
	ret = (bus.read_byte_data(addr, 0x30)&0x0F)<<12
	ret |= (bus.read_byte_data(addr, 0x40)&0x0F)<<8
	ret |= (bus.read_byte_data(addr, 0x50)&0x0F)<<4
	ret |= (bus.read_byte_data(addr, 0x60)&0x0F)
	#ret = read_i2c_block_data(addr, 0x30)

	if ret > 65000:
		#print hex(ret)
		ret-=0x10000
		if ret == -1:
			return "No response"
		elif ret == -2:
			return "No echo received"
	return ret

def sendStop():
	bus.write_byte(addr, 0x20)
	#time.sleep(0.2)
	#ret = 0x0000
	#ret = bus.read_byte(addr)
	#ret = ret<<8
	#ret|= bus.read_byte(addr)
	print "stop sent"
	#return ret
