#coding=utf8
from __future__ import print_function, absolute_import
from uliweb.orm import *
from uliweb.i18n import ugettext_lazy as _
from uliweb.utils.common import get_var
from uliweb.utils import date
from .__init__ import SUCCESS

class Async_Tasks(Model):
    task_id = Field(str, max_length=32, verbose_name=_('Task ID'), index=True, unique=True)
    title = Field(str, max_length=200, verbose_name=_('Title'))
    parent_task = Reference(reference_fieldname='task_id', verbose_name=_('Parent Task'),
                            index=True, collection_name='tasks')
    category = Field(str, max_length=40, verbose_name=_('Category'))
    message_source = Field(CHAR, max_length=1, verbose_name=_('Message Source'),
                           choices=get_var('ASYNC_TASKS/MESSAGE_SOURCE'), default='l')
    message_type = Field(CHAR, max_length=1, verbose_name=_('Message Type'),
                         choices=get_var('ASYNC_TASKS/MESSAGE_TYPE'))
    #如果command_name为空,表示无命令需要执行
    command_name = Field(str, max_length=256, verbose_name=_('Command Name'))
    command_info = Field(JSON, verbose_name=_('Command Info'))
    depend_tasks = Field(JSON, verbose_name=_('Depend Tasks'), default=[])
    status = Field(CHAR, max_length=1, verbose_name=_('Status'),
                   choices=get_var('ASYNC_TASKS/ASYNC_STATUS'), default='0', index=True)

    #记录当前状态,主要用在parent_task中
    current_status = Field(CHAR, max_length=1, verbose_name=_('Current Status'),
                   choices=get_var('ASYNC_TASKS/ASYNC_STATUS'), default='0')

    #子结点个数
    children_count = Field(int, verbose_name=_('Children Count'))

    created_time = Field(datetime.datetime, verbose_name=_('Created Time'), auto_now_add=True)
    execution_info = Field(TEXT, verbose_name=_('Execution Info'))
    message = Field(str, max_length=2000, verbose_name=_('Message'))
    startup_time = Field(datetime.datetime, verbose_name=_('Startup Time'))
    started_time = Field(datetime.datetime, verbose_name=_('Started Time'))
    finished_time = Field(datetime.datetime, verbose_name=_('Finished Time'))
    max_retry_times = Field(int, verbose_name=_('Max Retry Times'))
    retry_time_interval = Field(int, verbose_name=_('Retry Time Interval'))
    retry_times = Field(int, verbose_name=_('Retry Times'))
    timeout = Field(int, verbose_name=_('Timeout'))
    user_id = Field(str, max_length=40, default='SYS', verbose_name=_('User ID'))
    src_ip = Field(str, max_length=15, verbose_name=_('Source IP'))

    correlation = Field(str, max_length=80, verbose_name=_('Correlation'), index=True)
    correlation_link = Field(str, max_length=2000, verbose_name=_('Correlation Link'))

    version = Field(int)

    @classmethod
    def OnInit(cls):
        Index('async_tasks_idx', cls.c.created_time, cls.c.status)

    @classmethod
    def get_task(cls, task_id):
        return cls.get(cls.c.task_id==task_id)

    def get_handler(self, **kwargs):
        from . import Handler
        from uliweb.utils.common import import_attr
        cls = import_attr(self.command_info.get('base', Handler))
        return cls(self, **kwargs)

    def check_depend_tasks(self):
        """
        Check if depend pre tasks have done all, if exists unfinished task, then return False
        """

        if self._parent_task_:
            if self.parent_task.current_status != SUCCESS:
                return self.parent_task
        for t in self.depend_tasks:
            task = self.get_task(t)
            if task.status != SUCCESS:
                return task

    def reset(self, force=False, log=None):
        """
        :param force: True will reset without condition, False will only reset for
         Failed, Error, Cancel status
        """
        from . import SUCCESS, STARTED, QUEUED

        now = date.now()

        task = self
        if force or (not force and task.status!=SUCCESS and (task.status!=STARTED or
                task.status==STARTED and
                task.started_time + datetime.timedelta(milliseconds=task.timeout) > now)):
            task.status = QUEUED
            task.retry_times = 0
            task.startup_time = None
            task.execution_info = ''
            task.message = 'The task is reset'
            handler = self.get_handler(log=log)
            handler.save()

            #处理子结点
            for t in self.tasks:
                t.reset(force=force, log=log)

            return True
        else:
            return False

    def cancel(self, message='', process_child=False, log=None):
        """
        只处理状态为QUEUE, ERROR的记录,其它的不处理
        """
        from . import CANCEL, QUEUED, ERROR

        if self.status in (QUEUED, ERROR):
            self.status = CANCEL
            self.finished_time = date.now()
            self.message = message
            handler = self.get_handler(log=log)
            handler.save()

        if process_child:
            #处理子结点
            for t in self.tasks:
                t.cancel(message, process_child, log)

    @classmethod
    def clear_data(cls, days, count=5000):
        from datetime import timedelta

        His = get_model('async_tasks_his')

        now = date.now()

        i = 0
        for row in cls.filter(cls.c.status.in_(['C', '1', 'F']), cls.c.created_time<(now-timedelta(days=days))):
            his = His(**row.to_dict())
            his.save(insert=True)
            row.delete()

            i += 1
            if i == count:
                yield i
                i = 0
        yield i

    class Table:
        fields = [
            {'name':'task_id', 'width':150},
            {'name':'title', 'width':200},
            {'name':'command_name', 'width':150},
            {'name':'category', 'width':100},
            {'name':'message_source', 'width':60},
            {'name':'message_type', 'width':60},
            # {'name':'command_info', 'width':200},
            {'name':'status', 'width':120},
            {'name':'current_status', 'width':120, 'hidden':True},
            {'name':'retry_times', 'width':30},
            # {'name':'depend_tasks', 'width':150},
            {'name':'created_time', 'width':120},
            {'name':'startup_time', 'width':120},
            {'name':'started_time', 'width':120},
            {'name':'finished_time', 'width':120},
            {'name':'user_id', 'width':100},
            {'name':'src_ip', 'width':100},
            {'name':'parent', 'width':120},
            {'name':'children_count', 'width':120, 'hidden':True},
            {'name':'correlation', 'width':120},
        ]

class Async_Tasks_His(Async_Tasks):
    pass
