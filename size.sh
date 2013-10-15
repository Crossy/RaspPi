#!/bin/sh
info=info.log
error=error.log
maxsize=1000000
actualsize=$(stat -c '%s' $info)
if [ $actualsize -ge $maxsize ] ; then
    echo "info.log is over 1MB, truncating"
    tail -n 1000 $info > temp
    mv temp $info
fi
actualsize=$(stat -c '%s' $error)
if [ $actualsize -ge $maxsize ] ; then
    echo "error.log is over 1MB, truncating"
    tail -n 1000 $error > temp
    mv temp $error
fi
