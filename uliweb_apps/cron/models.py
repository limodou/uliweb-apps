#coding=utf-8
from uliweb.orm import *
from uliweb.utils.common import get_var
from uliweb.i18n import ugettext_lazy as _

class Cron_Job(Model):
    title = Field(str, max_length=300, verbose_name=_('Title'), required=True)
    time = Field(str, max_length=20, verbose_name=_('Time'), required=True) #m h d M w

    instances = ManyToMany('async_tasks', reference_fieldname='task_id')
    timeout = Field(int, verbose_name=_('Timeout')) #毫秒

    modified_user = Reference('user', verbose_name=_('Modified User'))
    modified_time = Field(DATETIME, verbose_name=_('Modified Time'),
                          auto_now=True, auto_now_add=True)
    enabled = Field(bool, verbose_name=_('Enabled'))
    version = Field(int)

    def __unicode__(self):
        return self.title

    class AddForm:
        fields = [
            'title', 'time',
        ]

    class EditForm:
        fields = [
            'title', 'time', 'enabled'
        ]

    class Table:
        fields = [
            {'name':'time', 'width':80},
            {'name':'title', 'width':300},
            {'name':'enabled', 'width':120},
            {'name':'action', 'width':120},
        ]


class Cron_Task(Model):
    ##UUID string
    id = Field(str, max_length=36, verbose_name=_('ID'), primary_key=True,
               index=True, unique=True)
    label = Field(str, max_length=300, verbose_name=_('Label'))
    cron_job = Reference('cron_job', verbose_name=_('Cron Job'), collection_name='tasks')
    depend_tasks = Field(JSON, verbose_name=_('Depend Tasks'),
                         default=[]) #[id, id, ...]
    # parent_task = Reference(verbose_name=_('Parent Task'), collection_name='children')
    # children_count = Field(int, verbose_name=_('Children Count'))
    command = Field(str, max_length=1000, verbose_name=_('Command'))
    work_directory = Field(str, max_length=1000, verbose_name=_('Work Directory'))
    queue = Field(str, max_length=256, verbose_name=_('Queue'))
    timeout = Field(int, verbose_name=_('Timeout')) #毫秒

    modified_user = Reference('user', verbose_name=_('Modified User'))
    modified_time = Field(DATETIME, verbose_name=_('Modified Time'),
                          auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.label

