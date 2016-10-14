#coding=utf8

from uliweb import expose

@expose('/ui/ztree')
class ZTreeView(object):

    @expose('')
    def index(self):
        return {}
