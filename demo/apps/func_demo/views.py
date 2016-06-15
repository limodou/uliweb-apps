#coding=utf-8
from uliweb import expose, functions

@expose('/func')
class FuncView(functions.MultiView):
    @expose('')
    def index(self):
        return {}

    def add(self):
        def pre_save(data):
            if request.user:
                data['author'] = request.user.id

        return self._add('blog', ok_url=url_for(self.list), pre_save=pre_save)

    def _get_query_view(self):
        from uliweb_layout.form.query_view import QueryModelView

        QueryForm = functions.get_form('QueryForm')
        fields = [
            {'name':'subject', 'like':'_%'},
            {'name':'created_time', 'op':'=='},
            {'name':'type', 'label':'类型', 'type':'select', 'choices':[('1', '是'), ('0', '否')], 'placeholder':'--请选择--'},
            {'name':'type1', 'label':'类型1', 'type':'select', 'multiple':True, 'choices':[('1', '是'), ('0', '否')], 'placeholder':'--请选择--'},
        ]
        layout = [
                ['subject'],
                ['created_time', 'type', 'type1']
            ]
        query = QueryModelView('blog', fields=fields, layout=layout, form_cls=QueryForm)
        return query

    def list(self):
        query = self._get_query_view()
        return self._list('blog', queryview=query, queryform=query.get_json())
