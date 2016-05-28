#coding=utf8
#cron schedule daemon
#Author: limodou
# Usage: uliweb call cron.daemon --gevent

from __future__ import print_function, absolute_import

from gevent import spawn

import os
import sys
import re
from uliweb import functions
from uliweb.orm import Begin, Commit, Rollback
import logging
from uliweb.utils import date
from uliweb.utils.sorteddict import SortedDict
import datetime
import time
import signal
import bisect

log = logging.getLogger(__name__)
is_exit = False

jobs = SortedDict()
jobs_time = []

def handler(signum, frame):
     global is_exit
     is_exit = True
     print ("Process %d received a signal %d" % (os.getpid(), signum))
     sys.exit(0)

def get_jobs():
    global jobs
    jobs = SortedDict()
    Job = functions.get_model('cron_job')

    for row in Job.filter(Job.c.enabled==True):
        jobs[row.id] = row

def get_exe_time(job):
    import croniter
    from uliweb import settings

    now = date.now(settings.CRON.TIMEZONE)

    cron = croniter.croniter(job.time, now)
    return cron.get_next()

def init():
    from uliweb.orm import Reset

    Reset()
    get_jobs()
    get_times()

def get_times():
    global jobs, jobs_time
    jobs_time = []
    for j in jobs.values():
        t = get_exe_time(j)
        bisect.insort(jobs_time, (t, j.id))

r_function = re.compile(r'(.*?)\((.*?)\)')

def parse_command(row):
    """
    解析命令格式,支持函数式 a.b() 和 普通的shell命令行
    :param row:
    :return:
    """
    from uliweb.utils import date

    def f(*args, **kwargs):
        return args, kwargs

    d = {
        'status':'0',
        'message':'',
        'command':row.command,
        'parameters':{},
    }
    b = r_function.match(row.command)
    if b:
        env = {'TODAY':date.today(), 'NOW':date.now(), 'f':f}
        d['command'] = b.group(1)
        para = b.group(2)
        para = os.path.expandvars(para)
        try:
            d['parameters'] = {}
            v = eval('f({})'.format(para), env)
            d['parameters']['_args'] = v[0]
            d['parameters'].update(v[1])
        except Exception as e:
            log.exception(e)
            d['status'] = 'F'
            d['message'] = 'Eval parameter {} error'.format(b.group(2))
    else:
        d['command'] = 'shell'
        d['parameters'] = {'cmd':row.command, 'cwd':row.work_directory}
    return d

def start_job(job, now=None):
    from uliweb.utils import date

    now =  now or date.now()

    log.info(u'Starting job [{title} -- {time}] at {now}'.format(title=job.title, now=now,
                                                           time=job.time))
    Task = functions.get_model('cron_task')

    Begin()
    try:
        parent = functions.AsyncCommand('', title=job.title, startup_time=now,
                                       category='cron', message_source='l',
                                       timeout=job.timeout,
                                       #todo add correlation to job
                                       )
        commands = []
        ids = {}

        #process task
        for row in Task.filter(Task.c.cron_job==job.id):
            #process async task
            d = parse_command(row)

            c = functions.AsyncCommand(
                                title=row.label,
                                category='cron',
                                message_source='l',
                                correlation=job.id,
                                queue=(row.queue or 'default').split(','),
                                timeout=row.timeout or None,
                                # correlation_link='/async_task/view/{0}?next=/cron/{1}'.format(job.id, obj.id)
                                **d
                                )

            commands.append((c, row.depend_tasks))
            ids[row.id] = c.task_id


            parent.add_child(c)

        #fix depends
        for c, depends in commands:
            _d = [ids[x] for x in depends]
            c.depend_tasks = _d


        functions.call_async(parent)
        job.instances.add(parent.task_id)
        Commit()
    except Exception as e:
        Rollback()
        log.exception(e)
        raise

def start_task(task_id, now=None):
    from uliweb.utils import date

    now =  now or date.now()

    try:
        task = functions.get_object('cron_task', task_id)
        log.info(u'Starting task [{title}] at {now}'.format(title=task.label, now=now))

        d = parse_command(task)

        c = functions.AsyncCommand(
                            title=task.label,
                            category='cron',
                            message_source='l',
                            correlation=task.id,
                            queue=(task.queue or 'default').split(','),
                            timeout=task.timeout or None,
                            # correlation_link='/async_task/view/{0}?next=/cron/{1}'.format(job.id, obj.id)
                            **d
                            )


        functions.call_async(c)
        return c
    except Exception as e:
        log.exception(e)
        raise

class BreakoutException(Exception):
    pass

class Breakout():
    """Breakout class using ALARM signal and redis pubsub."""

    def __init__(self, topic, dalay=3):
        self.delay = dalay
        redis = functions.get_redis()
        self.pub = redis.pubsub()
        self.pub.subscribe(topic)

        while 1:
            time.sleep(0.05)
            message = self.pub.get_message()
            if not message:
                break

        signal.signal(signal.SIGALRM, self.raise_exception)
        spawn(self.listen)

    def __enter__(self):
        pass

    def listen(self):
        for message in self.pub.listen():
            log.info('Received refresh command...')
            signal.alarm(self.delay)

    def __exit__(self, *args):
        pass

    def raise_exception(self, *args):
        raise BreakoutException()

def continue_lock(key, value, expiry_time=60, debug=False):
    def f(key=key, value=value, expiry_time=expiry_time):
        redis = functions.get_redis()
        while 1:
            v = redis.get(key)
            if v == value:
                redis.set(key, value, ex=expiry_time, xx=True)
                if debug:
                    log.debug('Continue lock')
            else:
                if debug:
                    log.debug('Not acquire lock yet')
            time.sleep(expiry_time/2)
    return f

def waiting_lock(key, value, expiry_time=60, debug=False):
    redis = functions.get_redis()
    while 1:
        v = redis.get(key)
        if not v:
            flag = redis.set(key, value, ex=expiry_time, nx=True)
            if flag:
                if debug:
                    log.info('Acquired cron lock')
                return True
        elif v == value:
            return True

        time.sleep(expiry_time)

def call(args, options, global_options):
    global jobs, jobs_time

    from uliweb import settings
    from uliweb.utils.common import get_uuid

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    log.info('=============================')
    log.info(' Cron Job Daemon Starting')
    log.info('=============================')
    log.info('Daemon process %d' % os.getpid())

    init()

    if len(jobs_time) == 0:
        log.info("Job queue is empty")
    else:
        log.info("Job queue size is {}".format(len(jobs_time)))

    breakout = Breakout('cron_refresh')

    if hasattr(options, 'lock_timeout'):
        timeout = options.lock_timeout
    else:
        timeout = settings.get_var('CRON/lock_timeout', 60)

    if hasattr(options, 'debug'):
        debug = options.debug
    else:
        debug = False
    key = 'cron:cron_instance'
    value = get_uuid()

    log.info('Key=[{}/{}], lock_timeout={}, debug={}'.format(key, value, timeout, debug))

    spawn(continue_lock(key, value, timeout, debug))

    while not is_exit:
        try:
            waiting_lock(key, value, timeout, debug)
            if jobs_time:
                with breakout:
                    _time, _id = jobs_time[0]
                    job = jobs[_id]

                    now = date.now()
                    t = _time - time.mktime(now.timetuple())
                    if t <= 0:
                        #产生一个新的时间
                        jobs_time.pop(0)
                        _t = get_exe_time(job)
                        bisect.insort(jobs_time, (_t, _id))
                        #启动作业
                        start_job(job, now)
                    else:
                        log.info(u"Sleep {0} seconds will start job [{2} -- {1}] at {3}".format(t,
                                        job.time, job.title, now+datetime.timedelta(seconds=t)))
            else:
                t = 60
            time.sleep(t)
        except BreakoutException as e:
            init()

