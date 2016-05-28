#coding=utf-8
from __future__ import print_function, absolute_import
from uliweb import decorators
#from .daemon import AsyncTask
from uliweb.utils.common import import_attr
import logging

log = logging.getLogger(__name__)

# @decorators.async_task(base=AsyncTask)
# def echo_async(*args, **kwargs):
#     print (args, kwargs)
#     return True

def echo(message, *args, **kwargs):
    print (message)
    return message

def callback(*args, **kwargs):
    print ('callback')
    return True

# @decorators.async_task(base=AsyncTask)
# def common_async_task(func, *args, **kwargs):
#     f = import_attr(func)
#     return f(*args, **kwargs)

def test_error(*args, **kwargs):
    print ('-----', kwargs)
    raise Exception('test error')

def test_cmd_list(*args, **kwargs):
    from . import AsyncCommandList, AsyncCommand

    c = AsyncCommand('shell', {'cmd':'ls'})
    c1 = AsyncCommand('shell', {'cmd':'ls'})
    c1.depend(c)
    List = AsyncCommandList()
    List.add(c, c1)
    return List

#执行shell命令
def shell(cmd, cwd=None, *args, **kwargs):
    import subprocess
    from uliweb import application
    from uliweb.utils.common import expand_path

    if not cwd:
        cwd = application.project_dir
    cwd = expand_path(cwd)
    log.info("Execute command line [%s] cwd=[%s]" % (cmd, cwd))
    result = subprocess.check_output(cmd, shell=True, cwd=cwd, stderr=subprocess.STDOUT)
    return result
