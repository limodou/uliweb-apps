#coding=utf-8
from uliweb import expose, functions
import logging
from uliweb.i18n import ugettext_lazy as _

log = logging.getLogger(__name__)

@expose('/cron')
class CronView(functions.MultiView):
    def _convert_title(self, value, obj):
        return u'''<a href="/cron/{id}">{title}</a>'''.format(id=obj.id, title=value)

    def _convert_view_details(self, value, obj):
        from uliweb import request
        path = request.path
        v = []
        v.append(u'<a href="/async_tasks/view/{0}?back_url={2}">{1}</a>'.format(
            obj.task_id, u'查看细节', path))
        #当状态不为成功或取消时,可以取消
        if obj.status not in ('1', 'C'):
            v.append(u'<a href="/async_tasks/cancel/{0}" class="cancelBtn">{1}</a>'.format(
                obj.task_id, u'取消'))
        return ' '.join(v)

    def _convert_action(self, value, obj):
        return u'''<a href="/cron/{0}/edit">{1}</a>
<a href="/cron/{0}/delete">{2}</a>'''.format(obj.id, _('Edit'), _('Delete'))

    def _convert_status(self, value, obj):
        #if the tasks is not
        v = obj.get_display_value('status')
        if value == '1':
            v = '<span class="label label-success">%s</span>' % v
        elif value == 'C':
            v = '<span class="label label-warning">%s</span>' % v
        elif value == '2':
            v = '<span class="label label-info">%s</span>' % v
        elif value == '0':
            v = '<span class="label label-default">%s</span>' % v
        else:
            v = '<span class="label label-important">%s</span>' % v
        return v

    def _convert_enabled(self, value, obj):
        if value:
            return '<span class="label label-success">启用</span>'
        else:
            return '<span class="label label-default">禁用</span>'

    @expose('')
    def list(self):
        return self._list('cron_job', fields_convert_map=['title', 'action', 'enabled'])

    def _refresh_jobs(self):
        from . import refresh_jobs

        refresh_jobs()

    def _post_save(self, data, obj):
        from uliweb import response
        response.post_commit = self._refresh_jobs()

    def add(self):
        from .forms import JobForm

        def pre_save(data):
            data['enabled'] = True
            data['modified_user'] = request.user.id

        return self._add('cron_job', ok_url='/cron/{id}',
                         post_save=self._post_save,
                         pre_save=pre_save,
                         form_cls=JobForm)

    @expose('<id>/edit')
    def edit(self, id):
        from .forms import JobForm

        def pre_save(obj, data):
            data['modified_user'] = request.user.id

        obj = functions.get_object('cron_job', int(id))
        return self._edit('cron_job', obj=obj, ok_url='/cron/{id}',
                          pre_save=pre_save,
                          post_save=self._post_save,
                          form_cls=JobForm)

    @expose('<id>/delete')
    def delete(self, id):
        def pre_delete(obj):
            response.post_commit = self._refresh_jobs()

        obj = functions.get_object('cron_job', int(id))
        return self._delete('cron_job', obj=obj, ok_url='/cron',
                            pre_delete=pre_delete)

    @expose('<id>/start')
    def start(self, id):
        from .daemon import start_job
        from uliweb.utils import date

        try:
            obj = functions.get_object('cron_job', int(id))
            now = date.now()
            start_job(obj, now)
            flash('启动作业 {} 成功'.format(id))
        except Exception as e:
            log.exception(e)
            flash('启动作业 {} 失败'.format(id), 'error')
        return redirect('/cron/{}'.format(id))

    def start_task(self, id):
        from .daemon import start_task

        try:
            c = start_task(id)
            return json({'success':True, 'message':'启动命令成功', 'id':c.task_id})
        except:
            return json({'success':False, 'message':'启动命令失败'})

    @expose('<id>')
    def view(self, id):
        """
        查看某个作业的执行信息
        """
        # Detail = functions.get_model('cron_job_details')
        Task = functions.get_model('async_tasks')
        job = functions.get_object('cron_job', int(id))
        template_data = {'job_id':id, 'job':job}
        # condition = Detail.c.cron_job==int(id)
        fields_convert_map = ['view_details', 'status']
        fields = [
            {'name':'task_id', 'width':250},
            {'name':'startup_time', 'width':150},
            {'name':'started_time', 'width':150},
            {'name':'finished_time', 'width':150},
            {'name':'status', 'width':60},
            {'name':'view_details', 'width':100},
        ]
        return self._list('async_tasks',
                          query=job.instances.fields('id', 'task_id',
                                                     'startup_time', 'started_time',
                                                     'finished_time', 'status'
                                                ),
                          queryview=None,
                          template_data=template_data,
                          fields=fields,
                          # condition=condition,
                          order_by=Task.c.startup_time.desc(),
                          fields_convert_map=fields_convert_map)

    @expose('<id>/view')
    def view_workflow(self, id):
        Job = functions.get_model('cron_job')
        Task = functions.get_model('cron_task')
        job = Job.get(int(id))

        action = request.GET.get('action')
        if action == 'get_tasks':
            return self._do_get_tasks(job)
        else:
            return {'job':job}

    @expose('<id>/workflow')
    def workflow(self, id):
        Job = functions.get_model('cron_job')
        Task = functions.get_model('cron_task')
        job = Job.get(int(id))

        action = request.GET.get('action')
        if action == 'get_tasks':
            return self._do_get_tasks(job)
        elif action == 'save':
            return self._do_save(job)
        else:
            return {'job':job}

    def _do_get_tasks(self, job):
        from uliweb import json

        tasks = []
        for t in job.tasks:
            d = {'id':str(t.id),
                 'command':t.command,
                 'title':t.command,
                 'label':t.label,
                 'work_directory':t.work_directory,
                 'depend_tasks':t.depend_tasks,
                 'queue':t.queue.split(','),
                 'timeout':t.timeout/60/1000,
                 # 'change':False,
                 }
            tasks.append(d)
        return json({'tasks':tasks})

    def _do_save(self, job):
        import json as _json
        from uliweb import request, json
        from uliweb.utils.common import expand_path

        Task = functions.get_model('cron_task')

        nodes = _json.loads(request.POST.get('nodes'))
        timeout = 0

        #对已有结点进行遍历,不存在的删除,已存在的更新,将依赖和子结点数清空
        for task in job.tasks:
            data = nodes.pop(task.id, None)
            #将分钟转为毫秒
            data['timeout'] = int(data['timeout']) * 60 * 1000
            if data['queue']:
                data['queue'] = ','.join(data['queue'])
            else:
                data['queue'] = 'default'
            if not data:
                task.delete()
            else:
                task.update(cron_job=job.id, modified_user=request.user.id, **data)
                task.save()
                timeout += task.timeout

        #nodes中剩余的就是新增的
        for _id, data in nodes.items():
            #将分钟转为毫秒
            data['timeout'] = int(data['timeout']) * 60 * 1000
            if data['queue']:
                data['queue'] = ','.join(data['queue'])
            else:
                data['queue'] = 'default'
            task = Task(cron_job=job.id, modified_user=request.user.id, **data)
            task.save()
            timeout += task.timeout

        #计算整个job的超时
        job.timeout = timeout
        job.save()
        return json({'success':True})


    @expose('<id>/add_task')
    def add_task(self, id):
        def pre_save(data):
            data['cron_job'] = int(id)

        def post_created_form(fcls):
            fcls.queue.multiple = True

        return self._add('cron_task',
                         json_result=True,
                         post_created_form=post_created_form,
                         pre_save=pre_save)

