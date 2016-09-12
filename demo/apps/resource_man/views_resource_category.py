#coding=utf-8
from uliweb import functions, expose, json

@expose('/resource_man/category')
class ResourceCategoryView(functions.MultiView):
    model_name = 'resource_category'
    def __init__(self):
        if not self.model_name:
            raise ValueError("model property is not assigned")
        self.model = functions.get_model(self.model_name)

    def list(self):
        result = []
        for row in self.model.filter(self.model.c.deleted==False):
            d = row.to_dict()
            result.append(d)
        return json(result)

    def save(self, relative_model=None):
        """
        保存category,同时根据relative_model删除对应的分类下的记录
        """
        import json as json_lib
        from uliweb import request
        from uliweb.utils import date

        data = json_lib.loads(request.POST['data'])
        ids = {0:0}
        objs = [] #记录更新的记录
        #先将所有记录置为删除状态
        self.model.all().update(deleted=True)
        for row in data:
            d = {'name':row['name'], 'parent':ids[row['parent']], 'order':row['order'],
                 'deleted':False, 'modified_time':date.now(), 'modified_user':request.user.id}
            flag = ''
            if not row['id'].isdigit():
                #新记录
                flag = 'new'
            else:
                obj = self.model.get(int(row['id']))
                if not obj:
                    flag = 'new'

            if flag == 'new':
                obj = self.model(**d)
            else:
                obj.update(**d)
            obj.save()
            objs.append(obj.to_dict())
            ids[row['id']] = obj.id
        self.model.filter(self.model.c.deleted==True).remove()

        if relative_model:
            R = functions.get_model(relative_model)
            for row in self.model.filter(self.model.c.deleted==True):
                R.filter(R.c.category==row.id).update(category=0)
                row.remove()

        return json({'success':True, 'message':'保存成功!', 'data':objs})

