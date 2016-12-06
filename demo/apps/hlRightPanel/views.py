# coding=utf-8
from uliweb import expose, functions, json


@expose('/hlRightPanel')
def index():
    return {}


@expose("/uli_toolbar/my_account")
def my_account():
    return {}


@expose("/uli_toolbar/my_favorite")
def my_favorite():
    return {}


@expose("/uli_toolbar/my_history")
def my_history():
    return {}


@expose("/uli_toolbar/ajaxPOST")
def ajaxPOST():
    var1 = request.POST.get("var1")
    var2 = request.POST.get("var2")
    print "var1=%s\r\nvar2=%s"%(var1,var2)
    return json({'success': True, 'msg': "", 'content': "<h1>AJAX POST</h1>"})
