#coding=utf8

from uliweb import expose

@expose('/ui/popover')
class WebuiPopoverView(object):
    @expose('')
    def index(self):
        return {}