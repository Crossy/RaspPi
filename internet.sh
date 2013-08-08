#!/bin/sh
echo "Attempting to connect to the internet"
echo "This may take some time"
sudo ./sakis3g connect USBINTERFACE="3" APN="telstra.internet"
