#coding=utf-8
from uliweb import expose, functions, url_for
from uliweb.utils.generic import get_object_display
import logging

log = logging.getLogger(__name__)

@expose('/resource_man')
class ResourceManView(functions.MultiView):
    def __begin__(self):
        return functions.require_login()

    def __init__(self):
        self.model = functions.get_model('resource')
        self.fields = ['name', 'title', 'value',
                       'description', 'target', 'status', 'deploy_type',
                       'icon', 'order', 'parent', 'id', 'permissions']

    def _convert_parent(self, value, data):
        return value

    def _convert_name(self, value, data):
        return u'<a href="{}">{}</a>'.format(url_for(self.view, id=data.id), value)

    def _get_query_view(self):
        from uliweb_layout.form.query_view import QueryModelView

        QueryForm = functions.get_form('QueryForm')
        fields = [
            {'name': 'name', 'like': '%_%'},
            {'name': 'title', 'like': '%_%'},
            {'name': 'deploy_type'} #隐藏条件
        ]
        layout = [
            ['name', 'title'],
        ]
        query = QueryModelView(self.model, fields=fields, layout=layout, form_cls=QueryForm)
        return query


    @expose('')
    def list(self):
        parent = int(request.GET.get('parent') or 0)
        condition = self.model.c.parent==parent
        query = self._get_query_view()
        return self._list(self.model, queryview=query,
                          condition=condition,
                          queryform=query.get_json(),
                          pagination=not bool(parent),
                          fields_convert_map=['parent', 'name']
                          )

    def add(self):
        from uliweb.utils.common import get_choice

        parent = int(request.GET.get('parent') or 0)

        def post_save(obj, data):
            if data.get('parent'):
                p = self.model.get(data['parent'])
                p.has_children = True
                p.save()

            #清除缓存
            obj.clear_menu()

        def post_created_form(fcls, obj):
            # fcls.permissions.choices = [('', '')]
            fcls.permissions.html_attrs = {'data-url': '/config/permissions/search',
                                           'placeholder': '请输入权限英文名称进行选择'}

        def success_data(obj, data):
            return get_object_display(self.model, obj,
                                      fields=self.fields,
                                      fields_convert_map=self._get_fields_convert_map(['name'])
                                      )

        def get_form_field(name):
            from uliweb.form import RadioSelectField
            if name == 'status':
                return RadioSelectField('状态', choices=settings.get_var('RESOURCE/STATUS'))

        return self._add(self.model,
                         layout_class='bs3h',
                         success_data=success_data,
                         static_fields=['parent'],
                         post_save=post_save,
                         data={'status':'00001', 'parent':parent},
                         default_data={'parent':parent},
                         post_created_form=post_created_form,
                         template_data={'type':get_choice(settings.get_var('RESOURCE/TYPE'), type) or ''},
                         get_form_field=get_form_field,
                         json_result=True)

    def edit(self, id):
        obj = self.model.get_or_notfound(int(id))

        def success_data(obj, data):
            return get_object_display(self.model, obj,
                                      fields=self.fields,
                                      # 获得真正的fields_convert_map
                                      fields_convert_map=self._get_fields_convert_map(['name']))

        def post_created_form(fcls, model, obj):
            # fcls.permissions.query = obj.permissions
            fcls.permissions.html_attrs = {'data-url':'/config/permissions/search',
                                           'placeholder':'请输入权限英文名称进行选择'}

        def get_form_field(name, obj):
            from uliweb.form import RadioSelectField
            if name == 'status':
                return RadioSelectField('状态', choices=settings.get_var('RESOURCE/STATUS'))

        def post_save(obj, data):
            #清除缓存
            obj.clear_menu()

        return self._edit(self.model, obj=obj,
                          layout_class="bs3h",
                          success_data=success_data,
                          static_fields=['parent'],
                          post_created_form=post_created_form,
                          get_form_field=get_form_field,
                          post_save=post_save,
                          json_result=True,
                          )

    def delete(self, id):
        obj = functions.get_object(self.model, int(id))
        obj.clear_menu()
        return self._delete(self.model, obj, json_result=True)

    def view(self, id):
        obj = self.model.get_or_notfound(id)
        return self._view(self.model, obj, layout_class='bs3dt')

    def move(self):
        import json as _json
        from uliweb.utils.date import now

        data = request.POST.get('data')
        d = _json.loads(data)
        for row in d['updated']:
            obj = self.model.get(row['id'])
            if not obj:
                return json({'success':False, 'message':'记录丢失 {}'.format(row['id'])})
            x = {}
            x['parent'] = row['parent']
            x['order'] = row['order']
            x['level'] = row['level']
            x['has_children'] = row.get('has_children', 0)
            obj.modified_user = request.user.id
            obj.modified_time = now()
            obj.update(**x)
            obj.save()

            obj.clear_menu()

        return json({'success': True, 'message': '处理成功'})


        # def save(self):
    #     import json as _json
    #     from uliweb.utils.date import now
    #
    #     type = request.GET.get('type')
    #     data = request.POST.get('data')
    #     d = _json.loads(data)
    #     n = 0
    #     Resource = functions.get_model('resource')
    #     try:
    #         for row in d['added']:
    #             n += 1
    #             row['id'] = None
    #             obj = Resource(**row)
    #             obj.type = type
    #             obj.modified_user = request.user.id
    #             obj.modified_time = now()
    #             obj.save()
    #         for row in d['updated']:
    #             n += 1
    #             obj = Resource.get(row['id'])
    #             if not obj:
    #                 return json({'success':False, 'message':'记录丢失 {}'.format(row['id'])})
    #             obj.update(**row)
    #             obj.save()
    #         for row in d['deleted']:
    #             n += 1
    #             obj = Resource.get(row['id'])
    #             if not obj:
    #                 return json({'success': False, 'message': '记录丢失 {}'.format(row['id'])})
    #             obj.delete()
    #
    #         if n > 0:
    #             return json({'success':True, 'message':'处理成功'})
    #         else:
    #             return json({'success':True, 'message':'无变化'})
    #     except Exception as e:
    #         log.exception(e)
    #         return json({'success':False, 'message':'后台处理出错'})