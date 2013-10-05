import ConfigParser
import datetime
import sys

#dt.now().time() < datetime.time(hour=22)

class Config:
    name = ''
    maxwaterheight = 250      #Centimetres
    sensorheightabovewater = 280        #Centimetres
    low_water_level = 50    #Percent

    quiet_time_start = datetime.time(hour=22,minute=0)
    quiet_time_end = datetime.time(hour=6, minute=0)
    off_time = 60   #Minutes
    max_alarms_per_day = 5
    retry_time = 15      #Minutes

    master = '0488598262'
    white_list = []

    def __init__(self):
        pass

    def read_config_file(self,filename='config.ini'):
        config = ConfigParser.SafeConfigParser(allow_no_value=True)
        try:
            with open(filename,'r') as fp:
                config.readfp(fp)
        except Exception as detail:
            sys.stderr.write(str(detail)+'\n')
            return False

        try:    #TODO: Check for negative values
            self.name = config.get('Tank','name')
            self.maxwaterheight = int(config.get('Tank', 'maxWaterHeight'))
            if self.maxwaterheight < 0:
                self.maxwaterheight = 30
            self.sensorheightabovewater = int(config.get('Tank', 'sensorHeight'))-self.maxwaterheight
            if self.sensorheightabovewater < 0:
                self.sensorheightabovewater = 30
            self.low_water_level = int(config.get('Tank','lowWaterLevel'))
            if self.low_water_level < 0:
                self.low_water_level = 5

            temp = config.get('Options', 'quietTimeStart')
            self.quiet_time_start = datetime.time(hour=int(temp[0:2]), minute=int(temp[2:4]))
            temp = config.get('Options', 'quietTimeEnd')
            self.quiet_time_end = datetime.time(hour=int(temp[0:2]), minute=int(temp[2:4]))
            if self.quiet_time_start < self.quiet_time_end:
                self.quiet_time_start = datetime.time(hour=22,minute=0)
            quiet_time_end = datetime.time(hour=6, minute=0)
            self.off_time = int(config.get('Options', 'offTime'))
            if self.off_time < 0:
                self.sample_period = 0
            self.max_alarms_per_day = int(config.get('Options', 'maxAlarmsPerDay'))
            if self.max_alarms_per_day < 0:
                self.max_alarms_per_day = 0
            self.retry_time = int(config.get('Options', 'retryTime'))
            if self.retry_time < 0:
                self.retry_time = 10

            self.white_list = config.options('WhiteList')
            if len(self.white_list) == 0:
                self.white_list.append(["0488598262", "master"])
            for no in self.white_list:
                if isinstance(no,tuple) and no[1] == 'master':
                    self.master = no[0]
                    break

        except ConfigParser.Error as detail:
            sys.stderr.write(str(detail)+'\n')
            pass
        except ValueError as detail:
            sys.stderr.write(str(detail)+'\n')
            pass
        return True

