import ConfigParser
import datetime
import sys

#dt.now().time() < datetime.time(hour=22)

class Config:
    name = ''
    maxwaterheight = 1      #Centimetres
    sensorheightabovewater = 1        #Centimetres
    low_water_level = 25    #Percent

    quiet_time_start = datetime.time(hour=22,minute=0)
    quiet_time_end = datetime.time(hour=6, minute=0)
    sample_period = 60   #Minutes
    max_alarms_per_day = 5

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

        try:
            self.name = config.get('Tank','name')
            self.maxwaterheight = int(config.get('Tank', 'maxWaterHeight'))
            self.sensorheightabovewater = int(config.get('Tank', 'sensorHeight'))-self.maxwaterheight
            self.low_water_level = int(config.get('Tank','lowWaterLevel'))

            #TODO: Convert these to times
            temp = config.get('Options', 'quietTimeStart')
            self.quiet_time_start = datetime.time(hour=int(temp[0:2]), minute=int(temp[2:4]))
            temp = config.get('Options', 'quietTimeEnd')
            self.quiet_time_end = datetime.time(hour=int(temp[0:2]), minute=int(temp[2:4]))
            self.sample_period = int(config.get('Options', 'samplePeriod'))
            self.max_alarms_per_day = int(config.get('Options', 'maxAlarmsPerDay'))

            self.white_list = config.options('WhiteList')
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

