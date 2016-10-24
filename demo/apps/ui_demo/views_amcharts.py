#coding=utf-8

from uliweb import expose

@expose('/ui/amcharts')
class AmChartsView(object):
    @expose('')
    def amcharts(self):
        return {}