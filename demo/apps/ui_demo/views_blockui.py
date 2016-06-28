#coding=utf8

from uliweb import expose

@expose('/ui/blockui')
class BlockUIView(object):
    @expose('')
    def index(self):
        return {}