#coding=utf8

from uliweb import expose

@expose('/ui/chooser')
class ChooserView(object):
    @expose('')
    def index(self):
        from .forms import ChooserForm

        ChooserForm.layout_class = 'bs3t'
        form = ChooserForm()
        return {'form':form}

    def tree(self):
        parent = request.values.get('parent', 0)
        s = []
        for i in range(5):
            d = {'name':'Node-{}-{}'.format(parent+1, i+1),
                 'id':'{}-{}'.format(parent+1, i+1), 'isPrent':True, 'open':False}
            s.append(d)
        return json(s)
  #       return json([
  #   { 'name':"父节点1 - 展开", 'open':True,
  #     'children': [
  #       { 'name':"父节点11 - 折叠",
  #         'children': [
  #           { 'name':"叶子节点111"},
  #           { 'name':"叶子节点112"},
  #           { 'name':"叶子节点113"},
  #           { 'name':"叶子节点114"}
  #         ]},
  #       { 'name':"父节点12 - 折叠",
  #         'children': [
  #           { 'name':"叶子节点121"},
  #           { 'name':"叶子节点122"},
  #           { 'name':"叶子节点123"},
  #           { 'name':"叶子节点124"}
  #         ]},
  #       { 'name':"父节点13 - 没有子节点", 'isParent':True}
  #     ]},
  #   { 'name':"父节点2 - 折叠",
  #     'children': [
  #       { 'name':"父节点21 - 展开", 'open':True,
  #         'children': [
  #           { 'name':"叶子节点211"},
  #           { 'name':"叶子节点212"},
  #           { 'name':"叶子节点213"},
  #           { 'name':"叶子节点214"}
  #         ]},
  #       { 'name':"父节点22 - 折叠",
  #         'children': [
  #           { 'name':"叶子节点221"},
  #           { 'name':"叶子节点222"},
  #           { 'name':"叶子节点223"},
  #           { 'name':"叶子节点224"}
  #         ]},
  #       { 'name':"父节点23 - 折叠",
  #         'children': [
  #           { 'name':"叶子节点231"},
  #           { 'name':"叶子节点232"},
  #           { 'name':"叶子节点233"},
  #           { 'name':"叶子节点234"}
  #         ]}
  #     ]},
  #   { 'name':"父节点3 - 没有子节点", 'isParent':True}
  #
  # ])
