from __future__ import absolute_import
import os, sys
import time
from uliweb import functions
from uliweb.orm import Reset
from uliweb.manage import make_simple_application

work_dir = os.getcwd()
os.chdir('../../..')
app = make_simple_application(project_dir='.')


def test_1():
    """
    >>> from async_tasks import AsyncCommand
    >>> task = AsyncCommand('echo', parameters={'message':'Hello'})
    >>> functions.call_async(task)
    >>> time.sleep(10)
    >>> Reset()
    >>> Task = functions.get_model('async_tasks')
    >>> t = Task.get_task(task.task_id)
    >>> print(t.execution_info)
    Hello
    """

def test_error():
    """
    >>> from async_tasks import AsyncCommand
    >>> task = AsyncCommand('test_error', parameters={'message':'Hello'})
    >>> functions.call_async(task)
    >>> time.sleep(10)
    >>> Reset()
    >>> Task = functions.get_model('async_tasks')
    >>> t = Task.get_task(task.task_id)
    >>> print(t.status)
    E
    """

def test_job_1():
    """
    >>> from async_tasks import AsyncCommand
    >>> job = AsyncCommand('', title='package')
    >>> task = AsyncCommand('echo', parameters={'message':'Hello'})
    >>> job.add_child(task)
    >>> functions.call_async(job)
    >>> time.sleep(10)
    >>> Task = functions.get_model('async_tasks')
    >>> t = Task.get_task(job.task_id)
    >>> print(t.status)
    2
    """

def test_job_error():
    """
    >>> from async_tasks import AsyncCommand
    >>> job = AsyncCommand('', title='package')
    >>> task = AsyncCommand('test_error', parameters={'message':'Hello'})
    >>> job.add_child(task)
    >>> functions.call_async(job)
    >>> time.sleep(10)
    >>> Task = functions.get_model('async_tasks')
    >>> t = Task.get_task(job.task_id)
    >>> print(t.status)
    E
    """

from async_tasks import AsyncCommand
job = AsyncCommand('', title='package')
task = AsyncCommand('echo', parameters={'message':'Hello'})
job.add_child(task)
job1 = AsyncCommand('', title='package')
task1 = AsyncCommand('echo', parameters={'message':'Hello'})
task2 = AsyncCommand('echo', parameters={'message':'Hello'})
task1.add_command(task2)
job1.add_child(task1, task2)
job.add_child(job1)
functions.call_async(job)
time.sleep(10)
Task = functions.get_model('async_tasks')
t = Task.get_task(job.task_id)
print(t.status)