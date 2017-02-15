#coding=utf8
#async tasks process daemon
from __future__ import print_function, absolute_import

import os
import sys
from uliweb import functions
from uliweb.orm import Begin, Commit, Rollback, Reset
import logging
from uliweb.utils import date
from . import (QUEUED, SUCCESS, STARTED, CANCEL, FAILED, ERROR)
import traceback
import time
import datetime
import signal

log = logging.getLogger(__name__)
is_exit = False


def handler(signum, frame):
     global is_exit
     print ("Process %d received a signal %d" % (os.getpid(), signum))
     sys.exit(0)
     # is_exit = True

def run_command(row):
    import json
    from uliweb import settings

    keys_queue = settings.get_var('ASYNC_TASKS/tasks_keys_queue')

    kw = row.command_info.copy()
    kw['task_id'] = row.task_id
    queue =kw['queue']
    try:
        redis = functions.get_redis()
        if not isinstance(queue, (tuple, list)):
            queue = [queue]
        msg = json.dumps(kw)
        #在添加消息到公共队列的同时,将任务ID添加到keys_queue中,用来记录当前将要,或正在执行的任务
        for q in queue:
            pipe = redis.pipeline()
            name = settings.ASYNC_TASKS_QUEUES.get(q or 'default') or q
            pipe.lpush(name, msg).sadd(keys_queue, row.task_id)
            pipe.execute()
            log.info('Put task_id {} to queue=[{}] and keys_queue=[{}]'.format(row.task_id, name, keys_queue))
    except Exception as e:
        _type, value, tb = sys.exc_info()
        txt =  ''.join(traceback.format_exception(_type, value, tb))
        handler = row.get_handler(log=log)
        handler.save(status=ERROR, execution_info=txt, finished_time=date.now())
        log.error('Run async task {} failed when push with redis'.format(row.task_id))
        log.exception(e)


def process_task(row):
    from uliweb import settings

    Task = functions.get_model('async_tasks')

    now = date.now()
    #check started status
    if row.status == STARTED:
        #check timeout
        if row.started_time + datetime.timedelta(milliseconds=row.timeout) > now:
            return
        else:
            #检查任务是否还在执行
            keys_queue = settings.get_var('ASYNC_TASKS/tasks_keys_queue')
            redis = functions.get_redis()
            if redis.sismember(keys_queue, row.task_id):
                return
            row.startup_time = now

    handler = row.get_handler(log=log)
    #check depend task
    depend_task = row.check_depend_tasks(log)
    if depend_task:
        #依赖任务或父任务为取消时,当前任务取消
        if depend_task.status == CANCEL or depend_task.current_status == CANCEL:
            msg = "Depend task {} has been cancelled.".format(depend_task.task_id)
            row.cancel(msg, log=log)
            log.debug("Current task {} cancelled because depend task {} status is CANCEL".format(
                row.task_id, depend_task.task_id
            ))
        #如果依赖任务失败,当前任务也置为失败
        elif depend_task.status == FAILED:
            msg = "Current task {} FAILED because depend task {} status is FAILED".format(
                row.task_id, depend_task.task_id
            )
            handler.save(status=FAILED, finished_time=date.now(), message=msg)
            log.info(msg)
        return
    if row.retry_times >= row.max_retry_times:
        msg = ('Async task {} reaches max retry times, '
                      'status changes to FAILED').format(row.task_id)
        handler.save(status=FAILED, finished_time=date.now(), message=msg)
        log.info(msg)
        return
    if row.startup_time and row.startup_time<=now or not row.startup_time:
        #处理父结点,如果current_status为成功,则不执行
        if row.children_count > 0 and row.current_status == SUCCESS:
            return
        handler.save(status=STARTED, started_time=date.now(),
                     retry_times=row.retry_times+1)
        log.info('Async task {0} [{1}({2!r})] started, retry_times={3}'.format(
            row.task_id,
            row.command_name,
            row.command_info.get('parameters', ''),
            row.retry_times))
        run_command(row)
    # else:
    #     log.debug("Current task {} skipped because it's not need to start yet".format(row.task_id))

def call(args, options, global_options):
    from uliweb import settings

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    check_point = settings.get_var('ASYNC_TASKS/check_point')

    log.info('=============================')
    log.info(' Async Task Daemon Starting')
    log.info('=============================')
    log.info('Daemon process %d' % os.getpid())
    log.info('Check point %ds' % check_point)

    Task = functions.get_model('async_tasks')
    query = Task.filter(~Task.c.status.in_([SUCCESS, CANCEL, FAILED])).\
        order_by(Task.c.created_time)

    redis = functions.get_redis()
    while not is_exit:
        Reset()
        for row in query:
            try:
                #log.debug('Ready to process async task {} - {}'.format(row.task_id, row.command_name))
                process_task(row)
            except Exception as e:
                log.exception(e)
        beat = redis.brpop('async_tasks_beat', check_point)
        #to prevent database submit slow than redis
        time.sleep(0.5)

