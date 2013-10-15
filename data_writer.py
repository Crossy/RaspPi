import csv
import datetime
import time
import sys

class DataWriter:
    DEBUG = True
    def __init__(self):
        pass

    def write_datapoint(self, datapoint, flags):
        now = datetime.datetime.now()
        filename = now.strftime("%Y-%m")+'.csv'
        with open(filename,'ab') as f:
            writer = csv.writer(f,'excel')
            dateTime = now.strftime("%Y-%m-%d %H:%M")
            row = [dateTime,"{0:.2f}".format(datapoint)]
            row.extend(flags)
            writer.writerow(row)
            f.close()
            if self.DEBUG:
                print "Wrote "+ dateTime + ", " + str(datapoint)
            return filename

    def get_previous_datapoints(self, n):
        now = datetime.datetime.now()
        datapoints = []
        filename = now.strftime("%Y-%m")+'.csv'
        try:
            with open(filename,'rb') as fp:
                lines = fp.readlines()
                needPrevMonth = False
                start = len(lines) - n
                if start < 0:
                    start = 0
                    needPrevMonth = True
                datapoints.extend(lines[start:len(lines)])
                datapoints = [dp.strip() for dp in datapoints]
                if needPrevMonth:
                    firstDay = datetime.date(day=1, month=now.month, year=now.year)
                    prevMonth = firstDay-datetime.timedelta(days=1)
                    with open(prevMonth.strftime("%Y-%m")+'.csv','rb') as fp1:
                        prevLines = fp1.readlines()
                        prevStart = len(prevLines) + len(lines) - n
                        if prevStart < 0:
                            prevStart = 0
                        datapoints.extend(prevLines[prevStart:len(prevLines)])
                        datapoints = [dp.strip() for dp in datapoints]
        except IOError as details:
            sys.stderr.write(str(details)+'\n')
        datapoints = [dp.split(',') for dp in datapoints]
        #Convert timestamp to datetime instances
        for i in range(len(datapoints)):
            dtString = datapoints[i][0]
            dt = datetime.datetime.strptime(dtString, "%Y-%m-%d %H:%M")
            datapoints[i][0] = dt
            datapoints[i][1] = float(datapoints[i][1])
        return datapoints

"""def main():
    while True:
        print write_test()
        time.sleep(3)"""

#main()
