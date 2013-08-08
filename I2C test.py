#!/usr/bin/python
import smbus

bus = smbus.SMBus(1)
slaveAddr = 0x10

def getDistance():
	return bus.read_word_data(slaveAddr, 0x30)

def sendStop():
	return bus.read_word_data(slaveAddr, 0x20)

def main():
	print "START..."
	print "dist: " + str(getDistance())
	#print sendStop()
	print "stop sent"

main()
