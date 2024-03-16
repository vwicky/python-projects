import pytz

# window settings
WINDOW_SIZE = '950x900'
WINDOW_TITLE = 'document similarity'

# time zones
tz_NY = pytz.timezone('America/New_York') 
tz_London = pytz.timezone('Europe/London')
TIMEZONE = pytz.timezone('Europe/Kyiv')

DAY_THRESHOLD, NIGHT_THRESHOLD = (8, 20)