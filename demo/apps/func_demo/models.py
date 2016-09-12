#coding=utf8

from uliweb.orm import *

class Blog(Model):
    subject = Field(str, max_length=500, verbose_name=u'标题')
    content = Field(TEXT, verbose_name=u'内容')
    author = Reference('user', verbose_name=u'作者')
    created_time = Field(DATETIME, verbose_name=u'创建时间', auto_now_add=True)
    modified_time = Field(DATETIME, verbose_name=u'修改时间', auto_now_add=True, auto_now=True)

    def __unicode__(self):
        return self.subject

    def get_url(self):
        return '/blog/{}'.format(self.id)

    class AddForm:
        fields = ['subject', 'content']

    class Table:
        fields = [
            {'name':'id', 'width':40, 'align':'center'},
            {'name':'subject', 'sort':True},
            'author', 'created_time', 'modified_time'
        ]