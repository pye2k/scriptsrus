#!/usr/bin/python

#
# Automatically adjusts times in the crontab for turning on/off the IR lights
#
# Requires:
# - python-crontab package via pip
# - /etc/motion/ir_control script
# - Weather Underground API key (for sunrise/sunset times)
#

import httplib
import json
from crontab import CronTab
import sys

# grab the api key from config
from api_keys import WEATHER_UNDERGROUND_API_KEY
apiKey = WEATHER_UNDERGROUND_API_KEY

# call the service
wu = httplib.HTTPConnection('api.wunderground.com')
resource = '/'.join(['/api', apiKey, 'astronomy', 'q', 'WA', 'Seattle.json'])
wu.request('GET', resource)
res = wu.getresponse()

# bail if we didn't get a 200 response
if (res.status != 200):
  print 'Failed due to: ' + res.reason
  sys.exit(-1)

# proceed and read the data
data = res.read()
parsed_json = json.loads(data)

# get times when the sun rises and sets
sunrise_hr = parsed_json['sun_phase']['sunrise']['hour']
sunrise_min = parsed_json['sun_phase']['sunrise']['minute']

sunset_hr = parsed_json['sun_phase']['sunset']['hour']
sunset_min = parsed_json['sun_phase']['sunset']['minute']

# have all the info we need to write the crontab
#cron = CronTab(tabfile='output.tab') # from a file, for testing
cron = CronTab(tabfile='/etc/crontab', user=False)
# find the job by comment
comment = 'motion IR adjustment - AUTOMAGIC, DO NOT EDIT'
iter = cron.find_comment(comment)
for job in iter:
  print 'Found existing job:'
  print job
# remove all matches
cron.remove_all(comment=comment)
# create a new job to turn on IR
on_job = cron.new(command='/etc/motion/ir_control on > /dev/null 2>&1', comment=comment, user='root')
on_job.hour.on(sunset_hr)
on_job.minute.on(sunset_min)
print 'Set IR control to ON at: ' + sunset_hr + ':' + sunset_min

# create a new job to turn off IR
off_job = cron.new(command='/etc/motion/ir_control off > /dev/null 2>&1', comment=comment, user='root')
off_job.hour.on(sunrise_hr)
off_job.minute.on(sunrise_min)
print 'Set IR control to OFF at: ' + sunrise_hr + ':' + sunrise_min

# write the cron
#cron.write('output.tab') # to a file, for testing
cron.write('/etc/crontab')
