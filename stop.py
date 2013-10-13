#!/usr/bin/env python
import I2C_link

def main():
    i2c = I2C_link.I2CConnection()
    i2c.send_stop()
    return

main()
