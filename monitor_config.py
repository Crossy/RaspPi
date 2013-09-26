import ConfigParser
import datetime
import sys

#dt.now().time() < datetime.time(hour=22)

class Config:
    name = ''
    tank_height = 0     #Centimetres
    low_water_level = 25    #Percent

    quiet_time_start = datetime.time(hour=22,minute=0)
    quiet_time_end = datetime.time(hour=6, minute=0)
    sample_period = 60   #Minutes

    master = '0488598262'
    white_list = []

    def __init__(self):
        pass

    def read_config_file(self,filename='Config.ini'):
        config = ConfigParser.SafeConfigParser(allow_no_value=True)
        try:
            with open(filename,'r') as fp:
                config.readfp(fp)
        except Exception as detail:
            sys.stderr.write(str(detail)+'\n')
            return False

        try:
            config.get('fd','fd')

            self.name = config.get('Tank','name')
            self.tank_height = config.get('Tank', 'height')
            self.low_water_level = config.get('Tank','lowWaterLevel')

            self.quiet_time_start = config.get('Options', 'quietTimeStart')
            self.quiet_time_end = config.get('Options', 'quietTimeEnd')
            self.sample_period = config.get('Options', 'samplePeriod')

            self.white_list = config.options('WhiteList')
            for no in self.white_list:
                if isinstance(no,tuple) and no[1] == 'master':
                    self.master = no[0]
                    break

        except ConfigParser.Error as detail:
            sys.stderr.write(str(detail)+'\n')
            pass
        return True

