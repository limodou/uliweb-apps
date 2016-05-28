import os
from uliweb import functions
from sqlalchemy import select, func
from uliweb.orm import do_
import logging

log = logging.getLogger(__name__)

# def refresh_jobs():
#     import signal
#     from uliweb import settings
#
#     pid_file = settings.get_var('CRON/pid_file')
#     with open(pid_file) as f:
#         t = f.read()
#         if t:
#             pid = int(t)
#             try:
#                 os.kill(pid, signal.SIGUSR1)
#             except OSError as e:
#                 pass

def refresh_jobs():
    redis = functions.get_redis()
    redis.publish('cron_refresh', 'refresh')