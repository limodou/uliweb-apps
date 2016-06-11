#coding=utf-8
from uliweb import functions, expose

@expose('/admin/permission/category')
class PermCategoryView(functions.MultiView):
    def __init__(self):
        self.model = functions.get_model('perm_category')

    def list(self):
        result = []
        for row in self.model.all():
            d = row.to_dict()
            result.append(d)
        return json(result)

    def save(self):
        import json as json_lib
        data = json_lib.loads(request.POST['data'])
        ids = {0:0}
        objs = []
        for row in data:
            d = {'name':row['name'], 'parent':ids[row['_parent']], 'order':row['order']}
            if not row['id'].isdigit():
                #新记录
                obj = self.model(**d)
            else:
                obj = self.model.get(int(row['id']))
                obj.update(**d)
            obj.save()
            ids[row['id']] = obj.id

        return json({'success':True, 'message':'保存成功!'})
