import csv
import datetime as dt
import time
import random

def write_test():
    n = dt.datetime.now()
    with open(n.strftime("%Y-%m")+'.csv','ab') as f:
        writer = csv.writer(f,'excel')
        date_time = n.strftime("%Y-%m-%d %H:%M")
        datapoint = random.random()
        writer.writerow([date_time,datapoint])
        f.close()
        return "Wrote "+ date_time + ", " + str(datapoint)

def read_test():
    t = dt.date.today()
    with open(t.strftime("%Y-%m")+'.csv','rb') as f:
        reader = csv.reader(f, 'excel')
        for row in reader:
            print row

def main():
    while True:
        print write_test()
        time.sleep(3)

main()
