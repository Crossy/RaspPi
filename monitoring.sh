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
if [ -e $thesis/debug ] ; then
   echo "RASPI will not shutdown because debug file present"
else
   sudo halt
fi
