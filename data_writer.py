import csv
import datetime as dt
import time
import sys

class DataWriter:
    DEBUG = True
    def __init__(self):
        pass

    def write_datapoint(self, datapoint):
        now = dt.datetime.now()
        with open(now.strftime("%Y-%m")+'.csv','ab') as f:
            writer = csv.writer(f,'excel')
            dateTime = now.strftime("%Y-%m-%d %H:%M")
            writer.writerow([dateTime,datapoint])
            f.close()
            if DEBUG:
                print "Wrote "+ dateTime + ", " + str(datapoint)
            return

    def get_previous_datapoints(self, n):
        if int(
        now = dt.datetime.now()
        datapoints = []
        try:
            with open(now.strftime("%Y-%m")+'.csv','rb') as fp:
                lines = fp.readlines()
                needPrevMonth = False
                start = len(lines) - n
                if start < 0:
                    start = 0
                    needPrevMonth = True
                datapoints.extend(lines[start:len(lines)])
                datapoints = [dp.strip() for dp in datapoints]
                if needPrevMonth:
                    firstDay = dt.date(day=1, month=now.month, year=now.year)
                    prevMonth = firstDay-dt.timedelta(days=1)
                    with open(prevMonth.strftime("%Y-%m")+'.csv','rb') as fp1:
                        prevLines = fp1.readlines()
                        prevStart = len(prevLines) + len(lines) - n
                        if prevStart < 0:
                            prevStart = 0
                        datapoints.extend(prevLines[prevStart:len(prevLines)])
                        datapoints = [dp.strip() for dp in datapoints]
        except IOError as details:
            sys.stderr.write(str(details)+'\n')
        return datapoints

def main():
    while True:
        print write_test()
        time.sleep(3)

#main()
