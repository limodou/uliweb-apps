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
        fields = [
            {'name':'subject', 'like':'_%'},
        ]
        layout = [
                'subject'
            ]
        return self._query_view('blog', fields=fields, layout=layout)

    def list(self):
        return self._list('blog', queryview=self._get_query_view())