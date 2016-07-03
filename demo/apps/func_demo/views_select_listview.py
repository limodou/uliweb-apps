#coding=utf-8
from uliweb import expose, functions

@expose('/func')
class FuncSelectListView(object):
    def create_query(self, url):
        from uliweb.form import UnicodeField, SelectField, StringField
        from uliweb_layout.form.query_view import QueryView

        QueryForm = functions.get_form('QueryForm')

        subject = StringField('标题')
        author = StringField('作者')
        uni = UnicodeField('Unicode')
        select = SelectField('单选', multiple=True, choices=[('1', '选项一'), ('2', '选项二')])
        fields = [('subject', subject), ('author', author), ('uni', uni), ('select', select)]
        layout = [('subject',), ('author', 'uni', 'select')]
        query = QueryView(fields=fields, layout=layout, form_cls=QueryForm)
        print query.get_json()
        return query

    def select_listview(self):
        from uliweb.utils.generic import SelectListView
        from sqlalchemy.sql import and_, or_, not_, select, func, true
        from uliweb.orm import reflect_table

        Blog = reflect_table('blog')

        #create query
        query_view = self.create_query(url_for(self.select_listview))
        c = query_view.run()

        print  query_view.get_json()
        print 'query-conditon', c
        print 'request', request.values

        #处理条件
        condition = None
        if c.get('subject'):
            condition = Blog.c.subject.like(c['subject']+'%')

        fields = [
            {'name':'subject', 'width':80, 'verbose_name':'标题'},
            {'name':'author', 'width':50, 'verbose_name':'作者', 'align':'center'},
        ]

        def _subject(value, obj):
            return u'<a href="#">{}</a>'.format(value)

        fields_convert_map = {'subject':_subject}

        query = select([Blog.c.subject, Blog.c.author], condition)

        view =  SelectListView(condition=None, #order_by=order_by,
            fields_convert_map=fields_convert_map, fields=fields,
            query=query,
            #, total=count, manual=True
            )

        if 'data' in request.values:
            return json(view.json())

        else:
            result = view.run()
            result.update({'query_form':query_view.get_json(),
                           'table':view})
            return result
