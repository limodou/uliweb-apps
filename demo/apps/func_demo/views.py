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

        return self._add('blog',
                         layout_class='bs3t',
                         ok_url=url_for(self.list), pre_save=pre_save,
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

        def _render_type(model, name, value, values):
            from sqlalchemy import true
            return true()

        QueryForm = functions.get_form('QueryForm')
        fields = [
            {'name':'subject', 'like':'%_%'},
            #{'name':'created_time', 'op':'=='},
            {'name':'type', 'label':'类型', 'type':'select', 'choices':[('1', '是'), ('0', '否')],
                'placeholder':'--请选择--', 'condition':_render_type},
            {'name':'type1', 'label':'类型1', 'type':'select', 'multiple':True, 'choices':[('1', '是'), ('0', '否')], 'placeholder':'--请选择--'},
            {'name':'type2', 'label':'类型2', 'type':'select', 'multiple':True, 'data-url':'/func/select2_search', 'placeholder':'--请选择--'},
            {'name':'created_time1', 'label':'日期', 'type':'date', 'width':100},
            {'name':'created_time', 'label':'日期', 'type':'date', 'range':True, 'width':100},
        ]
        layout = [
                ['subject', 'type2'],
                ['type', 'type1', 'created_time'],
                ['created_time1']
            ]

        functions.set_echo(True)
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
        page = int(request.values.get('page') or 1)
        limit = int(request.values.get('limit') or 10)
        if name:
            result = {'total':100,
                      'rows':[{'id':x, v_field: 'Text'+str(x)} for x in range((page-1)*limit+1, page*limit+1)]}
        else:
            result = []
        return json(result)
