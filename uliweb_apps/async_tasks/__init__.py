#coding=utf8
from __future__ import print_function, absolute_import
import sys
from uliweb import functions
from uliweb.utils import date
from uliweb.utils.date import parse_time
from uliweb.utils.common import import_attr, safe_str
import logging
import copy
import datetime

QUEUED = '0'
SUCCESS = '1'
STARTED = '2'
ERROR = 'E'
CANCEL = 'C'
FAILED = 'F'

class ErrorWrongSettingEntry(Exception):pass
class ErrorWrongCommand(Exception):pass
class ErrorWrongCommandType(Exception):pass
class AsyncTaskMissing(Exception):pass


log = logging.getLogger(__name__)

class AsyncCommandList(object):
    """
    用于异步命令执行后返回命令列表使用,主要是动态创建父子结点关系
    """
    def __init__(self, result=''):
        self.tasks = []
        self.result = result

    def add(self, *command):
        for c in command:
            self.tasks.append(c)

    def set_parent(self, parent):
        for t in self.tasks:
            t.parent_task = parent.task_id

    def commit(self, parent=None):
        for t in self.tasks:
            if parent:
                t.parent_task = parent.task_id
            t.commit()

class AsyncCommand(object):
    """
    用于定义一个异步命令,并且可以同时定义命令之前的关系.目前异步命令间可以分为:依赖关系和包含关系.
    依赖关系使用depend_tasks属性来保存,包含关系使用parent_task来建立父子关系,同时有一个children_count
    表示子结点个数.
    """
    def __init__(self, command, parameters=None, title=None, timeout=None, max_retry_times=None,
                 retry_time_interval=None, startup_time=None, base=None, task_id=None,
                 user_id=None, src_ip=None, version='1.0', correlation=None,
                 correlation_link=None, parent_task=None,
                 sync=False, queue=None, **kwargs):
        """
        depend is relative task, only when depend task run successfully this task will
        be started
        sync 表示是否同步执行还是异步, 当True时,执行call_sync时会直接处理
        queue使用配置中ASYNC_TASKS_QUEUES的值
        """
        from uliweb import settings, request
        from uliweb.utils.common import get_uuid

        self.name = ''
        self.function = ''
        self.title = title or command
        self.task_id = task_id or get_uuid()
        self.parent_task = parent_task
        self.timeout = timeout or parse_time(settings.get_var('ASYNC_TASKS/timeout')) #ms
        self.max_retry_times = max_retry_times or \
                               settings.get_var('ASYNC_TASKS/max_retry_times')
        self.retry_time_interval = retry_time_interval or parse_time(settings.get_var(
                                                'ASYNC_TASKS/retry_time_interval')) #1m
        #add direct queue name, it maybe a list
        if isinstance(queue, (tuple, list)):
            self.queue = queue
        else:
            self.queue = settings.ASYNC_TASKS_QUEUES.get(queue or 'default')
        self.parameters = parameters or settings.get_var('ASYNC_TASKS/parameters')
        self.startup_time = startup_time
        self.depend_tasks = []
        self.children_count = 0
        self.sync = sync
        self.task = None
        self.tasks = {}
        self.version = version
        self.base = base or settings.get_var('ASYNC_TASKS/base')
        if user_id:
            self.user_id = user_id
        else:
            if request and request.user:
                self.user_id = request.user.id
            else:
                self.user_id = 'SYS'
        self.src_ip = src_ip or settings.get_var('PARA/HOST')
        self.correlation = correlation
        self.correlation_link = correlation_link
        self.kwargs = kwargs or {} #external parameters

        #process function object
        if callable(command):
            command = command.__module__ + '.' + command.__name__
            self.name = command
        if not command:
            self.name = ''
            self.function = ''
        elif isinstance(command, dict):
            self.name = command.get('cmd_name', self.name)

            if self.name:
                s = settings.get_var('ASYNC_TASKS_COMMANDS/%s' % self.name)
                if s:
                    self._set_command(s)
                self._set_command(command)
        elif isinstance(command, (str, unicode)):
            if '.' not in command: #guess it as command name
                self.name = command
                s = settings.get_var('ASYNC_TASKS_COMMANDS/%s' % self.name)
                if s:
                    self._set_command(s)
                else:
                    raise ErrorWrongSettingEntry(self.name)
            else:
                self.function = command
                self.name = command
        else:
            raise ErrorWrongCommand(command)

    def _set_command(self, command):
        """
        以下项均可以在settings.ini中进行配置
        """
        c = command.copy()
        self.function = c.pop('function', self.function)
        self.title = c.pop('title', self.title)
        self.timeout = parse_time(c.pop('timeout', self.timeout))
        self.max_retry_times = c.pop('max_retry_times', self.max_retry_times)
        self.retry_time_interval = parse_time(c.pop('retry_time_interval',
                                               self.retry_time_interval))
        self.parameters = c.pop('parameters', self.parameters)
        self.startup_time = c.pop('startup_time', self.startup_time)
        self.queue = c.pop('queue', self.queue)
        self.base = c.pop('base', self.base)
        self.kwargs = c or self.kwargs
        self.task_id = c.pop('task_id', self.task_id)
        self.user_id = c.pop('user_id', self.user_id)
        self.src_ip = c.pop('src_ip', self.src_ip)

    def _make_info(self):
        """
        生成用于workers中的参数
        """
        ret = {
                'function':self.function,
                'parameters':self.parameters,
                'queue':self.queue,
                'base':self.base,
                'user_id':self.user_id,
                'src_ip':self.src_ip,
                }
        ret.update(self.kwargs)
        return ret

    def commit(self, session=None):
        Task = functions.get_model('async_tasks')
        if session:
            Task = Task.use(session)
        if self.parent_task and isinstance(self.parent_task, AsyncCommand):
            parent_task_id = self.parent_task.task_id
        else:
            parent_task_id = self.parent_task
        task = Task(task_id=self.task_id,
                    title=self.title,
                    parent_task=parent_task_id,
                    children_count=len(self.tasks),
                    command_name=self.name,
                    command_info=self._make_info(),
                    depend_tasks=self.depend_tasks,
                    startup_time=self.startup_time or date.now(),
                    timeout=self.timeout,
                    max_retry_times=self.max_retry_times,
                    retry_time_interval=self.retry_time_interval,
                    user_id=self.user_id,
                    src_ip=self.src_ip,
                    correlation=self.correlation,
                    correlation_link=self.correlation_link)
        task.update(**self.kwargs)
        task.save()
        self.task = task

        #commit child tasks
        for t in self.tasks.values():
            t.commit()

        log.info('Commit a task %s' % self.task_id)
        return task

    def depend(self, *command):
        """
        增加正向依赖
        """
        for c in command:
            self.depend_tasks.append(c.task_id)

    def add_command(self, *command):
        """
        增加反向依赖,不设置为子结点
        """
        for c in command:
            c.depend_tasks.append(self.task_id)

    def add_child(self, *command):
        """
        增加子命令
        """
        for c in command:
            self.tasks[c.task_id] = c
            c.parent_task = self

    def run(self):
        """
        直接运行当前的命令
        """
        f = import_attr(self.function)
        ret = f(**self.parameters)
        return ret

class Handler(object):
    def __init__(self, task, log, **kwargs):
        if isinstance(task, (str, unicode)):
            Task = functions.get_model('async_tasks')
            task = Task.get_task(task)
            if not task:
                raise AsyncTaskMissing('Async task {} can not be found'.format(task))

        self.task = task
        self.task_id = task.task_id
        self.func = task.command_info.get('function', '')
        self.log = log
        self.ret = ''
        self.parameters = copy.deepcopy(task.command_info.get('parameters', {}))

        # self.kwargs = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def run(self):
        import traceback

        Task = functions.get_model('async_Tasks')

        try:
            self.before()

            if not self.func:
                self.ret = 'empty'
                self.log.debug("Async task {} function is empty".format(self.task_id))
            else:
                f = import_attr(self.func)
                self.log.debug("Run Async task {} function {!r}({!r})".format(
                    self.task_id, f, self.parameters))
                #_args表示位置参数
                args = self.parameters.pop('_args', ())
                self.ret = f(*args, **self.parameters)
                self.log.debug("Execute {!r} with {!r} and the result is {!r}".format(
                    f, self.parameters, self.ret))

            self.on_finish()

            self.after()

            self.save()

        except Exception as e:
            type, value, tb = sys.exc_info()
            txt =  ''.join(traceback.format_exception(type, value, tb))
            if self.task.retry_times >= self.task.max_retry_times:
                status = FAILED
                finished_time = date.now()
                startup_time = self.task.startup_time
                msg =  'Async task {} reaches max retry times, status changes to FAILED'.format(self.task.task_id)
                self.log.info(msg)
            else:
                status = ERROR
                startup_time = (date.now() +
                    datetime.timedelta(milliseconds=self.task.retry_time_interval*(self.task.retry_times-1)))
                finished_time = None
                msg =  'Async task {} runs on error, it will startup at {}'.format(self.task.task_id, startup_time)
                self.log.info(msg)

            self.save(execution_info=txt,
                      finished_time=finished_time,
                      startup_time=startup_time,
                      status=status,
                      message=msg)
            self.log.exception(e)

    def before(self):
        pass

    def after(self):
        pass

    def on_finish(self):
        """
        在处理成功后执行此处理,如果返回True,表示不执行缺省处理,否则按缺省处理进行
        :param ret: 命令执行结果
        :return:
        """
        #增加对返回值的处理,当self.ret返回为AsyncCommandList时,将当前任务置为
        #父结点,增加关联的子结点
        #动态生成的父任务
        if isinstance(self.ret, AsyncCommandList):
            self.ret.commit(self.task)
            self.task.children_count = len(self.ret.tasks)
            self.task.current_status = SUCCESS
            self.task.status = STARTED
            self.task.execution_info=safe_str(self.ret.result)
        #处理父任务
        elif self.task.children_count > 0:
            self.task.current_status = SUCCESS
            self.task.status = STARTED
            self.task.execution_info=safe_str(self.ret)
        #一般任务
        else:
            self.task.status = SUCCESS
            self.task.finished_time = date.now()
            self.task.execution_info = safe_str(self.ret)

    def _saved(self, instance, created, old_value, new_value):
        self._new_data = new_value

    def save(self, **kwargs):
        from uliweb.orm import Begin, Commit, Rollback
        Begin()
        try:
            self.task.update(**kwargs)
            self._new_data = {}
            ret = self.task.save(version=True, saved=self._saved)
            Commit()
            if self._new_data:
                self.on_changed(self._new_data)

        except Exception as e:
            Rollback()
            self.log.exception(e)
            raise

    def on_changed(self, data):
        #处理完毕时,发送消息通知,激活worker守护进行处理
        redis = functions.get_redis()
        redis.lpush('async_tasks_beat', 'start')

        if 'status' in data:
            if data['status'] == SUCCESS:
                self.on_success()
            elif data['status'] == ERROR:
                self.on_error()
            elif data['status'] == FAILED:
                self.on_failure()
            elif data['status'] == CANCEL:
                self.on_cancel()
            elif data['status'] == QUEUED:
                self.on_queued()

        #process relative job status and time
        if self.task.parent_task:
            parent = self.task.parent_task

            #根据子结点结果计算父结点的状态
            if 'status' in data:
                self._sync_parent(parent)

            #出错要重置启动时间
            if parent.status == ERROR:
                parent.startup_time = (date.now() +
                    datetime.timedelta(milliseconds=parent.retry_time_interval))

            #处理启动时间,取最早时间
            if 'started_time' in data and (not parent.started_time or
                    parent.started_time and parent.started_time>data['started_time']):
                parent.started_time = data['started_time']

            #出错和待处理不置完成时间
            if parent.status not in (ERROR, QUEUED) and 'finished_time' in data and parent.status in ('1', 'C', 'F'):
                parent.finished_time = data['finished_time']

            #保存结果
            handler = parent.get_handler(log=self.log)
            handler.save()


    def _sync_parent(self, parent):
        from sqlalchemy import select, func
        from uliweb.orm import do_

        M = functions.get_model('async_tasks')
        sql = select([M.c.status, func.count('*')], M.c.parent_task==parent.task_id,
                     from_obj=[M.table]).group_by(M.c.status)
        status = {}
        for row in do_(sql):
            status[row[0]] = row[1]

        queued = status.get('0', 0)
        success = status.get('1', 0)
        started = status.get('2', 0)
        error = status.get('E', 0)
        failed = status.get('F', 0)
        cancel = status.get('C', 0)

        if started:
            parent.status = '2'
        elif failed:
            parent.status = 'F'
        elif error:
            parent.status = 'E'
        elif (queued and not filter(None, [success, started, error, failed, cancel])):
            parent.status = '0'
        elif (success and not filter(None, [queued, started, error, failed])):
            parent.status = '1'
        elif (cancel and not filter(None, [queued, success, started, error, failed])):
            parent.status = 'C'

    def on_success(self):
        self.log.info('Async task {} process successfully'.format(self.task_id))

    def on_failure(self):
        self.log.info('Async task {} process failed'.format(self.task_id))

    def on_error(self):
        self.log.info('Async task {} process error'.format(self.task_id))

    def on_cancel(self):
        self.log.info('Async task {} process cancelled'.format(self.task_id))

    def on_queued(self):
        self.log.info('Async task {} process queued'.format(self.task_id))


def call_async(commands, parameters=None, direct=True, auto_commit=True, session=None):
    """
    Submit an async task to database and queue.

    :param command: command could be a dict or a string or a function object
    :param direct: if True, it'll invoke underline worker api to execute the task
    :param auto_commit: if True, then it'll create new session to commit, False will use
                  current session object or passed session object, if current session
                  is not in transaction, it'll automatically start transaction
    :param session: Only used for auto_commit is False
    :return: task_id value

    Several invoke format:
    call_async({'cmd_name':'echo', 'parameters':...})

    or

    c = AsyncCommand('echo', parameters=...)
    call_async(c)
    """
    from uliweb.orm import get_session, Session
    from .daemon import process_task

    if auto_commit:
        session = Session()
    else:
        session = session or get_session()

    trans = False
    if auto_commit:
        session.begin()
        trans = True
    else:
        if not session.in_transaction():
            session.begin()
            trans = True

    try:
        if isinstance(commands, AsyncCommand):
            commands = [commands]
        elif isinstance(commands, AsyncCommandList):
            commands = commands.tasks
        elif not isinstance(commands, (list, tuple)):
            commands = [AsyncCommand(commands, kwargs=parameters)]

        #根据条数发送若干通知
        if direct:
            def f(n=len(commands)):
                redis = functions.get_redis()
                redis.lpush('async_tasks_beat', *['start']*n)
            session.post_commit_once = f

        tasks = []
        for c in commands:
            if not isinstance(c, AsyncCommand):
                msg = "Wrong command type, but %r type found" % c
                log.error(msg)
                raise ErrorWrongCommandType(msg)
            tasks.append(c.commit(session))

        if trans:
            session.commit()

    except:
        if trans:
            session.rollback()
        raise
