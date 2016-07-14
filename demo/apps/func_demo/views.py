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

        def post_created_form(fcls, model):
            fcls.subject.placeholder = '标题'
            fcls.subject.required = True

        return self._add('blog', ok_url=url_for(self.list), pre_save=pre_save,
                         post_created_form=post_created_form)

    def add1(self):
        def pre_save(data):
            if request.user:
                data['author'] = request.user.id

        def post_created_form(fcls, model):
            fcls.subject.placeholder = '标题'
            fcls.subject.required = True

        return self._add('blog', json_result=True, pre_save=pre_save,
                         post_created_form=post_created_form,
                         layout_class='bs3t'
                         )

    def edit(self, id):
        def pre_save(data, obj):
            if request.user:
                data['author'] = request.user.id

        def post_created_form(fcls, model, obj):
            fcls.subject.placeholder = '标题'
            fcls.subject.required = True

        return self._edit('blog', functions.get_object('blog', int(id)),
                        json_result=True, pre_save=pre_save,
                        post_created_form=post_created_form,
                        layout_class='bs3h'
                        )

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

    def simple_list(self):
        query = self._get_query_view()
        return self._list('blog', queryview=query, queryform=query.get_json(), pagination=False)

    def remove(self, id):
        return self._delete('blog', functions.get_object('blog', int(id)), json_result=True)

    def select2_search(self):
        name = request.GET.get('term', '')
        v_field = request.values.get('label', 'title')
        if name:
            result = [
                {'id': 1, v_field: 'Text1'},
                {'id': 2, v_field: 'Text2'},
                {'id': 3, v_field: 'Text3'},
                {'id': 4, v_field: 'Text4'},
            ]
        else:
            result = []
        return json(result)
