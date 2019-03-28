from uliweb.utils import date
from datetime import datetime
import croniter
import time

dt = datetime(2015, 12, 15)
d = date.to_timezone(dt, 'GMT+8')

cron = croniter.croniter('10 8 * * *', d)
t = cron.get_next()
print(time.localtime(t))
