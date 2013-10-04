#!/bin/bash
grep -Fxq "1" /sys/class/net/eth0/carrier
if [ $? == 0 ] ; then
    echo "Ethernet connected"
    exit 0
else
    echo "Ethernet not connected"
    exit 1
fi
