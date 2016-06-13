#coding=utf8

from uliweb import expose

@expose('/ui/ag-grid')
class AgGridView(object):
    def basic(self):
        return {}

    def create_query(self, url):
        from uliweb.form import UnicodeField, SelectField, StringField
        from uliweb_layout.form.query_view import QueryView

        QueryForm = functions.get_form('QueryForm')

        subject = StringField('标题')
        author = StringField('作者')
        fields = [('subject', subject), ('author', author)]
        layout = [('subject',), ('author', )]
        query = QueryView(fields=fields, layout=layout, form_cls=QueryForm)
        return query

    def remote(self):
        #create query
        query_view = self.create_query(url_for(self.remote))
        c = query_view.run()

        print  query_view.get_json()
        print 'query-conditon', c
        print 'request', request.values

        Blog = functions.get_model('blog')
        #处理条件
        condition = None
        if c.get('subject'):
            condition = Blog.c.subject.like(c['subject']+'%')

        fields = [
            {'name':'id', 'verbose_name':'Id', 'width':40, 'suppressSizeToFit':True, 'frozen':True, 'align':'center'},
            {'name':'subject', 'verbose_name':'标题/名称', 'headerTooltip':'This is a test'},
            {'name':'author', 'verbose_name':'标题/作者', 'suppressSizeToFit':True},
            {'name':'created_time', 'verbose_name':'创建时间', 'suppressSizeToFit':True},
            {'name':'modified_time', 'verbose_name':'修改时间', 'suppressSizeToFit':True},
            {'name':'abc', 'verbose_name':'修改时间', 'suppressSizeToFit':True, 'hidden':True},
            {'name':'def', 'verbose_name':'修改时间', 'suppressSizeToFit':True},
        ]
        view = functions.ListView('blog', fields=fields, condition=condition)
        if 'data' in request.GET:
            return json(view.json())
        else:
            result = view.run()
            result['table'] = view
            result['query_form'] = query_view.get_json()
            return result
