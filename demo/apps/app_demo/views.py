#coding=utf-8
from uliweb import expose

@expose('/app')
def app():
    response.template = 'app_demo_layout.html'
    return {}

