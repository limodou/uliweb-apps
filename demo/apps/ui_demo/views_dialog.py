#coding=utf8

from uliweb import expose

@expose('/ui/dialog')
class DialogView(object):
    def basic(self):
        return {}