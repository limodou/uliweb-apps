# coding=utf8
from uliweb import expose, functions, settings
from uliweb.i18n import gettext_lazy as _


@expose('/admin/permission')
class PermissionView(object):

    def __begin__(self):
        # return functions.require_login()
        #
        pass

    def _get_query_view(self, url):
        """
        Return a query view object
        """
        from uliweb.contrib.generic.forms import QueryForm

        Perm = functions.get_model('permission')

        fields = ['name', 'description']
        layout = [('name', 'description')]
        query = functions.QueryView(
            Perm, ok_url=url, fields=fields, layout=layout,
            form_cls=QueryForm)
        return query

    def _get_fields(self):
        """
        Return list fields info, and it'll be used in angularjs template
        """
        view = functions.ListView(self.model)
        return view.table_info['fields_list']

    @expose('')
    def list(self):
        Perm = functions.get_model('permission')

        query = self._get_query_view(url_for(self.__class__.list))
        c = query.run()

        condition = None

        if c.get('name'):
            condition = (Perm.c.name.like('%' + c['name'] + '%')) & condition
        
        if c.get('description'):
            condition = (Perm.c.description.like('%' + c['description'] + '%')) & condition

        def name(value, obj):
            return '<a href="/admin/permission/view/%d">%s</a>' % (obj.id, value)
            
        fields_convert_map = {
            'name':name
        }

        view = functions.ListView(Perm,
                                  # pageno=page, #get page info from request
                                  # rows_per_page=rows, #get rows info from
                                  # request
                                  pagination=True,
                                  condition=condition,
                                  fields_convert_map=fields_convert_map,
                                  )

        if 'data' in request.values:
            return json(view.json())

        result = view.run()
        result['view'] = view

        result['query_form'] = query.form

        return result

    def add(self):
        def pre_save(data):
            pass

        def post_created_form(fcls, model):
            pass

        def post_save(obj, data):
            pass

        def success_data(obj, data):
            d = obj.to_dict()
            return d

        def get_url(id):
            return url_for(self.__class__.list)

        template_data = {'layout': 'rbac_man_layout.html'}

        view = functions.AddView(self.model,
                                 ok_url=get_url,
                                 pre_save=pre_save,
                                 post_save=post_save,
                                 post_created_form=post_created_form,
                                 template_data=template_data,
                                 success_data=True,
                                 )
#        response.template = 'GenericView/add.html'
        return view.run(json_result=True)

    def view(self, id):
        """
        Show the detail of object. Template will receive an `object` variable 
        """
        
        from uliweb.utils.generic import get_obj_url
        obj = self.model.get_or_notfound(int(id))

        fields_convert_map = {}
        template_data = {}

        view = functions.DetailView(self.model,
                                    obj=obj,
                                    template_data=template_data,
                                    fields_convert_map=fields_convert_map,
                                    )
#        response.template = 'GenericView/view.html'
        result = view.run()
        roles = {}
        for role in obj.perm_roles:
            roles[role.id] = (get_obj_url(role), role.description)
        result['roles'] = roles
        return result

    def edit(self, id):
        def success_data(obj, data):
            d = obj.to_dict()
            return d

        def post_created_form(fcls, model, obj):
            pass

        template_data = {}

        obj = self.model.get_or_notfound(int(id))
        view = functions.EditView(self.model,
                                  ok_url=url_for(self.__class__.list),
                                  obj=obj,
                                  template_data=template_data,
                                  post_created_form=post_created_form,
                                  success_data=True,
                                  )
#        response.template = 'GenericView/edit.html'
        return view.run(json_result=True)

    def delete(self, id):
        def pre_delete(obj):
            pass

        obj = self.model.get_or_notfound(int(id))
        view = functions.DeleteView(self.model,
                                    ok_url=url_for(self.__class__.list),
                                    obj=obj,
                                    pre_delete=pre_delete,
                                    )
        return view.run(json_result=True)

    def search(self):
        name = request.GET.get('term', '')
        perms = request.values.get('perms')
        condition = None
        if perms:
            ids = [int(p) for p in perms.split(',')]
            condition = (self.model.c.id.in_(ids)) & condition

        v_field = request.values.get('label', 'title')
        if name:
            result = [{'id': obj.id, v_field: obj.name}
                      for obj in self.model.filter(condition).filter(self.model.c.name.like('%' + name + '%'))]
        else:
            result = []
        return json(result)
