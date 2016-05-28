#coding=utf8
#隔离区接收qpid的守护程序
from __future__ import print_function, absolute_import
from uliweb.utils.workers import *
from uliweb import functions
from . import Handler
import sys


class AsyncWorker(Worker):
    def init(self):
        from uliweb import settings

        self.redis = functions.get_redis()
        self.queue = self.kwargs['queue']
        self.work_queue = self.queue+':'+self.name
        self.keys_queue = settings.get_var('ASYNC_TASKS/tasks_keys_queue')

        #todo log

        self.log.info('{} {} created with queue={}, work queue={} timeout={} '
                      'max_requests={} soft_memory_limit={} hard_memory_limit={}'.format(
                            self.name, self.pid,
                            self.queue, self.work_queue,
                            self.timeout, self.max_requests,
                            self.soft_memory_limit,
                            self.hard_memory_limit))
        self.check_point = settings.get_var('ASYNC_TASKS_WORKERS/check_point')

    def get_message(self):
        message = self.redis.lindex(self.work_queue, 0)
        if not message:
            message = self.redis.brpoplpush(self.queue, self.work_queue, self.check_point)
        return message

    def run(self):
        """
        message should be {'function':, 'task_id':, 'base':, ...}),
        """
        import json
        from uliweb.utils.common import import_attr

        Task = functions.get_model('async_tasks')
        self.task_id = None
        self.handler = None

        message = self.get_message()
        if message:
            #count
            self.count += 1
            #todo args
            try:
                try:
                    kw = json.loads(message)
                    self.log.debug('Command message = %r' % kw)
                except Exception as e:
                    self.log.error('%s found an error:' % self.name)
                    self.log.exception(e)
                    return

                try:
                    self.task_id = kw.pop('task_id')
                    function = kw.pop('function')
                    parameters = kw.pop('parameters', {})
                    base = kw.pop('base', Handler)
                    cls = import_attr(base)
                except Exception as e:
                    self.log.exception(e)
                    return

                self.log.debug("cls={!r}, task_id={}, parameters={!r}, kw={!r}".format(cls, self.task_id,
                parameters, kw))
                self.handler = cls(self.task_id, log=self.log, **kw)
                self.handler.run()
            finally:
                self.handler = None
                self.clear_entry()

    def clear_entry(self):
        """
        清除redis中的当前记录
        """
        pipe = self.redis.pipeline()
        pipe.lpop(self.work_queue)
        task_id = self.task_id
        self.task_id = None
        if task_id:
            pipe.srem(self.keys_queue, task_id)
        pipe.execute()
        self.log.info("Clear worker task_id entry {}".format(task_id))

    def signal_handler(self, signum, frame):
        from . import ERROR
        from uliweb.utils import date

        msg = "Process {} received a signal {}".format(self.pid, signum)
        self.log.info (msg)
        if self.handler:
            self.handler.save(status=ERROR, execution_info=msg, finished_time=date.now())
        self.clear_entry()
        sys.exit(0)

    def signal_handler_usr1(self, signum, frame):
        from . import ERROR
        from uliweb.utils import date

        msg = "Process {} reached at hard memory limit".format(self.pid)
        self.log.info (msg)
        if self.handler:
            self.handler.save(status=ERROR, execution_info=msg, finished_time=date.now())
        self.clear_entry()
        sys.exit(0)

    def signal_handler_usr2(self, signum, frame):
        from . import ERROR
        from uliweb.utils import date

        msg = "Process {} reached at soft memory limit".format(self.pid)
        self.log.info (msg)
        if self.handler:
            self.handler.save(status=ERROR, execution_info=msg, finished_time=date.now())
        self.clear_entry()
        sys.exit(0)

def call(args, options, global_options):
    from uliweb import settings
    from multiprocessing import cpu_count

    check_point = settings.get_var('ASYNC_TASKS_WORKERS/check_point')
    queues = settings.get_var('ASYNC_TASKS_WORKERS/queues')

    #清除keys_queue
    keys_queue = settings.get_var('ASYNC_TASKS/tasks_keys_queue')
    redis = functions.get_redis()
    redis.delete(keys_queue)

    n = cpu_count()
    workers = []

    for x, queue in queues.items():
        max_requests = queue.get('max_requests')
        timeout = queue.get('timeout')
        soft_memory_limit = queue.get('soft_memory_limit')
        hard_memory_limit = queue.get('hard_memory_limit')
        number = queue.get('number', n) or n

        for i in range(number):
            workers.append(AsyncWorker(kwargs={'queue':x}, max_requests=max_requests,
                           timeout=timeout, soft_memory_limit=soft_memory_limit,
                           hard_memory_limit=hard_memory_limit))

    manager = Manager(workers, title='Async Workers Daemon',
                      check_point=check_point, daemon=True)

    manager.start()