#coding=utf-8
from uliweb import expose, functions, request, json
from uliweb.utils.common import query_string, request_url


@expose('/func/table_combine')
class FuncTableCombine(functions.MultiView):

    def _create_query_view(self):
        from uliweb_layout.form.query_view import QueryView
        from uliweb.form import StringField

        test = StringField('测试')

        fields = [
            ('test', test)
        ]

        layout = [
            ['test']
        ]

        query_form = functions.get_form('QueryForm')
        query = QueryView(fields=fields, layout=layout, form_cls=query_form)
        return query

    @expose('')
    def list(self):
        query_view = self._create_query_view()

        if 'data' in request.values:
            rows_data = [
                {'c1': '大分类一', 'c2': '小分类1', 'c3': '数据', 'c4': '数据', 'c5': '数据'},
                {'c1': '大分类一', 'c2': '小分类2', 'c3': '数据', 'c4': '数据', 'c5': '数据'},
                {'c1': '大分类一', 'c2': '小分类2', 'c3': '数据', 'c4': '数据', 'c5': '数据'},
                {'c1': '大分类二', 'c2': '小分类2', 'c3': '数据', 'c4': '数据', 'c5': '数据'},
                {'c1': '大分类二', 'c2': '小分类3', 'c3': '数据', 'c4': '数据', 'c5': '数据'},
                {'c1': '大分类二', 'c2': '小分类3', 'c3': '数据', 'c4': '数据', 'c5': '数据'}
            ]
            grid_data = {
                'page_rows': 10,
                'rows': rows_data,
                'limit': 10,
                'pageno': 1,
                'table_id': 'test_table',
                'total': '10',
                'page': '1'
            }
            return json(grid_data)

        else:
            fields_list = [
                {'name': 'c1', 'title': '字段1', 'width': 200, 'frozen': True},
                {'name': 'c2', 'title': '字段2', 'width': 200, 'frozen': True},
                {'name': 'c3', 'title': '字段3', 'width': 200},
                {'name': 'c4', 'title': '字段4', 'width': 200},
                {'name': 'c5', 'title': '字段5', 'width': 200},
            ]
            result = {
                'query_form': query_view.get_json(),
                'table': {
                    'data_url': query_string(request_url(), data=1),
                    'table_info': {
                        'fields_list': fields_list
                    }
                }
            }
            return result

