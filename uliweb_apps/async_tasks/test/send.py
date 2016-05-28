#coding=utf8
import os
from uliweb.manage import make_simple_application
from uliweb import functions

os.chdir('../../..')
app = make_simple_application(project_dir='.')

from async_tasks import AsyncCommand

c = AsyncCommand('async_tasks.tasks.echo', {'message':'hello'}, queue=['async_workers_localhost'])
functions.call_async(c)