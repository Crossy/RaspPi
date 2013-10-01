#!/bin/sh
cd thesis
echo "Starting the  monitoring process"
sudo ./monitoring.py >> info.log 2>> error.log
if [ $? != 0 ] ; then
    echo "Error occured while running monitoring.py"
    echo "Info Log"
    tail -n 20 info.log
    echo "Error Log"
    tail -n 20 error.log
else
    echo "Monitoring process completed successfully"
fi
