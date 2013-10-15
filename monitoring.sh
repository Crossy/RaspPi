#!/bin/bash
thesis=/home/ashley/thesis
cd $thesis
touch $thesis/info.log
touch $thesis/error.log
echo "Starting the  monitoring process"
sudo $thesis/monitoring.py >> $thesis/info.log 2>> $thesis/error.log
if [ $? != 0 ] ; then
    echo "Error occured while running monitoring.py"
    echo "Info Log"
    tail -n 20 info.log
    echo "Error Log"
    tail -n 20 error.log
else
    echo "Monitoring process completed successfully"
fi
echo "Starting shutdown process"
sudo $thesis/shutdown.py >> $thesis/info.log 2>> $thesis/error.log
if [ $? != 0 ] ; then
    echo "Error occurred while running shutdown process"
    echo "Info Log"
    tail -n 20 info.log
    echo "Error Log"
    tail -n 20 error.log
else
   echo "Shutdown process complted successfully"
fi
sudo $thesis/size.sh
if [ -e $thesis/debug ] ; then
   echo "RASPI will not shutdown because debug file present"
else
#   sudo i2cset -y 1 0x10 0x20
   sudo halt
fi
