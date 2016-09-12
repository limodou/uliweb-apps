# coding=utf-8
from uliweb.orm import *
from uliweb.utils.common import get_var

class Resource_Category(Model):
    __verbose_name__ = u'资源分类'

    name = Field(str, max_length=255, verbose_name=u'名称', index=True, unique=True)
    parent = Reference(verbose_name=u'父分类')
    order = Field(int, verbose_name=u'序号', index=True)
    deleted = Field(bool, verbose_name=u'删除标志')
    number = Field(int, verbose_name=u'个数', server_default=0)
    modified_user = Reference('user', verbose_name=u'修改人')
    modified_time = Field(DATETIME, verbose_name=u'修改时间', auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.name

class Resource(Model):
    __verbose_name__ = u'资源表'

#    category = Reference('resource_category', verbose_name=u'分类')
    name = Field(str, max_length=80, verbose_name=u'英文名称', index=True, unique=True, required=True)
    title = Field(str, max_length=200, verbose_name=u'标题', required=True)
    value = Field(str, max_length=512, verbose_name=u'值')
    description = Field(str, max_length=200, verbose_name=u'说明')
    parent = Reference(verbose_name=u'父结点', server_default='0')
    has_children = Field(bool, verbose_name=u'是否有子结点')
    icon = Field(str, max_length=20, verbose_name=u'图标')
    order = Field(int, verbose_name=u'序号')
    target = Field(str, max_length=10)
    type = Field(CHAR, max_length=5, choices=get_var('RESOURCE/TYPE'), verbose_name=u'类型')
    status = Field(CHAR, max_length=5, choices=get_var('RESOURCE/STATUS'), verbose_name=u'状态', server_default='00001')
    deploy_type = Field(CHAR, max_length=1, choices=get_var('PARA/DEPLOY_TYPE'), verbose_name=u'部署类型')
    permissions = ManyToMany('permission', verbose_name=u'权限')
    modified_user = Reference('user', verbose_name=u'修改人')
    modified_time = Field(DATETIME, verbose_name=u'修改时间', auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.name

    @classmethod
    def get_menu(cls, parent):
        from uliweb import functions, settings
        from uliweb.utils.common import Serial

        def _f(_p):
            menus = []
            for row in cls.filter(cls.c.parent == _p,
                                  cls.c.type == 'M0000',
                                  cls.c.deploy_type=='F',
                                  cls.c.status=='00001').order_by(cls.c.order):
                item = row.to_dict()
                item['link'] = row.value
                item['permissions'] = [x.name for x in row.permissions]
                menus.append(item)
                if row.has_children:
                    item['subs'] = _f(item.id)
                else:
                    item['subs'] = []
            return menus

        menus = []
        use_redis = settings.get_var('RESOURCE/USE_REDIS')
        key = 'MENU:{}'.format(parent)
        if use_redis:
            redis = functions.get_redis()
            v = redis.get(key)
            if v:
                menus = Serial.load(v)
        if not menus:
            p = cls.get(cls.c.name==parent)
            menus = _f(p.id)
            if menus and use_redis:
                redis.set(key, Serial.dump(menus))
        return menus

    @classmethod
    def iter_menu(cls, parent, user):
        from uliweb import functions

        def _f(_m):
            menus = []
            for row in _m:
                if row.get('permissions'):
                    if functions.has_permission(user, row['permissions']):
                        menus.append(row)
                else:
                    menus.append(row)
                if row.get('subs'):
                    row['subs'] = _f(row['subs'])
            return menus
        return _f(cls.get_menu(parent))

    def clear_menu(self):
        from uliweb import functions

        #只处理菜单根结点
        if self.type=='M0000':
            p = self
            while p.parent:
                p = p.parent
            key = 'MENU:{}'.format(p.name)
            redis = functions.get_redis()
            redis.delete(key)

    class Table:
        fields = [
            {'name':'name', 'width':120},
            {'name':'title', 'width':300},
            {'name':'value', 'width':200},
            {'name':'description'},
            {'name':'target', 'width':120},
            {'name':'status', 'width':60, 'align':'center'},
            {'name':'deploy_type', 'width':80, 'align':'center'},
            {'name':'icon', 'hidden':True},
            {'name':'order', 'hidden':True},
            {'name':'parent', 'hidden':True},
            {'name':'id', 'hidden':True},
            {'name':'has_children', 'hidden': True},
        ]

    class AddForm:
        fields = [
            'parent', 'name', 'title', 'value', 'description', 'target', 'status', 'icon', 'permissions'
        ]
        layout = {'fields': {
            'status': {'inline': True}
        }}

    class EditForm:
        fields = [
            'parent', 'name', 'title', 'value', 'description',
            'target', 'status', 'icon', 'permissions', 'modified_time'
        ]

        layout = {
            'fields': {
                'status': {'inline': True}
            },
        }

    class DetailView:
        fields = [
            'parent', 'name', 'title', 'value', 'description', 'target', 'status', 'icon',
            'permissions'
        ]
        layout = [
            '-- 基本信息 --',
            'parent',
            ['name', 'title', 'value'],
            'description',
            'target',
            'status',
            '-- 权限信息 --',
            'permissions'
        ]