#coding=utf-8
from __future__ import absolute_import
from uliweb import expose, functions
import logging

log = logging.getLogger(__name__)

@expose('/async_tasks')
class AsyncTasksView(functions.MultiView):
    def _convert_task_id(self, value, obj):
        return '<a href="/async_tasks/view/{0}" title="{0}" class="view" target="_blank">{0}</a>'.format(value)


    def _convert_status(self, value, obj):
        from . import SUCCESS, CANCEL, STARTED, QUEUED

        #if the tasks is not
        v = obj.get_display_value('status')
        if value == SUCCESS:
            v = '<span class="label label-success">%s</span>' % v
        elif value == CANCEL:
            v = '<span class="label label-warning">%s</span>' % v
        elif value == STARTED:
            v = '<span class="label label-info">%s</span>' % v
        elif value == QUEUED:
            v = '<span class="label label-default">%s</span>' % v
        else:
            v = '<span class="label label-important">%s</span>' % v
        if value not in (SUCCESS, CANCEL, QUEUED):
            return v + u' <a href="/async_tasks/reset/%s" class="reset">重置</a>' \
                   u' <a href="/async_tasks/cancel/%s" class="cancel">取消</a>' % (
                obj.task_id, obj.task_id)
        else:
            return v

    def _convert_correlation(self, value, obj):
        if obj.correlation_link:
            return '<a href="{0}" class="correlation" target="_blank">{1}</a>'.format(
                obj.correlation_link, obj.correlation)
        else:
            return value


    def _convert_command_info(self, value, obj):
        from uliweb.utils.common import pretty_dict
        import json

        return ''.join(pretty_dict(json.loads(value), leading='&nbsp;', newline='<br/>'))

    def _convert_timeout(self, value, obj):
        return '{} Minutes'.format(value/60/1000)

    _convert_retry_time_interval = _convert_timeout

    def _get_object(self, task_id):
        model = functions.get_model('async_tasks')
        obj = functions.get_object(model, condition=model.c.task_id==task_id)
        return obj


    def _get_query_view(self):
        from query.forms import QueryForm
        fields = [
            {'name':'task_id', 'like':'_%'},
            'category',
            {'name':'command_name', 'like':'%_%'},
            'status',
            {'name':'begin_created_date', 'label':'创建开始时间', 'type':'date'},
            {'name':'end_created_date', 'label':'创建结束时间', 'type':'date'},
            'message_type',
            'message_source',
            'correlation',
            'user_id',
            'src_ip',
        ]
        layout = [
                ('task_id', 'category', 'command_name', 'status'),
                ('begin_created_date', 'end_created_date'),
                ('correlation', 'message_type', 'message_source'),
                ('user_id', 'src_ip'),
            ]
        return self._query_view('async_tasks', fields=fields, layout=layout,
                                form_cls=QueryForm)


    @expose('')
    def list(self):
        order_by = functions.get_model('async_tasks').c.created_time.desc()
        return self._list('async_tasks',
                          queryview=self._get_query_view(),
                          fields_convert_map=['task_id', 'status', 'correlation'],
                          order_by=order_by)


    def reset(self, task_id):
        """
        Reset task status to initialization status
        """
        task = self._get_object(task_id)
        if task:
            task.reset(log=log)
            return json({'success':True, 'message':'Reset is ok.'})
        else:
            return json({'success':False, 'message':'Task %r can not be found.' % task_id})


    def cancel(self, task_id):
        task = self._get_object(task_id)
        if task:
            task.cancel(log=log)
            return json({'success':True, 'message':'Cancel is ok.'})
        else:
            return json({'success':False, 'message':'Task %r can not be found.' % task_id})


    def view(self, task_id):
        obj = self._get_object(task_id)
        action = request.GET.get('action')
        if action == 'get_tasks':
            return self._do_get_tasks(obj)
        else:
            return self._view('async_tasks', obj=obj, template_data={'task_id':task_id},
                          fields_convert_map=['command_info', 'correlation', 'timeout',
                                              'retry_time_interval'])


    def edit(self, task_id):
        obj = self._get_object(task_id)
        return self._edit('async_tasks', obj=obj,
                          template_data={'task_id':task_id},
                          ok_url=url_for(self.view, task_id=task_id),
                          fields=['timeout'])

    def _do_get_tasks(self, job):
        """
        获取执行详细信息
        """
        from uliweb import json
        Task = functions.get_model('async_tasks')

        tasks = []

        def get_obj(t):
            from uliweb.utils.timesince import timesince

            status_text = Task.status.get_display_value(t.status)
            d = {'id':t.task_id,
                 'label':t.title,
                 'title':'<br/>'.join([
                     '任务 ID :{}'.format(t.task_id),
                     '开始时间:{}'.format(t.started_time),
                     '结束时间:{}'.format(t.finished_time),
                     '执行状态:{}'.format(status_text),
                     '执行命令:{}'.format(t.command_name),
                     '执行参数:{!r}'.format(t.command_info.get('parameters', ''))
                 ]),
                 'depend_tasks':t.depend_tasks,
                 'parent_task':t._parent_task_,
                 'status':t.status,
                 'children_count':t.children_count,
                 'status_text':status_text,
                 'started_time':t.started_time,
                 'finished_time':t.finished_time,
                 }
            if t.status == 'E':
                d['label'] += u'({}/{})'.format(t.retry_times, timesince(t.startup_time))
            elif t.status == '1': #成功
                d['label'] += u'(用时:{}s)'.format((t.finished_time-t.started_time).seconds)
            return d

        def iter_objs(job):
            for t in job.tasks.all():
                tasks.append(get_obj(t))
                iter_objs(t)

        tasks.append(get_obj(job))
        iter_objs(job)
        return json({'tasks':tasks})
