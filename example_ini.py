import ConfigParser

def write_example():
    cfg = open('example.ini', 'w')

    config = ConfigParser.SafeConfigParser(allow_no_value=True)

    config.add_section('Tank')
    config.add_section('Options')
    config.add_section('WhiteList')

    config.set('Tank', 'Name', 'Test')
    config.set('Tank', 'Height','250')
    config.set('Tank', 'LowWaterLevel', '25')

    config.set('Options', 'QuietTimeStart', '2200')
    config.set('Options', 'QuietTimeEnd', '0600')
    config.set('Options', 'SamplePeriod', '60')
    #Low credit alarm?

    config.set('WhiteList', '0488598262', 'master')
    config.set('WhiteList', '0409275375')

    config.write(cfg)
    cfg.close()

def read_example():
    config = ConfigParser.SafeConfigParser(allow_no_value=True)
    config.read('example.ini')

    sections = config.sections()
    for section in sections:
        print config.items(section)
            
    print config.get('WhiteList','0488598262') == 'master'
