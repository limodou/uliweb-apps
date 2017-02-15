#coding=utf8
from uliweb import expose, functions

@expose('/ui/vue')
class VueView(object):
    @expose('')
    def index(self):
        return {}
