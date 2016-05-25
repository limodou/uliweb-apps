#coding=utf8
from uliweb import expose, functions

@expose('/', template='site/home.html')
def home():
    return {}