#coding=utf8

from uliweb import expose

@expose('/ui/ag-grid')
class AgGridView(object):
    def basic(self):
        return {}